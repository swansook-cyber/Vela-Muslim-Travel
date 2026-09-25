# Pilot Manual Review Log

This log records public-source cross-checks performed before any candidate is
approved or promoted. A source match is discovery evidence only unless the
record explicitly satisfies the approval rules.

## 2026-09-25 — นครศรีธรรมราช

### The Twin Lotus Hotel

- Candidate provider ID still resolves to **The Twin Lotus Hotel** at
  6 ถนนพัฒนาการคูขวาง ตำบลในเมือง อำเภอเมืองนครศรีธรรมราช.
- CICOT halal evidence currently identifies the certified scope as
  **ครัวฮาลาล** (halal kitchen), certificate **100C5470010356**, certified
  through **22 October 2026**.
- Keep the candidate scope as `HALAL_CERTIFIED_SERVICE`. Do not represent the
  whole hotel as halal-certified.
- Because the certificate is close to expiry, verify its current status again
  immediately before production promotion.
- Exact coordinates still require explicit map review in the Admin workflow.

Primary evidence:
- https://halal.co.th/th/product/detail/392345
- Existing Google Places provider ID: `ChIJF7qxAkYBUzAR81Ar0UQtRCw`

### ร้านอิสลามสตูลทุ่งสง

- Existing Google business provider ID
  `ChIJb3CdTvpHUjAR3tOKF9C10SI` still resolves to the same venue.
- Current listing still shows the candidate address in หนองหงส์, ทุ่งสง and
  phone **080-717-8803**.
- The public listing categorizes the venue as a halal restaurant, but this does
  not establish official halal certification.
- Keep `UNVERIFIED` until stronger evidence is reviewed.
- Exact coordinates still require explicit map review.

Primary discovery reference:
- https://www.google.com/maps/search/?api=1&query_place_id=ChIJb3CdTvpHUjAR3tOKF9C10SI

### มัสยิดอันซอรุสซุนนะฮฺ

- CICOT's current mosque directory confirms **มัสยิดอันซอรุสซุนนะฮฺ** in
  หมู่ 6 ตำบลปริก อำเภอทุ่งใหญ่ จังหวัดนครศรีธรรมราช 80240.
- Existing Google business provider ID
  `ChIJq-pE79cwUjARe4XMnk8_Iz8` still resolves to a mosque in the same area.
- Phone data is inconsistent across current public sources:
  - CICOT directory currently shows **081-367-2137**.
  - MasjidThai currently shows **095-671-7510**, which matches the staging CSV.
- Do not overwrite the candidate phone from automated research. Resolve the
  phone discrepancy during manual review or leave the phone unverified.
- Exact coordinates still require explicit map review.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/178/6
- Existing Google business provider ID: `ChIJq-pE79cwUjARe4XMnk8_Iz8`

Secondary cross-check:
- https://masjidthai.com/masjid/mosqhistory.php?id=TlJUMDA1Mw%3D%3D

## Review rule

A successful web/source cross-check does **not** change `review_state`.
Candidates remain behind the controlled sequence:

`DISCOVERED → GEOCODED → APPROVED → PROMOTED`

Coordinates must be selected and visually checked by the reviewer before
`GEOCODED`. Evidence and trust scope must be reviewed again before
`APPROVED`.
