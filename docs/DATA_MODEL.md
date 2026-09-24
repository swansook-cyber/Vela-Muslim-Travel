# Core Data Model

## Design goals

1. One geographic model for all place categories.
2. Trust-sensitive claims must be traceable.
3. Route search must be spatially efficient.
4. Data can be corrected without deleting history.
5. "Halal certified" is never inferred.

## Core entities

### places

Common record for restaurant, accommodation, mosque, and prayer room.

Important fields:

- id
- slug
- place_type
- name_th
- name_en
- latitude / longitude via PostGIS geography
- address
- district / province
- phone
- website_url
- social_url
- active
- source_status
- created_at / updated_at

### place_verifications

Stores evidence behind a Muslim/halal status.

Important fields:

- place_id
- claim_type
- trust_status
- source_type
- source_reference
- verified_at
- expires_at
- note
- verified_by

A place may have multiple verification records over time.

### restaurant_details

Restaurant-specific attributes:

- cuisine
- opening-hours payload
- parking
- price level
- takeaway
- delivery

### accommodation_details

Accommodation-specific attributes:

- halal_food_available
- prayer_space_available
- alcohol_policy
- bidet_available
- family_friendly
- parking
- nearest_mosque_distance_m
- check_in_time
- check_out_time

### mosque_details

Mosque/prayer-room specific attributes:

- friday_prayer
- women_prayer_area
- ablution_available
- parking

## Why verification is separate

A restaurant can change ownership or lose/renew certification. An accommodation can remain Muslim-friendly while a specific restaurant inside it has separate certification.

Keeping verification evidence separate prevents a stale single field from becoming a permanent truth.

## Geospatial representation

Use:

```sql
geography(Point, 4326)
```

for each place.

For route proximity, convert the route polyline to a PostGIS geometry/geography and use spatial operators such as:

- ST_DWithin
- ST_LineLocatePoint
- ST_Distance

The route engine and database must remain decoupled so the routing provider can be replaced later.
