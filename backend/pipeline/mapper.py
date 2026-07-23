"""Config-driven field mapping (the generalization of the old field_mapping).

Given a :class:`PipelineConfig`, splits an extracted ``{key: value}`` dict into
the DB destinations: values for known ``AssessmentData`` columns (coerced to the
column's Python type, incl. ORM enum members) versus values for config-defined
fields with no column (stored in the dynamic JSON area). Coercion never raises —
uncoercible or unknown keys are dropped — so one bad field can't lose the turn.

Hybrid storage: a field whose ``name`` matches an ``AssessmentData`` column is
stored there; everything else goes to JSON.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

from backend.models import AssessmentData
from backend.pipeline.config import FieldSpec, PipelineConfig

logger = logging.getLogger(__name__)

# Columns that are never a destination for extracted data.
_SYSTEM_COLUMNS = {"id", "assessment_id", "created_at", "updated_at", "branch_data"}

_TRUE = {"true", "yes", "ya", "1"}
_FALSE = {"false", "no", "tidak", "0"}


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


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


def _to_enum_member(enum_cls: type[Enum], canonical: str) -> Enum | None:
    if canonical in enum_cls.__members__:
        return enum_cls[canonical]
    for member in enum_cls:
        if str(member.value).upper() == canonical.upper():
            return member
    return None


class FieldMapper:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

        # Registry of real columns and their ORM enum classes.
        self._columns: set[str] = set()
        self._enum_classes: dict[str, type[Enum]] = {}
        for column in AssessmentData.__table__.columns:
            if column.name in _SYSTEM_COLUMNS:
                continue
            self._columns.add(column.name)
            enum_cls = getattr(column.type, "enum_class", None)
            if enum_cls is not None:
                self._enum_classes[column.name] = enum_cls

        # Input-key lookup (canonical names + aliases).
        self._by_key: dict[str, FieldSpec] = {}
        for spec in config.fields:
            self._by_key[spec.name] = spec
            for alias in spec.aliases:
                self._by_key[alias] = spec

    def known_input_keys(self) -> set[str]:
        return set(self._by_key)

    def map(self, fields: dict | None) -> tuple[dict, dict]:
        """Return ``(column_values, json_values)`` for the extracted ``fields``."""
        columns: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        for raw_key, value in (fields or {}).items():
            if value is None:
                continue
            spec = self._by_key.get(raw_key)
            if spec is None:
                logger.debug("dropping unmapped field %r", raw_key)
                continue
            coerced = self._coerce(spec, value)
            if coerced is None:
                continue
            if spec.name in self._columns:
                columns[spec.name] = coerced
            else:
                extra[spec.name] = coerced
        return columns, extra

    def _coerce(self, spec: FieldSpec, value: Any) -> Any:
        if spec.type == "enum":
            return self._coerce_enum(spec, value)
        if spec.type == "integer":
            return _coerce_int(value)
        if spec.type == "decimal":
            return _coerce_decimal(value)
        if spec.type == "boolean":
            return _coerce_bool(value)
        if spec.type == "list":
            coerced = _coerce_list(value)
            return coerced or None
        s = str(value).strip()
        return s or None

    def _coerce_enum(self, spec: FieldSpec, value: Any) -> Any:
        normalized_allowed = {_norm(option): option for option in spec.enum_options}
        canonical = normalized_allowed.get(_norm(value))
        if canonical is None:
            logger.debug("dropping uncoercible enum field %r=%r", spec.name, value)
            return None
        enum_cls = self._enum_classes.get(spec.name)
        if enum_cls is not None:
            return _to_enum_member(enum_cls, canonical)
        return canonical
