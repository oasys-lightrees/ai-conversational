"""Tests for AssessmentService (DB-backed; requires Postgres, no API key)."""

from __future__ import annotations

import uuid

import pytest

from backend.models.enums import AssessmentStatus, PropertyType
from backend.services.assessment_service import AssessmentNotFound, AssessmentService


def test_create_and_get(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    assert assessment.id is not None
    assert assessment.status == AssessmentStatus.IN_PROGRESS
    assert assessment.completion_percentage == 0

    fetched = svc.get(assessment.id)
    assert fetched.id == assessment.id
    assert fetched.data is not None


def test_update_data_maps_and_recomputes_completion(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.update_data(
        assessment.id,
        {"property_type": "Villa", "location": "Bali", "business_stage": "Underperforming"},
    )
    fetched = svc.get(assessment.id)
    assert fetched.data.property_type == PropertyType.VILLA
    assert fetched.data.property_location == "Bali"
    # required = 3 always + 4 underperforming branch = 7; 3 present -> 43%
    assert fetched.completion_percentage == 43


def test_update_data_writes_branch_blob(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.update_data(
        assessment.id,
        {"business_stage": "Planning", "target_launch_date": "2026-01"},
    )
    fetched = svc.get(assessment.id)
    assert fetched.data.branch_data == {"target_launch_date": "2026-01"}


def test_update_data_merges_across_turns(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.update_data(assessment.id, {"property_type": "Villa"})
    svc.update_data(assessment.id, {"location": "Bali"})
    fetched = svc.get(assessment.id)
    assert fetched.data.property_type == PropertyType.VILLA
    assert fetched.data.property_location == "Bali"


def test_update_data_unknown_id_raises(db_session):
    svc = AssessmentService(db_session)
    with pytest.raises(AssessmentNotFound):
        svc.update_data(uuid.uuid4(), {})


def test_delete_removes_assessment(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.delete(assessment.id)
    assert svc.get(assessment.id) is None


def test_delete_unknown_id_raises(db_session):
    svc = AssessmentService(db_session)
    with pytest.raises(AssessmentNotFound):
        svc.delete(uuid.uuid4())


def test_to_state_dict_flattens_branch_and_enums(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.update_data(
        assessment.id,
        {"property_type": "Villa", "business_stage": "Planning", "investment_budget": 50000},
    )
    fetched = svc.get(assessment.id)
    state = svc.to_state_dict(fetched.data)
    assert state["property_type"] == "VILLA"  # enum -> value
    assert state["investment_budget"] == 50000  # flattened from branch_data
