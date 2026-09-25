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
