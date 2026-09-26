import { useEffect, useMemo, useState } from "react";

import { ProductionPlaces } from "./ProductionPlaces";
import {
  checkCandidatePromotion,
  fetchAdminAudit,
  fetchAdminDashboard,
  fetchCandidateReadiness,
  fetchCandidateReviewProgress,
  fetchCandidateReviewQueue,
  fetchCandidates,
  fetchPilotReadiness,
  fetchPhase0Completion,
  promoteCandidate,
  resolveCandidateGooglePlace,
  resolveCandidateGooglePlaces,
  searchDestination,
  updateCandidate,
} from "./api";
import type {
  AdminAuditEntry,
  AdminDashboard,
  CandidatePromotionCheckResponse,
  CandidateReadinessResponse,
  CandidateResult,
  CandidateReviewProgressResponse,
  CandidateReviewState,
  CandidateReviewTask,
  GeocodeResult,
  PilotReadinessResponse,
  Phase0CompletionResponse,
} from "./types";

const pilotProvinces = [
  "",
  "นครศรีธรรมราช",
  "สุราษฎร์ธานี",
  "ชุมพร",
  "ประจวบคีรีขันธ์",
  "เพชรบุรี",
  "สระบุรี",
  "นครราชสีมา",
];

const pilotProvinceSet = new Set(pilotProvinces.filter(Boolean));

const candidateTypes: Array<{ value: "" | CandidateResult["place_type"]; label: string }> = [
  { value: "", label: "ทุกประเภท" },
  { value: "RESTAURANT", label: "ร้านอาหาร" },
  { value: "ACCOMMODATION", label: "ที่พัก" },
  { value: "MOSQUE", label: "มัสยิด" },
  { value: "PRAYER_ROOM", label: "ห้องละหมาด" },
];

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
  holdReason: string;
  sourceCheckedAt: string;
  coordinateCheckedAt: string;
  slug: string;
}

function isCandidateReviewTask(
  candidate: CandidateResult,
): candidate is CandidateReviewTask {
  return (
    "approval_blockers" in candidate &&
    "maps_search_url" in candidate &&
    "ready_to_approve" in candidate
  );
}

function isGoogleResolvableCandidate(candidate: CandidateResult): boolean {
  return (
    candidate.review_state === "DISCOVERED" &&
    Boolean(candidate.external_id) &&
    ["google_business", "google_places"].includes(
      candidate.external_provider || "",
    ) &&
    !candidate.coordinate_checked_at
  );
}


function candidateNextAction(
  candidate: CandidateResult,
  reviewTask: CandidateReviewTask | null,
  draft: Draft,
): string {
  if (candidate.review_state === "PROMOTED") {
    return "อยู่ใน production แล้ว";
  }
  if (candidate.review_state === "APPROVED") {
    return "ตรวจ duplicate / slug แล้ว Promote";
  }
  if (candidate.review_state === "REJECTED") {
    return "ตรวจเหตุผลก่อนเปิดกลับเข้า review";
  }

  if (draft.holdReason.trim()) {
    return "แก้ Manual hold ก่อนดำเนินต่อ";
  }

  if (!draft.latitude || !draft.longitude) {
    return isGoogleResolvableCandidate(candidate)
      ? "ดึงพิกัดจาก Google Place ID"
      : "ค้นหาและเลือกพิกัด";
  }

  if (!draft.coordinateCheckedAt) {
    return "เปิดแผนที่ ตรวจตำแหน่ง แล้ว ยืนยันพิกัด";
  }

  if (candidate.review_state === "DISCOVERED") {
    return "บันทึกเป็น GEOCODED";
  }

  if (reviewTask?.ready_to_approve) {
    return reviewTask.review_warnings.length > 0
      ? "ทบทวนคำเตือนก่อนอนุมัติ"
      : "พร้อมอนุมัติ";
  }

  if (!draft.sourceCheckedAt) {
    return "ตรวจหลักฐานต้นทางและยืนยัน Source cross-check";
  }

  if (reviewTask && reviewTask.approval_blockers.length > 0) {
    return "แก้ Approval blockers ที่เหลือ";
  }

  return "ตรวจข้อมูลก่อนดำเนินการต่อ";
}

