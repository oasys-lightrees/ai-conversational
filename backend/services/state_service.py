"""State service — required-field detection, completion, and stage tracking.

Prompt 2 in ``docs/05`` frames missing-field detection as an LLM step, but the
required-field rules in ``docs/03`` are deterministic, so this implementation is
**rule-based and needs no API key**. That lets ``AssessmentService.update_data``
recompute completion synchronously (Decision D3 in the plan) without a model
call. The constructor still accepts an ``OpenAIService`` for forward
compatibility, but the methods below do not use it.

State shape: these methods operate on a flat ``dict`` produced by
``AssessmentService.to_state_dict`` — column values (enums as their string
value) plus the ``branch_data`` keys flattened to the top level, with absent
fields omitted.
"""

from __future__ import annotations

from backend.models.enums import BusinessStage
from backend.services.openai_service import OpenAIService

# Required regardless of branch (docs/03: property_type, location, business_stage).
REQUIRED_ALWAYS: tuple[str, ...] = (
    "property_type",
    "property_location",
    "business_stage",
)

# Conditionally required, keyed off business_stage (docs/03 branch fields).
# Underperforming's fields all map to real columns; the rest live in branch_data.
BRANCH_REQUIRED: dict[BusinessStage, tuple[str, ...]] = {
    BusinessStage.PLANNING: ("target_launch_date", "investment_budget"),
    BusinessStage.IDLE_PROPERTY: (
        "reason_not_operating",
        "target_launch_date",
        "main_obstacle",
    ),
    BusinessStage.UNDERPERFORMING: (
        "occupancy_rate",
        "monthly_revenue",
        "average_room_rate",
        "booking_platforms",
    ),
    BusinessStage.OPERATING_SUCCESSFULLY: ("expansion_plan", "automation_interest"),
}

# Optional sections used only for finer-grained stage tracking (not completion).
_OPERATIONS_FIELDS = (
    "staff_count",
    "check_in_process",
    "housekeeping_process",
    "maintenance_process",
    "complaint_handling",
)
_TECHNOLOGY_FIELDS = (
    "uses_pms",
    "pms_name",
    "accounting_system",
    "booking_platforms",
    "communication_channels",
)


def _present(state: dict, key: str) -> bool:
    """True if ``key`` holds a meaningful value (0 counts; ""/[] do not)."""
    value = state.get(key)
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


class StateService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai = openai_service or OpenAIService()

    def _required_fields(self, state: dict) -> list[str]:
        required = list(REQUIRED_ALWAYS)
        stage_value = state.get("business_stage")
        if stage_value:
            try:
                stage = BusinessStage(stage_value)
            except ValueError:
                stage = None
            if stage is not None:
                required.extend(BRANCH_REQUIRED.get(stage, ()))
        return required

    def missing_fields(self, current_state: dict) -> list[str]:
        """Required fields (always + active branch) that are not yet present."""
        return [
            f for f in self._required_fields(current_state) if not _present(current_state, f)
        ]

    def completion_percentage(self, current_state: dict) -> int:
        """Percentage of required fields present, as an integer 0–100."""
        required = self._required_fields(current_state)
        if not required:
            return 0
        present = sum(1 for f in required if _present(current_state, f))
        return int(round(present / len(required) * 100))

    def current_stage(self, current_state: dict) -> str:
        """The section the conversation is currently working through.

        Walks the flow in docs/03. Note this is finer-grained than completion:
        completion tracks *required* fields, whereas the stage keeps advancing
        through optional sections until everything has been touched.
        """
        if not (
            _present(current_state, "property_type")
            and _present(current_state, "property_location")
        ):
            return "PROPERTY_PROFILE"
        if not _present(current_state, "business_stage"):
            return "BUSINESS_STAGE"
        if self.missing_fields(current_state):
            return "BRANCH"
        if not any(_present(current_state, f) for f in _OPERATIONS_FIELDS):
            return "OPERATIONS"
        if not any(_present(current_state, f) for f in _TECHNOLOGY_FIELDS):
            return "TECHNOLOGY"
        if not _present(current_state, "pain_points"):
            return "PAIN_POINTS"
        if not _present(current_state, "business_goals"):
            return "GOALS"
        return "COMPLETE"
