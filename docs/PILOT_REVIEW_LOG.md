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
- Coordinate verification completed from the current Google Directions
  destination for the listing: **8.17611110, 99.63243720**.
- Staging state is now `GEOCODED`; trust remains `UNVERIFIED`.

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
- Coordinate verification completed from MasjidThai's embedded Google Map:
  **8.2407216433, 99.4464044519**.
- Staging state is now `GEOCODED`, but the phone discrepancy remains an
  explicit manual hold and still blocks approval.

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


## 2026-09-25 — ชุมพร

### มัสยิดนูรุ้ลเอี๊ยะซาน

- CICOT currently confirms **มัสยิดนูรุ้ลเอี๊ยะซาน** at
  **88 หมู่ 7 ตำบลชุมโค อำเภอปะทิว จังหวัดชุมพร 86160** with phone
  **086-282-3212**.
- The existing Google business ID `ChIJQ5PVCG9I_zARGdUJDBT9v_g` still resolves
  to a mosque in ตำบลชุมโค, ปะทิว.
- The Google listing currently shows phone **081-264-1355**, which conflicts
  with the CICOT directory.
- Keep the CICOT address as the authoritative administrative reference and do
  not auto-overwrite the phone. Resolve the phone discrepancy during manual
  review.
- Exact coordinates still require explicit visual review.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/207

### มัสยิดมูฮาญิรีน

- The existing Google business ID `ChIJJeREHGyz-DARhCUH0WYc12Y` still resolves
  to **มัสยิดมูฮาญิรีน** in the Tha Sae area.
- MasjidThai currently identifies the registered mosque as **เลขที่ 1 หมู่ 1
  ตำบลหงษ์เจริญ อำเภอท่าแซะ จังหวัดชุมพร 86140**, phone **087-894-9117**.
- This does not match the staging address text `P5Q6+4G8 ตำบลท่าแซะ` exactly.
  Treat the staging map address as a discovery locator, not a verified
  administrative address.
- Use the registered mosque record to confirm identity before selecting a map
  coordinate.

Primary evidence:
- https://masjidthai.com/masjid/view.php?id=rVGXJWqb3BtgUm0gYil1274M06iMc8DuZtJi9qdZ400

### กะมา ครัวมุสลิม ฮาลาล

- Existing Google business ID `ChIJBzAp2VpN_zARrGXZ_BL7X98` still resolves to
  **กะมา ครัวมุสลิม ฮาลาล** at **48 หมู่ 2 ถนนเพชรเกษม ตำบลทรัพย์อนันต์
  อำเภอท่าแซะ จังหวัดชุมพร 86140**.
- Current listing phone **096-698-7642** matches staging.
- The listing categorizes the venue as a halal restaurant and shows current
  opening hours, but this is not official halal-certification evidence.
- Keep `UNVERIFIED` until stronger evidence is established.
- Exact coordinates still require explicit visual review.

## 2026-09-25 — ประจวบคีรีขันธ์

### มัสยิดนุรุ้ลอีมาน

- CICOT currently confirms **มัสยิดนุรุ้ลอีมาน** at **หมู่ 2
  ตำบลพงศ์ประศาสน์ อำเภอบางสะพาน จังหวัดประจวบคีรีขันธ์ 77140**.
- The current Google business result resolves to a mosque in the same
  ตำบลพงศ์ประศาสน์ / บางสะพาน area.
- A September 2026 local event source identifies the same mosque as
  **เลขที่ 2 หมู่ 9 ตำบลพงศ์ประศาสน์**, creating a Moo-number discrepancy with
  CICOT.
- Do not normalize the Moo number automatically. Confirm the exact parcel/map
  identity during coordinate review.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/2/4

Recent supporting cross-check:
- https://thaifaithday.com/events/ruam-namjai-nurul-iman-bangsaphan-2569-tfd-0361/

### มัสยิดดารุ้ลอิบาดะห์

- CICOT currently confirms the mosque at **หมู่ 4 ตำบลไร่เก่า
  อำเภอสามร้อยยอด จังหวัดประจวบคีรีขันธ์ 77180** with phone
  **086-712-5973**.
