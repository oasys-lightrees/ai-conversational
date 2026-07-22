"""Tests for ExtractionService (Prompt 1). The model is faked; no network.

Extraction returns schema-vocabulary fields (uncoerced); these tests verify the
cleaning/filtering contract and that the output feeds field_mapping correctly.
"""

from __future__ import annotations

from decimal import Decimal

from backend.models.enums import BusinessStage, PropertyType
from backend.services.extraction_service import ExtractionService
from backend.services.field_mapping import map_extracted_to_columns
from tests.conftest import FakeOpenAIService


def test_returns_extracted_fields():
    fake = FakeOpenAIService(json_result={"property_type": "Villa", "location": "Bali", "total_units": 12})
    result = ExtractionService(fake).extract("Saya punya villa di Bali dengan 12 kamar.", {})
    assert result == {"property_type": "Villa", "location": "Bali", "total_units": 12}


def test_drops_null_and_empty_values():
    fake = FakeOpenAIService(
        json_result={"location": "Bali", "property_name": None, "pain_points": [], "pms_name": "  "}
    )
    result = ExtractionService(fake).extract("...", {})
    assert result == {"location": "Bali"}


def test_drops_keys_outside_schema():
    fake = FakeOpenAIService(json_result={"location": "Bali", "favorite_color": "blue"})
    result = ExtractionService(fake).extract("...", {})
    assert result == {"location": "Bali"}


def test_user_prompt_includes_message_and_collected_state():
    fake = FakeOpenAIService(json_result={})
    ExtractionService(fake).extract("halo dunia", {"property_type": "VILLA"})
    assert "halo dunia" in fake.last_user
    assert "property_type" in fake.last_user


def test_system_prompt_lists_enum_options():
    fake = FakeOpenAIService(json_result={})
    ExtractionService(fake).extract("x", {})
    # enum options are derived from the model, so e.g. VILLA must appear
    assert "VILLA" in fake.last_system
    assert "UNDERPERFORMING" in fake.last_system


def test_branch_hint_added_when_stage_known():
    fake = FakeOpenAIService(json_result={})
    ExtractionService(fake).extract("x", {"business_stage": "PLANNING"})
    assert "PLANNING" in fake.last_user
    assert "target_launch_date" in fake.last_user


def test_extraction_output_maps_to_columns():
    """The pipeline: raw extraction -> field_mapping -> columns/branch."""
    fake = FakeOpenAIService(
        json_result={
            "property_type": "Villa",
            "location": "Bali",
            "total_units": 12,
            "business_stage": "Planning",
            "target_launch_date": "2026-03",
        }
    )
    extracted = ExtractionService(fake).extract("...", {})
    columns, branch = map_extracted_to_columns(extracted)
    assert columns["property_type"] is PropertyType.VILLA
    assert columns["property_location"] == "Bali"
    assert columns["total_units"] == 12
    assert columns["business_stage"] is BusinessStage.PLANNING
    assert branch == {"target_launch_date": "2026-03"}
