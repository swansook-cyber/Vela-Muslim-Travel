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


## 2026-09-25 — สุราษฎร์ธานี

### มัสยิดมูฮัมมาดียะห์ บ้านดอนมะม่วง

- CICOT currently confirms the mosque at หมู่ 2 ตำบลท่าชนะ อำเภอท่าชนะ
  จังหวัดสุราษฎร์ธานี 84170 with phone **083-503-6602**.
- A current Google business result with the same mosque name resolves in
  ตำบลประสงค์, อำเภอท่าชนะ instead of the CICOT locality.
- Treat that map result as potentially mismatched or imprecise. Do not accept
  its coordinate automatically; geocode and visually verify against the
  official CICOT address during manual review.
- Keep the current staging address and phone from CICOT until the coordinate
  identity is resolved.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/6

### มัสยิดอิกอมุสซอลาฮ์ บ้านหนองจอก

- CICOT currently confirms the mosque at หมู่ 4 ตำบลท่าสะท้อน อำเภอพุนพิน
  จังหวัดสุราษฎร์ธานี 84130 with phone **089-735-6089**.
- A current Google business result resolves a mosque with the same name in
  ตำบลท่าสะท้อน, พุนพิน and shows the same phone.
- Local government material for ตำบลท่าสะท้อน also identifies the mosque
  education center at **37 หมู่ 4 ตำบลท่าสะท้อน**.
- This is a strong identity cross-check, but exact coordinates still require
  explicit map review before `GEOCODED`.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/4

Supporting local-government evidence:
- https://www.tasaton.go.th/storage/uploads/175393451026.pdf

### สุราษฎร์ฮาลาลฟู๊ด

- Makan Halal Guide currently lists the restaurant on the
  สุราษฎร์ธานี-นครศรีธรรมราช road in ตำบลท่าทองใหม่, กาญจนดิษฐ์ with phone
  **093-882-4903**.
- Wongnai independently lists the same restaurant name, same phone and
  ท่าทองใหม่ location.
- These sources support the discovery identity, but neither source establishes
  current official halal certification.
- Keep `UNVERIFIED` until stronger certification/ownership evidence is found.
- Exact coordinates still require explicit map review.

Primary discovery evidence:
- https://makanhalalguide.com/shop/detail/2909

Secondary cross-check:
- https://www.wongnai.com/restaurants/657355hU-%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B2%E0%B8%A9%E0%B8%8E%E0%B8%A3%E0%B9%8C%E0%B8%AE%E0%B8%B2%E0%B8%A5%E0%B8%B2%E0%B8%A5%E0%B8%9F%E0%B8%B9%E0%B9%8A%E0%B8%94

## Review rule

A successful web/source cross-check does **not** change `review_state`.
Candidates remain behind the controlled sequence:

`DISCOVERED → GEOCODED → APPROVED → PROMOTED`

Coordinates must be selected and visually checked by the reviewer before
`GEOCODED`. Evidence and trust scope must be reviewed again before
`APPROVED`.