- MasjidThai independently confirms the same registered mosque, same Moo,
  subdistrict and district.
- The current Google business result resolves to the same Rai Kao /
  Sam Roi Yot area.
- Rai Kao Subdistrict Administrative Organization also lists
  **มัสยิดดารู้ลอิบาดะห์** on its local map.
- Identity confidence is strong; exact coordinates still require explicit map
  review before `GEOCODED`.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/2/4
- https://masjidthai.com/masjid/mosqhistory.php?id=UEtOMDAwNA%3D%3D
- https://raikao.go.th/public/

### เน้นเนื้อ@ประจวบฮาลาล

- Makan Halal Guide and Wongnai currently agree on the venue at **143/2
  ตำบลคลองวาฬ อำเภอเมืองประจวบคีรีขันธ์ 77000**, phone **084-455-6783**.
- Wongnai describes it as a halal restaurant, and Makan Halal Guide lists
  Muslim-travel amenities including a prayer room.
- The current Google business listing is marked **Temporarily Closed**.
- Do not approve or promote this candidate while closure status is unresolved.
  Recheck that the restaurant is operating before any state advancement.
- These public listings still do not establish official halal certification;
  retain `UNVERIFIED`.

Primary evidence:
- https://makanhalalguide.com/shop/detail/3761
- https://www.wongnai.com/restaurants/2642013wt-%E0%B9%80%E0%B8%99%E0%B9%89%E0%B8%99%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD-%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%A7%E0%B8%9A%E0%B8%AE%E0%B8%B2%E0%B8%A5%E0%B8%B2%E0%B8%A5-%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%A7%E0%B8%9A%E0%B8%AE%E0%B8%B2%E0%B8%A5%E0%B8%B2%E0%B8%A5


## 2026-09-25 — เพชรบุรี

### มัสยิดกลางจังหวัดเพชรบุรี

- The existing Google business ID `ChIJP0BtFTom_TARfXE8GeUMrYM` still resolves
  to **มัสยิดกลางจังหวัดเพชรบุรี** at the staging address in the Ban Laem /
  Tha Raeng area.
- Community cultural records identify the central mosque in Tha Raeng as
  **มัสยิดยามิอุ้ลอิสลาม (มัสยิดกลาง)**, หมู่ 4 ตำบลท่าแร้ง อำเภอบ้านแหลม.
- The current map address and the community description support the same
  central-mosque identity, but exact coordinates still require explicit map
  review.

Supporting evidence:
- https://wikicommunity.sac.or.th/community/1182

### อาหารอิสลามบังเพชรบุรี ลุงบัง

- A current Google business listing resolves to **ลุงบัง อาหารอิสลาม HALAL** in
  ตำบลหัวสะพาน, อำเภอเมืองเพชรบุรี with phone **089-836-0894**, matching the
  staging phone.
- The candidate source and current business listing support the venue as a
  Muslim/halal restaurant discovery candidate.
- These public listings are not official certification evidence. Keep
  `UNVERIFIED`.
- Exact coordinates still require controlled map review.

## 2026-09-25 — สระบุรี

### มัสยิดยะบัลเราะห์มะฮ์

- CICOT currently confirms **มัสยิดยะบัลเราะห์มะฮ์** at หมู่ 2 ตำบลมิตรภาพ
  อำเภอมวกเหล็ก จังหวัดสระบุรี 18180.
- Saraburi provincial planning documents independently list the same mosque in
  ตำบลมิตรภาพ, อำเภอมวกเหล็ก.
- The current Google business result resolves to the same Muak Lek area.
- Identity confidence is strong; exact coordinates still require explicit map
  review before `GEOCODED`.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/6

Supporting provincial evidence:
- https://www.saraburipao.go.th/plan66-70.pdf

### มัสยิดมะบาดุลบารี

- CICOT currently confirms **มัสยิดมะบาดุลบารี** in ตำบลปากเพรียว
  อำเภอเมืองสระบุรี 18000.
- A current provincial social report gives the more specific address
  **369 ถนนพหลโยธิน ตำบลปากเพรียว อำเภอเมืองสระบุรี**.
- The current Google business result resolves to a mosque in the same
  Pak Phriao / Mueang Saraburi area.
