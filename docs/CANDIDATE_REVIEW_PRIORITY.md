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
- **1** (`เน้นเนื้อ@ประจวบฮาลาล`) does not use a Google provider in staging and
  is also under an explicit temporary-closure hold.

Google resolver output is still a suggestion only. A reviewer must open the
suggested point on the map, confirm the exact venue, record
`coordinate_checked_at`, and resolve any manual hold before approval.


## Google coordinate execution queue

For the current 7 Google-resolvable pilot candidates, review the straightforward
items first so the queue shrinks quickly, then handle the address-discrepancy
case separately.

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
6. **คุณย่าเขาใหญ่ KhunYaaKhaoyai HalalResort**
   - Google Place ID: `ChIJVy7c7Bg7HDERjTbk8mJLjSI`
   - No manual hold recorded.

For each item: resolve the Google coordinate into draft, open the exact point on
Google Maps, visually confirm the venue identity, then use
**ยืนยันพิกัด + บันทึก GEOCODED**. This step must not infer certification or
approve the candidate.

### Coordinate review with an existing hold

7. **มัสยิดยันน่าตุ้ลฟิรเดาซ์**
   - Google Place ID: `ChIJg8AZfzEqHDERIEmyXoK-g_0`
   - Keep the manual hold after coordinate confirmation.
   - Reconcile current CICOT Moo 2 with historical Mu 11 / Kaek Market /
     Trok Chumchon Surao evidence before approval.
   - Do not infer coordinates from the historical address.

### Non-Google coordinate hold

**เน้นเนื้อ@ประจวบฮาลาล** stays outside the Google queue. Its current Google
business status was recorded as temporarily closed, so reopening must be
confirmed before approval even after coordinates are established.
