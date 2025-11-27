"""Start and help command handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import build_start_keyboard
from app.utils import safe_message_transition
from app.constants import Messages

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Clear any existing state
    await state.clear()

    await message.answer(
        Messages.WELCOME, reply_markup=build_start_keyboard(), parse_mode="HTML"
    )


@router.callback_query(F.data == "start")
async def callback_start(callback: CallbackQuery, state: FSMContext):
    """Handle start button."""
    await state.clear()

    await safe_message_transition(
        callback, Messages.WELCOME, reply_markup=build_start_keyboard()
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(Messages.HELP, parse_mode="HTML")


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Handle help button."""
    from app.keyboards.inline import build_help_keyboard

    await safe_message_transition(
        callback, Messages.HELP, reply_markup=build_help_keyboard()
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(Messages.NOTHING_TO_CANCEL)
        return

    await state.clear()
    await message.answer(Messages.CANCEL_COMMAND, reply_markup=build_start_keyboard())


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Handle cancel button."""
    await state.clear()

    await safe_message_transition(
        callback, Messages.CANCEL_MESSAGE, reply_markup=build_start_keyboard()
    )
    await callback.answer()
