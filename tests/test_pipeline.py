"""Tests for the configurable pipeline: custom configs drive mapping, state,
and prompts; hybrid storage routes non-column fields to JSON.
"""

from __future__ import annotations

from decimal import Decimal

from backend.models.enums import PropertyType
from backend.pipeline import DEFAULT_CONFIG, FieldMapper, PipelineConfig
from backend.pipeline.config import FieldSpec
from backend.services.assessment_service import AssessmentService
from backend.services.extraction_service import ExtractionService
from backend.services.state_service import StateService
from tests.conftest import FakeOpenAIService

# A small custom config: one column-backed enum + two dynamic (no-column) fields.
CUSTOM = PipelineConfig(
    knowledge="Custom domain knowledge XYZ.",
    style="Speak concisely like an analyst.",
    language="en",
    fields=[
        FieldSpec(name="property_type", type="enum", enum_options=["VILLA", "HOTEL"], required=True, section="A"),
        FieldSpec(name="wifi_speed", label="WiFi Speed", type="integer", required=True, section="B"),
        FieldSpec(name="favorite_color", label="Favorite Color", type="string", section="B"),
    ],
)


# --- FieldSpec / required logic ---------------------------------------------


def test_required_when_conditional():
    spec = FieldSpec(name="x", required_when={"business_stage": ["UNDERPERFORMING"]})
    assert spec.is_required({"business_stage": "UNDERPERFORMING"})
    assert not spec.is_required({"business_stage": "PLANNING"})
    assert not spec.is_required({})


# --- FieldMapper hybrid storage ---------------------------------------------


def test_mapper_routes_column_vs_json():
    columns, extra = FieldMapper(CUSTOM).map(
        {"property_type": "Villa", "wifi_speed": "100", "favorite_color": "blue"}
    )
    assert columns == {"property_type": PropertyType.VILLA}  # column-backed enum
    assert extra == {"wifi_speed": 100, "favorite_color": "blue"}  # no column -> JSON


def test_mapper_drops_unknown_and_uncoercible():
    columns, extra = FieldMapper(CUSTOM).map(
        {"property_type": "Spaceship", "unknown_field": "x", "wifi_speed": "fast"}
    )
    assert columns == {} and extra == {}


def test_default_config_required_always():
    always = {f.name for f in DEFAULT_CONFIG.fields if f.required}
    assert always == {"property_type", "property_location", "business_stage"}


# --- StateService with a custom config --------------------------------------


def test_state_service_custom_required():
    svc = StateService(config=CUSTOM)
    assert set(svc.missing_fields({})) == {"property_type", "wifi_speed"}
    assert svc.completion_percentage({}) == 0
    full = {"property_type": "VILLA", "wifi_speed": 100}
    assert svc.missing_fields(full) == []
    assert svc.completion_percentage(full) == 100


# --- Prompts carry knowledge / style / fields -------------------------------


def test_extraction_prompt_uses_config():
    system = ExtractionService(FakeOpenAIService(), CUSTOM)._system_prompt()
    assert "Custom domain knowledge XYZ." in system
    assert "Speak concisely like an analyst." in system
    assert "wifi_speed" in system
    assert "VILLA" in system  # enum options listed


# --- DB round-trip: dynamic field persists to JSON --------------------------


def test_custom_field_persists_to_json(db_session):
    svc = AssessmentService(db_session, config=CUSTOM)
    assessment = svc.create()
    svc.update_data(assessment.id, {"property_type": "Villa", "wifi_speed": 50})
    fetched = svc.get(assessment.id)
    assert fetched.data.property_type == PropertyType.VILLA  # typed column
    assert fetched.data.branch_data == {"wifi_speed": 50}  # dynamic -> JSON
    # required = property_type + wifi_speed, both present -> 100
    assert fetched.completion_percentage == 100
    # to_state_dict flattens the JSON field back to the top level
    state = svc.to_state_dict(fetched.data)
    assert state["wifi_speed"] == 50
