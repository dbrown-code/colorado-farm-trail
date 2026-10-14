# Colorado Open Producer Registry — Schema (DRAFT v0.1)

> Draft for maintainer review. Follows [`CORE_PROJECT_CHARTER.md`](CORE_PROJECT_CHARTER.md).
> Canonical form is plain CSV tables; JSON, GeoJSON and SQLite are built from them.
> A Frictionless `datapackage.json` will be generated from this spec once it is agreed.

## Model in one picture

```
producer 1 ──< presence >── 1 place
   │                          │
   ├──< source_link           └── county (FIPS)
   ├──< field_source
   └──< service_area (derived from presences, or set by hand)
```

- **producer**: one record per producer. This is the unit behind a producer homepage.
- **place**: a physical location with coordinates (a farm, a stand, a market, a store).
- **presence**: how a producer relates to a place (home base, sells at a market, stocked at a store).
- **service_area**: counties where a producer can be found. Derived from presences, or set by hand
  for producers who deliver or ship.
- **source_link / field_source**: where each record and each field came from, and when it was checked.

A producer with no place at all (online or wholesale only) is valid. A producer whose only
presences are four markets is valid.

## Field classes

Every field has a class that decides whether it appears in the public release.

| Class | Meaning | In public release |
|---|---|---|
| `fact` | A checkable fact (name, address, phone, coordinates) | Yes |
| `controlled` | Value from a project vocabulary (categories, products, kinds) | Yes |
| `owned` | Text written by the project, or submitted by the producer under the contributor statement | Yes |
| `source_prose` | Descriptive text copied from a source | **No.** Link only (see `source_link`) |
| `personal` | Could identify a person rather than a business (home address the producer hides, personal social profile) | **No**, unless the business itself publishes it for customers |

## Identifiers

- IDs are stable, never reused, and namespaced: `co-p-000123` (producer), `co-pl-000456` (place).
- Slugs (`aspen-moon-farm`, with `-2` on collisions) are separate from IDs and may change; the ID may not.
- Merged duplicates keep a redirect in `id_aliases` so old IDs still resolve.

## Table: `producers`

| Field | Type | Class | Notes |
|---|---|---|---|
| `producer_id` | string | fact | Required. Primary key |
| `slug` | string | fact | Homepage path |
| `name` | string | fact | Required. Business name |
| `kind` | enum | controlled | `farm`, `ranch`, `orchard`, `maker`, `winery`, `market`, `food_hub`, `retailer`, `organization`. A farmers' market is a recurring multi-vendor gathering (see `farmers-market-definition`) |
| `categories` | list | controlled | From the category vocabulary below. Primary first |
| `products` | list | controlled | From the product vocabulary |
| `seasonal_months` | list | fact | Months operating, 1–12. Empty if unknown |
| `hours_structured` | list | fact | `{days, open, close, season_start, season_end}` entries. See `hours_text` |
| `hours_text` | string | fact | Fallback when hours cannot be structured. Verbatim and short |
| `website` | url | fact | The business's own site |
| `phone` | string | fact | Public business phone |
| `email` | string | fact/personal | Only if the business publishes it for customers |
| `facebook`, `instagram` | url | fact/personal | Business pages only |
| `sales_channels` | list | controlled | `on_farm`, `farm_stand`, `farmers_market`, `csa`, `online`, `wholesale`, `retail_partners`, `delivery` |
| `certified_organic` | bool/null | fact | Null = unknown, never assumed false |
| `accepts_snap` | bool/null | fact | |
| `ada_accessible` | bool/null | fact | |
| `call_first` | bool/null | fact | |
| `description` | string | owned | Only text we wrote or the producer submitted. Never copied |
| `status` | enum | fact | `active`, `seasonal_closed`, `closed`, `unverified`, `removed` |
| `claimed` | bool | fact | Producer has confirmed their record |
| `opted_out_fields` | list | fact | Fields the producer asked to have removed |
| `first_seen`, `last_verified` | date | fact | |

## Table: `places`

| Field | Type | Class | Notes |
|---|---|---|---|
| `place_id` | string | fact | Required |
| `name` | string | fact | Place name if different from the producer |
| `kind` | enum | controlled | `home_base`, `farm_stand`, `market`, `store`, `pickup_point`, `other` |
| `address`, `city`, `zip` | string | fact/personal | Honors `hide_address` |
| `hide_address` | bool | fact | When true, public release keeps city and county only, and coordinates are rounded to the town |
| `state` | string | fact | `CO`. A field, not a constant |
| `county_fips` | string | fact | 5-digit FIPS (e.g. `08117`). County name is derived |
| `lat`, `lon` | number | fact | Null if not known |
| `geo_source` | enum | fact | `source`, `geocoder`, `manual` |
| `google_place_id` | string | fact | Stored for link-outs and live photo thumbnails. No photos or photo URLs stored |
| `photo_url`, `photo_credit`, `photo_license` | string | owned | Only when the producer submitted the photo with an open license |

