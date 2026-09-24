import type {
  AlongRouteResponse,
  CandidateResult,
  CandidateReviewState,
  Coordinate,
  GeocodeResult,
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
): Promise<CandidateResult[]> {
  const url = new URL(`${API_BASE_URL}/admin/candidates`);
  if (reviewState) {
    url.searchParams.set("review_state", reviewState);
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
