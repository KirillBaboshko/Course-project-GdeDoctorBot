"""Inline keyboards for bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from app.constants import ButtonLabels


def build_paginated_keyboard(
    items: List[dict],
    callback_prefix: str,
    page: int,
    total_pages: int,
    id_key: str = "id",
    name_key: str = "name",
    back_callback: str = None,
) -> InlineKeyboardMarkup:
    """Build paginated inline keyboard.

    Args:
        items: List of items to display
        callback_prefix: Prefix for callback data
        page: Current page number
        total_pages: Total number of pages
        id_key: Key for item ID in dict
        name_key: Key for item name in dict
        back_callback: Optional callback data for back button

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    # Add item buttons
    for item in items:
        builder.button(
            text=item[name_key], callback_data=f"{callback_prefix}:{item[id_key]}"
        )

    # Adjust to one button per row
    builder.adjust(1)

    # Add pagination buttons
    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text=ButtonLabels.PREV,
                callback_data=f"page:{callback_prefix}:{page - 1}",
            )
        )

    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text=ButtonLabels.NEXT,
                callback_data=f"page:{callback_prefix}:{page + 1}",
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Add navigation buttons
    nav_buttons = []
    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(text=ButtonLabels.BACK, callback_data=back_callback)
        )
    nav_buttons.append(
        InlineKeyboardButton(text=ButtonLabels.HOME, callback_data="start")
    )
    builder.row(*nav_buttons)

    return builder.as_markup()


def build_doctor_actions_keyboard(
    doctor_id: int, hospital_id: int, lon: float, lat: float
) -> InlineKeyboardMarkup:
    """Build keyboard with doctor actions.

    Args:
        doctor_id: Doctor ID
        hospital_id: Hospital ID
        lon: Longitude
        lat: Latitude

    Returns:
        InlineKeyboardMarkup
    """
    # Yandex Maps URL
    maps_url = f"https://yandex.ru/maps/?ll={lon},{lat}&z=16&pt={lon},{lat},comma"

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=ButtonLabels.VIEW_ON_MAP, url=maps_url))

    builder.row(
        InlineKeyboardButton(
            text=ButtonLabels.VIEW_REVIEWS, callback_data=f"reviews:{doctor_id}"
        ),
        InlineKeyboardButton(
            text=ButtonLabels.WRITE_REVIEW,
            callback_data=f"write_review:{doctor_id}:{hospital_id}",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text=ButtonLabels.BACK_TO_LIST, callback_data="back_to_doctors"
        )
    )

    builder.row(
        InlineKeyboardButton(text=ButtonLabels.NEW_SEARCH, callback_data="new_search"),
        InlineKeyboardButton(text=ButtonLabels.HOME, callback_data="start"),
    )

    return builder.as_markup()


def build_reviews_keyboard(doctor_id: int, hospital_id: int = 0) -> InlineKeyboardMarkup:
    """Build keyboard for reviews page.

    Args:
        doctor_id: Doctor ID
        hospital_id: Hospital ID (optional, defaults to 0)

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=ButtonLabels.WRITE_REVIEW, callback_data=f"write_review:{doctor_id}:{hospital_id}"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=ButtonLabels.BACK_TO_DOCTOR,
            callback_data=f"back_to_doctor:{doctor_id}",
        ),
        InlineKeyboardButton(text=ButtonLabels.HOME, callback_data="start"),
    )

    return builder.as_markup()


def build_start_keyboard() -> InlineKeyboardMarkup:
    """Build start menu keyboard.

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=ButtonLabels.FIND_DOCTOR, callback_data="find_doctor")
    )

    builder.row(InlineKeyboardButton(text=ButtonLabels.HELP, callback_data="help"))

    return builder.as_markup()


def build_help_keyboard() -> InlineKeyboardMarkup:
    """Build help menu keyboard.

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=ButtonLabels.HOME, callback_data="start"))

    return builder.as_markup()


def build_review_success_keyboard(doctor_id: int) -> InlineKeyboardMarkup:
    """Build keyboard after successful review submission.

    Args:
        doctor_id: Doctor ID to return to

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=ButtonLabels.BACK_TO_DOCTOR,
            callback_data=f"back_to_doctor:{doctor_id}",
        )
    )

    builder.row(
        InlineKeyboardButton(text=ButtonLabels.NEW_SEARCH, callback_data="new_search"),
        InlineKeyboardButton(text=ButtonLabels.HOME, callback_data="start"),
    )

    return builder.as_markup()


def build_cancel_keyboard() -> InlineKeyboardMarkup:
    """Build cancel keyboard.

    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=ButtonLabels.CANCEL, callback_data="cancel"))

    return builder.as_markup()