- Keep the staging candidate until exact map coordinates are explicitly
  reviewed.

Primary evidence:
- https://www.cicot.or.th/th/mosque/lists/2/2

Supporting address evidence:
- https://www.m-society.go.th/ewtadmin/ewt/mso_web/download/article/article_20211109112144.pdf

### ครัวมุสลิม สระบุรี

- Wongnai currently lists **ครัวมุสลิมสระบุรี** at **544/1-2 หมู่ 9
  ถนนเลี่ยงเมือง ตำบลมิตรภาพ อำเภอมวกเหล็ก จังหวัดสระบุรี 18180** with phone
  **087-707-4480**, matching staging.
- The current Google business result also resolves to a halal restaurant in
  Muak Lek with the same phone.
- These sources confirm the operating identity but do not establish current
  official halal certification.
- Keep `UNVERIFIED`; exact coordinates still require controlled review.

Primary discovery evidence:
- https://www.wongnai.com/restaurants/150373KW-%E0%B8%84%E0%B8%A3%E0%B8%B1%E0%B8%A7%E0%B8%A1%E0%B8%B8%E0%B8%AA%E0%B8%A5%E0%B8%B4%E0%B8%A1-%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5


## 2026-09-25 — นครราชสีมา / เขาใหญ่

### SALASA HALAL RESTAURANT KHAOYAI

- Existing Google business ID `ChIJgZfAAmsyHDERlceMtKji41g` still resolves
  to **SALASA HALAL RESTAURANT KHAOYAI** at **165 หมู่ 15 ถนนธนะรัชต์
  ตำบลหมูสี อำเภอปากช่อง จังหวัดนครราชสีมา 30130**, phone **080-050-4193**.
- Current travel/restaurant sources continue to describe the venue as a halal
  restaurant and show active opening hours.
- These public sources do not establish an official halal certificate. Keep
  `UNVERIFIED`.
- Exact coordinates still require explicit visual review.

### มัสยิดยันน่าตุ้ลฟิรเดาซ์

- CICOT currently confirms **มัสยิดยันน่าตุ้ลฟิรเดาซ์** at หมู่ 2
  ตำบลปากช่อง อำเภอปากช่อง จังหวัดนครราชสีมา 30130.
- Existing Google business ID `ChIJg8AZfzEqHDERIEmyXoK-g_0` still resolves
  to the mosque in Pak Chong, currently shown near ถนนเทศบาล 22 ซอย 1.
- The two sources support the same mosque identity but use different address
  styles. Exact coordinates require explicit visual review before
  `GEOCODED`.

Primary evidence:
- https://cicot.or.th/th/mosque/lists/2/3

### ร้านอาหารอิสลามตลาดแขก อ.ปากช่อง

- Existing Google business ID `ChIJu4-pVzEqHDERNKY1RFId_Yc` still resolves to
  the same halal restaurant in Pak Chong with phone **088-711-7127**.
- Wongnai and current restaurant directories also show the same restaurant
  name, Pak Chong location and phone.
- Public halal-category listings are not official certification evidence.
  Retain `UNVERIFIED`.
- Exact coordinates still require controlled map review.

Supporting evidence:
- https://www.wongnai.com/restaurants/1141227fc-%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%AD%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%AD%E0%B8%B4%E0%B8%AA%E0%B8%A5%E0%B8%B2%E0%B8%A1%E0%B8%95%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B9%81%E0%B8%82%E0%B8%81

### อาซีย๊ะอาหารอิสลาม Halal

- Existing Google business ID `ChIJ3XS9QSsrHDER4FprdurFZCo` still resolves to
  **43 ซอยเทศบาล 35 อำเภอปากช่อง จังหวัดนครราชสีมา 30130**, phone
  **087-445-1746**.
- Makan Halal Guide independently lists the same address and phone and
  identifies Muslim-travel amenities such as a prayer room.
- These sources support the operating identity but do not establish official
  halal certification. Keep `UNVERIFIED`.
- Exact coordinates still require controlled review.

Primary discovery evidence:
- https://makanhalalguide.com/shop/detail/952

### Ayah Restaurant Halal

