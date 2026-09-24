import { FormEvent, useState } from "react";

import { fetchAlongRoute, fetchNearby, searchDestination } from "./api";
import { MapView } from "./MapView";
import type {
  AlongRouteResponse,
  GeocodeResult,
  PlaceResult,
  PlaceType,
} from "./types";

const allTypes: { value: PlaceType; label: string }[] = [
  { value: "RESTAURANT", label: "ร้านอาหาร" },
  { value: "ACCOMMODATION", label: "ที่พัก" },
  { value: "MOSQUE", label: "มัสยิด" },
  { value: "PRAYER_ROOM", label: "ห้องละหมาด" },
];

const typeLabels: Record<PlaceType, string> = {
  RESTAURANT: "ร้านอาหาร",
  ACCOMMODATION: "ที่พัก",
  MOSQUE: "มัสยิด",
  PRAYER_ROOM: "ห้องละหมาด",
};

const trustLabels: Record<string, string> = {
  HALAL_CERTIFIED: "ฮาลาลรับรอง",
  HALAL_CERTIFIED_SERVICE: "มีบริการที่ได้รับรองฮาลาล",
  MUSLIM_OWNED: "ร้าน/กิจการมุสลิม",
  MUSLIM_FRIENDLY: "รองรับนักเดินทางมุสลิม",
  UNVERIFIED: "ยังไม่ได้ยืนยัน",
};

function safeHttpUrl(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }

  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:"
      ? url.toString()
      : null;
  } catch {
    return null;
  }
}

function verificationLabel(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return `ตรวจล่าสุด ${date.toLocaleDateString("th-TH", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })}`;
}

function placeFeatures(place: PlaceResult): string[] {
  const features: string[] = [];

  if (place.halal_food_available) features.push("มีอาหารฮาลาล");
  if (place.prayer_space_available) features.push("มีพื้นที่ละหมาด");
  if (place.bidet_available) features.push("มีสายฉีดชำระ");
  if (place.family_friendly) features.push("เหมาะกับครอบครัว");
  if (place.friday_prayer) features.push("ละหมาดวันศุกร์");
  if (place.women_prayer_area) features.push("พื้นที่ละหมาดผู้หญิง");
  if (place.ablution_available) features.push("มีที่อาบน้ำละหมาด");
  if (place.parking) features.push("มีที่จอดรถ");

  return features.slice(0, 5);
}

function formatDistance(meters: number): string {
  return meters >= 1000
    ? `${(meters / 1000).toFixed(1)} กม.`
    : `${Math.round(meters)} ม.`;
}

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return hours > 0 ? `${hours} ชม. ${rest} นาที` : `${minutes} นาที`;
}

function formatRouteProgress(progress: number, totalSeconds: number): string {
  const elapsed = Math.max(0, Math.min(1, progress)) * totalSeconds;
  return `ประมาณ ${formatDuration(elapsed)} จากต้นทาง`;
}

