from datetime import datetime
from enum import StrEnum

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
    created_at: datetime
    updated_at: datetime


class CandidateReviewUpdate(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    review_state: CandidateReviewState | None = None
    review_note: str | None = None


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
