import { useState } from "react";

import { fetchAdminPlaces, updateAdminPlace } from "./api";
import type { AdminPlaceResult } from "./types";

interface Props {
  adminKey: string;
}

interface Draft {
  name_th: string;
  address: string;
  phone: string;
  latitude: string;
  longitude: string;
}

export function ProductionPlaces({ adminKey }: Props) {
  const [places, setPlaces] = useState<AdminPlaceResult[]>([]);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [includeInactive, setIncludeInactive] = useState(true);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function seedDrafts(items: AdminPlaceResult[]) {
    setDrafts(
      Object.fromEntries(
        items.map((place) => [
          place.id,
          {
            name_th: place.name_th,
            address: place.address || "",
            phone: place.phone || "",
            latitude: String(place.latitude),
            longitude: String(place.longitude),
          },
        ]),
      ),
    );
  }

  async function load() {
    if (!adminKey) {
      setError("กรุณาใส่ Admin API Key ด้านบนก่อน");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const items = await fetchAdminPlaces(adminKey, includeInactive);
      setPlaces(items);
      seedDrafts(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "โหลด production places ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  function patchDraft(placeId: string, patch: Partial<Draft>) {
    setDrafts((current) => ({
      ...current,
      [placeId]: {
        ...current[placeId],
        ...patch,
      },
    }));
  }

  async function save(place: AdminPlaceResult) {
    const draft = drafts[place.id];
    if (!draft) return;

    const latitude = Number(draft.latitude);
    const longitude = Number(draft.longitude);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      setError("Latitude/Longitude ไม่ถูกต้อง");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const updated = await updateAdminPlace(adminKey, place.id, {
        name_th: draft.name_th,
        address: draft.address || null,
        phone: draft.phone || null,
        latitude,
        longitude,
      });
      setMessage(`บันทึก ${updated.name_th} แล้ว`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "บันทึกสถานที่ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  async function toggleActive(place: AdminPlaceResult) {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const updated = await updateAdminPlace(adminKey, place.id, {
        active: !place.active,
      });
      setMessage(
        updated.active
          ? `เปิดใช้งาน ${updated.name_th} แล้ว`
          : `ปิดใช้งาน ${updated.name_th} แล้ว`,
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "เปลี่ยนสถานะไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="production-admin">
      <div className="production-admin-head">
        <div>
          <h2>Production Places</h2>
          <p>แก้ไขข้อมูลหรือปิดใช้งานสถานที่โดยไม่ลบประวัติ</p>
        </div>
        <label className="check">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(event) => setIncludeInactive(event.target.checked)}
          />
          รวมรายการที่ปิดใช้งาน
        </label>
        <button type="button" onClick={load} disabled={loading}>
          {loading ? "กำลังโหลด…" : "โหลด Production Places"}
        </button>
      </div>

      {message && <p className="admin-message">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="production-place-list">
        {places.map((place) => {
          const draft = drafts[place.id];
          if (!draft) return null;

          return (
            <article
              key={place.id}
              className={
                place.active
                  ? "production-place-card"
                  : "production-place-card is-inactive"
              }
            >
              <div className="candidate-head">
                <div>
                  <span className="type">{place.place_type}</span>
                  <h3>{place.name_th}</h3>
                  <p>{place.slug}</p>
                </div>
                <strong>{place.active ? "ACTIVE" : "INACTIVE"}</strong>
              </div>

              <label>
                ชื่อ
                <input
                  value={draft.name_th}
                  onChange={(event) =>
                    patchDraft(place.id, { name_th: event.target.value })
                  }
                />
              </label>

              <label>
                ที่อยู่
                <textarea
                  rows={2}
                  value={draft.address}
                  onChange={(event) =>
                    patchDraft(place.id, { address: event.target.value })
                  }
                />
              </label>

              <label>
                โทรศัพท์
                <input
                  value={draft.phone}
                  onChange={(event) =>
                    patchDraft(place.id, { phone: event.target.value })
                  }
                />
              </label>

              <div className="coordinate-grid">
                <label>
                  Latitude
                  <input
                    value={draft.latitude}
                    onChange={(event) =>
                      patchDraft(place.id, { latitude: event.target.value })
                    }
                  />
                </label>
                <label>
                  Longitude
                  <input
                    value={draft.longitude}
                    onChange={(event) =>
                      patchDraft(place.id, { longitude: event.target.value })
                    }
                  />
                </label>
              </div>

              <div className="candidate-actions">
                <button type="button" onClick={() => save(place)} disabled={loading}>
                  บันทึก
                </button>
                <button
                  type="button"
                  className={place.active ? "danger" : "secondary"}
                  onClick={() => toggleActive(place)}
                  disabled={loading}
                >
                  {place.active ? "ปิดใช้งาน" : "เปิดใช้งาน"}
                </button>
                <a
                  className="admin-map-link"
                  href={`https://www.google.com/maps/search/?api=1&query=${place.latitude},${place.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  ตรวจบนแผนที่
                </a>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