- Existing Google business ID `ChIJRzDp-aosHDERVOymRnYsn6o` still resolves to
  **Ayah Restaurant Halal** at plus-code **M84W+X7F**, Pak Chong, phone
  **083-652-6945**.
- Current restaurant/travel sources show the same phone and active restaurant.
- Tripadvisor uses the more conventional address **16/6 หมู่ 5 ถนนมิตรภาพ
  ปากช่อง 30320** while other sources use the plus-code / Sap Wai wording.
- Do not normalize the address automatically. Confirm exact location and
  administrative address during coordinate review.
- No official certification evidence was established in this review; keep
  `UNVERIFIED`.

### คุณย่าเขาใหญ่ KhunYaaKhaoyai HalalResort

- Existing Google business ID `ChIJVy7c7Bg7HDERjTbk8mJLjSI` still resolves to
  the hotel at **49/1 หมู่ 5 ตำบลวังกะทะ อำเภอปากช่อง จังหวัดนครราชสีมา
  30130**, phone **084-673-1717**, matching staging.
- Current public sources continue to identify the property using the
  `HalalResort` name.
- No evidence reviewed here establishes whole-property halal certification.
  Keep `UNVERIFIED` and do not infer certification from the property name.
- Exact coordinates and Muslim-friendly facility claims still require manual
  verification before approval.


### Coordinate verification update — 2026-09-25

- **มัสยิดมูฮัมมาดียะห์ บ้านดอนมะม่วง** — GEOCODED at
  `9.5154625, 99.164546875` from the current same-name Google business Plus Code
  `G587+5RM`. The CICOT-vs-Google locality discrepancy remains an explicit
  manual hold, so this candidate is not approval-ready.
- **มัสยิดอิกอมุสซอลาฮ์ บ้านหนองจอก** — GEOCODED at
  `9.035931, 99.235434` from Tha Sathon Subdistrict Administrative
  Organization UTM coordinates `X 525875 / Y 998833`, converted from
  EPSG:32647 to WGS84. CICOT, MasjidThai and PSU sources support the same
  mosque identity.
- **สุราษฎร์ฮาลาลฟู๊ด** — GEOCODED at `9.1485375, 99.392671875` from Cybo Plus
  Code `49XV+C37`, with name/phone/address cross-checked against Wongnai and
  Makan Halal Guide. Trust remains `UNVERIFIED`.


### Coordinate verification update — 2026-09-25 (ชุมพร)

- **มัสยิดนูรุ้ลเอี๊ยะซาน** — GEOCODED at `10.8061625, 99.353109375`
  from the current Google business Plus Code `R943+F69`. CICOT confirms the
  Moo 7, Chum Kho, Pathio identity, but the Google and CICOT phone numbers still
  conflict, so the existing manual hold remains.
- **มัสยิดมูฮาญิรีน** — GEOCODED at `10.7377875, 99.161328125` from the
  current Google business / Trip.com Plus Code `P5Q6+4G8`. MasjidThai
  registers the mosque at 1 Moo 1, Hong Charoen, Tha Sae; the address-identity
  discrepancy remains an explicit manual hold.
- **กะมา ครัวมุสลิม ฮาลาล** remains `DISCOVERED`. The current Google
  business listing still matches the staging name, 48 Moo 2 Phet Kasem Road,
  Sap Anan, Tha Sae and phone 096-698-7642, but no exact public coordinate or
  Plus Code was found in this pass. Nearby-distance descriptions are not
  sufficient evidence for coordinate promotion.


> Plus Code coordinate note: short Plus Codes in this log are recovered using
> the place locality and decoded with Google's official Open Location Code
> 11-character grid algorithm. The stored coordinate is the center of the
> decoded Plus Code area; direct coordinates from embedded maps, directions or
> official UTM records remain preferred when available.

## Review rule

A successful web/source cross-check does **not** change `review_state`.
Candidates remain behind the controlled sequence:

`DISCOVERED → GEOCODED → APPROVED → PROMOTED`

Coordinates must be selected and visually checked by the reviewer before
`GEOCODED`. Evidence and trust scope must be reviewed again before
`APPROVED`.
