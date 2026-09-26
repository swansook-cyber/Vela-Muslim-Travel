from app.tools.route_smoke import build_parser, summarize_rows


def test_route_smoke_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--origin-lat",
            "8.16",
            "--origin-lng",
            "99.68",
            "--destination-lat",
            "14.53",
            "--destination-lng",
            "101.37",
        ]
    )

    assert args.corridor_km == 5.0
    assert args.limit == 50
    assert args.place_types is None


def test_route_smoke_parser_accepts_repeated_types() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--origin-lat",
            "8.16",
            "--origin-lng",
            "99.68",
            "--destination-lat",
            "14.53",
            "--destination-lng",
            "101.37",
            "--type",
            "RESTAURANT",
            "--type",
            "MOSQUE",
        ]
    )

    assert args.place_types == ["RESTAURANT", "MOSQUE"]


def test_route_smoke_parser_accepts_core_gate() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--origin-lat",
            "8.16",
            "--origin-lng",
            "99.68",
            "--destination-lat",
            "14.53",
            "--destination-lng",
            "101.37",
            "--require-core-types",
        ]
    )

    assert args.require_core_types is True


def test_route_smoke_summary_tracks_core_coverage() -> None:
    rows = [
        {
            "place_type": "RESTAURANT",
            "province": "ชุมพร",
            "verification_expired": False,
        },
        {
            "place_type": "MOSQUE",
            "province": "ประจวบคีรีขันธ์",
            "verification_expired": False,
        },
        {
            "place_type": "ACCOMMODATION",
            "province": "นครราชสีมา",
            "verification_expired": True,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["counts"]["RESTAURANT"] == 1
    assert summary["counts"]["MOSQUE"] == 1
    assert summary["counts"]["ACCOMMODATION"] == 1
    assert summary["expired"] == 1
    assert summary["core_ready"] is True
    assert summary["provinces"] == [
        "ชุมพร",
        "นครราชสีมา",
        "ประจวบคีรีขันธ์",
    ]


def test_route_smoke_summary_accepts_prayer_room_for_prayer_coverage() -> None:
    rows = [
        {
            "place_type": "RESTAURANT",
            "province": "ชุมพร",
            "verification_expired": False,
        },
        {
            "place_type": "PRAYER_ROOM",
            "province": "ชุมพร",
            "verification_expired": False,
        },
        {
            "place_type": "ACCOMMODATION",
            "province": "ชุมพร",
            "verification_expired": False,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["core"]["prayer"] is True
    assert summary["core_ready"] is True


def test_route_smoke_summary_reports_missing_accommodation() -> None:
    rows = [
        {
            "place_type": "RESTAURANT",
            "province": "ชุมพร",
            "verification_expired": False,
        },
        {
            "place_type": "MOSQUE",
            "province": "ชุมพร",
            "verification_expired": False,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["core"]["accommodation"] is False
    assert summary["core_ready"] is False
