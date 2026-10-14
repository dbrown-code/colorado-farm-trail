# Colorado Open Producer Registry — Schema (DRAFT v0.1)

> Draft for maintainer review. Follows [`CORE_PROJECT_CHARTER.md`](CORE_PROJECT_CHARTER.md).
> Canonical form is plain CSV tables; JSON, GeoJSON and SQLite are built from them.
> A Frictionless `datapackage.json` will be generated from this spec once it is agreed.

## Model in one picture

```
producer 1 ──< presence >── 1 place ── county (FIPS)
   │                          │
   ├──< market_vendor >── 1 market ───┤ (each market has one place)
   ├──< outlet_supplier >── 1 outlet ─┘ (each outlet has one place)
   ├──< service_area (derived from presences, markets and outlets, or set by hand)
   └──< source_link / field_source (for producers, markets and outlets)
```

- **producer**: one record per producer. This is the unit behind a producer homepage.
- **market**: a recurring multi-vendor gathering. Not a producer: it is its own record type, tied
  to one place, with its own hours, season and programs.
- **outlet**: a restaurant, caterer, grocer, farm store or garden center that sells or serves local
  food. Not a producer: its own record type, tied to one place, kept deliberately thin.
- **outlet_supplier**: a sourced claim that a producer supplies an outlet.
- **place**: a physical location with coordinates (a farm, a stand, a market site, an outlet).
- **presence**: how a producer relates to a place (home base, farm stand, CSA drop-off).
- **market_vendor**: a producer selling at a market in a given year.
- **service_area**: counties where a producer can be found. Derived from presences and market
  participation, or set by hand for producers who deliver or ship.
- **source_link / field_source**: where each record and each field came from, and when it was checked.

A producer with no place at all (online or wholesale only) is valid. A producer whose only
connections are four markets is valid.

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

- IDs are stable, never reused, and namespaced: `co-p-000123` (producer), `co-m-000789` (market), `co-o-000321` (outlet),
  `co-pl-000456` (place).
- Slugs (`aspen-moon-farm`, with `-2` on collisions) are separate from IDs and may change; the ID may not.
- Merged duplicates keep a redirect in `id_aliases` so old IDs still resolve.

## Table: `producers`

| Field | Type | Class | Notes |
|---|---|---|---|
| `producer_id` | string | fact | Required. Primary key |
| `slug` | string | fact | Homepage path |
| `name` | string | fact | Required. Business name |
| `kind` | enum | controlled | `farm`, `ranch`, `orchard`, `maker`, `winery`. Markets are not producers (see `markets`). Food hubs, retailers and organizations are not decided yet (see open questions) |
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
| `kind` | enum | controlled | `home_base`, `farm_stand`, `market_site`, `outlet_site`, `pickup_point`, `other` |
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
| `role` | enum | controlled | `home_base`, `farm_stand`, `csa_dropoff`, `pickup`. Markets are in `market_vendors` and stores or restaurants in `outlet_suppliers`, not here |
| `days`, `hours_text` | list/string | fact | When they are at that place |
| `season_start`, `season_end` | date/month | fact | Months or dates |
| `status` | enum | fact | `confirmed`, `listed`, `unverified` |

## Table: `markets`

A recurring gathering where several vendors sell at a fixed place. A market has exactly one place;
a market that moves between sites is one record per site, linked by `network_name`.

| Field | Type | Class | Notes |
|---|---|---|---|
| `market_id` | string | fact | Required. Primary key |
| `slug` | string | fact | Page path |
| `name` | string | fact | Required |
| `place_id` | string | fact | FK. Required |
| `operator` | string | fact | Organization that runs it |
| `network_name` | string | fact | For markets run as a series at several sites |
| `days`, `season_start`, `season_end` | list/date | fact | When it runs |
| `hours_structured`, `hours_text` | list/string | fact | As for producers |
| `website`, `phone`, `email`, `facebook`, `instagram` | string | fact/personal | Public contact for the market |
| `accepts_snap`, `double_up`, `accepts_wic`, `ada_accessible` | bool/null | fact | Null = unknown |
| `status` | enum | fact | `active`, `seasonal_closed`, `closed`, `unverified` |
| `first_seen`, `last_verified` | date | fact | |

## Table: `market_vendors`

| Field | Type | Class | Notes |
|---|---|---|---|
| `market_id` | string | fact | FK |
| `producer_id` | string | fact | FK |
| `year` | integer | fact | Vendor lists change yearly. Required |
| `days`, `season_start`, `season_end` | list/date | fact | If narrower than the market's own |
| `status` | enum | fact | `confirmed`, `listed`, `unverified` |
| `list_source` | string | fact | Which vendor list said so |

## Table: `outlets`

A restaurant, caterer, grocer, farm store or garden center. Thin on purpose: identity, location and
a link to where the business describes itself. The Registry holds no menus, prices or descriptions.
One record per location; chains share a `brand`.

