from pathlib import Path

import pytest

from app.tools.import_candidates import load_candidates, parse_candidate


def candidate_row() -> dict[str, str]:
    return {
        "name": "Example",
        "place_type": "RESTAURANT",
        "address": "Example address",
        "district": "Example district",
        "province": "Bangkok",
        "phone": "",
        "latitude": "",
        "longitude": "",
        "proposed_trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com",
        "external_provider": "example",
        "external_id": "example-1",
        "certification_number": "",
        "certification_expires_at": "",
        "review_state": "DISCOVERED",
        "review_note": "",
        "review_hold_reason": "",
        "source_checked_at": "",
        "coordinate_checked_at": "",
    }


def test_candidate_parses_discovery_row() -> None:
    candidate = parse_candidate(candidate_row(), 2)
    assert candidate.review_state == "DISCOVERED"
    assert candidate.proposed_trust_status == "UNVERIFIED"


def test_certified_candidate_requires_certificate_number() -> None:
    row = candidate_row()
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"

    with pytest.raises(ValueError, match="certification_number"):
        parse_candidate(row, 2)


def test_accommodation_certified_service_is_allowed() -> None:
    row = candidate_row()
    row["place_type"] = "ACCOMMODATION"
    row["proposed_trust_status"] = "HALAL_CERTIFIED_SERVICE"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"
    row["certification_expires_at"] = "2026-12-31T23:59:59+07:00"

    candidate = parse_candidate(row, 2)
    assert candidate.certification_number == "TEST-123"


def test_accommodation_whole_property_certified_label_is_rejected() -> None:
    row = candidate_row()
    row["place_type"] = "ACCOMMODATION"
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"

    with pytest.raises(ValueError, match="HALAL_CERTIFIED_SERVICE"):
        parse_candidate(row, 2)


def test_pilot_candidate_queue_is_valid() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) >= 24
    assert any(
        candidate.proposed_trust_status == "HALAL_CERTIFIED"
        for candidate in candidates
    )
    assert any(
        candidate.proposed_trust_status == "HALAL_CERTIFIED_SERVICE"
        for candidate in candidates
    )


def test_geocoded_candidate_requires_coordinates() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"

    with pytest.raises(ValueError, match="requires coordinates"):
        parse_candidate(row, 2)


def test_candidate_accepts_reviewed_coordinates() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"
    row["latitude"] = "14.529001"
    row["longitude"] = "101.372001"
    row["coordinate_checked_at"] = "2026-09-25T11:30:00+07:00"

    candidate = parse_candidate(row, 2)

    assert candidate.latitude == pytest.approx(14.529001)
    assert candidate.longitude == pytest.approx(101.372001)
    assert candidate.coordinate_checked_at is not None


def test_certified_candidate_requires_expiry() -> None:
    row = candidate_row()
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"

    with pytest.raises(ValueError, match="certification_expires_at"):
        parse_candidate(row, 2)


def test_candidate_requires_reference_for_known_source() -> None:
    row = candidate_row()
    row["source_reference"] = ""

    with pytest.raises(ValueError, match="requires source_reference"):
        parse_candidate(row, 2)


def test_unknown_source_may_omit_reference() -> None:
    row = candidate_row()
    row["source_type"] = "UNKNOWN"
    row["source_reference"] = ""

    candidate = parse_candidate(row, 2)
    assert candidate.source_reference is None


def test_candidate_parses_manual_review_hold() -> None:
    row = candidate_row()
    row["review_hold_reason"] = "Confirm current operating status"

    candidate = parse_candidate(row, 2)

    assert candidate.review_hold_reason == "Confirm current operating status"


def test_pilot_queue_contains_explicit_review_holds() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    held = [candidate for candidate in candidates if candidate.review_hold_reason]

    assert held == []


def test_candidate_parses_source_checked_at() -> None:
    row = candidate_row()
    row["source_checked_at"] = "2026-09-25T11:23:00+07:00"

    candidate = parse_candidate(row, 2)

    assert candidate.source_checked_at is not None
    assert candidate.source_checked_at.isoformat() == "2026-09-25T11:23:00+07:00"


