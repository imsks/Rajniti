import json
from enum import Enum as _Enum
from pathlib import Path
from typing import List

# Load states from data/states.json
_STATES_PATH = Path(__file__).resolve().parents[1] / "data" / "states.json"
try:
    with open(_STATES_PATH, "r", encoding="utf-8") as _f:
        STATES: List[str] = json.load(_f)
except Exception:
    STATES = []


class RelationEnum(str, _Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    SIBLING = "SIBLING"
    SON = "SON"
    DAUGHTER = "DAUGHTER"
    WIFE = "WIFE"
    HUSBAND = "HUSBAND"
    OTHERS = "OTHERS"


class QualificationEnum(str, _Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    DIPLOMA = "DIPLOMA"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTORATE = "DOCTORATE"
    PROFESSIONAL = "PROFESSIONAL"
    OTHERS = "OTHERS"


class PoliticianType(str, _Enum):
    MP = "MP"
    MLA = "MLA"


class StatusEnum(str, _Enum):
    WON = "WON"
    LOST = "LOST"
    CONTESTED = "CONTESTED"


def _make_state_enum():
    try:
        members = {s.upper().replace(" ", "_").replace("-", "_"): s for s in STATES}
        return _Enum("State", members, type=str)
    except Exception:
        return _Enum("State", {"UNKNOWN": "UNKNOWN"}, type=str)


State = _make_state_enum()
