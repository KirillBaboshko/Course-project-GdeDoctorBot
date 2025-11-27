"""Message utilities for safe message editing."""

from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from typing import Optional


async def safe_message_transition(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
) -> Message:
    """
    Universal message transition handler for callbacks.

    Handles all types of message transitions:
    - Text to text (edit)
    - Photo to text (delete + send)
    - Any media to text (delete + send)

    This is the RECOMMENDED way to handle navigation in callback handlers.

    Args:
        callback: CallbackQuery object
        text: New message text
        reply_markup: Optional inline keyboard
        parse_mode: Parse mode for the message (default: HTML)

    Returns:
        The new or edited message
    """
    message = callback.message

    # Always try to delete and send new for callbacks
    # This is safer and more predictable
    try:
        await message.delete()
    except Exception:
        pass

    return await message.answer(
        text=text, reply_markup=reply_markup, parse_mode=parse_mode
    )


async def safe_edit_markup(
    message: Message, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> bool:
    """
    Safely edit message reply markup (keyboard).

    This is safer than edit_reply_markup as it handles cases where
    the message might not exist or can't be edited.

    Args:
        message: Message object to edit
        reply_markup: New inline keyboard

    Returns:
        True if successful, False otherwise
    """
    try:
        await message.edit_reply_markup(reply_markup=reply_markup)
        return True
    except TelegramBadRequest:
        # Message can't be edited (too old, deleted, etc.)
        return False
    except Exception:
        # Any other error
        return False
