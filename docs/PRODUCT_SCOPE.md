# Product Scope — V1

## Positioning

Vela Muslim Travel is a travel utility for Muslim travelers in Thailand. Its core value is not merely a directory of places; it is helping a traveler make decisions while on a real trip.

## Primary journeys

### 1. Near Me

A traveler opens the app and sees nearby:

- restaurants,
- accommodations,
- mosques,
- prayer rooms.

Results must show distance, current open/closed data when available, and verification freshness.

### 2. Along My Route

A traveler chooses an origin and destination. The system finds useful places near the actual route and shows:

- order encountered along the journey,
- distance from route,
- estimated detour where routing data permits,
- place category,
- Muslim/halal status,
- verification source and date.

### 3. Accommodation search

Accommodation is a first-class category, not an afterthought.

Useful attributes include:

- Muslim-owned
- Muslim-friendly
- halal food available
- prayer space available
- alcohol-free property or alcohol policy
- bidet / hand spray
- family-friendly
- parking
- nearest mosque distance
- check-in/check-out information

A property must not be labeled "halal certified" unless that claim has a verifiable certification source.

## Place categories

- RESTAURANT
- ACCOMMODATION
- MOSQUE
- PRAYER_ROOM

## Trust labels

### Restaurants

- HALAL_CERTIFIED
- MUSLIM_OWNED
- MUSLIM_FRIENDLY
- UNVERIFIED

### Accommodations

- HALAL_CERTIFIED_SERVICE
- MUSLIM_OWNED
- MUSLIM_FRIENDLY
- UNVERIFIED

The UI should explain what each label means.


### Muslim-owned businesses

A restaurant or accommodation **does not need official halal certification to
be useful to Muslim travelers**.

Use `MUSLIM_OWNED` when there is credible evidence that the business is owned
or operated by Muslims, even when no current halal certificate exists.

This label means only:

- the business is Muslim-owned / Muslim-operated based on reviewed evidence,
- it is **not** the same as `HALAL_CERTIFIED`,
- no certification claim should be shown unless an official certificate is
  separately verified.

Acceptable evidence may include:

- an explicit statement from the business owner or official business page,
- a provincial Islamic committee / Muslim business directory that identifies
  Muslim ownership,
- a reliable interview/news/profile naming the owner and Muslim ownership,
- field verification recorded by an Admin reviewer.

Do **not** infer Muslim ownership from:

- a Muslim-sounding personal or business name,
- Arabic/Islamic branding alone,
- menu appearance,
- customer reviews alone,
- location near a mosque.

When ownership evidence is credible but food/certification evidence is absent,
prefer `MUSLIM_OWNED` over `UNVERIFIED`; keep the UI wording explicit so the
traveler can decide.

## Verification

Every trust-sensitive claim should have:

- source type,
- source reference,
- verified date,
- optional expiry date,
- reviewer/admin note.

Potential source types:

- OFFICIAL_CERTIFICATION
- BUSINESS_OWNER
- FIELD_CHECK
- COMMUNITY_REPORT
- PUBLIC_WEB_SOURCE
- UNKNOWN

## V1 exclusions

Do not build these until route search and data quality work reliably:

- booking/payment
- star ratings or social-review platform
- prayer-time calculation
- qibla compass
- loyalty program
- complex member profiles
- nationwide public editing
- AI-generated halal claims

## Initial validation corridor

Use one practical long-distance corridor for QA before nationwide expansion:

Southern Thailand → Prachuap Khiri Khan → Phetchaburi → Bangkok region → Saraburi / Nakhon Ratchasima.

The exact seed places must be manually verified before being treated as production data.
