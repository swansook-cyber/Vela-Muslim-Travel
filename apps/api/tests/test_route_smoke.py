from app.tools.route_smoke import build_parser


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