export default function App() {
  const [originLat, setOriginLat] = useState("");
  const [originLng, setOriginLng] = useState("");
  const [originQuery, setOriginQuery] = useState("");
  const [originResults, setOriginResults] = useState<GeocodeResult[]>([]);
  const [selectedOrigin, setSelectedOrigin] = useState("");
  const [destinationLat, setDestinationLat] = useState("");
  const [destinationLng, setDestinationLng] = useState("");
  const [destinationQuery, setDestinationQuery] = useState("");
  const [destinationResults, setDestinationResults] = useState<GeocodeResult[]>([]);
  const [selectedDestination, setSelectedDestination] = useState("");
  const [corridorKm, setCorridorKm] = useState("5");
  const [types, setTypes] = useState<PlaceType[]>(
    allTypes.map((item) => item.value),
  );
  const [routeResult, setRouteResult] = useState<AlongRouteResponse | null>(null);
  const [nearbyPlaces, setNearbyPlaces] = useState<PlaceResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [error, setError] = useState("");
  const [locating, setLocating] = useState(false);

  const visiblePlaces = routeResult?.places ?? nearbyPlaces ?? [];

  function useCurrentLocation() {
    if (!navigator.geolocation) {
      setError("อุปกรณ์นี้ไม่รองรับการระบุตำแหน่ง");
      return;
    }

    setLocating(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setOriginLat(position.coords.latitude.toFixed(6));
        setOriginLng(position.coords.longitude.toFixed(6));
        setSelectedOrigin("ตำแหน่งปัจจุบัน");
        setOriginQuery("ตำแหน่งปัจจุบัน");
        setOriginResults([]);
        setLocating(false);
      },
      () => {
        setError("ไม่สามารถอ่านตำแหน่งปัจจุบันได้ กรุณาตรวจสิทธิ์ Location");
        setLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10_000,
        maximumAge: 60_000,
      },
    );
  }

  async function findOrigin() {
    const query = originQuery.trim();
    if (query.length < 2) {
      setError("กรุณาพิมพ์ชื่อต้นทางอย่างน้อย 2 ตัวอักษร");
      return;
    }

    setGeocoding(true);
    setError("");
    setOriginResults([]);

    try {
      const results = await searchDestination(query);
      setOriginResults(results);
      if (results.length === 0) {
        setError("ไม่พบต้นทาง ลองระบุชื่ออำเภอ จังหวัด หรือสถานที่ให้ชัดขึ้น");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "ค้นหาต้นทางไม่สำเร็จ");
    } finally {
      setGeocoding(false);
    }
  }

  function chooseOrigin(item: GeocodeResult) {
    setOriginLat(item.latitude.toFixed(6));
    setOriginLng(item.longitude.toFixed(6));
    setSelectedOrigin(item.display_name);
    setOriginQuery(item.display_name);
    setOriginResults([]);
    setError("");
  }

  async function findDestination() {
    const query = destinationQuery.trim();
    if (query.length < 2) {
      setError("กรุณาพิมพ์ชื่อปลายทางอย่างน้อย 2 ตัวอักษร");
      return;
    }

    setGeocoding(true);
    setError("");
    setDestinationResults([]);

    try {
      const results = await searchDestination(query);
      setDestinationResults(results);
      if (results.length === 0) {
        setError("ไม่พบปลายทาง ลองระบุชื่ออำเภอ จังหวัด หรือสถานที่ให้ชัดขึ้น");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "ค้นหาปลายทางไม่สำเร็จ");
    } finally {
      setGeocoding(false);
    }
  }

  function chooseDestination(item: GeocodeResult) {
    setDestinationLat(item.latitude.toFixed(6));
    setDestinationLng(item.longitude.toFixed(6));
    setSelectedDestination(item.display_name);
    setDestinationQuery(item.display_name);
    setDestinationResults([]);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();

    const originLatitude = Number(originLat);
    const originLongitude = Number(originLng);
    const destinationLatitude = Number(destinationLat);
    const destinationLongitude = Number(destinationLng);

    if (
      !originLat ||
      !originLng ||
      !Number.isFinite(originLatitude) ||
      !Number.isFinite(originLongitude)
    ) {
      setError("กรุณาใช้ตำแหน่งปัจจุบันหรือระบุพิกัดต้นทางก่อนค้นหา");
      return;
    }

    if (
      !destinationLat ||
      !destinationLng ||
      !Number.isFinite(destinationLatitude) ||
      !Number.isFinite(destinationLongitude)
    ) {
      setError("กรุณาค้นหาและเลือกปลายทางก่อนค้นหาตามเส้นทาง");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetchAlongRoute({
        origin: {
          latitude: originLatitude,
          longitude: originLongitude,
        },
        destination: {
          latitude: destinationLatitude,
          longitude: destinationLongitude,
        },
        corridorRadiusM: Number(corridorKm) * 1000,
        placeTypes: types,
      });
      setNearbyPlaces(null);
      setRouteResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ไม่สามารถค้นหาเส้นทางได้");
    } finally {
      setLoading(false);
    }
  }

  async function searchNearby() {
    const latitude = Number(originLat);
    const longitude = Number(originLng);

    if (
      !originLat ||
      !originLng ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude)
    ) {
      setError("กรุณาใช้ตำแหน่งปัจจุบันหรือระบุพิกัดต้นทางก่อนค้นหาใกล้ฉัน");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const places = await fetchNearby({
        latitude,
        longitude,
        radiusM: Number(corridorKm) * 1000,
        placeTypes: types,
      });
      setRouteResult(null);
      setNearbyPlaces(places);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ไม่สามารถค้นหาใกล้ฉันได้");
    } finally {
      setLoading(false);
    }
  }

  function toggleType(type: PlaceType) {
    setTypes((current) =>
      current.includes(type)
        ? current.filter((item) => item !== type)
        : [...current, type],
    );
  }

  return (
    <main>
      <header className="hero">
        <p className="eyebrow">VelaLab</p>
        <h1>Vela Muslim Travel</h1>
        <p>
          ค้นหาร้านอาหาร ที่พัก มัสยิด และห้องละหมาดทั้งใกล้ตัวและระหว่างเส้นทาง
        </p>
      </header>

      <section className="workspace">
        <form className="search-panel" onSubmit={submit}>
          <h2>ค้นหาสำหรับการเดินทาง</h2>

          <div className="destination-search">
            <label>
              ต้นทาง
              <div className="inline-action">
                <input
                  value={originQuery}
                  onChange={(event) => {
                    setOriginQuery(event.target.value);
                    setSelectedOrigin("");
                    setOriginResults([]);
                  }}
                  placeholder="เช่น ทุ่งสง, เพชรบุรี, บ้านฉัน"
                />
                <button
                  type="button"
                  className="compact"
                  onClick={findOrigin}
                  disabled={geocoding}
                >
                  {geocoding ? "ค้นหา…" : "ค้นหา"}
                </button>
              </div>
            </label>

            {originResults.length > 0 && (
              <div className="destination-results">
                {originResults.map((item) => (
                  <button
                    key={`origin-${item.latitude}-${item.longitude}-${item.display_name}`}
                    type="button"
                    className="destination-option"
                    onClick={() => chooseOrigin(item)}
                  >
                    {item.display_name}
                  </button>
                ))}
              </div>
            )}

            {selectedOrigin && (
              <p className="selected-destination">
                ต้นทางที่เลือก: {selectedOrigin}
              </p>
            )}
          </div>

          <button
            type="button"
            className="secondary"
            onClick={useCurrentLocation}
            disabled={locating}
          >
            {locating ? "กำลังหาตำแหน่ง…" : "ใช้ตำแหน่งปัจจุบันเป็นต้นทาง"}
          </button>

          <div className="destination-search">
            <label>
              ปลายทาง
              <div className="inline-action">
                <input
                  value={destinationQuery}
                  onChange={(event) => {
                    setDestinationQuery(event.target.value);
                    setSelectedDestination("");
                    setDestinationResults([]);
                  }}
                  placeholder="เช่น เขาใหญ่, ชะอำ, เพชรบุรี"
                />
                <button
                  type="button"
                  className="compact"
                  onClick={findDestination}
                  disabled={geocoding}
                >
                  {geocoding ? "ค้นหา…" : "ค้นหา"}
                </button>
              </div>
            </label>

            {destinationResults.length > 0 && (
              <div className="destination-results">
                {destinationResults.map((item) => (
                  <button
                    key={`${item.latitude}-${item.longitude}-${item.display_name}`}
                    type="button"
                    className="destination-option"
                    onClick={() => chooseDestination(item)}
                  >
                    {item.display_name}
                  </button>
                ))}
              </div>
            )}

            {selectedDestination && (
              <p className="selected-destination">
                ปลายทางที่เลือก: {selectedDestination}
              </p>
            )}
          </div>

          <details className="advanced">
            <summary>พิกัด / ตัวเลือกขั้นสูง</summary>
            <div className="coordinate-grid">
              <label>
                ต้นทาง Latitude
                <input value={originLat} onChange={(e) => setOriginLat(e.target.value)} />
              </label>
              <label>
                ต้นทาง Longitude
                <input value={originLng} onChange={(e) => setOriginLng(e.target.value)} />
              </label>
              <label>
                ปลายทาง Latitude
                <input
                  value={destinationLat}
                  onChange={(e) => setDestinationLat(e.target.value)}
                />
              </label>
              <label>
                ปลายทาง Longitude
                <input
                  value={destinationLng}
                  onChange={(e) => setDestinationLng(e.target.value)}
                />
              </label>
            </div>
          </details>

          <label>
            รัศมีค้นหา / ระยะจากเส้นทาง
            <select value={corridorKm} onChange={(e) => setCorridorKm(e.target.value)}>
              <option value="2">2 กม.</option>
              <option value="5">5 กม.</option>
              <option value="10">10 กม.</option>
              <option value="20">20 กม.</option>
            </select>
          </label>

          <fieldset>
            <legend>แสดง</legend>
            <div className="filters">
              {allTypes.map((item) => (
                <label key={item.value} className="check">
                  <input
                    type="checkbox"
                    checked={types.includes(item.value)}
                    onChange={() => toggleType(item.value)}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </fieldset>

          <div className="action-stack">
            <button disabled={loading || types.length === 0}>
              {loading ? "กำลังค้นหา…" : "ค้นหาตามเส้นทาง"}
            </button>
            <button
              type="button"
              className="secondary"
              disabled={loading || types.length === 0}
              onClick={searchNearby}
            >
              ค้นหารอบต้นทาง
            </button>
          </div>

          <p className="hint">
            การค้นหาชื่อสถานที่เกิดขึ้นเมื่อกดปุ่มค้นหาเท่านั้น ไม่ทำ autocomplete ต่อเนื่อง
          </p>
          {error && <p className="error">{error}</p>}
        </form>

        <MapView route={routeResult?.route ?? null} places={visiblePlaces} />
      </section>

      {(routeResult || nearbyPlaces) && (
        <section className="results">
          <div className="summary">
            {routeResult ? (
              <>
                <strong>{formatDistance(routeResult.route.distance_m)}</strong>
                <span>{formatDuration(routeResult.route.duration_s)}</span>
                <span>{visiblePlaces.length} สถานที่บนเส้นทาง</span>
              </>
            ) : (
              <>
                <strong>{visiblePlaces.length} สถานที่ใกล้ต้นทาง</strong>
                <span>ภายใน {corridorKm} กม.</span>
              </>
            )}
          </div>

          <div className="place-list">
            {visiblePlaces.map((place) => (
              <article key={place.id} className="place-card">
                <div>
                  <span className="type">{typeLabels[place.place_type]}</span>
                  <h3>{place.name_th}</h3>
                  <p>{[place.district, place.province].filter(Boolean).join(" · ")}</p>
                  {placeFeatures(place).length > 0 && (
                    <div className="feature-chips">
                      {placeFeatures(place).map((feature) => (
                        <span key={feature}>{feature}</span>
                      ))}
                    </div>
                  )}
                  <div className="place-actions">
                    <a
                      href={`https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Google Maps
                    </a>
                    <a
                      href={`https://maps.apple.com/?daddr=${place.latitude},${place.longitude}&dirflg=d`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Apple Maps
                    </a>
                    {place.phone && <a href={`tel:${place.phone}`}>โทร</a>}
                    {safeHttpUrl(place.source_reference) && (
                      <a
                        href={safeHttpUrl(place.source_reference) ?? undefined}
                        target="_blank"
                        rel="noreferrer"
                      >
                        ดูหลักฐาน
                      </a>
                    )}
                  </div>
                </div>
                <div className="place-meta">
                  {place.distance_m != null && (
                    <span>
                      {routeResult ? "ห่างเส้นทาง " : "ระยะ "}
                      {formatDistance(place.distance_m)}
                    </span>
                  )}
                  {routeResult && place.route_progress != null && (
                    <span>
                      {formatRouteProgress(
                        place.route_progress,
                        routeResult.route.duration_s,
                      )}
                    </span>
                  )}
                  <strong
                    className={
                      place.verification_expired
                        ? "trust-badge trust-expired"
                        : "trust-badge"
                    }
                  >
                    {place.verification_expired
                      ? "หลักฐานหมดอายุ"
                      : trustLabels[place.trust_status || "UNVERIFIED"] ||
                        place.trust_status ||
                        "ยังไม่ได้ยืนยัน"}
                  </strong>
                  {verificationLabel(place.verified_at) && (
                    <span>{verificationLabel(place.verified_at)}</span>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
