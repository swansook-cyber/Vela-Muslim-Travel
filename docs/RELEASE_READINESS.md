# Release Readiness

Checkpoint: 2026-09-26

This file is the short operational checklist for moving Vela Muslim Travel from
the current reviewed pilot into a usable release. It does not replace
`docs/PHASE0_ACCEPTANCE.md`; it turns those rules into execution order.

## 1. Code readiness

Current implementation includes:

- traveler PWA for Near Me and Along My Route,
- MapLibre route/result map,
- road-detour checks,
- trust/provenance/freshness display,
- Google/Apple Maps handoff,
- Admin candidate review and production maintenance,
- Google Place-ID coordinate resolver,
- Google Fast Lane,
- approval blockers and state-machine guards,
- duplicate/slug/certificate promotion preflight,
- Phase 0 Completion dashboard,
- guarded Final Phase 0 Acceptance,
- production Docker Compose, health checks, backups and deploy preflight,
- API, Web, PostGIS integration and Container CI.

No new product feature is required to close Phase 0.

## 2. Pilot data readiness

Before continuing manual review on an existing deployment, sync the current
candidate seed using the controlled dry-run/apply procedure in
`deploy/DEPLOYMENT.md`. This is required for the 2026-09-26 KhunYaa phone
conflict hold to appear in the running Admin queue.

Seed checkpoint:

- 23 candidates inside the seven-province pilot corridor,
- 15 GEOCODED,
- 8 DISCOVERED,
- 7 DISCOVERED candidates are Google-resolvable,
- 5 of those are Google Fast Lane candidates without manual holds,
- 2 Google-resolvable candidates have explicit holds,
- 1 non-Google candidate has a temporary-closure hold.

### Execute first — Google Fast Lane

1. มัสยิดกลางจังหวัดเพชรบุรี
2. SALASA HALAL RESTAURANT KHAOYAI
3. ร้านอาหารอิสลามตลาดแขก อ.ปากช่อง
4. อาซีย๊ะอาหารอิสลาม Halal
5. กะมา ครัวมุสลิม ฮาลาล

For every item:

`resolve draft → open exact map point → visually confirm venue → GEOCODED`

Do not infer certification or approve automatically.

### Then resolve held coordinate work

- คุณย่าเขาใหญ่ KhunYaaKhaoyai HalalResort:
  Google currently matches the seed phone 084-673-1717, while Makan Halal Guide
  and TripNiceDay publish 089-791-3785. Resolve the phone conflict before
  approval; coordinate review can proceed while the hold remains.
- มัสยิดยันน่าตุ้ลฟิรเดาซ์:
  keep the address hold until current CICOT Moo 2 and historical
  Mu 11 / Kaek Market / Trok Chumchon Surao evidence is reconciled.
- เน้นเนื้อ@ประจวบฮาลาล:
  confirm reopening before approval; current checkpoint records a temporarily
  closed Google business status.

### Resolve existing GEOCODED holds before approval

- มัสยิดอันซอรุสซุนนะฮฺ — conflicting phone sources.
- มัสยิดนูรุ้ลเอี๊ยะซาน — conflicting CICOT/Google phone.
- มัสยิดมูฮาญิรีน — registered address versus map address.
- Ayah Restaurant Halal — plus-code/Sap Wai versus 16/6 Moo 5 address.
- มัสยิดมูฮัมมาดียะห์ บ้านดอนมะม่วง — Tha Chana versus same-name map result.
- มัสยิดนุรุ้ลอีมาน — Moo 2 versus Moo 9.
- Twin Lotus Hotel — halal certification is service/kitchen scope only and
  expires 2026-10-22; re-check before promotion.

## 3. Approval and promotion

For each candidate after review blockers are clear:

1. APPROVE only from GEOCODED.
2. Run promotion preflight.
3. Resolve duplicate/slug/certificate blockers.
4. Promote to production.
5. Re-open Phase 0 Completion and continue until:
   - active review pending = 0,
   - approved waiting promotion = 0,
   - production coverage gate passes.

The dashboard must then show `MECHANICAL READY`.

## 4. Final route acceptance

After Mechanical Ready:

1. Run the real pilot route smoke matrix at 2 km.
2. Run and require the 5 km core-category gate to pass.
3. Run the same route at 10 km.
4. Inspect stop ordering, practical detours and evidence freshness.
5. Tick all Final Manual Acceptance checks in Admin.
6. Press **Accept Phase 0**.

The Admin dashboard must then show:

`PHASE 0 COMPLETE`

Any later pilot-candidate update newer than the acceptance record invalidates
the final acceptance and requires the manual route checks again.

## 5. Production launch

Before starting production:

```bash
python3 deploy/preflight.py deploy/.env
```

Then:

```bash
docker compose --env-file deploy/.env -f docker-compose.prod.yml up -d --build
curl -fsS http://127.0.0.1:8080/api/health
```

Verify:

- traveler PWA loads,
- Near Me works,
- Along My Route works,
- trust/freshness is visible on results,
- Admin loads,
- Google resolver is enabled only when its private API key is configured,
- Phase 0 Completion shows the expected final state.

## Stop condition

Do not add unrelated features before this checklist reaches
`PHASE 0 COMPLETE`. The remaining work is data review, promotion, route QA and
deployment verification—not feature expansion.
