"""Tests for the field-mapping module (pure; no DB, no network).

This is the highest-frequency silent-bug surface (a dropped field means the
conversation loops forever), so it gets first-class coverage.
"""

from __future__ import annotations

from decimal import Decimal

from backend.models.enums import BusinessStage, PropertyType
from backend.services.field_mapping import RENAME, map_extracted_to_columns


def test_location_renamed_to_property_location():
    cols, branch = map_extracted_to_columns({"location": "Bali"})
    assert cols == {"property_location": "Bali"}
    assert branch == {}


def test_property_type_string_to_enum():
    cols, _ = map_extracted_to_columns({"property_type": "Villa"})
    assert cols["property_type"] is PropertyType.VILLA


def test_enum_multiword_and_casing():
    cols, _ = map_extracted_to_columns({"property_type": "boarding house"})
    assert cols["property_type"] is PropertyType.BOARDING_HOUSE


def test_business_stage_enum():
    cols, _ = map_extracted_to_columns({"business_stage": "Underperforming"})
    assert cols["business_stage"] is BusinessStage.UNDERPERFORMING


def test_numeric_coercion():
    cols, _ = map_extracted_to_columns({"total_units": "12", "occupancy_rate": "65.5"})
    assert cols["total_units"] == 12
    assert cols["occupancy_rate"] == Decimal("65.5")


def test_bool_coercion_indonesian():
    cols, _ = map_extracted_to_columns({"uses_pms": "ya"})
    assert cols["uses_pms"] is True


def test_list_wrapping():
    cols, _ = map_extracted_to_columns({"pain_points": "Low Occupancy"})
    assert cols["pain_points"] == ["Low Occupancy"]


def test_booking_channels_renamed_to_platforms():
    cols, _ = map_extracted_to_columns({"booking_channels": ["Airbnb"]})
    assert cols["booking_platforms"] == ["Airbnb"]


def test_branch_field_routed_to_branch_dict():
    cols, branch = map_extracted_to_columns({"target_launch_date": "2026-01"})
    assert cols == {}
    assert branch == {"target_launch_date": "2026-01"}


def test_unknown_key_dropped():
    cols, branch = map_extracted_to_columns({"favorite_color": "blue"})
    assert cols == {} and branch == {}


def test_uncoercible_enum_dropped_not_raised():
    cols, _ = map_extracted_to_columns({"property_type": "Spaceship"})
    assert "property_type" not in cols


def test_none_values_skipped():
    cols, branch = map_extracted_to_columns({"location": None})
    assert cols == {} and branch == {}


def test_empty_input():
    assert map_extracted_to_columns(None) == ({}, {})
    assert map_extracted_to_columns({}) == ({}, {})


def test_no_documented_field_silently_vanishes():
    """Every documented extractable field must land in columns or branch_data."""
    documented = {
        "property_name": "Sunset Villa",
        "property_type": "Villa",
        "location": "Bali",
        "ownership_type": "Owned",
        "total_units": 12,
        "business_stage": "Underperforming",
        "occupancy_rate": 65,
        "monthly_revenue": 1000,
        "average_room_rate": 100,
        "staff_count": 5,
        "check_in_process": "Manual",
        "housekeeping_process": "Semi Digital",
        "maintenance_process": "Manual",
        "complaint_handling": "Manual",
        "uses_pms": True,
        "pms_name": "Cloudbeds",
        "accounting_system": "Xero",
        "booking_platforms": ["Airbnb"],
        "communication_channels": ["WhatsApp"],
        "pain_points": ["Low Occupancy"],
        "business_goals": ["Increase Revenue"],
        "target_launch_date": "2026-01",
        "investment_budget": 50000,
        "reason_not_operating": "renovation",
        "main_obstacle": "permits",
        "expansion_plan": "second villa",
        "automation_interest": "high",
    }
    cols, branch = map_extracted_to_columns(documented)
    landed = set(cols) | set(branch)
    expected = {RENAME.get(k, k) for k in documented}
    missing = expected - landed
    assert not missing, f"fields silently vanished: {missing}"
