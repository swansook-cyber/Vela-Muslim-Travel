import type { AlongRouteResponse, Coordinate, PlaceType } from "./types";

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
