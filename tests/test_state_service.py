"""Tests for the rule-based StateService (pure; no DB, no network)."""

from __future__ import annotations

from backend.pipeline import DEFAULT_CONFIG
from backend.services.state_service import StateService

svc = StateService()

_BY_NAME = {f.name: f for f in DEFAULT_CONFIG.fields}
_ALWAYS_REQUIRED = [f.name for f in DEFAULT_CONFIG.fields if f.required]
_PROPERTY_PROFILE = [
    "property_name",
    "property_type",
    "property_location",
    "ownership_type",
    "total_units",
]

_DUMMY = {"string": "x", "integer": 1, "decimal": 1, "boolean": True, "list": ["x"]}


def _value(name: str):
    spec = _BY_NAME[name]
    return spec.enum_options[0] if spec.type == "enum" else _DUMMY[spec.type]


def fill(*names: str, **overrides) -> dict:
    """A state with ``names`` populated with type-appropriate placeholder values."""
    state = {name: _value(name) for name in names}
    state.update(overrides)
    return state


def fill_required(**overrides) -> dict:
    """A state with every always-required field populated."""
    return fill(*_ALWAYS_REQUIRED, **overrides)


def test_empty_state_requires_every_section():
    missing = set(svc.missing_fields({}))
    assert svc.completion_percentage({}) == 0
    assert svc.current_stage({}) == "PROPERTY_PROFILE"
    # Each section the assessment is meant to cover is represented from the
    # start — only required fields are ever asked about (see default_config).
    assert {
        "property_type",
        "business_stage",
        "staff_count",
        "uses_pms",
        "pain_points",
        "business_goals",
    } <= missing
    # ...but no stage-specific branch field, since the stage is still unknown.
    assert missing.isdisjoint({"target_launch_date", "occupancy_rate", "expansion_plan"})


def test_property_profile_complete_advances_to_business_stage():
    state = fill(*_PROPERTY_PROFILE)
    assert svc.current_stage(state) == "BUSINESS_STAGE"
    assert "business_stage" in svc.missing_fields(state)


def test_profile_and_branch_alone_do_not_complete_the_assessment():
    """Regression: the assessment used to close after ~5 answers, never asking
    about operations, technology, pain points, or goals."""
    state = fill(
        *_PROPERTY_PROFILE,
        business_stage="UNDERPERFORMING",
        occupancy_rate=65,
        monthly_revenue=1000,
        average_room_rate=100,
        booking_platforms=["Airbnb"],
    )
    assert set(svc.missing_fields(state)) == {
        "staff_count",
        "check_in_process",
        "housekeeping_process",
        "maintenance_process",
        "complaint_handling",
        "uses_pms",
        "accounting_system",
        "communication_channels",
        "pain_points",
        "business_goals",
    }
    assert svc.current_stage(state) == "OPERATIONS"
    # 10 of 20 required (16 always + 4 underperforming branch) present.
    assert svc.completion_percentage(state) == 50


def test_complete_when_every_required_field_present():
    state = fill_required(
        business_stage="OPERATING_SUCCESSFULLY",
        expansion_plan="x",
        automation_interest="x",
        uses_pms=False,  # so pms_name stays optional
    )
    assert svc.missing_fields(state) == []
    assert svc.completion_percentage(state) == 100
    assert svc.current_stage(state) == "COMPLETE"


def test_pms_name_required_only_when_a_pms_is_used():
    spec = _BY_NAME["pms_name"]
    assert spec.is_required({"uses_pms": True})
    assert not spec.is_required({"uses_pms": False})
    assert not spec.is_required({})


def test_planning_branch_requirements():
    state = fill_required(business_stage="PLANNING", uses_pms=False)
    assert set(svc.missing_fields(state)) == {"target_launch_date", "investment_budget"}
    assert svc.current_stage(state) == "BRANCH"
    # 16 of 18 required (16 always + 2 planning branch) present.
    assert svc.completion_percentage(state) == 89


def test_zero_counts_as_present():
    state = fill_required(
        business_stage="UNDERPERFORMING",
        occupancy_rate=0,
        monthly_revenue=0,
        average_room_rate=0,
        booking_platforms=["X"],
        total_units=0,
        staff_count=0,
        uses_pms=False,
    )
    assert svc.missing_fields(state) == []


def test_unknown_stage_value_uses_only_always_required():
    state = fill_required(business_stage="NONSENSE", uses_pms=False)
    # unparseable stage -> no branch fields added; the 16 always-required are present
    assert svc.missing_fields(state) == []
    assert svc.completion_percentage(state) == 100
