"""Map extractor output (schema-doc vocabulary) to ORM columns / branch_data.

The extraction model (Prompt 1, ``docs/05``) speaks the vocabulary in
``docs/03``; the database uses column names, enum members, and a ``branch_data``
JSONB blob for stage-specific fields. Every mismatch here is a *silent
data-loss* bug — a dropped field means ``completion_percentage`` never rises and
the conversation loops asking the same question forever. So all translation
lives in this one module, with its own test suite (``tests/test_field_mapping``).

The single entry point is :func:`map_extracted_to_columns`, which returns a
``(column_values, branch_data_values)`` pair. Coercion never raises: a value it
cannot interpret is dropped (logged at debug), so one bad field can never lose
the whole turn.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

from backend.models.enums import (
    BusinessStage,
    OwnershipType,
    ProcessType,
    PropertyType,
)

logger = logging.getLogger(__name__)

# --- Vocabulary reconciliation (docs key -> DB destination) -------------------

# Renames: the extractor key differs from the column name.
#   ``booking_channels`` (docs/03 Underperforming branch) is treated as the same
#   field as the ``booking_platforms`` column (Open Question 2 in the plan).
RENAME: dict[str, str] = {
    "location": "property_location",
    "booking_channels": "booking_platforms",
}

# Columns backed by an enum type; values arrive as free text ("Villa").
ENUM_COLUMNS: dict[str, type[Enum]] = {
    "property_type": PropertyType,
    "business_stage": BusinessStage,
    "ownership_type": OwnershipType,
    "check_in_process": ProcessType,
    "housekeeping_process": ProcessType,
    "maintenance_process": ProcessType,
    "complaint_handling": ProcessType,
}

INT_COLUMNS: frozenset[str] = frozenset({"total_units", "staff_count"})
DECIMAL_COLUMNS: frozenset[str] = frozenset(
    {"occupancy_rate", "monthly_revenue", "average_room_rate"}
)
BOOL_COLUMNS: frozenset[str] = frozenset({"uses_pms"})
STR_COLUMNS: frozenset[str] = frozenset(
    {"property_name", "property_location", "pms_name", "accounting_system"}
)
LIST_COLUMNS: frozenset[str] = frozenset(
    {"booking_platforms", "communication_channels", "pain_points", "business_goals"}
)

# Stage-specific fields with no dedicated column; routed into ``branch_data``.
BRANCH_DATA_FIELDS: frozenset[str] = frozenset(
    {
        "target_launch_date",
        "investment_budget",
        "reason_not_operating",
        "main_obstacle",
        "expansion_plan",
        "automation_interest",
    }
)


# --- Coercion helpers (all return None on failure; callers drop None) ---------


def _coerce_enum(enum_cls: type[Enum], value: Any) -> Enum | None:
    if isinstance(value, enum_cls):
        return value
    key = str(value).strip().upper().replace(" ", "_").replace("-", "_")
    if key in enum_cls.__members__:
        return enum_cls[key]
    for member in enum_cls:
        if str(member.value).upper() == key:
            return member
    return None


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def _coerce_decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


_TRUE = {"true", "yes", "ya", "1"}
_FALSE = {"false", "no", "tidak", "0"}


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in _TRUE:
            return True
        if s in _FALSE:
            return False
    return None


def _coerce_list(value: Any) -> list | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    return [value]


# --- Entry point --------------------------------------------------------------


def map_extracted_to_columns(fields: dict | None) -> tuple[dict, dict]:
    """Translate extracted ``fields`` into DB destinations.

    Returns ``(column_values, branch_data_values)``:

    - ``column_values`` maps directly onto ``AssessmentData`` columns (enums
      coerced to members, numbers/bools/lists normalized).
    - ``branch_data_values`` holds stage-specific keys destined for the
      ``branch_data`` JSONB blob.

    Keys that are unknown or fail coercion are dropped (logged at debug), never
    raised — so a single bad field cannot lose the rest of the turn.
    """
    columns: dict[str, Any] = {}
    branch: dict[str, Any] = {}

    for raw_key, value in (fields or {}).items():
        if value is None:
            continue
        key = RENAME.get(raw_key, raw_key)

        if key in BRANCH_DATA_FIELDS:
            branch[key] = value
        elif key in ENUM_COLUMNS:
            coerced = _coerce_enum(ENUM_COLUMNS[key], value)
            if coerced is not None:
                columns[key] = coerced
            else:
                logger.debug("dropping uncoercible enum field %r=%r", raw_key, value)
        elif key in INT_COLUMNS:
            coerced = _coerce_int(value)
            if coerced is not None:
                columns[key] = coerced
        elif key in DECIMAL_COLUMNS:
            coerced = _coerce_decimal(value)
            if coerced is not None:
                columns[key] = coerced
        elif key in BOOL_COLUMNS:
            coerced = _coerce_bool(value)
            if coerced is not None:
                columns[key] = coerced
        elif key in LIST_COLUMNS:
            coerced = _coerce_list(value)
            if coerced:
                columns[key] = coerced
        elif key in STR_COLUMNS:
            s = str(value).strip()
            if s:
                columns[key] = s
        else:
            logger.debug("dropping unmapped field %r", raw_key)

    return columns, branch