## Table: `presences`

| Field | Type | Class | Notes |
|---|---|---|---|
| `presence_id` | string | fact | Primary key |
| `producer_id` | string | fact | FK |
| `place_id` | string | fact | FK |
| `role` | enum | controlled | `home_base`, `sells_at`, `stocked_at`, `csa_dropoff`, `pickup` |
| `days`, `hours_text` | list/string | fact | When they are at that place |
| `season_start`, `season_end` | date/month | fact | Months or dates, per year |
| `year` | integer | fact | Market vendor lists change yearly. Blank for ongoing |
| `status` | enum | fact | `confirmed`, `listed`, `unverified` |

## Table: `service_areas`

| Field | Type | Class | Notes |
|---|---|---|---|
| `producer_id` | string | fact | FK |
| `county_fips` | string | fact | |
| `basis` | enum | fact | `home_base`, `market`, `store`, `delivery`, `manual` |
| `derived` | bool | fact | True when computed from presences. Rebuilt on every release |

A county filter matches a producer when any `service_areas` row for that county exists.
Apps may label `home_base` as "Grows here" and the other bases as "Sells here".

## Table: `source_links`

Per producer, links to the original listings. Apps may pull display content from these links.

| Field | Type | Class | Notes |
|---|---|---|---|
| `producer_id` | string | fact | FK |
| `source` | string | fact | `producer_site`, `usda_lfd`, `colorado_proud`, `cfma`, `chaffee_provides`, … |
| `url` | url | fact | The listing page |
| `source_record_id` | string | fact | Stable ID at the source, for change detection |
| `last_seen` | date | fact | Last time the link worked |
| `link_status` | enum | fact | `ok`, `redirect`, `dead`, `unchecked` |

## Table: `field_sources`

Provenance for each populated field. Attribution for the public release is built from this table.

| Field | Type | Notes |
|---|---|---|
| `record_type` | enum | `producer`, `place`, `presence` |
| `record_id` | string | |
| `field` | string | e.g. `phone` |
| `source` | string | Source name |
| `source_url` | url | |
| `verified_by` | string | Source, partner or `producer` |
| `verified_on` | date | |

## Vocabularies

- **Categories** follow the existing labels (Farmers' Market, On-Farm / Ranch Sales, Meat Producer &
  Packer, Farm Products (online), Agritourism, CSA Farm, Roadside Market, U-Pick, Garden Center /
  Greenhouse, Winery, Grocery Store, Farm Store, Bakery, Food Maker, Restaurant, Caterer, Wholesale
  Grower, Food Hub, Food Bank, Community Food Hub, Organization), plus the badge "Sells to Schools".
  The Farm Trail's map groups are an app concern and stay in the app.
- **Products** reuse the normalized product list from the Farm Trail data.
- Colorado-specific attributes (for example Colorado Proud membership) go in a separate
  `state_attributes` table, never in the core tables.

## What a producer homepage reads

One producer row, its places via presences (home base pin, plus market pins), service areas for
the county list, `source_links` for the "More from the source" links, and `google_place_id` for
the Maps directions link and optional live photos.

## Public release rules

Public export drops `source_prose` and `personal` fields, applies `hide_address` and
`opted_out_fields`, and writes the sources into the release notes. Removed producers appear
as ID only.

## Mapping from today's data

| Today (Phase 2 raw CSV) | Becomes |
|---|---|
| Business Name, Category, Phone, Website, Email, Facebook, Instagram, Hours, Months Open, Products, Certified Organic, SNAP, ADA Accessible, Call first? | `producers` |
| Address, City, Zip, County, Latitude, Longitude, Geo Source | `places` (kind `home_base`, or `market` for market records) |
| Where to Get It | `presences` (`stocked_at`) once the named stores are resolved to places |
| Market vendor lists (Phase 3 prospects) | `presences` (`sells_at`, with `year`) |
| Notes | Dropped from the public release; the link goes in `source_links` |
| Source, Source ID, Source Updated, Provenance | `source_links`, `field_sources` |
| Possible Dup Of, dedup decisions | Merge decisions and `id_aliases` |

## Open questions

1. **Are markets producers?** The draft treats a market as a `producers` row with `kind = market`,
   so it can have its own contact, hours and SNAP data, and vendors link to its place. The
   alternative is a separate `markets` table. Which feels right?
2. **Hours:** how much of the existing free-text hours can be structured automatically versus
   left in `hours_text`?
3. **Producer-submitted fields:** which ones can a claimed producer edit directly (description,
   photo, hours) versus only propose changes to?
4. **Multiple home bases:** a producer with two farms gets two `home_base` presences. Is that fine, or
   should one be primary?