def test_all_corridor_candidates_have_source_cross_check_time() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    corridor = [
        candidate
        for candidate in candidates
        if candidate.province != "กรุงเทพมหานคร"
    ]

    assert len(corridor) == 23
    assert all(candidate.source_checked_at is not None for candidate in corridor)


def test_geocoded_candidate_requires_coordinate_checked_at() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"
    row["latitude"] = "14.529001"
    row["longitude"] = "101.372001"

    with pytest.raises(ValueError, match="requires coordinate_checked_at"):
        parse_candidate(row, 2)


def test_geocoded_candidate_accepts_coordinate_checked_at() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"
    row["latitude"] = "14.529001"
    row["longitude"] = "101.372001"
    row["coordinate_checked_at"] = "2026-09-25T11:30:00+07:00"

    candidate = parse_candidate(row, 2)

    assert candidate.coordinate_checked_at is not None


def test_pak_chong_mosque_address_convention_is_resolved() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    mosque = next(
        candidate
        for candidate in candidates
        if candidate.name == "มัสยิดยันน่าตุ้ลฟิรเดาซ์"
    )

    assert mosque.review_state == "DISCOVERED"
    assert mosque.review_hold_reason is None
    assert "เทศบาล 22" in (mosque.address or "")
    assert mosque.coordinate_checked_at is None


def test_khunyaa_phone_conflict_is_resolved_without_changing_trust() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    khunyaa = next(
        candidate
        for candidate in candidates
        if candidate.name == "คุณย่าเขาใหญ่ KhunYaaKhaoyai HalalResort"
    )

    assert khunyaa.review_state == "DISCOVERED"
    assert khunyaa.phone == "+66 89 791 3785"
    assert khunyaa.review_hold_reason is None
    assert khunyaa.proposed_trust_status == "UNVERIFIED"


def test_pilot_seed_checkpoint_counts_match_release_readiness() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    pilot = [
        candidate
        for candidate in candidates
        if candidate.province != "กรุงเทพมหานคร"
    ]
    discovered = [
        candidate for candidate in pilot if candidate.review_state == "DISCOVERED"
    ]
    geocoded = [
        candidate for candidate in pilot if candidate.review_state == "GEOCODED"
    ]
    google_resolvable = [
        candidate
        for candidate in discovered
        if candidate.external_provider in {"google_business", "google_places"}
        and candidate.external_id
    ]
    google_fast_lane = [
        candidate
        for candidate in google_resolvable
        if not candidate.review_hold_reason
    ]

    assert len(pilot) == 23
    assert len(geocoded) == 15
    assert len(discovered) == 8
    assert len(google_resolvable) == 8
    assert len(google_fast_lane) == 8


def test_ayah_address_identity_is_resolved_without_changing_trust() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    ayah = next(
        candidate for candidate in candidates if candidate.name == "Ayah Restaurant Halal"
    )

    assert ayah.review_state == "GEOCODED"
    assert ayah.review_hold_reason is None
    assert ayah.proposed_trust_status == "UNVERIFIED"


def test_nurul_iman_uses_provincial_committee_address() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    mosque = next(
        candidate
        for candidate in candidates
        if candidate.name == "มัสยิดนุรุ้ลอีมาน"
    )

    assert mosque.review_state == "GEOCODED"
    assert mosque.review_hold_reason is None
    assert mosque.address is not None
    assert "หมู่ 9" in mosque.address
    assert mosque.external_provider == "google_business"
    assert mosque.external_id == "ChIJuRf2yOIg_zARYoz1y1-VwV8"


def test_nen_nuea_operating_hold_is_resolved_without_claiming_certification() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    restaurant = next(
        candidate
        for candidate in candidates
        if candidate.name == "เน้นเนื้อ@ประจวบฮาลาล"
    )

    assert restaurant.review_state == "DISCOVERED"
    assert restaurant.review_hold_reason is None
    assert restaurant.proposed_trust_status == "UNVERIFIED"
    assert restaurant.latitude is None
    assert restaurant.longitude is None


def test_nen_nuea_is_now_google_resolvable_without_manual_hold() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    restaurant = next(
        candidate
        for candidate in candidates
        if candidate.name == "เน้นเนื้อ@ประจวบฮาลาล"
    )

    assert restaurant.review_state == "DISCOVERED"
    assert restaurant.review_hold_reason is None
    assert restaurant.external_provider == "google_business"
    assert restaurant.external_id == "ChIJP1rc7lSF_jAREG6AfeqnSho"
    assert restaurant.latitude is None
    assert restaurant.longitude is None


