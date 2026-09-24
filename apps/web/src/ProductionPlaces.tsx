import { useState } from "react";

import {
  addPlaceVerification,
  fetchAdminPlaces,
  fetchPlaceVerifications,
  updateAdminPlace,
} from "./api";
import type {
  AdminPlaceResult,
  AdminVerificationResult,
} from "./types";

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

interface VerificationDraft {
  trust_status: string;
  source_type: string;
  source_reference: string;
  expires_at: string;
  note: string;
}

const trustOptions = [
  "UNVERIFIED",
  "MUSLIM_OWNED",
  "MUSLIM_FRIENDLY",
  "HALAL_CERTIFIED",
  "HALAL_CERTIFIED_SERVICE",
];

const sourceOptions = [
  "UNKNOWN",
  "PUBLIC_WEB_SOURCE",
  "COMMUNITY_REPORT",
  "FIELD_CHECK",
  "BUSINESS_OWNER",
  "OFFICIAL_CERTIFICATION",
];

function defaultVerificationDraft(): VerificationDraft {
  return {
    trust_status: "UNVERIFIED",
    source_type: "PUBLIC_WEB_SOURCE",
    source_reference: "",
    expires_at: "",
    note: "",
  };
}

export function ProductionPlaces({ adminKey }: Props) {
  const [places, setPlaces] = useState<AdminPlaceResult[]>([]);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [verificationDrafts, setVerificationDrafts] = useState<
    Record<string, VerificationDraft>
  >({});
  const [verificationHistory, setVerificationHistory] = useState<
    Record<string, AdminVerificationResult[]>
  >({});
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

    setVerificationDrafts((current) => {
      const next = { ...current };
      for (const place of items) {
        next[place.id] ??= defaultVerificationDraft();
      }
      return next;
    });
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

  function patchVerification(
    placeId: string,
    patch: Partial<VerificationDraft>,
  ) {
    setVerificationDrafts((current) => ({
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

  async function loadVerificationHistory(place: AdminPlaceResult) {
    setLoading(true);
    setError("");

    try {
      const rows = await fetchPlaceVerifications(adminKey, place.id);
      setVerificationHistory((current) => ({
        ...current,
        [place.id]: rows,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "โหลดประวัติหลักฐานไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  async function addVerification(place: AdminPlaceResult) {
    const draft = verificationDrafts[place.id] || defaultVerificationDraft();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      await addPlaceVerification(adminKey, place.id, {
        trust_status: draft.trust_status,
        source_type: draft.source_type,
        source_reference: draft.source_reference || undefined,
        verified_at: new Date().toISOString(),
        expires_at: draft.expires_at
          ? new Date(draft.expires_at).toISOString()
          : undefined,
        note: draft.note || undefined,
      });
      setMessage(`เพิ่มหลักฐานใหม่ให้ ${place.name_th} แล้ว`);
      setVerificationDrafts((current) => ({
        ...current,
        [place.id]: defaultVerificationDraft(),
      }));
      await loadVerificationHistory(place);
    } catch (err) {
      setError(err instanceof Error ? err.message : "เพิ่มหลักฐานไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="production-admin">
      <div className="production-admin-head">
        <div>
          <h2>Production Places</h2>
          <p>แก้ไขข้อมูล ปิดใช้งาน และเพิ่มหลักฐานใหม่โดยไม่ลบประวัติเดิม</p>
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
          const verification =
            verificationDrafts[place.id] || defaultVerificationDraft();
          const history = verificationHistory[place.id] || [];
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

              <details className="verification-editor">
                <summary>หลักฐาน / Trust Status</summary>
                <div className="verification-grid">
                  <label>
                    Trust status
                    <select
                      value={verification.trust_status}
                      onChange={(event) =>
                        patchVerification(place.id, {
                          trust_status: event.target.value,
                        })
                      }
                    >
                      {trustOptions.map((item) => (
                        <option value={item} key={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Source type
                    <select
                      value={verification.source_type}
                      onChange={(event) =>
                        patchVerification(place.id, {
                          source_type: event.target.value,
                        })
                      }
                    >
                      {sourceOptions.map((item) => (
                        <option value={item} key={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Source URL
                    <input
                      value={verification.source_reference}
                      onChange={(event) =>
                        patchVerification(place.id, {
                          source_reference: event.target.value,
                        })
                      }
                    />
                  </label>
                  <label>
                    วันหมดอายุ (ถ้ามี)
                    <input
                      type="date"
                      value={verification.expires_at}
                      onChange={(event) =>
                        patchVerification(place.id, {
                          expires_at: event.target.value,
                        })
                      }
                    />
                  </label>
                </div>
                <label>
                  Note
                  <textarea
                    rows={2}
                    value={verification.note}
                    onChange={(event) =>
                      patchVerification(place.id, { note: event.target.value })
                    }
                  />
                </label>
                <div className="candidate-actions">
                  <button
                    type="button"
                    onClick={() => addVerification(place)}
                    disabled={loading}
                  >
                    เพิ่มหลักฐานใหม่
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => loadVerificationHistory(place)}
                    disabled={loading}
                  >
                    ดูประวัติ
                  </button>
                </div>

                {history.length > 0 && (
                  <div className="verification-history">
                    {history.map((item) => (
                      <div key={item.id}>
                        <strong>{item.trust_status}</strong>
                        <span>{item.source_type}</span>
                        <span>
                          {item.verified_at
                            ? new Date(item.verified_at).toLocaleDateString("th-TH")
                            : "ไม่ระบุวันที่"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </details>
            </article>
          );
        })}
      </div>
    </section>
  );
}
