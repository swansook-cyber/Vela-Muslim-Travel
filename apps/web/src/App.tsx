import { FormEvent, useState } from "react";

import { fetchAlongRoute } from "./api";
import { MapView } from "./MapView";
import type { AlongRouteResponse, PlaceType } from "./types";

const allTypes: { value: PlaceType; label: string }[] = [
  { value: "RESTAURANT", label: "ร้านอาหาร" },
  { value: "ACCOMMODATION", label: "ที่พัก" },
  { value: "MOSQUE", label: "มัสยิด" },
  { value: "PRAYER_ROOM", label: "ห้องละหมาด" },
];

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

export default function App() {
  const [originLat, setOriginLat] = useState("8.1646");
  const [originLng, setOriginLng] = useState("99.6804");
  const [destinationLat, setDestinationLat] = useState("14.5289");
  const [destinationLng, setDestinationLng] = useState("101.3722");
  const [corridorKm, setCorridorKm] = useState("5");
  const [types, setTypes] = useState<PlaceType[]>(
    allTypes.map((item) => item.value),
  );
  const [result, setResult] = useState<AlongRouteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [locating, setLocating] = useState(false);

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

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetchAlongRoute({
        origin: {
          latitude: Number(originLat),
          longitude: Number(originLng),
        },
        destination: {
          latitude: Number(destinationLat),
          longitude: Number(destinationLng),
        },
        corridorRadiusM: Number(corridorKm) * 1000,
        placeTypes: types,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ไม่สามารถค้นหาเส้นทางได้");
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
          ค้นหาร้านอาหาร ที่พัก มัสยิด และห้องละหมาดที่อยู่ระหว่างเส้นทาง
        </p>
      </header>

      <section className="workspace">
        <form className="search-panel" onSubmit={submit}>
          <h2>ค้นหาระหว่างทาง</h2>

          <button
            type="button"
            className="secondary"
            onClick={useCurrentLocation}
            disabled={locating}
          >
            {locating ? "กำลังหาตำแหน่ง…" : "ใช้ตำแหน่งปัจจุบันเป็นต้นทาง"}
          </button>

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

          <label>
            ระยะห่างจากเส้นทาง
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

          <button disabled={loading || types.length === 0}>
            {loading ? "กำลังค้นหา…" : "ค้นหาตามเส้นทาง"}
          </button>
          <p className="hint">
            พิกัดเริ่มต้นเป็นเพียงชุดทดสอบ Phase 0 และเปลี่ยนได้
          </p>
          {error && <p className="error">{error}</p>}
        </form>

        <MapView result={result} />
      </section>

      {result && (
        <section className="results">
          <div className="summary">
            <strong>{formatDistance(result.route.distance_m)}</strong>
            <span>{formatDuration(result.route.duration_s)}</span>
            <span>{result.places.length} สถานที่บนเส้นทาง</span>
          </div>

          <div className="place-list">
            {result.places.map((place) => (
              <article key={place.id} className="place-card">
                <div>
                  <span className="type">{place.place_type}</span>
                  <h3>{place.name_th}</h3>
                  <p>{[place.district, place.province].filter(Boolean).join(" · ")}</p>
                </div>
                <div className="place-meta">
                  {place.distance_m != null && (
                    <span>ห่างเส้นทาง {formatDistance(place.distance_m)}</span>
                  )}
                  <span>{place.trust_status || "UNVERIFIED"}</span>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
