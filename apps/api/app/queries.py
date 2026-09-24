import json

from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from .routing import RouteResult
from .schemas import NearbyRequest, PlaceType

LATEST_VERIFICATION_SQL = """
LEFT JOIN LATERAL (
    SELECT
        pv.trust_status::text AS trust_status,
        pv.source_type::text AS verification_source_type,
        pv.source_reference,
        pv.verified_at,
        pv.expires_at
    FROM place_verifications pv
    WHERE pv.place_id = p.id
    ORDER BY
        pv.verified_at DESC NULLS LAST,
        pv.created_at DESC
    LIMIT 1
) verification ON true
"""

PLACE_COLUMNS_SQL = """
    p.id::text,
    p.slug,
    p.place_type::text,
    p.name_th,
    p.name_en,
    p.address,
    p.district,
    p.province,
    p.phone,
    p.website_url,
    p.social_url,
    ST_Y(p.location::geometry) AS latitude,
    ST_X(p.location::geometry) AS longitude,
    verification.trust_status,
    verification.verification_source_type,
    verification.source_reference,
    verification.verified_at,
    verification.expires_at
"""


def _place_types_value(place_types: list[PlaceType] | None) -> list[str] | None:
    return [item.value for item in place_types] if place_types else None


async def find_place_by_slug(
    session: AsyncSession,
    slug: str,
) -> dict | None:
    sql = text(
        f"""
        SELECT
            {PLACE_COLUMNS_SQL}
        FROM places p
        {LATEST_VERIFICATION_SQL}
        WHERE p.active = true
          AND p.slug = :slug
        LIMIT 1
        """
    )

    row = (await session.execute(sql, {"slug": slug})).mappings().first()
    return dict(row) if row else None


async def find_nearby_places(
    session: AsyncSession,
    request: NearbyRequest,
) -> list[dict]:
    sql = text(
        f"""
        SELECT
            {PLACE_COLUMNS_SQL},
            ST_Distance(
                p.location,
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography
            ) AS distance_m
        FROM places p
        {LATEST_VERIFICATION_SQL}
        WHERE p.active = true
          AND ST_DWithin(
                p.location,
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
                :radius_m
          )
          AND (:place_types_is_null OR p.place_type::text IN :place_types)
        ORDER BY distance_m
        LIMIT :limit
        """
    ).bindparams(bindparam("place_types", expanding=True))

    place_types = _place_types_value(request.place_types)
    params = {
        "latitude": request.latitude,
        "longitude": request.longitude,
        "radius_m": request.radius_m,
        "place_types_is_null": place_types is None,
        "place_types": place_types or ["__NONE__"],
        "limit": request.limit,
    }

    rows = (await session.execute(sql, params)).mappings().all()
    return [dict(row) for row in rows]


async def find_places_along_route(
    session: AsyncSession,
    route: RouteResult,
    corridor_radius_m: int,
    place_types: list[PlaceType] | None,
    limit: int,
) -> list[dict]:
    route_geojson = json.dumps(
        {
            "type": "LineString",
            "coordinates": route.coordinates,
        }
    )

    sql = text(
        f"""
        WITH route AS (
            SELECT ST_SetSRID(ST_GeomFromGeoJSON(:route_geojson), 4326) AS geom
        )
        SELECT
            {PLACE_COLUMNS_SQL},
            ST_Distance(
                p.location,
                route.geom::geography
            ) AS distance_m,
            ST_LineLocatePoint(
                route.geom,
                ST_ClosestPoint(route.geom, p.location::geometry)
            ) AS route_progress
        FROM places p
        CROSS JOIN route
        {LATEST_VERIFICATION_SQL}
        WHERE p.active = true
          AND ST_DWithin(
                p.location,
                route.geom::geography,
                :corridor_radius_m
          )
          AND (:place_types_is_null OR p.place_type::text IN :place_types)
        ORDER BY route_progress, distance_m
        LIMIT :limit
        """
    ).bindparams(bindparam("place_types", expanding=True))

    types_value = _place_types_value(place_types)
    params = {
        "route_geojson": route_geojson,
        "corridor_radius_m": corridor_radius_m,
        "place_types_is_null": types_value is None,
        "place_types": types_value or ["__NONE__"],
        "limit": limit,
    }

    rows = (await session.execute(sql, params)).mappings().all()
    return [dict(row) for row in rows]
