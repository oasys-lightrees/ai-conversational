"""Tests for the rule-based StateService (pure; no DB, no network)."""

from __future__ import annotations

from backend.services.state_service import StateService

svc = StateService()


def test_empty_state():
    assert svc.completion_percentage({}) == 0
    assert set(svc.missing_fields({})) == {
        "property_type",
        "property_location",
        "business_stage",
    }
    assert svc.current_stage({}) == "PROPERTY_PROFILE"


def test_property_only_advances_to_business_stage():
    state = {"property_type": "VILLA", "property_location": "Bali"}
    assert svc.current_stage(state) == "BUSINESS_STAGE"


def test_planning_branch_requirements():
    state = {
        "property_type": "VILLA",
        "property_location": "Bali",
        "business_stage": "PLANNING",
    }
    assert set(svc.missing_fields(state)) == {"target_launch_date", "investment_budget"}
    assert svc.current_stage(state) == "BRANCH"
    # 3 of 5 required present -> 60%
    assert svc.completion_percentage(state) == 60


def test_underperforming_required_complete():
    state = {
        "property_type": "VILLA",
        "property_location": "Bali",
        "business_stage": "UNDERPERFORMING",
        "occupancy_rate": 65,
        "monthly_revenue": 1000,
        "average_room_rate": 100,
        "booking_platforms": ["Airbnb"],
    }
    assert svc.missing_fields(state) == []
    assert svc.completion_percentage(state) == 100
    # optional sections untouched -> stage keeps advancing
    assert svc.current_stage(state) == "OPERATIONS"


def test_zero_counts_as_present():
    state = {
        "property_type": "VILLA",
        "property_location": "Bali",
        "business_stage": "UNDERPERFORMING",
        "occupancy_rate": 0,
        "monthly_revenue": 0,
        "average_room_rate": 0,
        "booking_platforms": ["X"],
    }
    assert svc.missing_fields(state) == []


def test_unknown_stage_value_uses_only_always_required():
    state = {
        "property_type": "VILLA",
        "property_location": "Bali",
        "business_stage": "NONSENSE",
    }
    # unparseable stage -> no branch fields added; required = 3, all present
    assert svc.missing_fields(state) == []
    assert svc.completion_percentage(state) == 100