def test_bangkok_expansion_seed_is_reviewable_without_coordinates() -> None:
    path = Path("../../database/seeds/bangkok_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 9
    assert {candidate.province for candidate in candidates} == {"กรุงเทพมหานคร"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 1


def test_bangkok_expansion_does_not_overstate_halal_certification() -> None:
    path = Path("../../database/seeds/bangkok_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert commercial
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_bangkok_expansion_supports_non_certified_muslim_business_labels() -> None:
    path = Path("../../database/seeds/bangkok_expansion_review_queue.csv")
    candidates = load_candidates(path)

    allowed = {"MUSLIM_OWNED", "MUSLIM_FRIENDLY", "UNVERIFIED"}
    uncertified = [
        candidate
        for candidate in candidates
        if not candidate.certification_number
    ]

    assert uncertified
    assert all(candidate.proposed_trust_status in allowed for candidate in uncertified)


def test_phuket_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/phuket_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"ภูเก็ต"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_phuket_muslim_owned_restaurants_do_not_claim_certification() -> None:
    path = Path("../../database/seeds/phuket_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate for candidate in candidates if candidate.place_type == "RESTAURANT"
    ]

    assert len(restaurants) == 5
    assert all(
        candidate.proposed_trust_status == "MUSLIM_OWNED"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_phuket_hotels_remain_muslim_friendly_without_certificate_number() -> None:
    path = Path("../../database/seeds/phuket_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotels = [
        candidate
        for candidate in candidates
        if candidate.place_type == "ACCOMMODATION"
    ]

    assert len(hotels) == 3
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in hotels
    )
    assert all(not candidate.certification_number for candidate in hotels)
    assert {candidate.name for candidate in hotels} == {
        "Andaman Beach Hotel Phuket - Handwritten Collection",
        "Bangtao Beach Chalet",
        "Harmony Patong Hotel",
    }


def test_krabi_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/krabi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"กระบี่"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_krabi_expansion_preserves_muslim_owned_without_certification_claim() -> None:
    path = Path("../../database/seeds/krabi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    muslim_owned = [
        candidate
        for candidate in candidates
        if candidate.proposed_trust_status == "MUSLIM_OWNED"
    ]

    assert len(muslim_owned) == 6
    assert any(
        candidate.name == "Aonang Silver Orchid Resort"
        and candidate.place_type == "ACCOMMODATION"
        for candidate in muslim_owned
    )
    assert all(not candidate.certification_number for candidate in muslim_owned)


def test_krabi_muslim_friendly_hotels_do_not_overstate_certification() -> None:
    path = Path("../../database/seeds/krabi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    muslim_friendly = [
        candidate
        for candidate in candidates
        if candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
    ]

    assert {candidate.name for candidate in muslim_friendly} == {
        "Krabi Front Bay Resort",
        "Railay Princess Resort & Spa",
    }
    assert all(not candidate.certification_number for candidate in muslim_friendly)


def test_chiang_mai_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/chiang_mai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"เชียงใหม่"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_chiang_mai_muslim_owned_labels_require_explicit_evidence() -> None:
    path = Path("../../database/seeds/chiang_mai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    muslim_owned = [
        candidate
        for candidate in candidates
        if candidate.proposed_trust_status == "MUSLIM_OWNED"
    ]

    assert len(muslim_owned) == 6
    assert {candidate.name for candidate in muslim_owned} == {
        "Tai Restaurant",
        "Khao Soi Islam",
        "Ruammit II",
        "Gulf Restaurant Chiang Mai",
        "Ruammit 1",
        "Al-Farooq Hotel Chiang Mai",
    }
    assert all(not candidate.certification_number for candidate in muslim_owned)


def test_chiang_mai_uncertain_hotel_operation_is_held() -> None:
    path = Path("../../database/seeds/chiang_mai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotel = next(
        candidate
        for candidate in candidates
        if candidate.name == "Al-Farooq Hotel Chiang Mai"
    )

    assert hotel.proposed_trust_status == "MUSLIM_OWNED"
    assert hotel.review_hold_reason is not None
    assert "current hotel operation" in hotel.review_hold_reason


def test_chonburi_pattaya_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/chonburi_pattaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"ชลบุรี"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_chonburi_pattaya_restaurants_preserve_muslim_owned_label() -> None:
    path = Path("../../database/seeds/chonburi_pattaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate
        for candidate in candidates
        if candidate.place_type == "RESTAURANT"
    ]

    assert len(restaurants) == 5
    assert all(
        candidate.proposed_trust_status == "MUSLIM_OWNED"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_hard_rock_pattaya_certification_is_service_scope_only() -> None:
    path = Path("../../database/seeds/chonburi_pattaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotel = next(
        candidate
        for candidate in candidates
        if candidate.name == "Hard Rock Hotel Pattaya"
    )

    assert hotel.proposed_trust_status == "HALAL_CERTIFIED_SERVICE"
    assert hotel.source_type == "OFFICIAL_CERTIFICATION"
    assert hotel.certification_number == "100J5760010662"
    assert hotel.certification_expires_at is not None


def test_muslim_seafood_address_requires_reconciliation() -> None:
    path = Path("../../database/seeds/chonburi_pattaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurant = next(
        candidate
        for candidate in candidates
        if candidate.name == "Muslim Seafood Restaurant"
    )

    assert restaurant.review_hold_reason is not None
    assert "locality" in restaurant.review_hold_reason


def test_songkhla_hat_yai_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/songkhla_hat_yai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"สงขลา"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_songkhla_hat_yai_restaurants_preserve_muslim_owned_label() -> None:
    path = Path("../../database/seeds/songkhla_hat_yai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate
        for candidate in candidates
        if candidate.place_type == "RESTAURANT"
    ]

    assert len(restaurants) == 5
    assert all(
        candidate.proposed_trust_status == "MUSLIM_OWNED"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_songkhla_hat_yai_hotels_do_not_overstate_certification() -> None:
    path = Path("../../database/seeds/songkhla_hat_yai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotels = [
        candidate
        for candidate in candidates
        if candidate.place_type == "ACCOMMODATION"
    ]

    assert {candidate.name for candidate in hotels} == {
        "Alfahad Hotel",
        "Hatyai Paradise Hotel",
        "Yannaty Hotel",
    }
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in hotels
    )
    assert all(not candidate.certification_number for candidate in hotels)


def test_phang_nga_expansion_prefers_quality_over_fixed_batch_size() -> None:
    path = Path("../../database/seeds/phang_nga_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 11
    assert {candidate.province for candidate in candidates} == {"พังงา"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 3
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_phang_nga_uncertain_restaurants_do_not_claim_muslim_ownership() -> None:
    path = Path("../../database/seeds/phang_nga_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate for candidate in candidates if candidate.place_type == "RESTAURANT"
    ]

    assert restaurants
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_phang_nga_excludes_disputed_flavours_of_india() -> None:
    path = Path("../../database/seeds/phang_nga_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert all(
        "Flavours Of India" not in candidate.name
        for candidate in candidates
    )


def test_trang_expansion_prefers_reviewable_quality() -> None:
    path = Path("../../database/seeds/trang_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 11
    assert {candidate.province for candidate in candidates} == {"ตรัง"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 4
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 2


def test_trang_restaurants_do_not_infer_muslim_ownership() -> None:
    path = Path("../../database/seeds/trang_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate for candidate in candidates if candidate.place_type == "RESTAURANT"
    ]

    assert restaurants
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_trang_oasis_requires_exact_address_review() -> None:
    path = Path("../../database/seeds/trang_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotel = next(
        candidate
        for candidate in candidates
        if candidate.name == "Trang Oasis Waterpark Hotel"
    )

    assert hotel.proposed_trust_status == "MUSLIM_FRIENDLY"
    assert hotel.review_hold_reason is not None
    assert "street address" in hotel.review_hold_reason


def test_ayutthaya_expansion_seed_has_balanced_tourism_coverage() -> None:
    path = Path("../../database/seeds/ayutthaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 13
    assert {candidate.province for candidate in candidates} == {"พระนครศรีอยุธยา"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 5
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_ayutthaya_muslim_owned_is_explicit_not_inferred() -> None:
    path = Path("../../database/seeds/ayutthaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    owned = {
        candidate.name
        for candidate in candidates
        if candidate.proposed_trust_status == "MUSLIM_OWNED"
    }

    assert owned == {
        "Krua Muslim Krung Kao Ayutthaya",
        "Hatyai Fried Chicken Muhammad Ayutthaya",
    }


def test_ayutthaya_hotels_remain_muslim_friendly_without_cert_number() -> None:
    path = Path("../../database/seeds/ayutthaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotels = [
        candidate for candidate in candidates if candidate.place_type == "ACCOMMODATION"
    ]

    assert len(hotels) == 3
    assert all(candidate.proposed_trust_status == "MUSLIM_FRIENDLY" for candidate in hotels)
    assert all(not candidate.certification_number for candidate in hotels)


def test_ayutthaya_incomplete_addresses_are_held() -> None:
    path = Path("../../database/seeds/ayutthaya_expansion_review_queue.csv")
    candidates = load_candidates(path)

    held = [candidate.name for candidate in candidates if candidate.review_hold_reason]

    assert set(held) == {
        "Krua Muslim Krung Kao Ayutthaya",
        "RUS Hotel & Convention Ayutthaya",
    }


def test_kanchanaburi_expansion_prefers_quality_over_fixed_size() -> None:
    path = Path("../../database/seeds/kanchanaburi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 10
    assert {candidate.province for candidate in candidates} == {"กาญจนบุรี"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 4
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 1


def test_kanchanaburi_restaurants_do_not_infer_muslim_ownership() -> None:
    path = Path("../../database/seeds/kanchanaburi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate for candidate in candidates if candidate.place_type == "RESTAURANT"
    ]

    assert restaurants
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in restaurants
    )


def test_sanctuary_kanchanaburi_has_address_hold_not_certification_claim() -> None:
    path = Path("../../database/seeds/kanchanaburi_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotel = next(
        candidate
        for candidate in candidates
        if candidate.name == "Sanctuary Kanchanaburi"
    )

    assert hotel.proposed_trust_status == "MUSLIM_FRIENDLY"
    assert hotel.review_hold_reason is not None
    assert hotel.certification_number is None


def test_wave_one_expansion_manifest_counts() -> None:
    paths = [
        Path("../../database/seeds/bangkok_expansion_review_queue.csv"),
        Path("../../database/seeds/phuket_expansion_review_queue.csv"),
        Path("../../database/seeds/krabi_expansion_review_queue.csv"),
        Path("../../database/seeds/chiang_mai_expansion_review_queue.csv"),
        Path("../../database/seeds/chonburi_pattaya_expansion_review_queue.csv"),
        Path("../../database/seeds/songkhla_hat_yai_expansion_review_queue.csv"),
        Path("../../database/seeds/phang_nga_expansion_review_queue.csv"),
        Path("../../database/seeds/trang_expansion_review_queue.csv"),
        Path("../../database/seeds/ayutthaya_expansion_review_queue.csv"),
        Path("../../database/seeds/kanchanaburi_expansion_review_queue.csv"),
    ]

    candidates = [
        candidate
        for path in paths
        for candidate in load_candidates(path)
    ]

    assert len(candidates) == 118
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 50
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 42
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 26

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert len(commercial) == 68
    assert sum(
        candidate.proposed_trust_status == "MUSLIM_OWNED"
        for candidate in commercial
    ) == 29
    assert sum(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    ) == 38
    assert sum(
        candidate.proposed_trust_status == "HALAL_CERTIFIED_SERVICE"
        for candidate in commercial
    ) == 1
    assert sum(bool(candidate.review_hold_reason) for candidate in candidates) == 6


def test_surat_thani_koh_samui_expansion_seed_has_balanced_coverage() -> None:
    path = Path("../../database/seeds/surat_thani_koh_samui_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 10
    assert {candidate.province for candidate in candidates} == {"สุราษฎร์ธานี"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 2
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_surat_thani_koh_samui_commercial_candidates_do_not_overstate_certification() -> None:
    path = Path("../../database/seeds/surat_thani_koh_samui_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert commercial
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_surat_thani_koh_samui_expansion_prefers_current_active_places() -> None:
    path = Path("../../database/seeds/surat_thani_koh_samui_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 10
    assert {candidate.province for candidate in candidates} == {"สุราษฎร์ธานี"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 2
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_surat_thani_koh_samui_commercial_places_are_muslim_friendly() -> None:
    path = Path("../../database/seeds/surat_thani_koh_samui_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert len(commercial) == 5
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_surat_thani_koh_samui_excludes_closed_ihsan_restaurant() -> None:
    path = Path("../../database/seeds/surat_thani_koh_samui_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert all(
        candidate.name != "Ihsan Muslim Restaurant"
        for candidate in candidates
    )


def test_chiang_rai_expansion_seed_has_balanced_coverage() -> None:
    path = Path("../../database/seeds/chiang_rai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 11
    assert {candidate.province for candidate in candidates} == {"เชียงราย"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 3
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 2


def test_chiang_rai_muslim_owned_restaurants_do_not_claim_certification() -> None:
    path = Path("../../database/seeds/chiang_rai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    restaurants = [
        candidate for candidate in candidates if candidate.place_type == "RESTAURANT"
    ]

    assert len(restaurants) == 3
    assert all(
        candidate.proposed_trust_status == "MUSLIM_OWNED"
        for candidate in restaurants
    )
    assert all(not candidate.certification_number for candidate in restaurants)


def test_chiang_rai_hotels_remain_muslim_friendly_without_certificate_number() -> None:
    path = Path("../../database/seeds/chiang_rai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    hotels = [
        candidate
        for candidate in candidates
        if candidate.place_type == "ACCOMMODATION"
    ]

    assert len(hotels) == 3
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in hotels
    )
    assert all(not candidate.certification_number for candidate in hotels)


def test_rayong_koh_samet_expansion_seed_has_balanced_coverage() -> None:
    path = Path("../../database/seeds/rayong_koh_samet_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 11
    assert {candidate.province for candidate in candidates} == {"ระยอง"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 3
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_rayong_commercial_candidates_stay_muslim_friendly_without_owner_or_certificate_proof() -> None:
    path = Path("../../database/seeds/rayong_koh_samet_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert commercial
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_trat_koh_chang_expansion_seed_has_balanced_coverage() -> None:
    path = Path("../../database/seeds/trat_koh_chang_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 11
    assert {candidate.province for candidate in candidates} == {"ตราด"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 5
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 3
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_trat_commercial_candidates_do_not_claim_muslim_ownership_or_certification() -> None:
    path = Path("../../database/seeds/trat_koh_chang_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert commercial
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_mae_hong_son_pai_expansion_uses_conservative_batch_size() -> None:
    path = Path("../../database/seeds/mae_hong_son_pai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 9
    assert {candidate.province for candidate in candidates} == {"แม่ฮ่องสอน"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 3
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 4
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 2


def test_mae_hong_son_pai_commercial_candidates_do_not_overclaim_trust() -> None:
    path = Path("../../database/seeds/mae_hong_son_pai_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert len(commercial) == 6
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)


def test_udon_thani_expansion_uses_conservative_batch_size() -> None:
    path = Path("../../database/seeds/udon_thani_expansion_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) == 8
    assert {candidate.province for candidate in candidates} == {"อุดรธานี"}
    assert all(candidate.review_state == "DISCOVERED" for candidate in candidates)
    assert all(candidate.latitude is None for candidate in candidates)
    assert all(candidate.longitude is None for candidate in candidates)
    assert sum(candidate.place_type == "MOSQUE" for candidate in candidates) == 2
    assert sum(candidate.place_type == "RESTAURANT" for candidate in candidates) == 3
    assert sum(candidate.place_type == "ACCOMMODATION" for candidate in candidates) == 3


def test_udon_thani_commercial_candidates_do_not_overclaim_trust() -> None:
    path = Path("../../database/seeds/udon_thani_expansion_review_queue.csv")
    candidates = load_candidates(path)

    commercial = [
        candidate
        for candidate in candidates
        if candidate.place_type in {"RESTAURANT", "ACCOMMODATION"}
    ]

    assert len(commercial) == 6
    assert all(
        candidate.proposed_trust_status == "MUSLIM_FRIENDLY"
        for candidate in commercial
    )
    assert all(not candidate.certification_number for candidate in commercial)