export default function AdminApp() {
  const [adminKey, setAdminKey] = useState(
    () => sessionStorage.getItem("vela-admin-key") || "",
  );
  const [filter, setFilter] = useState<CandidateReviewState | "">("DISCOVERED");
  const [provinceFilter, setProvinceFilter] = useState("");
  const [typeFilter, setTypeFilter] =
    useState<"" | CandidateResult["place_type"]>("");
  const [readinessFilter, setReadinessFilter] =
    useState<
      | "ALL"
      | "READY"
      | "BLOCKED"
      | "COORDINATE_PENDING"
      | "GOOGLE_RESOLVABLE"
      | "GOOGLE_FAST_LANE"
      | "MANUAL_HOLD"
      | "EVIDENCE"
    >("ALL");
  const [candidates, setCandidates] = useState<CandidateResult[]>([]);
  const [singleReviewMode, setSingleReviewMode] = useState(false);
  const [pilotQueueOnly, setPilotQueueOnly] = useState(false);
  const [reviewIndex, setReviewIndex] = useState(0);
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [audit, setAudit] = useState<AdminAuditEntry[]>([]);
  const [pilotReadiness, setPilotReadiness] =
    useState<PilotReadinessResponse | null>(null);
  const [candidateReadiness, setCandidateReadiness] =
    useState<CandidateReadinessResponse | null>(null);
  const [reviewProgress, setReviewProgress] =
    useState<CandidateReviewProgressResponse | null>(null);
  const [phase0Completion, setPhase0Completion] =
    useState<Phase0CompletionResponse | null>(null);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [loading, setLoading] = useState(false);
  const [geocodeSuggestions, setGeocodeSuggestions] = useState<
    Record<string, GeocodeResult[]>
  >({});
  const [promotionChecks, setPromotionChecks] = useState<
    Record<string, CandidatePromotionCheckResponse>
  >({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const displayedCandidates = useMemo(() => {
    const scopedCandidates = pilotQueueOnly
      ? candidates.filter(
          (candidate) =>
            Boolean(candidate.province) &&
            pilotProvinceSet.has(candidate.province || ""),
        )
      : candidates;

    if (
      readinessFilter === "ALL" ||
      (filter !== "DISCOVERED" && filter !== "GEOCODED")
    ) {
      return scopedCandidates;
    }

    return scopedCandidates.filter((candidate) => {
      if (!isCandidateReviewTask(candidate)) return false;

      if (readinessFilter === "READY") {
        return candidate.ready_to_approve;
      }
      if (readinessFilter === "BLOCKED") {
        return !candidate.ready_to_approve;
      }
      if (readinessFilter === "COORDINATE_PENDING") {
        return candidate.approval_blockers.some((blocker) =>
          [
            "reviewed coordinates are required",
            "coordinate verification date is required",
          ].includes(blocker),
        );
      }
      if (readinessFilter === "GOOGLE_RESOLVABLE") {
        return isGoogleResolvableCandidate(candidate);
      }
      if (readinessFilter === "GOOGLE_FAST_LANE") {
        return (
          isGoogleResolvableCandidate(candidate) &&
          !candidate.approval_blockers.some((blocker) =>
            blocker.startsWith("manual review hold:"),
          )
        );
      }
      if (readinessFilter === "MANUAL_HOLD") {
        return candidate.approval_blockers.some((blocker) =>
          blocker.startsWith("manual review hold:"),
        );
      }
      if (readinessFilter === "EVIDENCE") {
        return candidate.approval_blockers.some(
          (blocker) =>
            ![
              "reviewed coordinates are required",
              "coordinate verification date is required",
            ].includes(blocker) &&
            !blocker.startsWith("manual review hold:"),
        );
      }
      return true;
    });
  }, [candidates, filter, pilotQueueOnly, readinessFilter]);

  const filteredCount = displayedCandidates.length;
  const batchGoogleCandidates = displayedCandidates.filter(
    isGoogleResolvableCandidate,
  );
  const safeReviewIndex = Math.min(
    reviewIndex,
    Math.max(displayedCandidates.length - 1, 0),
  );
  const visibleCandidates =
    singleReviewMode && displayedCandidates.length > 0
      ? [displayedCandidates[safeReviewIndex]]
      : displayedCandidates;

  useEffect(() => {
    setReviewIndex((current) =>
      Math.min(current, Math.max(displayedCandidates.length - 1, 0)),
    );
  }, [displayedCandidates.length]);

  function initializeDrafts(items: CandidateResult[]) {
    setDrafts((current) => {
      const next = { ...current };
      for (const item of items) {
        next[item.id] ??= {
          latitude: item.latitude?.toString() || "",
          longitude: item.longitude?.toString() || "",
          note: item.review_note || "",
          holdReason: item.review_hold_reason || "",
          sourceCheckedAt: item.source_checked_at || "",
          coordinateCheckedAt: item.coordinate_checked_at || "",
          slug: suggestedSlug(item),
        };
      }
      return next;
    });
  }

  async function load(overrides?: {
    province?: string;
    reviewState?: CandidateReviewState | "";
    readiness?: typeof readinessFilter;
    placeType?: "" | CandidateResult["place_type"];
    pilotOnly?: boolean;
  }) {
    if (!adminKey) {
      setError("กรุณาใส่ Admin API Key");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    sessionStorage.setItem("vela-admin-key", adminKey);

    try {
      const activeProvince = overrides?.province ?? provinceFilter;
      const activeFilter = overrides?.reviewState ?? filter;
      const activeType = overrides?.placeType ?? typeFilter;
      const activePilotOnly = overrides?.pilotOnly ?? pilotQueueOnly;
      const candidateRequest =
        activeFilter === "DISCOVERED" || activeFilter === "GEOCODED"
          ? fetchCandidateReviewQueue(
              adminKey,
              activeFilter,
              activeProvince || undefined,
              activeType || undefined,
              activePilotOnly,
            )
          : fetchCandidates(
              adminKey,
              activeFilter || undefined,
              activeProvince || undefined,
              activeType || undefined,
            );

      const [
        items,
        stats,
        recentAudit,
        readiness,
        candidateCoverage,
        progress,
        completion,
      ] = await Promise.all([
        candidateRequest,
        fetchAdminDashboard(adminKey),
        fetchAdminAudit(adminKey, 12),
        fetchPilotReadiness(adminKey),
        fetchCandidateReadiness(adminKey),
        fetchCandidateReviewProgress(adminKey),
        fetchPhase0Completion(adminKey),
      ]);
      if (overrides?.province !== undefined) {
        setProvinceFilter(overrides.province);
      }
      if (overrides?.reviewState !== undefined) {
        setFilter(overrides.reviewState);
      }
      if (overrides?.readiness !== undefined) {
        setReadinessFilter(overrides.readiness);
      }
      if (overrides?.placeType !== undefined) {
        setTypeFilter(overrides.placeType);
      }
      if (overrides?.pilotOnly !== undefined) {
        setPilotQueueOnly(overrides.pilotOnly);
      }
      setCandidates(items);
      setPromotionChecks({});
      setDashboard(stats);
      setAudit(recentAudit);
      setPilotReadiness(readiness);
      setCandidateReadiness(candidateCoverage);
      setReviewProgress(progress);
      setPhase0Completion(completion);
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
    setPromotionChecks((current) => {
      if (!(candidateId in current)) return current;
      const next = { ...current };
      delete next[candidateId];
      return next;
    });
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

  async function resolveGooglePlace(candidate: CandidateResult) {
    if (
      !candidate.external_id ||
      !["google_business", "google_places"].includes(
        candidate.external_provider || "",
      )
    ) {
      setError("Candidate นี้ไม่มี Google Place ID ที่ใช้ resolve พิกัดได้");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const result = await resolveCandidateGooglePlace(adminKey, candidate.id);
      const currentNote = drafts[candidate.id]?.note || "";
      const resolverNote =
        `Google Place ID coordinate suggestion: ${result.external_id}`;

      updateDraft(candidate.id, {
        latitude: result.latitude.toFixed(7),
        longitude: result.longitude.toFixed(7),
        note: [currentNote, resolverNote].filter(Boolean).join("\n"),
        coordinateCheckedAt: "",
      });
      setMessage(
        `ดึงพิกัดจาก Google Place ID ของ ${candidate.name} แล้ว กรุณาเปิดพิกัดบนแผนที่และยืนยันก่อนบันทึก`,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "ดึงพิกัดจาก Google Place ID ไม่สำเร็จ",
      );
    } finally {
      setLoading(false);
    }
  }

  async function resolveVisibleGooglePlaces() {
    if (!dashboard?.google_places_resolver_enabled) {
      setError("Google Places resolver ยังไม่ได้ตั้งค่าบน server");
      return;
    }
    if (batchGoogleCandidates.length === 0) {
      setMessage("ไม่มี candidate Google ที่รอดึงพิกัดในรายการปัจจุบัน");
      return;
    }

    setLoading(true);
    setError("");
    setMessage(
      `กำลังดึงพิกัด Google Place ID ${batchGoogleCandidates.length} รายการ…`,
    );

    try {
      const response = await resolveCandidateGooglePlaces(
        adminKey,
        batchGoogleCandidates.map((candidate) => candidate.id),
      );
      const patches: Record<string, Partial<Draft>> = {};
      const failures: string[] = [];
      const byId = new Map(
        batchGoogleCandidates.map((candidate) => [candidate.id, candidate]),
      );

      for (const item of response.results) {
        const candidate = byId.get(item.candidate_id);
        if (!candidate) continue;

        if (!item.suggestion) {
          failures.push(candidate.name);
          continue;
        }

        const currentNote =
          drafts[candidate.id]?.note || candidate.review_note || "";
        const resolverNote =
          `Google Place ID coordinate suggestion: ${item.suggestion.external_id}`;
        const note = currentNote.includes(resolverNote)
          ? currentNote
          : [currentNote, resolverNote].filter(Boolean).join("\n");

        patches[candidate.id] = {
          latitude: item.suggestion.latitude.toFixed(7),
          longitude: item.suggestion.longitude.toFixed(7),
          note,
          coordinateCheckedAt: "",
        };
      }

      if (Object.keys(patches).length > 0) {
        setDrafts((current) => {
          const next = { ...current };
          for (const [candidateId, patch] of Object.entries(patches)) {
            next[candidateId] = {
              ...next[candidateId],
              ...patch,
            };
          }
          return next;
        });
      }

      if (failures.length > 0) {
        setError(
          `ดึงพิกัดไม่สำเร็จ ${failures.length} รายการ: ${failures.join(", ")}`,
        );
      }
      setMessage(
        `ดึงพิกัดเข้า draft แล้ว ${Object.keys(patches).length}/${batchGoogleCandidates.length} รายการ กรุณาเปิดแผนที่และยืนยันแต่ละจุดก่อนบันทึก`,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "ดึงพิกัด Google Place ID แบบกลุ่มไม่สำเร็จ",
      );
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
      coordinateCheckedAt: "",
    });
    setGeocodeSuggestions((current) => ({
      ...current,
      [candidate.id]: [],
    }));
    setMessage(
      "เลือกพิกัดแล้ว กรุณาเปิดแผนที่ตรวจตำแหน่งก่อนบันทึกเป็น GEOCODED หรือ APPROVED",
    );
  }

  async function confirmCoordinateAndSave(candidate: CandidateResult) {
    const draft = drafts[candidate.id];
    if (!draft?.latitude || !draft?.longitude) {
      setError("ต้องมี latitude/longitude ก่อนยืนยันพิกัด");
      return;
    }

    const latitude = Number(draft.latitude);
    const longitude = Number(draft.longitude);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      setError("latitude/longitude ไม่ถูกต้อง");
      return;
    }

    const coordinateCheckedAt = new Date().toISOString();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      await updateCandidate(adminKey, candidate.id, {
        latitude,
        longitude,
        review_state: "GEOCODED",
        review_note: draft.note || undefined,
        review_hold_reason: draft.holdReason ?? "",
        source_checked_at: draft.sourceCheckedAt || undefined,
        coordinate_checked_at: coordinateCheckedAt,
      });
      setMessage(`ยืนยันพิกัดและบันทึก ${candidate.name} เป็น GEOCODED แล้ว`);
      await load();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "ยืนยันพิกัดและบันทึก GEOCODED ไม่สำเร็จ",
      );
    } finally {
      setLoading(false);
    }
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
        review_hold_reason: draft?.holdReason ?? "",
        source_checked_at: draft?.sourceCheckedAt || undefined,
        coordinate_checked_at: draft?.coordinateCheckedAt || undefined,
      });
      setMessage(`อัปเดต ${candidate.name} เป็น ${state} แล้ว`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "อัปเดต candidate ไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  async function preflightPromotion(candidate: CandidateResult) {
    const draft = drafts[candidate.id];
    if (!draft?.slug.trim()) {
      setError("กรุณาระบุ slug ก่อนตรวจ promotion");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const result = await checkCandidatePromotion(
        adminKey,
        candidate.id,
        draft.slug.trim(),
      );
      setPromotionChecks((current) => ({
        ...current,
        [candidate.id]: result,
      }));

      if (result.can_promote) {
        setMessage(`${candidate.name} ผ่าน promotion preflight`);
      } else if (result.promotion_blockers.length > 0) {
        setError(result.promotion_blockers.join(" · "));
      } else if (result.duplicate) {
        setError(
          `พบสถานที่ประเภทเดียวกันใกล้ ${result.duplicate.distance_m.toFixed(
            0,
          )} ม.: ${result.duplicate.name_th} (${result.duplicate.slug})`,
        );
      } else if (result.slug_exists) {
        setError(`slug "${draft.slug.trim()}" ถูกใช้แล้ว`);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "ตรวจ promotion preflight ไม่สำเร็จ",
      );
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
        <label>
          จังหวัด
          <select
            value={provinceFilter}
            onChange={(event) => setProvinceFilter(event.target.value)}
          >
            {pilotProvinces.map((province) => (
              <option key={province || "all"} value={province}>
                {province || "ทุกจังหวัดนำร่อง"}
              </option>
            ))}
          </select>
        </label>
        <label>
          ประเภท
          <select
            value={typeFilter}
            onChange={(event) =>
              setTypeFilter(
                event.target.value as "" | CandidateResult["place_type"],
              )
            }
          >
            {candidateTypes.map((item) => (
              <option key={item.value || "all"} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          ความพร้อม
          <select
            value={readinessFilter}
            disabled={filter !== "DISCOVERED" && filter !== "GEOCODED"}
            onChange={(event) =>
              setReadinessFilter(
                event.target.value as
                  | "ALL"
                  | "READY"
                  | "BLOCKED"
                  | "COORDINATE_PENDING"
                  | "GOOGLE_RESOLVABLE"
                  | "MANUAL_HOLD"
                  | "EVIDENCE",
              )
            }
          >
            <option value="ALL">ทั้งหมด</option>
            <option value="READY">พร้อมอนุมัติ</option>
            <option value="BLOCKED">ยังติด blocker</option>
            <option value="COORDINATE_PENDING">พิกัดยังไม่ครบ</option>
            <option value="GOOGLE_RESOLVABLE">Google ดึงพิกัดได้</option>
            <option value="GOOGLE_FAST_LANE">Google Fast Lane (ไม่มี hold)</option>
            <option value="MANUAL_HOLD">มี Manual hold</option>
            <option value="EVIDENCE">หลักฐานยังไม่ผ่าน</option>
          </select>
        </label>
        <button
          type="button"
          onClick={() => void load({ pilotOnly: false })}
          disabled={loading}
        >
          {loading ? "กำลังทำงาน…" : "โหลดรายการ"}
        </button>
      </section>

      {message && <p className="admin-message">{message}</p>}
      {error && <p className="error">{error}</p>}

      {phase0Completion && (
        <section className="pilot-readiness">
          <div className="pilot-readiness-head">
            <div>
              <h2>Phase 0 Completion</h2>
              <p>
                {phase0Completion.mechanical_ready
                  ? "Mechanical Ready — เหลือ Final Manual Acceptance"
                  : "ยังไม่สมบูรณ์ — ทำ blocker ด้านล่างให้หมดก่อน"}
              </p>
              <small>
                Review ค้าง {phase0Completion.active_review_pending} · รอ Promote{" "}
                {phase0Completion.approved_waiting_promotion} · Promoted{" "}
                {phase0Completion.promoted_candidates} · Rejected{" "}
                {phase0Completion.rejected_candidates}
              </small>
            </div>
            <strong>
              {phase0Completion.mechanical_ready ? "MECHANICAL READY" : "IN PROGRESS"}
            </strong>
          </div>

          {!phase0Completion.mechanical_ready && (
            <div className="review-queue-actions">
              {phase0Completion.google_fast_lane > 0 && (
                <button
                  type="button"
                  className="secondary"
                  disabled={loading}
                  onClick={() => {
                    setSingleReviewMode(true);
                    setReviewIndex(0);
                    void load({
                      province: "",
                      reviewState: "DISCOVERED",
                      readiness: "GOOGLE_FAST_LANE",
                      placeType: "",
                      pilotOnly: true,
                    });
                  }}
                >
                  ทำ Google Fast Lane {phase0Completion.google_fast_lane}
                </button>
              )}
              {phase0Completion.approved_waiting_promotion > 0 && (
                <button
                  type="button"
                  className="secondary"
                  disabled={loading}
                  onClick={() =>
                    void load({
                      province: "",
                      reviewState: "APPROVED",
                      readiness: "ALL",
                      placeType: "",
                      pilotOnly: true,
                    })
                  }
                >
                  Promote คิว Pilot {phase0Completion.approved_waiting_promotion}
                </button>
              )}
            </div>
          )}

          {!phase0Completion.mechanical_ready &&
            phase0Completion.blockers.length > 0 && (
              <div className="approval-blockers">
                <strong>สิ่งที่ต้องทำก่อนปิด Phase 0</strong>
                <ul>
                  {phase0Completion.blockers.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

          {phase0Completion.mechanical_ready &&
            phase0Completion.manual_acceptance_required && (
              <div className="approval-blockers">
                <strong>Final Manual Acceptance</strong>
                <ul>
                  {phase0Completion.manual_acceptance_steps.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
        </section>
      )}

      {dashboard && (
        <section className="admin-dashboard">
          <div><strong>{dashboard.candidates_total}</strong><span>Candidate ทั้งหมด</span></div>
          <div><strong>{dashboard.discovered}</strong><span>รอตรวจ</span></div>
          <div><strong>{dashboard.geocoded}</strong><span>มีพิกัดแล้ว</span></div>
          <div>
            <strong>{dashboard.approved}</strong>
            <span>รอ Promote</span>
            {dashboard.approved > 0 && (
              <button
                type="button"
                className="secondary"
                disabled={loading}
                onClick={() =>
                  void load({
                    province: "",
                    reviewState: "APPROVED",
                    readiness: "ALL",
                    placeType: "",
                    pilotOnly: false,
                  })
                }
              >
                เปิดคิว
              </button>
            )}
          </div>
          <div><strong>{dashboard.promoted}</strong><span>Promoted</span></div>
          <div><strong>{dashboard.production_places}</strong><span>Production places</span></div>
          <div><strong>{dashboard.certifications_expiring_30d}</strong><span>หลักฐานใกล้หมดอายุ 30 วัน</span></div>
          <div><strong>{dashboard.expired_verifications}</strong><span>หลักฐานหมดอายุ</span></div>
        </section>
      )}

      {reviewProgress && (
        <section className="pilot-readiness review-progress">
          <div className="pilot-readiness-head">
            <div>
              <h2>Manual Review Progress</h2>
              <p>
                เหลือ {reviewProgress.pending} รายการในขั้นตรวจพิกัด/หลักฐาน
                ก่อนอนุมัติ
              </p>
              <small>
                พิกัดค้าง {reviewProgress.coordinate_pending} · Google ดึงได้{" "}
                {reviewProgress.google_resolvable} · Manual hold{" "}
                {reviewProgress.manual_hold} · หลักฐาน{" "}
                {reviewProgress.evidence_blocked}
              </small>
            </div>
            <div className="review-queue-actions">
              {reviewProgress.ready_to_approve > 0 && (
                <button
                  type="button"
                  className="secondary"
                  disabled={loading}
                  onClick={() =>
                    void load({
                      province: "",
                      reviewState: "GEOCODED",
                      readiness: "READY",
                      placeType: "",
                    })
                  }
                >
                  เปิดคิวพร้อมอนุมัติ {reviewProgress.ready_to_approve}
                </button>
              )}
              {reviewProgress.google_fast_lane > 0 && (
                <button
                  type="button"
                  className="secondary"
                  disabled={loading}
                  onClick={() => {
                    setSingleReviewMode(true);
                    setReviewIndex(0);
                    void load({
                      province: "",
                      reviewState: "DISCOVERED",
                      readiness: "GOOGLE_FAST_LANE",
                      placeType: "",
                      pilotOnly: true,
                    });
                  }}
                >
                  เปิด Google Fast Lane {reviewProgress.google_fast_lane}
                </button>
              )}
              {reviewProgress.google_resolvable > 0 && (
                <button
                  type="button"
                  className="secondary"
                  disabled={loading}
                  onClick={() => {
                    setSingleReviewMode(true);
                    setReviewIndex(0);
                    void load({
                      province: "",
                      reviewState: "DISCOVERED",
                      readiness: "GOOGLE_RESOLVABLE",
                      placeType: "",
                      pilotOnly: true,
                    });
                  }}
                >
                  เปิดคิว Google {reviewProgress.google_resolvable}
                </button>
              )}
              <strong
                className={
                  reviewProgress.blocked === 0 ? "ready" : "not-ready"
                }
              >
                {reviewProgress.ready_to_approve} READY · {reviewProgress.blocked} BLOCKED
              </strong>
            </div>
          </div>
          <div className="pilot-readiness-grid">
            {reviewProgress.provinces.map((item) => (
              <button
                key={item.province}
                type="button"
                className="progress-province"
                disabled={loading}
                onClick={() =>
                  void load({ province: item.province, pilotOnly: true })
                }
              >
                <strong>{item.province}</strong>
                <span>{item.pending} ค้าง</span>
                <small>
                  พร้อมอนุมัติ {item.ready_to_approve} · ติด blocker{" "}
                  {item.blocked}
                </small>
                <small>
                  พิกัด {item.coordinate_pending} · Google {item.google_resolvable} ·
                  Fast {item.google_fast_lane} · Hold {item.manual_hold} · หลักฐาน{" "}
                  {item.evidence_blocked}
                </small>
              </button>
            ))}
          </div>
        </section>
      )}

      {candidateReadiness && (
        <section className="pilot-readiness candidate-readiness">
          <div className="pilot-readiness-head">
            <div>
              <h2>Candidate Coverage</h2>
              <p>
                {candidateReadiness.ready
                  ? "Discovery queue ครบร้านอาหารและมัสยิดทุกจังหวัดเป้าหมาย และมีที่พักอย่างน้อย 2 จังหวัด"
                  : "Discovery queue ยังมีช่องว่างก่อนเริ่ม review เต็มเส้นทาง"}
              </p>
            </div>
            <strong className={candidateReadiness.ready ? "ready" : "not-ready"}>
              {candidateReadiness.ready ? "REVIEW READY" : "GAPS"}
            </strong>
          </div>
          <div className="pilot-readiness-grid">
            {candidateReadiness.provinces.map((item) => (
              <div key={item.province}>
                <strong>{item.province}</strong>
                <small>
                  ร้าน {item.restaurants} · มัสยิด {item.mosques} · ที่พัก{" "}
                  {item.accommodation}
                </small>
                <small>
                  มีพิกัด {item.geocoded} · อนุมัติ {item.approved} · Promote{" "}
                  {item.promoted}
                </small>
              </div>
            ))}
          </div>
        </section>
      )}

      {pilotReadiness && (
        <section className="pilot-readiness">
          <div className="pilot-readiness-head">
            <div>
              <h2>Pilot Readiness</h2>
              <p>
                {pilotReadiness.ready
                  ? "ทุกจังหวัดมีร้านอาหารและมัสยิด และมีที่พักอย่างน้อย 2 จังหวัด"
                  : "Production coverage ยังไม่ครบ: ต้องมีร้านอาหารและมัสยิดทุกจังหวัด และที่พักอย่างน้อย 2 จังหวัด"}
              </p>
              <small>
                ที่พักครอบคลุม {pilotReadiness.accommodation_provinces}/
                {pilotReadiness.required_accommodation_provinces} จังหวัดขั้นต่ำ
              </small>
            </div>
            <strong className={pilotReadiness.ready ? "ready" : "not-ready"}>
              {pilotReadiness.ready ? "READY" : "NOT READY"}
            </strong>
          </div>
          <div className="pilot-readiness-grid">
            {pilotReadiness.provinces.map((item) => (
              <div key={item.province}>
                <strong>{item.province}</strong>
                <span>{item.total} จุด</span>
                <small>
                  ร้าน {item.restaurants} · มัสยิด {item.mosques} · ที่พัก{" "}
                  {item.accommodation}
                </small>
                {item.missing_types.filter((type) => type !== "ACCOMMODATION").length > 0 && (
                  <small>
                    ขาดขั้นต่ำรายจังหวัด:{" "}
                    {item.missing_types
                      .filter((type) => type !== "ACCOMMODATION")
                      .join(", ")}
                  </small>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="review-queue-bar">
        <div className="admin-summary">
          {filteredCount} candidates ในรายการปัจจุบัน
          {pilotQueueOnly && <span>{" "}· Pilot queue</span>}
          {readinessFilter === "GOOGLE_RESOLVABLE" && (
            <span>
              {" "}· Google queue เหลือ {filteredCount}
            </span>
          )}
          {singleReviewMode && filteredCount > 0 && (
            <span>
              {" "}· กำลังตรวจ {safeReviewIndex + 1}/{filteredCount}
            </span>
          )}
          {singleReviewMode && filteredCount === 0 && (
            <span>{" "}· คิวนี้เสร็จแล้ว</span>
          )}
        </div>
        <div className="review-queue-actions">
          {dashboard?.google_places_resolver_enabled && (
            <button
              type="button"
              className="secondary"
              disabled={loading || batchGoogleCandidates.length === 0}
              onClick={() => void resolveVisibleGooglePlaces()}
              title="เติมพิกัดลง draft เท่านั้น ยังไม่ยืนยันหรือบันทึก state"
            >
              ดึง Google พิกัด {batchGoogleCandidates.length} รายการ
            </button>
          )}
          <button
            type="button"
            className="secondary"
            disabled={filteredCount === 0}
            onClick={() => {
              setSingleReviewMode((current) => !current);
              setReviewIndex(0);
            }}
          >
            {singleReviewMode ? "แสดงทั้งหมด" : "ตรวจทีละรายการ"}
          </button>
          {singleReviewMode && (
            <>
              <button
                type="button"
                className="secondary"
                disabled={safeReviewIndex <= 0}
                onClick={() => setReviewIndex(safeReviewIndex - 1)}
              >
                ก่อนหน้า
              </button>
              <button
                type="button"
                className="secondary"
                disabled={safeReviewIndex >= filteredCount - 1}
                onClick={() => setReviewIndex(safeReviewIndex + 1)}
              >
                ถัดไป
              </button>
            </>
          )}
        </div>
      </div>

      {audit.length > 0 && (
        <section className="admin-audit">
          <h2>กิจกรรมล่าสุด</h2>
          {audit.map((entry) => (
            <div key={entry.id}>
              <strong>{entry.action}</strong>
              <span>{entry.entity_id || entry.entity_type}</span>
              <time>{new Date(entry.created_at).toLocaleString("th-TH")}</time>
            </div>
          ))}
        </section>
      )}

      <ProductionPlaces adminKey={adminKey} />

      <section className="candidate-list">
        {visibleCandidates.map((candidate) => {
          const draft = drafts[candidate.id] || {
            latitude: "",
            longitude: "",
            note: "",
            holdReason: "",
            sourceCheckedAt: candidate.source_checked_at || "",
            coordinateCheckedAt: candidate.coordinate_checked_at || "",
            slug: suggestedSlug(candidate),
          };
          const evidenceUrl = safeHttpUrl(candidate.source_reference);
          const reviewTask = isCandidateReviewTask(candidate)
            ? candidate
            : null;
          const nextAction = candidateNextAction(candidate, reviewTask, draft);
          const hasUnsavedCoordinateDraft =
            Boolean(draft.latitude && draft.longitude) &&
            (
              Number(draft.latitude) !== candidate.latitude ||
              Number(draft.longitude) !== candidate.longitude
            );

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
                  <small>
                    ขั้นตอนถัดไป: <strong>{nextAction}</strong>
                  </small>
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
                <div>
                  <dt>Source checked</dt>
                  <dd>
                    {candidate.source_checked_at
                      ? new Date(candidate.source_checked_at).toLocaleString("th-TH")
                      : "ยังไม่ได้ยืนยัน"}
                  </dd>
                </div>
              </dl>

              <p>{candidate.address || "ไม่มีที่อยู่ใน staging"}</p>

              <div className="candidate-review-links">
                {evidenceUrl && (
                  <a href={evidenceUrl} target="_blank" rel="noreferrer">
                    เปิดหลักฐานต้นทาง
                  </a>
                )}
                {reviewTask?.maps_search_url && (
                  <a
                    href={reviewTask.maps_search_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    เปิดสถานที่บน Google Maps
                  </a>
                )}
              </div>

              {reviewTask && reviewTask.approval_blockers.length > 0 && (
                  <div className="approval-blockers">
                    <strong>ยังอนุมัติไม่ได้</strong>
                    <ul>
                      {reviewTask.approval_blockers.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

              {reviewTask && reviewTask.review_warnings.length > 0 && (
                <div className="approval-blockers">
                  <strong>คำเตือนก่อน Promote</strong>
                  <ul>
                    {reviewTask.review_warnings.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {hasUnsavedCoordinateDraft && (
                <p className="admin-message">
                  มีพิกัดใหม่ใน draft — ยังไม่ได้บันทึกหรือยืนยัน
                </p>
              )}

              <div className="coordinate-grid">
                <label>
                  Latitude
                  <input
                    value={draft.latitude}
                    onChange={(event) =>
                      updateDraft(candidate.id, {
                        latitude: event.target.value,
                        coordinateCheckedAt: "",
                      })
                    }
                  />
                </label>
                <label>
                  Longitude
                  <input
                    value={draft.longitude}
                    onChange={(event) =>
                      updateDraft(candidate.id, {
                        longitude: event.target.value,
                        coordinateCheckedAt: "",
                      })
                    }
                  />
                </label>
              </div>

              <div className="candidate-actions">
                {dashboard?.google_places_resolver_enabled &&
                  candidate.external_id &&
                  ["google_business", "google_places"].includes(
                    candidate.external_provider || "",
                  ) && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => void resolveGooglePlace(candidate)}
                      disabled={loading}
                    >
                      ดึงพิกัดจาก Google Place ID
                    </button>
                  )}
                <button
                  type="button"
                  className="secondary"
                  onClick={() => locate(candidate)}
                  disabled={loading}
                >
                  ค้นหาพิกัดจากชื่อ/ที่อยู่
                </button>
              </div>

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

              {draft.latitude && draft.longitude && (
                <div className="source-check-control">
                  <div>
                    <strong>Coordinate verification</strong>
                    <small>
                      {draft.coordinateCheckedAt
                        ? `ตรวจพิกัดล่าสุด ${new Date(
                            draft.coordinateCheckedAt,
                          ).toLocaleString("th-TH")}`
                        : "ยังไม่ได้ยืนยันพิกัดนี้"}
                    </small>
                  </div>
                  <div className="candidate-actions">
                    <button
                      type="button"
                      className="secondary"
                      onClick={() =>
                        updateDraft(candidate.id, {
                          coordinateCheckedAt: new Date().toISOString(),
                        })
                      }
                      disabled={loading}
                    >
                      ยืนยันพิกัดนี้แล้ว
                    </button>
                    {candidate.review_state === "DISCOVERED" && (
                      <button
                        type="button"
                        onClick={() => void confirmCoordinateAndSave(candidate)}
                        disabled={loading}
                        title="ใช้หลังเปิดพิกัดบนแผนที่และตรวจว่าเป็นสถานที่ถูกต้องแล้ว"
                      >
                        ยืนยันพิกัด + บันทึก GEOCODED
                      </button>
                    )}
                  </div>
                </div>
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

              <label>
                Manual review hold
                <textarea
                  value={draft.holdReason}
                  onChange={(event) =>
                    updateDraft(candidate.id, {
                      holdReason: event.target.value,
                    })
                  }
                  rows={2}
                  placeholder="เว้นว่างเมื่อตรวจและแก้ประเด็นนี้เรียบร้อยแล้ว"
                />
                <small>
                  ถ้ามีข้อความในช่องนี้ ระบบจะไม่อนุญาตให้ APPROVED
                </small>
              </label>

              <div className="source-check-control">
                <div>
                  <strong>Source cross-check</strong>
                  <small>
                    {draft.sourceCheckedAt
                      ? `ตรวจล่าสุด ${new Date(draft.sourceCheckedAt).toLocaleString("th-TH")}`
                      : "ยังไม่ได้ยืนยันการตรวจ source"}
                  </small>
                </div>
                <button
                  type="button"
                  className="secondary"
                  onClick={() =>
                    updateDraft(candidate.id, {
                      sourceCheckedAt: new Date().toISOString(),
                    })
                  }
                  disabled={loading}
                >
                  ยืนยันว่าตรวจ source ตอนนี้
                </button>
              </div>

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
                  disabled={
                    loading ||
                    candidate.review_state !== "GEOCODED" ||
                    (reviewTask !== null && !reviewTask.ready_to_approve)
                  }
                  title={
                    candidate.review_state !== "GEOCODED"
                      ? "ต้องบันทึกเป็น GEOCODED ก่อนอนุมัติ"
                      : reviewTask !== null && !reviewTask.ready_to_approve
                        ? "ต้องแก้ approval blockers ก่อนอนุมัติ"
                        : undefined
                  }
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
                    className="secondary"
                    onClick={() => void preflightPromotion(candidate)}
                    disabled={loading}
                  >
                    ตรวจ duplicate / slug
                  </button>
                  {promotionChecks[candidate.id] && (
                    <small>
                      {promotionChecks[candidate.id].can_promote
                        ? "Preflight ผ่าน"
                        : promotionChecks[candidate.id].promotion_blockers.length > 0
                          ? promotionChecks[candidate.id].promotion_blockers.join(" · ")
                          : promotionChecks[candidate.id].duplicate
                            ? `พบ ${promotionChecks[candidate.id].duplicate?.name_th} ใกล้ ${promotionChecks[candidate.id].duplicate?.distance_m.toFixed(0)} ม.`
                            : "slug ซ้ำ"}
                    </small>
                  )}
                  <button
                    type="button"
                    onClick={() => promote(candidate)}
                    disabled={
                      loading ||
                      promotionChecks[candidate.id]?.can_promote !== true
                    }
                    title={
                      promotionChecks[candidate.id]?.can_promote === true
                        ? undefined
                        : "ตรวจ duplicate / slug ให้ผ่านก่อน promote"
                    }
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
