"""FSM states for doctor search."""

from aiogram.fsm.state import State, StatesGroup
from dataclasses import dataclass
from typing import Optional


class SearchStates(StatesGroup):
    """States for doctor search flow."""

    selecting_specialty = State()
    selecting_hospital = State()
    selecting_doctor = State()


@dataclass
class SearchData:
    """Data stored during search."""

    specialty_id: Optional[int] = None
    specialty_name: Optional[str] = None
    hospital_id: Optional[int] = None
    hospital_name: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    doctor_address: Optional[str] = None
