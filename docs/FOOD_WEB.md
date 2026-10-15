# Where the data comes from: the Colorado Open Food Web

**Data work moved on 2026-10-15.** The Farm Trail no longer builds, researches or maintains the dataset.
That is done in the open, in the
[Colorado Open Food Web](https://github.com/open-food-web/colorado-open-food-web), which pulls the
sources on a schedule, verifies contact details, and publishes versioned releases. This app is one example
of an app built on it.

## What the app reads

A **pinned release** in `data/foodweb/`:

| File | Used for |
|---|---|
| `directory.csv` | The map (`scripts/build_map_data.py`), the calendar preview, the guide's listings |
| `csa.json` | The CSA finder |
| `places.json` | "Near a town or ZIP" search |
| `supply-network-nodes.csv`, `supply-network-edges.csv` | The local food guide |
| `MANIFEST.json` | The version, counts, and the sha256 of each file |

The current pin is in `data/foodweb/MANIFEST.json`.

## Updating

```bash
python scripts/update_foodweb.py v2026.11.1     # downloads the release and checks every sha256
python scripts/build_map_data.py                # data/markets.json
python scripts/csa/build_finder_data.py         # csa/csa-data.js
python scripts/guide/build_guide_data.py        # guide/guide-data.js
```

Review the diff before committing. A new Food Web release never changes an old one, so the app upgrades only
when it chooses to.

## What stays in the app

- **Listing descriptions** (`data/overlay/notes.csv`): the release carries facts only, so the app keeps its own
  descriptions, keyed by name and town. Showing them, with a link back to the source, is the app's choice.
- **Display rules**: which categories the public map shows, their groups, colors and badges
  (`scripts/appdata/categories.py`).
- **Content that is the app's own**: day plans, events, branding, marketing.

## Corrections and new listings

Send them to the Food Web, not here: [open an issue](https://github.com/open-food-web/colorado-open-food-web/issues/new/choose).
Emails appear only when the business lists the address on its own website or Facebook page, so a few listings
show fewer contact details than before.

## Where the old pipeline went

The pipeline, the research and the data documents moved to the Food Web on 2026-10-15 and were removed from
this repo (git history keeps them). In the Food Web:

| Was here | Now |
|---|---|
| `scripts/scrape/` (sources, merge, build) | `scripts/scrape/` in the Food Web, run on a schedule |
| `source-data/`, `data-compiled/` | `inputs/`, `snapshots/` and `data/` in the Food Web; raw third-party material in a private sources repo |
| `docs/DATA.md`, `DEDUP_STANDARDS.md`, `UPDATE_ENGINE.md`, `LINK_CHECKING.md`, `CATEGORIES.md`, `ENTITY_REGISTRY.md` | `docs/` in the Food Web |
| `docs/BUSINESS_SUBMISSIONS.md` and the form script | `docs/FEEDBACK.md` and `intake/` in the Food Web |
| `docs/CORE_PROJECT_CHARTER.md`, `FOOD_WEB_SCHEMA.md` | `docs/CHARTER.md`, `docs/SCHEMA.md` in the Food Web |

The Gunnison Valley prototype (`gunnison-valley/`, `scripts/gunnison_site/`) still reads the raw build; run it with
`--inputs` pointing at a checkout of the Food Web's private sources repo.
