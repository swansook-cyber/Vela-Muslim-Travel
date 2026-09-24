import { useEffect, useMemo, useState } from "react";

import {
  fetchCandidates,
  promoteCandidate,
  searchDestination,
  updateCandidate,
} from "./api";
import type {
  CandidateResult,
  CandidateReviewState,
  GeocodeResult,
} from "./types";

const reviewStates: Array<{ value: CandidateReviewState | ""; label: string }> = [
  { value: "", label: "ทั้งหมด" },
  { value: "DISCOVERED", label: "รอตรวจ" },
  { value: "GEOCODED", label: "มีพิกัดแล้ว" },
  { value: "APPROVED", label: "อนุมัติแล้ว" },
  { value: "PROMOTED", label: "เข้า production แล้ว" },
  { value: "REJECTED", label: "ปฏิเสธ" },
];

function safeHttpUrl(value: string | null | undefined): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.toString() : null;
  } catch {
    return null;
  }
}

function suggestedSlug(candidate: CandidateResult): string {
  const external = candidate.external_id
    ?.toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return external ? `place-${external}` : `place-${candidate.id.slice(0, 8)}`;
}

interface Draft {
  latitude: string;
  longitude: string;
  note: string;
  slug: string;
}

export default function AdminApp() {
  const [adminKey, setAdminKey] = useState(
    () => sessionStorage.getItem("vela-admin-key") || "",
  );
  const [filter, setFilter] = useState<CandidateReviewState | "">("DISCOVERED");
  const [candidates, setCandidates] = useState<CandidateResult[]>([]);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [loading, setLoading] = useState(false);
  const [geocodeSuggestions, setGeocodeSuggestions] = useState<
    Record<string, GeocodeResult[]>
  >({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const filteredCount = useMemo(() => candidates.length, [candidates]);

  function initializeDrafts(items: CandidateResult[]) {
    setDrafts((current) => {
      const next = { ...current };
      for (const item of items) {
        next[item.id] ??= {
          latitude: item.latitude?.toString() || "",
          longitude: item.longitude?.toString() || "",
          note: item.review_note || "",
          slug: suggestedSlug(item),
        };
      }
      return next;
    });
  }

  async function load() {
    if (!adminKey) {
      setError("กรุณาใส่ Admin API Key");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    sessionStorage.setItem("vela-admin-key", adminKey);

    try {
      const items = await fetchCandidates(adminKey, filter || undefined);
      setCandidates(items);
      initializeDrafts(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "โหลด candidate ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (adminKey) {
      void load();
    }
    // Initial load only. Filter changes are applied by the explicit refresh button.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updateDraft(candidateId: string, patch: Partial<Draft>) {
    setDrafts((current) => ({
      ...current,
      [candidateId]: {
        ...current[candidateId],
        ...patch,
      },
    }));
  }

  async function locate(candidate: CandidateResult) {
    const query = [candidate.name, candidate.address, candidate.province]
      .filter(Boolean)
      .join(" ");

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const results = await searchDestination(query);
      if (!results.length) {
        setError(`ไม่พบพิกัดสำหรับ ${candidate.name}`);
        return;
      }

      setGeocodeSuggestions((current) => ({
        ...current,
        [candidate.id]: results,
      }));
      setMessage(
        `พบ ${results.length} พิกัดสำหรับ ${candidate.name} กรุณาเลือกและตรวจสอบก่อนบันทึก`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "ค้นหาพิกัดไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  function chooseCoordinate(candidate: CandidateResult, item: GeocodeResult) {
    const currentNote = drafts[candidate.id]?.note || "";
    const geocodeNote = `พิกัดที่เลือก: ${item.display_name}`;

    updateDraft(candidate.id, {
      latitude: item.latitude.toFixed(6),
      longitude: item.longitude.toFixed(6),
      note: [currentNote, geocodeNote].filter(Boolean).join("\n"),
    });
    setGeocodeSuggestions((current) => ({
      ...current,
      [candidate.id]: [],
    }));
    setMessage(
      "เลือกพิกัดแล้ว กรุณาเปิดแผนที่ตรวจตำแหน่งก่อนบันทึกเป็น GEOCODED หรือ APPROVED",
    );
  }

  async function saveState(
    candidate: CandidateResult,
    state: CandidateReviewState,
  ) {
    const draft = drafts[candidate.id];
    const latitude = draft?.latitude ? Number(draft.latitude) : undefined;
    const longitude = draft?.longitude ? Number(draft.longitude) : undefined;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      await updateCandidate(adminKey, candidate.id, {
        latitude,
        longitude,
        review_state: state,
        review_note: draft?.note || undefined,
      });
      setMessage(`อัปเดต ${candidate.name} เป็น ${state} แล้ว`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "อัปเดต candidate ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  async function promote(candidate: CandidateResult) {
    const draft = drafts[candidate.id];
    if (!draft?.slug) {
      setError("กรุณาระบุ slug ก่อน promote");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      await promoteCandidate(adminKey, candidate.id, draft.slug, candidate.name);
      setMessage(`Promote ${candidate.name} เข้า production แล้ว`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Promote ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="admin-page">
      <header className="hero">
        <p className="eyebrow">Vela Muslim Travel</p>
        <h1>Candidate Review</h1>
        <p>
          ตรวจหลักฐาน พิกัด และขอบเขตการรับรองก่อนนำสถานที่เข้า production
        </p>
      </header>

      <section className="admin-toolbar">
        <label>
          Admin API Key
          <input
            type="password"
            value={adminKey}
            onChange={(event) => setAdminKey(event.target.value)}
            autoComplete="off"
          />
        </label>
        <label>
          สถานะ
          <select
            value={filter}
            onChange={(event) =>
              setFilter(event.target.value as CandidateReviewState | "")
            }
          >
            {reviewStates.map((item) => (
              <option key={item.value || "all"} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={load} disabled={loading}>
          {loading ? "กำลังทำงาน…" : "โหลดรายการ"}
        </button>
      </section>

      {message && <p className="admin-message">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="admin-summary">{filteredCount} candidates</div>

      <section className="candidate-list">
        {candidates.map((candidate) => {
          const draft = drafts[candidate.id] || {
            latitude: "",
            longitude: "",
            note: "",
            slug: suggestedSlug(candidate),
          };
          const evidenceUrl = safeHttpUrl(candidate.source_reference);

          return (
            <article className="candidate-card" key={candidate.id}>
              <div className="candidate-head">
                <div>
                  <span className="type">{candidate.place_type}</span>
                  <h2>{candidate.name}</h2>
                  <p>
                    {[candidate.district, candidate.province]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                </div>
                <strong>{candidate.review_state}</strong>
              </div>

              <dl className="candidate-facts">
                <div>
                  <dt>Trust</dt>
                  <dd>{candidate.proposed_trust_status}</dd>
                </div>
                <div>
                  <dt>Source</dt>
                  <dd>{candidate.source_type}</dd>
                </div>
                <div>
                  <dt>Certificate</dt>
                  <dd>{candidate.certification_number || "—"}</dd>
                </div>
                <div>
                  <dt>Expiry</dt>
                  <dd>
                    {candidate.certification_expires_at
                      ? new Date(candidate.certification_expires_at).toLocaleDateString(
                          "th-TH",
                        )
                      : "—"}
                  </dd>
                </div>
              </dl>

              <p>{candidate.address || "ไม่มีที่อยู่ใน staging"}</p>

              {evidenceUrl && (
                <p>
                  <a href={evidenceUrl} target="_blank" rel="noreferrer">
                    เปิดหลักฐานต้นทาง
                  </a>
                </p>
              )}

              <div className="coordinate-grid">
                <label>
                  Latitude
                  <input
                    value={draft.latitude}
                    onChange={(event) =>
                      updateDraft(candidate.id, { latitude: event.target.value })
                    }
                  />
                </label>
                <label>
                  Longitude
                  <input
                    value={draft.longitude}
                    onChange={(event) =>
                      updateDraft(candidate.id, { longitude: event.target.value })
                    }
                  />
                </label>
              </div>

              <button
                type="button"
                className="secondary"
                onClick={() => locate(candidate)}
                disabled={loading}
              >
                ค้นหาพิกัดจากชื่อ/ที่อยู่
              </button>

              {(geocodeSuggestions[candidate.id]?.length ?? 0) > 0 && (
                <div className="geocode-suggestions">
                  {geocodeSuggestions[candidate.id].map((item) => (
                    <button
                      key={`${item.latitude}-${item.longitude}-${item.display_name}`}
                      type="button"
                      className="geocode-suggestion"
                      onClick={() => chooseCoordinate(candidate, item)}
                    >
                      <strong>{item.display_name}</strong>
                      <span>
                        {item.latitude.toFixed(6)}, {item.longitude.toFixed(6)}
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {draft.latitude && draft.longitude && (
                <p className="coordinate-review-link">
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                      `${draft.latitude},${draft.longitude}`,
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    เปิดพิกัดนี้บน Google Maps เพื่อตรวจสอบ
                  </a>
                </p>
              )}

              <label>
                Review note
                <textarea
                  value={draft.note}
                  onChange={(event) =>
                    updateDraft(candidate.id, { note: event.target.value })
                  }
                  rows={3}
                />
              </label>

              <div className="candidate-actions">
                <button
                  type="button"
                  className="secondary"
                  onClick={() => saveState(candidate, "GEOCODED")}
                  disabled={loading}
                >
                  บันทึกพิกัด
                </button>
                <button
                  type="button"
                  onClick={() => saveState(candidate, "APPROVED")}
                  disabled={loading}
                >
                  อนุมัติ
                </button>
                <button
                  type="button"
                  className="danger"
                  onClick={() => saveState(candidate, "REJECTED")}
                  disabled={loading}
                >
                  ปฏิเสธ
                </button>
              </div>

              {candidate.review_state === "APPROVED" && (
                <div className="promote-box">
                  <label>
                    Production slug
                    <input
                      value={draft.slug}
                      onChange={(event) =>
                        updateDraft(candidate.id, { slug: event.target.value })
                      }
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => promote(candidate)}
                    disabled={loading}
                  >
                    Promote เข้า production
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </section>
    </main>
  );
}
