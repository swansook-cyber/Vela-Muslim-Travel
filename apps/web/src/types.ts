export type PlaceType =
  | "RESTAURANT"
  | "ACCOMMODATION"
  | "MOSQUE"
  | "PRAYER_ROOM";

export interface Coordinate {
  latitude: number;
  longitude: number;
}

export interface PlaceResult {
  id: string;
  slug: string;
  place_type: PlaceType;
  name_th: string;
  name_en?: string | null;
  address?: string | null;
  district?: string | null;
  province?: string | null;
  phone?: string | null;
  website_url?: string | null;
  social_url?: string | null;
  latitude: number;
  longitude: number;
  distance_m?: number | null;
  route_progress?: number | null;
  trust_status?: string | null;
  verification_source_type?: string | null;
  source_reference?: string | null;
  verified_at?: string | null;
  expires_at?: string | null;
  verification_expired?: boolean;
  parking?: boolean | null;
  cuisine?: string[] | null;
  opening_hours?: Record<string, unknown> | null;
  takeaway?: boolean | null;
  delivery?: boolean | null;
  price_level?: number | null;
  halal_food_available?: boolean | null;
  prayer_space_available?: boolean | null;
  alcohol_policy?: string | null;
  bidet_available?: boolean | null;
  family_friendly?: boolean | null;
  nearest_mosque_distance_m?: number | null;
  check_in_time?: string | null;
  check_out_time?: string | null;
  friday_prayer?: boolean | null;
  women_prayer_area?: boolean | null;
  ablution_available?: boolean | null;
}

export interface AlongRouteResponse {
  route: {
    distance_m: number;
    duration_s: number;
    geometry: {
      type: "LineString";
      coordinates: number[][];
    };
  };
  places: PlaceResult[];
}


export interface GeocodeResult {
  display_name: string;
  latitude: number;
  longitude: number;
  category?: string | null;
  place_type?: string | null;
}


export type CandidateReviewState =
  | "DISCOVERED"
  | "GEOCODED"
  | "APPROVED"
  | "PROMOTED"
  | "REJECTED";

export interface CandidateResult {
  id: string;
  name: string;
  place_type: PlaceType;
  address?: string | null;
  district?: string | null;
  province?: string | null;
  phone?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  proposed_trust_status: string;
  source_type: string;
  source_reference?: string | null;
  external_provider?: string | null;
  external_id?: string | null;
  certification_number?: string | null;
  certification_expires_at?: string | null;
  review_state: CandidateReviewState;
  review_note?: string | null;
  review_hold_reason?: string | null;
  source_checked_at?: string | null;
  coordinate_checked_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateCoordinateSuggestion {
  candidate_id: string;
  provider: "google_places";
  external_id: string;
  latitude: number;
  longitude: number;
}

export interface CandidateReviewTask extends CandidateResult {
  maps_search_url: string;
  approval_blockers: string[];
  ready_to_approve: boolean;
}

export interface CandidateReviewProvinceProgress {
  province: string;
  pending: number;
  ready_to_approve: number;
  blocked: number;
  coordinate_pending: number;
  manual_hold: number;
  evidence_blocked: number;
}

export interface CandidateReviewProgressResponse {
  pending: number;
  ready_to_approve: number;
  blocked: number;
  coordinate_pending: number;
  manual_hold: number;
  evidence_blocked: number;
  provinces: CandidateReviewProvinceProgress[];
}


export interface AdminDashboard {
  candidates_total: number;
  discovered: number;
  geocoded: number;
  approved: number;
  promoted: number;
  rejected: number;
  production_places: number;
  expired_verifications: number;
  certifications_expiring_30d: number;
  google_places_resolver_enabled: boolean;
}


export interface AdminAuditEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id?: string | null;
  details: Record<string, unknown>;
  created_at: string;
}


export interface AdminPlaceResult {
  id: string;
  slug: string;
  place_type: PlaceType;
  name_th: string;
  name_en?: string | null;
  address?: string | null;
  district?: string | null;
  province?: string | null;
  phone?: string | null;
  website_url?: string | null;
  social_url?: string | null;
  active: boolean;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at: string;
}

export interface AdminPlaceUpdate {
  slug?: string;
  name_th?: string;
  name_en?: string | null;
  address?: string | null;
  district?: string | null;
  province?: string | null;
  phone?: string | null;
  website_url?: string | null;
  social_url?: string | null;
  active?: boolean;
  latitude?: number;
  longitude?: number;
}


export interface AdminVerificationResult {
  id: string;
  trust_status: string;
  source_type: string;
  source_reference?: string | null;
  verified_at?: string | null;
  expires_at?: string | null;
  note?: string | null;
  verified_by?: string | null;
  created_at: string;
}


export interface DetourResponse {
  route_distance_m: number;
  route_duration_s: number;
  added_distance_m: number;
  added_duration_s: number;
}


export interface PilotProvinceReadiness {
  province: string;
  restaurants: number;
  mosques: number;
  accommodation: number;
  total: number;
  missing_types: string[];
}

export interface PilotReadinessResponse {
  ready: boolean;
  provinces: PilotProvinceReadiness[];
}


export interface CandidateProvinceReadiness {
  province: string;
  restaurants: number;
  mosques: number;
  accommodation: number;
  geocoded: number;
  approved: number;
  promoted: number;
}

export interface CandidateReadinessResponse {
  ready: boolean;
  provinces: CandidateProvinceReadiness[];
}
