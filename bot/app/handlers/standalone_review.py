"""Standalone review handlers - works without backend."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from app.keyboards.inline import build_reviews_keyboard, build_cancel_keyboard
from app.states.review import ReviewStates
from app.states.search import SearchData
from app.utils import safe_message_transition
from app.constants import Messages, Limits

router = Router()
logger = logging.getLogger(__name__)


async def get_data_service(callback_or_message):
    """Get data service from bot context."""
    # Try to get from bot's context
    if hasattr(callback_or_message.bot, '_data_service'):
        return callback_or_message.bot._data_service
    return None


@router.callback_query(F.data.startswith("reviews:"))
async def show_reviews(callback: CallbackQuery, state: FSMContext):
    """Show reviews for doctor."""
    doctor_id = int(callback.data.split(":")[1])

    try:
        # Get hospital_id from state
        data = await state.get_data()
        hospital_id = data.get("hospital_id", 0)
        
        logger.info(f"Showing reviews for doctor_id={doctor_id}, hospital_id={hospital_id}")

        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get reviews
        reviews = await data_service.get_reviews(doctor_id=doctor_id)

        if not reviews:
            text = "📝 <b>Отзывы</b>\n\nПока нет отзывов об этом враче.\nБудьте первым!"
        else:
            text = "📝 <b>Отзывы</b>\n\n"

            for review in reviews[:10]:  # Show max 10 reviews
                user = review.get("user_name", "Аноним")
                review_text = review.get("review_text", "")
                date = review.get("created_at", "")[:10]  # YYYY-MM-DD

                text += f"👤 <b>{user}</b> ({date})\n{review_text}\n\n"

        keyboard = build_reviews_keyboard(doctor_id, hospital_id)

        await safe_message_transition(callback, text, reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing reviews: {e}")
        await callback.answer("Ошибка при загрузке отзывов", show_alert=True)


@router.callback_query(F.data.startswith("write_review:"))
async def start_write_review(callback: CallbackQuery, state: FSMContext):
    """Start writing review process."""
    logger.info(f"Starting write review, callback data: {callback.data}")
    doctor_id = int(callback.data.split(":")[1])
    hospital_id = int(callback.data.split(":")[2])

    logger.info(f"Parsed doctor_id={doctor_id}, hospital_id={hospital_id}")
    
    # Store doctor and hospital IDs
    await state.update_data(doctor_id=doctor_id, hospital_id=hospital_id)
    await state.set_state(ReviewStates.waiting_for_review)
    
    logger.info(f"State updated with doctor_id={doctor_id}, hospital_id={hospital_id}")

    text = (
        "✍️ <b>Написать отзыв</b>\n\n"
        "Пожалуйста, напишите ваш отзыв о враче.\n"
        f"Минимум {Limits.REVIEW_MIN_LENGTH} символов, "
        f"максимум {Limits.REVIEW_MAX_LENGTH} символов."
    )

    # Delete previous message and send new one
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(
        text,
        reply_markup=build_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ReviewStates.waiting_for_review)
async def process_review(message: Message, state: FSMContext):
    """Process review text."""
    review_text = message.text.strip()

    # Validate review length
    if len(review_text) < Limits.REVIEW_MIN_LENGTH:
        await message.answer(
            f"❌ Отзыв слишком короткий. Минимум {Limits.REVIEW_MIN_LENGTH} символов."
        )
        return

    if len(review_text) > Limits.REVIEW_MAX_LENGTH:
        await message.answer(
            f"❌ Отзыв слишком длинный. Максимум {Limits.REVIEW_MAX_LENGTH} символов."
        )
        return

    try:
        # Get data service
        data_service = await get_data_service(message)
        if not data_service:
            await message.answer("Ошибка сервиса данных")
            await state.clear()
            return

        # Get stored data
        data = await state.get_data()
        doctor_id = data.get("doctor_id")
        hospital_id = data.get("hospital_id")

        logger.info(f"Retrieved from state: doctor_id={doctor_id}, hospital_id={hospital_id}")

        if not doctor_id or not hospital_id:
            logger.error(f"Missing data in state: doctor_id={doctor_id}, hospital_id={hospital_id}, full_data={data}")
            await message.answer("Ошибка: не найдены данные о враче")
            await state.clear()
            return

        # Get user name
        user_name = message.from_user.full_name or message.from_user.username or "Аноним"

        # Create review
        await data_service.create_review(
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            user_name=user_name,
            review_text=review_text,
        )

        # Import keyboard function
        from app.keyboards.inline import build_review_success_keyboard
        
        await message.answer(
            "✅ <b>Отзыв успешно добавлен!</b>\n\nСпасибо за ваш отзыв. "
            "Он поможет другим пользователям при выборе врача.",
            reply_markup=build_review_success_keyboard(doctor_id),
            parse_mode="HTML",
        )

        # Clear FSM state but keep data (doctor_id, hospital_id) for navigation
        await state.set_state(None)

    except Exception as e:
        logger.error(f"Error creating review: {e}")
        await message.answer("❌ Ошибка при сохранении отзыва. Попробуйте позже.")
        await state.clear()


@router.callback_query(F.data == "cancel_review")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    """Cancel review writing."""
    await state.clear()
    await callback.message.answer("❌ Написание отзыва отменено.")
    await callback.answer()
