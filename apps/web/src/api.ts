import type {
  AdminAuditEntry,
  AdminDashboard,
  AdminPlaceResult,
  AdminPlaceUpdate,
  AdminVerificationResult,
  AlongRouteResponse,
  CandidateCoordinateBatchResponse,
  CandidateCoordinateSuggestion,
  CandidateReadinessResponse,
  CandidateResult,
  CandidatePromotionCheckResponse,
  CandidateReviewProgressResponse,
  CandidateReviewState,
  CandidateReviewTask,
  Coordinate,
  DetourResponse,
  GeocodeResult,
  PilotReadinessResponse,
  Phase0CompletionResponse,
  PlaceResult,
  PlaceType,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export interface AlongRouteInput {
  origin: Coordinate;
  destination: Coordinate;
  corridorRadiusM: number;
  placeTypes: PlaceType[];
}

export async function fetchAlongRoute(
  input: AlongRouteInput,
): Promise<AlongRouteResponse> {
  const response = await fetch(`${API_BASE_URL}/routes/along`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      origin: input.origin,
      destination: input.destination,
      corridor_radius_m: input.corridorRadiusM,
      place_types: input.placeTypes,
      limit: 100,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API request failed: ${response.status}`);
  }

  return response.json() as Promise<AlongRouteResponse>;
}


export interface NearbyInput extends Coordinate {
  radiusM: number;
  placeTypes: PlaceType[];
}

export async function fetchNearby(input: NearbyInput): Promise<PlaceResult[]> {
  const response = await fetch(`${API_BASE_URL}/places/nearby`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      latitude: input.latitude,
      longitude: input.longitude,
      radius_m: input.radiusM,
      place_types: input.placeTypes,
      limit: 100,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API request failed: ${response.status}`);
  }

  return response.json() as Promise<PlaceResult[]>;
}


