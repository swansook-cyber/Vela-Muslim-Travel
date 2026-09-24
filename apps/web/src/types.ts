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
