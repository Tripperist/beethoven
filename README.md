# Beethoven Pilgrimage 2027

A public site tracking a Beethoven 200th-anniversary trip (Bonn → Vienna, core
March–April 2027, with related events tracked through June 2027) and cataloging
everything Beethoven-related worth knowing about — on the route or not.

**Live site:** https://tripperist.github.io/beethoven/

| Page | What it's for |
|---|---|
| [`index.html`](index.html) | **Concert Monitor** — ticket on-sale status, booking urgency, per-venue notes |
| [`catalog.html`](catalog.html) | **The Catalog** — every sight, museum, tavern, and event, organized by place |
| [`beethoven_pilgrimage_2027_catalog.kml`](beethoven_pilgrimage_2027_catalog.kml) | **The Map** — the same catalog as pins, for Google Earth or Google Maps |

## How this repo works

All three pages above are **generated** from one file, [`build/data.py`](build/data.py) —
it's the single source of truth for every place, concert, and event in the project.
Nothing in `index.html`, `catalog.html`, or the `.kml` should ever be hand-edited
directly: they're rebuilt from `data.py` by three small scripts, and hand-editing
the output would just get overwritten (or silently drift out of sync) next time
someone regenerates.

```
build/data.py  →  build/gen_catalog.py  →  catalog.html
               →  build/gen_kml.py      →  beethoven_pilgrimage_2027_catalog.kml
               →  build/gen_index.py    →  index.html
```

Every place has an `id` that's reused as the anchor across all three outputs, so a
catalog card, its KML pin, and (if it's a tracked venue) its Concert Monitor card
all link back and forth to each other automatically.

## Regenerating all the files

After any change to `build/data.py`, run all three generators **from the repo
root** (they write relative paths, so running them from inside `build/` writes
stray copies there instead of updating the real files):

```bash
python build/gen_catalog.py && python build/gen_kml.py && python build/gen_index.py
```

Then commit `data.py` together with all three regenerated outputs — they should
always move as one unit.

## Adding a new place

### Option A — the `add_place.py` CLI (recommended)

The easiest way to add a place and regenerate everything in one step:

```bash
python build/add_place.py --city linz --kind sight \
  --id linz-castle --name "Linz Castle" --latlon "48.3049,14.2843" \
  --body "The Renaissance castle overlooking the Danube, with a small local-history museum."
```

- `--city` must match an existing section id in `data.py` (`bonn`, `cologne`,
  `koblenz`, `heidelberg`, `regensburg`, `munich`, `salzburg`, `linz`, `wachau`,
  `vienna`, `baden`, `moedling`, `vienna-farewell`, `network`).
- `--kind` is one of `sight`, `museum`, `tavern`, `extended`, `concert`,
  `flagship`, `network`.
- `--latlon` takes coordinates in the normal **`LAT,LON`** order (like you'd copy
  from Google Maps) — the script converts it internally.
- `--body` is the catalog description; basic HTML (`<b>`, `<em>`) is fine.

To also add the place to the Concert Monitor (a booking-status card on
`index.html`), add:

```bash
  --monitor-group Vienna \
  --monitor-desc "Booking-focused description for the monitor card." \
  --monitor-badge-text "Worth checking" --monitor-badge-class purple \
  --chip "Mar 2027|TBC"
```

`--monitor-group` must match an existing Concert Monitor section label (`Bonn`,
`Cologne`, `EU Anniversary Network`, `Linz`, `Vienna`, `Specialist ticket
services`). Leave the `--monitor-*` flags off for a place that's catalog/map-only.

Other useful flags: `--link` (venue website), `--status confirmed|tentative`,
`--event-date YYYY-MM-DD` (repeatable), `--event-label`, `--dry-run` (preview
without writing), `--no-regen` (skip auto-regenerating after adding). Full
reference:

```bash
python build/add_place.py --help
```

The script validates everything before writing (unique id, known city/kind/group,
valid coordinates) and automatically reverts `data.py` if the result doesn't parse
— it's safe to experiment with `--dry-run` first.

### Option B — edit `data.py` by hand

For anything the CLI doesn't cover (a brand-new city section, more elaborate
formatting, bulk changes), edit `build/data.py` directly:

1. Find the right city's block inside `SECTIONS` (or add a new
   `{"id": ..., "title": ..., "subtitle": ..., "entries": [...]}` block for a new
   city).
2. Add an entry to that section's `entries` list:
   ```python
   {"id":"city-shortname","name":"Display Name","kind":"sight",
    "coords":"LON,LAT,0",
    "body":"Descriptive prose for the catalog."},
   ```
   - `id` must be unique across the whole file.
   - `coords` is **`lon,lat,0`** — KML order, the reverse of the CLI's `--latlon`.
3. For a concert venue, also add `status`, `link`, and optionally
   `event_dates`/`event_label`; for one tracked in the Concert Monitor, add a
   `"monitor": {...}` block (see existing entries for the shape) and list its `id`
   under the right group in `MONITOR_GROUPS`.
4. Regenerate (see above).

## Dates: two philosophies, on purpose

- **Sights, museums, taverns** carry **no date** — the day-by-day itinerary order
  isn't fixed yet, so don't add day numbers or specific dates to these.
- **Concerts and events** carry **real calendar dates** once confirmed, or are
  explicitly marked `tentative` when not. Never invent a date — mark it tentative
  instead.

## Content scope

This is a maximalist catalog, not just a narrow itinerary — if you find a new
Beethoven-related concert, exhibition, or event anywhere (on the core route or
not), it belongs here. Err toward including things rather than filtering for
relevance.

## License

MIT — see [`LICENSE`](LICENSE).
