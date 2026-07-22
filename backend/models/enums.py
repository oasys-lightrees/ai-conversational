"""Enumerations used across the assessment domain.

Values mirror the design documents in ``docs/03-assessment-schema.MD`` and
``docs/07-database-design.MD``.
"""

import enum


class AssessmentStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class PropertyType(str, enum.Enum):
    VILLA = "VILLA"
    HOTEL = "HOTEL"
    APARTMENT = "APARTMENT"
    BOARDING_HOUSE = "BOARDING_HOUSE"
    GUEST_HOUSE = "GUEST_HOUSE"
    RESORT = "RESORT"
    COMMERCIAL_BUILDING = "COMMERCIAL_BUILDING"
    OTHER = "OTHER"


class BusinessStage(str, enum.Enum):
    PLANNING = "PLANNING"
    IDLE_PROPERTY = "IDLE_PROPERTY"
    UNDERPERFORMING = "UNDERPERFORMING"
    OPERATING_SUCCESSFULLY = "OPERATING_SUCCESSFULLY"


class ProcessType(str, enum.Enum):
    MANUAL = "MANUAL"
    SEMI_DIGITAL = "SEMI_DIGITAL"
    FULLY_DIGITAL = "FULLY_DIGITAL"


class OwnershipType(str, enum.Enum):
    OWNED = "OWNED"
    LEASED = "LEASED"
    MANAGED = "MANAGED"
    OTHER = "OTHER"


class ConversationRole(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class RecommendationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
