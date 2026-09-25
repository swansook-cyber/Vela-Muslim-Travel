# Pilot Source Audit

Checked: 2026-09-25

The Phase 0 pilot queue now distinguishes business discovery evidence from
official mosque-directory evidence.

## Official mosque-directory confirmations

- **มัสยิดอันซอรุสซุนนะฮฺ — ทุ่งใหญ่, นครศรีธรรมราช**
  - CICOT directory confirms the mosque in Moo 6, Prik, Thung Yai.
  - The queue retains the Google business external ID only for deduplication.
  - Coordinates remain unapproved until manual geocode review.

- **มัสยิดนูรุ้ลเอี๊ยะซาน — ปะทิว, ชุมพร**
  - CICOT directory confirms the mosque in Moo 7, Chum Kho, Pathio.
  - Directory phone/address replace weaker discovery-only metadata.
  - Coordinates remain unapproved until manual geocode review.

- **มัสยิดยันน่าตุ้ลฟิรเดาซ์ — ปากช่อง, นครราชสีมา**
  - CICOT directory confirms the mosque in Moo 2, Pak Chong.
  - Coordinates remain unapproved until manual geocode review.

## Restaurant claims

Business listings that describe a restaurant as halal remain
`UNVERIFIED` unless current official certification evidence is available.

The text "halal restaurant" in a map/business listing is discovery evidence,
not proof of certification.

## Import gate

Every candidate whose `source_type` is not `UNKNOWN` must include a
`source_reference`. This prevents provenance from being silently lost before
admin review and promotion.


## Corridor expansion: สุราษฎร์ธานี / ประจวบคีรีขันธ์ / สระบุรี

The queue now includes official-directory mosque candidates in the three
previously uncovered northbound provinces:

- Surat Thani: Tha Chana and Phunphin
- Prachuap Khiri Khan: Bang Saphan and Sam Roi Yot
- Saraburi: Muak Lek and Mueang Saraburi

These records come from the CICOT mosque directory and remain
`DISCOVERED` with empty coordinates until controlled geocode review.


## Restaurant discovery coverage for corridor gaps

Three additional restaurant candidates were added to avoid a mosque-only
dataset in newly covered provinces:

- Surat Halal Food — Kanchanadit, Surat Thani — Makan Halal Guide
- Nen Nuea @ Prachuap Halal — Mueang Prachuap Khiri Khan — Makan Halal Guide
- Muslim Kitchen Saraburi — Muak Lek, Saraburi — Wongnai

These sources are discovery evidence only. All three remain `UNVERIFIED`
and are not represented as officially halal-certified.
