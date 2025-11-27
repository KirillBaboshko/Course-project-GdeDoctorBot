"""Standalone doctor search handlers - works without backend."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
import logging

from app.keyboards.inline import build_paginated_keyboard, build_doctor_actions_keyboard
from app.states.search import SearchStates, SearchData
from app.utils import safe_message_transition, safe_edit_markup
from app.constants import Messages, LogMessages

router = Router()
logger = logging.getLogger(__name__)


async def get_data_service(callback: CallbackQuery):
    """Get data service from bot context."""
    # Try to get from bot's context
    if hasattr(callback.bot, '_data_service'):
        return callback.bot._data_service
    return None


async def show_doctor_card(
    callback: CallbackQuery,
    doctor_id: int,
    hospital_id: int,
) -> None:
    """
    Show doctor card with map.

    Args:
        callback: Callback query
        doctor_id: Doctor ID
        hospital_id: Hospital ID
    """
    try:
        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get doctor details
        doctor = await data_service.get_doctor(
            doctor_id=doctor_id, hospital_id=hospital_id
        )

        if not doctor:
            await callback.answer("Врач не найден", show_alert=True)
            return

        # Get coordinates for map link and static map
        lon, lat = 0, 0
        coords_available = False
        
        # Try to geocode address (requires API key)
        if data_service.yandex_api_key and doctor.get("address") and doctor["address"] != "Адрес не указан":
            try:
                coords = await data_service.geocode(doctor["address"])
                lon, lat = coords["lon"], coords["lat"]
                coords_available = True
                logger.info(f"Geocoded address: {doctor['address']} -> {lon}, {lat}")
            except Exception as e:
                logger.warning(f"Failed to geocode address: {e}")
        
        # Try to get static map (doesn't require API key!)
        map_photo = None
        if coords_available:
            try:
                map_photo = await data_service.get_static_map(lon=lon, lat=lat)
                logger.info("✅ Static map loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load static map: {e}")

        # Build message
        message = f"👨‍⚕️ <b>{doctor['name']}</b>\n\n"
        message += f"🏥 <b>Больница:</b> {doctor['hospital_name']}\n"
        message += f"🩺 <b>Специальность:</b> {doctor['specialty_name']}\n"
        
        if doctor.get("address") and doctor["address"] != "Адрес не указан":
            message += f"📍 <b>Адрес:</b> {doctor['address']}\n"
        
        # Send message with or without map
        keyboard = build_doctor_actions_keyboard(
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            lon=lon,
            lat=lat,
        )
        
        # Delete previous message
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        # Send message with or without photo
        if map_photo:
            await callback.message.answer_photo(
                BufferedInputFile(map_photo, filename="map.png"),
                caption=message,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        else:
            await callback.message.answer(
                message,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

        await callback.answer()

    except Exception as e:
        logger.error(LogMessages.ERROR_SHOWING_DOCTOR_CARD.format(error=e))
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data == "find_doctor")
async def start_search(callback: CallbackQuery, state: FSMContext):
    """Start doctor search process."""
    try:
        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get specialties
        specialties_data = await data_service.get_specialties(limit=100)
        specialties = specialties_data.get("items", [])

        if not specialties:
            await callback.answer("Специальности не найдены", show_alert=True)
            return

        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=specialties,
            callback_prefix="specialty",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
        )

        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            "🔍 <b>Поиск врача</b>\n\nШаг 1 из 3: Выберите специальность врача",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        await state.set_state(SearchStates.selecting_specialty)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error starting search: {e}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data.startswith("specialty:"))
async def select_specialty(callback: CallbackQuery, state: FSMContext):
    """Handle specialty selection."""
    logger.info(f"Callback data: {callback.data}")
    try:
        specialty_id = int(callback.data.split(":")[1])
        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get hospitals for this specialty
        hospitals_data = await data_service.get_hospitals(
            specialty_id=specialty_id, limit=100
        )
        hospitals = hospitals_data.get("items", [])

        if not hospitals:
            await callback.answer("Больницы не найдены", show_alert=True)
            return

        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=hospitals,
            callback_prefix="hospital",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
            back_callback="back_to_specialties",
        )

        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            "🔍 <b>Поиск врача</b>\n\nШаг 2 из 3: Выберите медицинское учреждение",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        # Store specialty ID
        await state.update_data(specialty_id=specialty_id)
        await state.set_state(SearchStates.selecting_hospital)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error selecting specialty: {e}, callback data: {callback.data}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data.startswith("hospital:"))
async def select_hospital(callback: CallbackQuery, state: FSMContext):
    """Handle hospital selection."""
    logger.info(f"Callback data: {callback.data}")
    try:
        hospital_id = int(callback.data.split(":")[1])
        data = await state.get_data()
        specialty_id = data.get("specialty_id")

        if not specialty_id:
            await callback.answer("Ошибка: не выбрана специальность", show_alert=True)
            return

        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get doctors for this hospital and specialty
        doctors_data = await data_service.get_doctors(
            hospital_id=hospital_id, specialty_id=specialty_id, limit=100
        )
        doctors = doctors_data.get("items", [])

        if not doctors:
            await callback.answer("Врачи не найдены", show_alert=True)
            return

        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=doctors,
            callback_prefix="doctor",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
            back_callback="back_to_hospitals",
        )

        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            "🔍 <b>Поиск врача</b>\n\nШаг 3 из 3: Выберите врача",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        # Store hospital ID
        await state.update_data(hospital_id=hospital_id)
        await state.set_state(SearchStates.selecting_doctor)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error selecting hospital: {e}, callback data: {callback.data}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data.startswith("doctor:"))
async def select_doctor(callback: CallbackQuery, state: FSMContext):
    """Handle doctor selection."""
    logger.info(f"Callback data: {callback.data}")
    try:
        doctor_id = int(callback.data.split(":")[1])
        data = await state.get_data()
        hospital_id = data.get("hospital_id")

        if not hospital_id:
            await callback.answer("Ошибка: не выбрана больница", show_alert=True)
            return

        # Get specialty and hospital names for display
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get doctor details to extract names
        doctor = await data_service.get_doctor(doctor_id, hospital_id)
        if not doctor:
            await callback.answer("Врач не найден", show_alert=True)
            return

        # Store doctor and hospital info in state for navigation and reviews
        await state.update_data(doctor_id=doctor_id, hospital_id=hospital_id)
        
        # Show doctor card
        await show_doctor_card(
            callback=callback,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
        )

    except Exception as e:
        logger.error(f"Error selecting doctor: {e}, callback data: {callback.data}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data == "back_to_doctors")
async def back_to_doctors(callback: CallbackQuery, state: FSMContext):
    """Go back to doctor selection."""
    logger.info("Back to doctors list")
    try:
        data = await state.get_data()
        hospital_id = data.get("hospital_id")
        specialty_id = data.get("specialty_id")

        if not hospital_id or not specialty_id:
            await callback.answer("Ошибка: данные поиска потеряны", show_alert=True)
            await start_search(callback, state)
            return

        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get doctors for this hospital and specialty
        doctors_data = await data_service.get_doctors(
            hospital_id=hospital_id, specialty_id=specialty_id, limit=100
        )
        doctors = doctors_data.get("items", [])

        if not doctors:
            await callback.answer("Врачи не найдены", show_alert=True)
            return

        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=doctors,
            callback_prefix="doctor",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
            back_callback="back_to_hospitals",
        )

        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            "🔍 <b>Поиск врача</b>\n\nШаг 3 из 3: Выберите врача",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        await state.set_state(SearchStates.selecting_doctor)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error going back to doctors: {e}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data == "back_to_hospitals")
async def back_to_hospitals(callback: CallbackQuery, state: FSMContext):
    """Go back to hospital selection."""
    logger.info("Back to hospitals list")
    try:
        data = await state.get_data()
        specialty_id = data.get("specialty_id")

        if not specialty_id:
            await callback.answer("Ошибка: специальность не выбрана", show_alert=True)
            await start_search(callback, state)
            return

        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return

        # Get hospitals for this specialty
        hospitals_data = await data_service.get_hospitals(
            specialty_id=specialty_id, limit=100
        )
        hospitals = hospitals_data.get("items", [])

        if not hospitals:
            await callback.answer("Больницы не найдены", show_alert=True)
            return

        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=hospitals,
            callback_prefix="hospital",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
            back_callback="back_to_specialties",
        )

        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            "🔍 <b>Поиск врача</b>\n\nШаг 2 из 3: Выберите медицинское учреждение",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        await state.set_state(SearchStates.selecting_hospital)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error going back to hospitals: {e}")
        await callback.answer(Messages.ERROR_LOADING_DATA, show_alert=True)


@router.callback_query(F.data == "back_to_specialties")
async def back_to_specialties(callback: CallbackQuery, state: FSMContext):
    """Go back to specialty selection."""
    logger.info("Back to specialties list")
    await start_search(callback, state)


@router.callback_query(F.data == "new_search")
async def new_search(callback: CallbackQuery, state: FSMContext):
    """Start new search."""
    logger.info("Starting new search")
    await state.clear()
    await start_search(callback, state)



@router.callback_query(F.data.startswith("back_to_doctor:"))
async def back_to_doctor(callback: CallbackQuery, state: FSMContext):
    """Go back to doctor details from reviews."""
    doctor_id = int(callback.data.split(":")[1])
    
    logger.info(f"Back to doctor {doctor_id}")
    try:
        data = await state.get_data()
        hospital_id = data.get("hospital_id")

        if not hospital_id:
            await callback.answer("Ошибка: данные о больнице потеряны", show_alert=True)
            await start_search(callback, state)
            return

        # Show doctor card
        await show_doctor_card(
            callback=callback,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
        )

    except Exception as e:
        logger.error(f"Error going back to doctor: {e}")
        await callback.answer("Ошибка при загрузке данных", show_alert=True)