| Field | Type | Class | Notes |
|---|---|---|---|
| `outlet_id` | string | fact | Required. Primary key |
| `slug` | string | fact | Page path |
| `name` | string | fact | Required |
| `kind` | enum | controlled | `restaurant`, `caterer`, `grocery`, `farm_store`, `garden_center`, `other_retail` |
| `brand` | string | fact | Chain or group name, for multi-location businesses |
| `place_id` | string | fact | FK. Required |
| `website`, `phone` | string | fact | Public business contact |
| `facebook`, `instagram` | url | fact/personal | Business pages only |
| `status` | enum | fact | `active`, `seasonal_closed`, `closed`, `unverified` |
| `first_seen`, `last_verified` | date | fact | Restaurants close often; `last_verified` matters |

## Table: `outlet_suppliers`

The most perishable data in the Registry: who buys from whom changes with menus and seasons.

| Field | Type | Class | Notes |
|---|---|---|---|
| `outlet_id` | string | fact | FK |
| `producer_id` | string | fact | FK |
| `basis` | enum | fact | `outlet_says`, `producer_says`, `both`, `third_party` |
| `source_url` | url | fact | Page that states it (menu, supplier list, producer page) |
| `observed_on` | date | fact | When the claim was seen. Required |
| `status` | enum | fact | `current`, `unverified`, `ended` |

## Table: `service_areas`

| Field | Type | Class | Notes |
|---|---|---|---|
| `producer_id` | string | fact | FK |
| `county_fips` | string | fact | |
| `basis` | enum | fact | `home_base`, `market`, `store`, `delivery`, `manual` (`market` comes from `market_vendors` through the market's place, `store` from `outlet_suppliers` through the outlet's place) |
| `derived` | bool | fact | True when computed from presences. Rebuilt on every release |

A county filter matches a producer when any `service_areas` row for that county exists.
Apps may label `home_base` as "Grows here" and the other bases as "Sells here".

## Table: `source_links`

Per producer, market or outlet, links to the original listings. Apps may pull display content from these links.

| Field | Type | Class | Notes |
|---|---|---|---|
| `record_type` | enum | fact | `producer`, `market`, `outlet` |
| `record_id` | string | fact | FK |
| `source` | string | fact | `producer_site`, `usda_lfd`, `colorado_proud`, `cfma`, `chaffee_provides`, … |
| `url` | url | fact | The listing page |
| `source_record_id` | string | fact | Stable ID at the source, for change detection |
| `last_seen` | date | fact | Last time the link worked |
| `link_status` | enum | fact | `ok`, `redirect`, `dead`, `unchecked` |

## Table: `field_sources`

Provenance for each populated field. Attribution for the public release is built from this table.

| Field | Type | Notes |
|---|---|---|
| `record_type` | enum | `producer`, `market`, `outlet`, `place`, `presence`, `market_vendor`, `outlet_supplier` |
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

One producer row, its places via presences (home base pin), its markets via `market_vendors`
(market pins), its outlets via `outlet_suppliers` ("where to buy" and "where to eat"), service areas for
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
| Address, City, Zip, County, Latitude, Longitude, Geo Source | `places` (kind `home_base`, or `market_site` for a market's place) |
| Records categorized "Farmers' Market" | `markets` (not `producers`), each with its `place_id` |
| Where to Get It | `outlet_suppliers`, once each named store or restaurant is resolved to an `outlets` record |
| Records categorized Grocery Store, Farm Store, Garden Center / Greenhouse, Restaurant, Caterer | `outlets` (not `producers`), each with its `place_id`. A record that is also a producer (a bakery with a café) becomes one `producers` row and one `outlets` row |
| Market vendor lists (Phase 3 prospects) | `market_vendors` (with `year`) |
| Notes | Dropped from the public release; the link goes in `source_links` |
| Source, Source ID, Source Updated, Provenance | `source_links`, `field_sources` |
| Possible Dup Of, dedup decisions | Merge decisions and `id_aliases` |

## Open questions

1. **Hubs, food banks and organizations.** Producers, markets and outlets are in v1. Food hubs, food banks and
   support organizations are not producers or outlets. Plan: an `organizations` table in v2, designed
   together with the supply-network graph in the food guide.
2. **Hours:** how much of the existing free-text hours can be structured automatically versus
   left in `hours_text`?
3. **Producer-submitted fields:** which ones can a claimed producer edit directly (description,
   photo, hours) versus only propose changes to?
4. **Multiple home bases:** a producer with two farms gets two `home_base` presences. Is that fine, or
   should one be primary?
5. **Merged duplicates:** define an `id_aliases` table (`old_id`, `new_id`, `merged_on`) and the
   convention for multi-value fields in CSV (`;`-separated, with hours in their own table).
6. **Producer that is also an outlet.** A bakery with a café is one `producers` row plus one `outlets`
   row sharing a place. Is linking them with an optional `producer_id` on the outlet enough?
7. **Outlet claims at scale.** `outlet_suppliers` rows need a source and date. Should the public release
   hide rows older than a set age (for example 18 months) unless re-observed?
