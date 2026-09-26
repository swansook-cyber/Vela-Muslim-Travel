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
    source_checked_at: datetime | None = None
    coordinate_checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CandidateReviewUpdate(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    review_state: CandidateReviewState | None = None
    review_note: str | None = None
    review_hold_reason: str | None = Field(default=None, max_length=500)
    source_checked_at: datetime | None = None
    coordinate_checked_at: datetime | None = None


class CandidateCoordinateSuggestion(BaseModel):
    candidate_id: str
    provider: Literal["google_places"]
    external_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    formatted_address: str | None = None


class CandidateCoordinateBatchRequest(BaseModel):
    candidate_ids: list[str] = Field(min_length=1, max_length=25)


class CandidateCoordinateBatchItem(BaseModel):
    candidate_id: str
    suggestion: CandidateCoordinateSuggestion | None = None
    error: str | None = None


class CandidateCoordinateBatchResponse(BaseModel):
    results: list[CandidateCoordinateBatchItem]


class CandidatePromotionDuplicate(BaseModel):
    id: str
    slug: str
    name_th: str
    distance_m: float


class CandidatePromotionCheckResponse(BaseModel):
    can_promote: bool
    slug_exists: bool
    duplicate: CandidatePromotionDuplicate | None = None
    promotion_blockers: list[str] = Field(default_factory=list)


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
    google_places_resolver_enabled: bool = False


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
    accommodation_provinces: int
    required_accommodation_provinces: int = 2
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
    review_warnings: list[str]
    ready_to_approve: bool


class CandidateReviewProvinceProgress(BaseModel):
    province: str
    pending: int
    ready_to_approve: int
    blocked: int
    coordinate_pending: int
    google_resolvable: int
    google_fast_lane: int
    manual_hold: int
    evidence_blocked: int


class CandidateReviewProgressResponse(BaseModel):
    pending: int
    ready_to_approve: int
    blocked: int
    coordinate_pending: int
    google_resolvable: int
    google_fast_lane: int
    manual_hold: int
    evidence_blocked: int
    provinces: list[CandidateReviewProvinceProgress]


class Phase0AcceptanceRequest(BaseModel):
    route_smoke_2km_checked: bool
    route_smoke_5km_core_pass: bool
    route_smoke_10km_checked: bool
    detours_and_evidence_checked: bool
    note: str | None = Field(default=None, max_length=1000)


class Phase0CompletionResponse(BaseModel):
    mechanical_ready: bool
    final_complete: bool
    candidate_review_complete: bool
    promotion_queue_complete: bool
    production_coverage_ready: bool
    active_review_pending: int
    approved_waiting_promotion: int
    promoted_candidates: int
    rejected_candidates: int
    manual_hold: int
    google_fast_lane: int
    blockers: list[str]
    manual_acceptance_required: bool
    accepted_at: datetime | None = None
    manual_acceptance_steps: list[str]
