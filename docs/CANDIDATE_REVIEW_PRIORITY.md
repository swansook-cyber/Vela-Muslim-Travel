# Candidate Review Priority

The Admin candidate list supports filtering by:

- review state,
- pilot province,
- place type.

Default ordering prioritizes the initial road corridor:

1. นครศรีธรรมราช
2. สุราษฎร์ธานี
3. ชุมพร
4. ประจวบคีรีขันธ์
5. เพชรบุรี
6. สระบุรี
7. นครราชสีมา

This keeps review work aligned with the route-first pilot instead of expanding
the directory nationwide before the core trip experience is proven.


## Current review milestone — 2026-09-25

The first public-source cross-check pass is complete for all **23 candidates**
inside the seven-province pilot corridor.

The seed file contains **24 candidates total**: 23 in the pilot corridor plus
one Bangkok candidate outside the corridor.

Cross-check completion does not move candidate state. The next gate is manual
coordinate verification in Admin:

1. open the source evidence,
2. compare current public identity/address/phone,
3. select a coordinate candidate,
4. visually verify the exact map location,
5. save as `GEOCODED`,
6. resolve any evidence, closure, address or phone discrepancy,
7. approve only after server blockers are clear.

Known review flags from the first pass are recorded in
`docs/PILOT_REVIEW_LOG.md`. In particular, temporary-closure or conflicting
address/phone evidence must be resolved rather than normalized automatically.


## Coordinate queue checkpoint — 2026-09-26

The pilot corridor currently has **15 GEOCODED** candidates and **8 DISCOVERED**
candidates remaining.

Of those 8 coordinate-pending candidates:

- **7** already carry a Google business/place ID and can use the Admin
  server-side Google batch resolver to obtain draft coordinate suggestions.
- **1** (`เน้นเนื้อ@ประจวบฮาลาล`) does not use a Google provider in staging.
  Its operating-status hold was resolved on 2026-09-26, but exact coordinates
  still require manual review.

Google resolver output is still a suggestion only. A reviewer must open the
suggested point on the map, confirm the exact venue, record
`coordinate_checked_at`, and resolve any manual hold before approval.


## Google coordinate execution queue

For the current 7 Google-resolvable pilot candidates, review the **6**
no-hold items first so the queue shrinks quickly, then handle the one
Google-resolvable candidate with an explicit hold separately.

### Straightforward coordinate review

1. **มัสยิดกลางจังหวัดเพชรบุรี**
   - Google Place ID: `ChIJP0BtFTom_TARfXE8GeUMrYM`
   - No manual hold recorded.
2. **SALASA HALAL RESTAURANT KHAOYAI**
   - Google Place ID: `ChIJgZfAAmsyHDERlceMtKji41g`
   - No manual hold recorded.
3. **ร้านอาหารอิสลามตลาดแขก อ.ปากช่อง**
   - Google Place ID: `ChIJu4-pVzEqHDERNKY1RFId_Yc`
   - No manual hold recorded.
4. **อาซีย๊ะอาหารอิสลาม Halal**
   - Google Place ID: `ChIJ3XS9QSsrHDER4FprdurFZCo`
   - No manual hold recorded.
5. **กะมา ครัวมุสลิม ฮาลาล**
   - Google Place ID: `ChIJBzAp2VpN_zARrGXZ_BL7X98`
   - No manual hold recorded.
6. **มัสยิดยันน่าตุ้ลฟิรเดาซ์**
   - Google Place ID: `ChIJg8AZfzEqHDERIEmyXoK-g_0`
   - Current canonical address: 3 ถนนเทศบาล 22 ซอย 1 ปากช่อง.
   - Moo 2 / Moo 11 historical-address difference is retained in review notes,
     but no longer blocks coordinate review or later approval by itself.
For each item: resolve the Google coordinate into draft, open the exact point on
Google Maps, visually confirm the venue identity, then use
**ยืนยันพิกัด + บันทึก GEOCODED**. This step must not infer certification or
approve the candidate.

### Coordinate review with an existing hold

7. **คุณย่าเขาใหญ่ KhunYaaKhaoyai HalalResort**
   - Google Place ID: `ChIJVy7c7Bg7HDERjTbk8mJLjSI`
   - Google still matches the staging address and phone 084-673-1717.
   - Current Makan Halal Guide and TripNiceDay publish phone 089-791-3785.
   - Resolve the phone conflict before approval. Coordinate review may continue,
     but the hold must remain after GEOCODED.

### Non-Google coordinate review

**เน้นเนื้อ@ประจวบฮาลาล** stays outside the Google queue because staging does
not carry a Google provider ID. The prior temporary-closure hold was cleared on
2026-09-26 after current Makan, Wongnai/LINE MAN and Restaurant Guru activity
confirmed ongoing operation. It remains `DISCOVERED` until an exact coordinate
is manually reviewed.
