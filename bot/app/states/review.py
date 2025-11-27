"""FSM states for reviews."""

from aiogram.fsm.state import State, StatesGroup


class ReviewStates(StatesGroup):
    """States for review flow."""

    waiting_for_review = State()
