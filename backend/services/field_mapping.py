"""Backward-compatible shim over the config-driven mapper.

The mapping logic now lives in ``backend.pipeline`` and is driven by a
``PipelineConfig``. This module preserves the original module-level API bound to
``DEFAULT_CONFIG`` so existing callers and tests keep working. New code should
use ``FieldMapper(config)`` directly.
"""

from __future__ import annotations

from backend.pipeline.default_config import DEFAULT_CONFIG
from backend.pipeline.mapper import FieldMapper

_default_mapper = FieldMapper(DEFAULT_CONFIG)

# Alias -> canonical name, derived from the default config (e.g. location ->
# property_location, booking_channels -> booking_platforms).
RENAME: dict[str, str] = {
    alias: field.name for field in DEFAULT_CONFIG.fields for alias in field.aliases
}


def map_extracted_to_columns(fields: dict | None) -> tuple[dict, dict]:
    """Split extracted ``fields`` into (column_values, json_values)."""
    return _default_mapper.map(fields)


def known_input_fields() -> set[str]:
    """Every input key the default mapper accepts (names + aliases)."""
    return _default_mapper.known_input_keys()