export async function searchDestination(query: string): Promise<GeocodeResult[]> {
  const url = new URL(`${API_BASE_URL}/geocode/search`);
  url.searchParams.set("q", query);

  const response = await fetch(url);

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Geocoding request failed: ${response.status}`);
  }

  return response.json() as Promise<GeocodeResult[]>;
}


function adminHeaders(adminKey: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Admin-Key": adminKey,
  };
}

export async function fetchCandidates(
  adminKey: string,
  reviewState?: CandidateReviewState,
  province?: string,
  placeType?: PlaceType,
): Promise<CandidateResult[]> {
  const url = new URL(`${API_BASE_URL}/admin/candidates`);
  if (reviewState) {
    url.searchParams.set("review_state", reviewState);
  }
  if (province) {
    url.searchParams.set("province", province);
  }
  if (placeType) {
    url.searchParams.set("place_type", placeType);
  }

  const response = await fetch(url, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateResult[]>;
}

export interface CandidateReviewInput {
  latitude?: number;
  longitude?: number;
  review_state?: CandidateReviewState;
  review_note?: string;
  review_hold_reason?: string;
  source_checked_at?: string;
  coordinate_checked_at?: string;
}

export async function updateCandidate(
  adminKey: string,
  candidateId: string,
  update: CandidateReviewInput,
): Promise<CandidateResult> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidates/${encodeURIComponent(candidateId)}`,
    {
      method: "PATCH",
      headers: adminHeaders(adminKey),
      body: JSON.stringify(update),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateResult>;
}

export async function resolveCandidateGooglePlace(
  adminKey: string,
  candidateId: string,
): Promise<CandidateCoordinateSuggestion> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidates/${encodeURIComponent(candidateId)}/resolve-google-place`,
    {
      method: "POST",
      headers: adminHeaders(adminKey),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateCoordinateSuggestion>;
}


export async function resolveCandidateGooglePlaces(
  adminKey: string,
  candidateIds: string[],
): Promise<CandidateCoordinateBatchResponse> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidates/resolve-google-places`,
    {
      method: "POST",
      headers: adminHeaders(adminKey),
      body: JSON.stringify({ candidate_ids: candidateIds }),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateCoordinateBatchResponse>;
}


export async function checkCandidatePromotion(
  adminKey: string,
  candidateId: string,
  slug: string,
): Promise<CandidatePromotionCheckResponse> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidates/${encodeURIComponent(candidateId)}/promotion-check`,
    {
      method: "POST",
      headers: adminHeaders(adminKey),
      body: JSON.stringify({ slug }),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidatePromotionCheckResponse>;
}


export async function promoteCandidate(
  adminKey: string,
  candidateId: string,
  slug: string,
  nameTh?: string,
): Promise<{ candidate_id: string; place_id: string; slug: string }> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidates/${encodeURIComponent(candidateId)}/promote`,
    {
      method: "POST",
      headers: adminHeaders(adminKey),
      body: JSON.stringify({
        slug,
        name_th: nameTh || undefined,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}


export async function fetchAdminDashboard(
  adminKey: string,
): Promise<AdminDashboard> {
  const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminDashboard>;
}


export async function fetchAdminAudit(
  adminKey: string,
  limit = 20,
): Promise<AdminAuditEntry[]> {
  const url = new URL(`${API_BASE_URL}/admin/audit`);
  url.searchParams.set("limit", String(limit));

  const response = await fetch(url, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminAuditEntry[]>;
}


export async function fetchAdminPlaces(
  adminKey: string,
  includeInactive = true,
): Promise<AdminPlaceResult[]> {
  const url = new URL(`${API_BASE_URL}/admin/places`);
  url.searchParams.set("include_inactive", String(includeInactive));

  const response = await fetch(url, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminPlaceResult[]>;
}

export async function updateAdminPlace(
  adminKey: string,
  placeId: string,
  update: AdminPlaceUpdate,
): Promise<AdminPlaceResult> {
  const response = await fetch(
    `${API_BASE_URL}/admin/places/${encodeURIComponent(placeId)}`,
    {
      method: "PATCH",
      headers: adminHeaders(adminKey),
      body: JSON.stringify(update),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminPlaceResult>;
}


export async function fetchPlaceVerifications(
  adminKey: string,
  placeId: string,
): Promise<AdminVerificationResult[]> {
  const response = await fetch(
    `${API_BASE_URL}/admin/places/${encodeURIComponent(placeId)}/verifications`,
    { headers: adminHeaders(adminKey) },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminVerificationResult[]>;
}

export interface AddVerificationInput {
  trust_status: string;
  source_type: string;
  source_reference?: string;
  verified_at: string;
  expires_at?: string;
  note?: string;
}

export async function addPlaceVerification(
  adminKey: string,
  placeId: string,
  input: AddVerificationInput,
): Promise<AdminVerificationResult> {
  const response = await fetch(
    `${API_BASE_URL}/admin/places/${encodeURIComponent(placeId)}/verifications`,
    {
      method: "POST",
      headers: adminHeaders(adminKey),
      body: JSON.stringify(input),
    },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<AdminVerificationResult>;
}


export interface DetourInput {
  origin: Coordinate;
  destination: Coordinate;
  stop: Coordinate;
  baseDistanceM: number;
  baseDurationS: number;
}

export async function fetchDetour(
  input: DetourInput,
): Promise<DetourResponse> {
  const response = await fetch(`${API_BASE_URL}/routes/detour`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      origin: input.origin,
      destination: input.destination,
      stop: input.stop,
      base_distance_m: input.baseDistanceM,
      base_duration_s: input.baseDurationS,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Detour request failed: ${response.status}`);
  }

  return response.json() as Promise<DetourResponse>;
}


export async function fetchPilotReadiness(
  adminKey: string,
): Promise<PilotReadinessResponse> {
  const response = await fetch(`${API_BASE_URL}/admin/pilot-readiness`, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<PilotReadinessResponse>;
}


export async function fetchCandidateReviewProgress(
  adminKey: string,
): Promise<CandidateReviewProgressResponse> {
  const response = await fetch(
    `${API_BASE_URL}/admin/candidate-review-progress`,
    { headers: adminHeaders(adminKey) },
  );

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateReviewProgressResponse>;
}


export async function fetchCandidateReadiness(
  adminKey: string,
): Promise<CandidateReadinessResponse> {
  const response = await fetch(`${API_BASE_URL}/admin/candidate-readiness`, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateReadinessResponse>;
}


export async function fetchCandidateReviewQueue(
  adminKey: string,
  reviewState: CandidateReviewState = "DISCOVERED",
  province?: string,
  placeType?: PlaceType,
  pilotOnly = false,
): Promise<CandidateReviewTask[]> {
  const url = new URL(`${API_BASE_URL}/admin/candidates/review-queue`);
  url.searchParams.set("review_state", reviewState);
  if (province) {
    url.searchParams.set("province", province);
  }
  if (placeType) {
    url.searchParams.set("place_type", placeType);
  }
  if (pilotOnly) {
    url.searchParams.set("pilot_only", "true");
  }

  const response = await fetch(url, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<CandidateReviewTask[]>;
}

export async function fetchPhase0Completion(
  adminKey: string,
): Promise<Phase0CompletionResponse> {
  const response = await fetch(`${API_BASE_URL}/admin/phase0-completion`, {
    headers: adminHeaders(adminKey),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json() as Promise<Phase0CompletionResponse>;
}
