from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from .schemas import PlaceType


class CandidateReviewState(StrEnum):
    DISCOVERED = "DISCOVERED"
    GEOCODED = "GEOCODED"
    APPROVED = "APPROVED"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"


class CandidateResult(BaseModel):
    id: str
    name: str
    place_type: PlaceType
    address: str | None = None
    district: str | None = None
    province: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    proposed_trust_status: str
    source_type: str
    source_reference: str | None = None
    external_provider: str | None = None
    external_id: str | None = None
    certification_number: str | None = None
    certification_expires_at: datetime | None = None
    review_state: CandidateReviewState
    review_note: str | None = None
    review_hold_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class CandidateReviewUpdate(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    review_state: CandidateReviewState | None = None
    review_note: str | None = None
    review_hold_reason: str | None = Field(default=None, max_length=500)


class CandidatePromoteRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name_th: str | None = Field(default=None, min_length=1, max_length=250)


class CandidatePromoteResponse(BaseModel):
    candidate_id: str
    place_id: str
    slug: str


class AdminDashboard(BaseModel):
    candidates_total: int
    discovered: int
    geocoded: int
    approved: int
    promoted: int
    rejected: int
    production_places: int
    expired_verifications: int
    certifications_expiring_30d: int


class AdminAuditEntry(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str | None = None
    details: dict
    created_at: datetime


class AdminPlaceResult(BaseModel):
    id: str
    slug: str
    place_type: PlaceType
    name_th: str
    name_en: str | None = None
    address: str | None = None
    district: str | None = None
    province: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    active: bool
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime


class AdminPlaceUpdate(BaseModel):
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    name_th: str | None = Field(default=None, min_length=1, max_length=250)
    name_en: str | None = Field(default=None, max_length=250)
    address: str | None = None
    district: str | None = None
    province: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    active: bool | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class AdminVerificationCreate(BaseModel):
    trust_status: Literal[
        "HALAL_CERTIFIED",
        "HALAL_CERTIFIED_SERVICE",
        "MUSLIM_OWNED",
        "MUSLIM_FRIENDLY",
        "UNVERIFIED",
    ]
    source_type: Literal[
        "OFFICIAL_CERTIFICATION",
        "BUSINESS_OWNER",
        "FIELD_CHECK",
        "COMMUNITY_REPORT",
        "PUBLIC_WEB_SOURCE",
        "UNKNOWN",
    ]
    source_reference: str | None = None
    verified_at: datetime
    expires_at: datetime | None = None
    note: str | None = None


class AdminVerificationResult(BaseModel):
    id: str
    trust_status: str
    source_type: str
    source_reference: str | None = None
    verified_at: datetime | None = None
    expires_at: datetime | None = None
    note: str | None = None
    verified_by: str | None = None
    created_at: datetime


class PilotProvinceReadiness(BaseModel):
    province: str
    restaurants: int
    mosques: int
    accommodation: int
    total: int
    missing_types: list[str]


class PilotReadinessResponse(BaseModel):
    ready: bool
    provinces: list[PilotProvinceReadiness]


class CandidateProvinceReadiness(BaseModel):
    province: str
    restaurants: int
    mosques: int
    accommodation: int
    geocoded: int
    approved: int
    promoted: int


class CandidateReadinessResponse(BaseModel):
    ready: bool
    provinces: list[CandidateProvinceReadiness]


class CandidateReviewTask(CandidateResult):
    maps_search_url: str
    approval_blockers: list[str]
    ready_to_approve: bool


class CandidateReviewProvinceProgress(BaseModel):
    province: str
    pending: int
    ready_to_approve: int
    blocked: int


class CandidateReviewProgressResponse(BaseModel):
    pending: int
    ready_to_approve: int
    blocked: int
    provinces: list[CandidateReviewProvinceProgress]
