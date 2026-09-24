from app.schemas import GeoJsonLineString, RouteSummary


def test_route_summary_carries_geojson_linestring() -> None:
    summary = RouteSummary(
        distance_m=1234,
        duration_s=567,
        geometry=GeoJsonLineString(
            coordinates=[[100.0, 13.0], [100.1, 13.1]]
        ),
    )

    assert summary.geometry.type == "LineString"
    assert summary.geometry.coordinates[1] == [100.1, 13.1]
