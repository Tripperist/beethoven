# Beethoven Pilgrimage 2027 — Project Notes

Public GitHub Pages site tracking a Beethoven 200th-anniversary trip (Bonn → Vienna,
March–April 2027 core, tracking events through June 2027) and cataloging everything
Beethoven-related worth knowing about, on-route or not.

**Live root URL:** `https://tripperist.github.io/beethoven/`
(Not `.github.com` — that's not a Pages domain and will 404. Easy typo to reintroduce.)

## Files

| File | Purpose |
|---|---|
| `index.html` | Concert monitor — tracks ticket on-sale status, booking urgency, per-venue notes |
| `catalog.html` | The full compendium — every sight, museum, tavern, and event, organized by place |
| `beethoven_pilgrimage_2027_catalog.kml` | Visual/map representation of the catalog, for Google Earth / Maps |
| `build/data.py` | **Single source of truth** for everything in all three generated files above |
| `build/gen_catalog.py` | Reads `data.py` → writes `catalog.html` |
| `build/gen_kml.py` | Reads `data.py` → writes the `.kml` |
| `build/gen_index.py` | Reads `data.py` → writes `index.html` (the concert monitor) |
| `LICENSE` | MIT |

## Critical rule: regenerate, don't hand-edit

`index.html`, `catalog.html`, and the `.kml` are **all three** generated from
`build/data.py` — none of them should be hand-edited directly, or they'll silently
drift apart. Every entry in `data.py` has an `id` that's reused as the anchor in
whichever of the three files it appears in, so the same `id` is what ties a catalog
card, a KML placemark's "Full entry in the Beethoven Catalog →" link, and a Concert
Monitor venue card together. Venues that are actively tracked for booking status also
carry a `monitor` sub-dict (booking-focused prose/chips/badge, distinct in tone from
the catalog's historical `body` text) — its presence is what makes `gen_catalog.py`
and `gen_kml.py` emit a "Booking status in the Concert Monitor →" link back to
`index.html#that-id`. Two ticket-agency entries (Interlude Travel, Classic Journeys)
live in `MONITOR_ONLY` instead of `SECTIONS`, since they're not physical Beethoven
sites and have no coords, catalog card, or KML placemark of their own.

**Workflow for any content change:** edit `build/data.py` → run, **from the repo
root** (the scripts write relative output paths, so running them from inside `build/`
writes stray copies there instead of updating the real files):
```
python build/gen_catalog.py && python build/gen_kml.py && python build/gen_index.py
```
→ commit all four changed files together (`data.py`, `catalog.html`, the `.kml`,
`index.html`).

## Dates: two different philosophies, on purpose

- **Sights, museums, taverns** in `data.py` / the catalog carry **no date at all**.
  The day-by-day order of the trip is explicitly not fixed yet — don't add itinerary
  day numbers ("Day 9", "March 18") back into these entries.
- **Concerts and events** carry **real calendar dates** when confirmed (via
  `event_dates` / `event_label` / `status: "confirmed"` in `data.py`), or are
  explicitly marked `status: "tentative"` when not. Never invent or guess a date —
  mark it tentative and say so, the way the existing entries do.
- The KML mirrors this: sight placemarks have no `<TimeStamp>`; event placemarks do,
  built automatically from `event_dates` in `data.py`.

## Content scope

This is a maximalist catalog, not just a narrow itinerary. If you (or the user) find
a new Beethoven-related concert, exhibition, or event anywhere — on the core Bonn–
Vienna route or not — it belongs in `data.py`, tagged appropriately (`kind: "network"`
for off-route/context entries, using the existing `network` section as the place for
those). Err toward including things rather than filtering for relevance.

Every entry's `coords` (stored KML-style as `lon,lat,alt`) automatically produces a
"View on Google Maps" link via the `maps_url()` helper in `data.py` — don't hand-write
Maps URLs, and don't forget the lon/lat swap if you ever touch that function.

## Known open items

- The original day-by-day itinerary docx and the earlier (pre-catalog) merged KML
  exist in project history but are superseded by `catalog.html` / the new KML —
  confirm with the user whether those should stay in the repo for reference or be
  removed.
- Several event dates are still genuinely unconfirmed (Konzerthaus Vienna, Cologne,
  Munich, Salzburg concerts) — these are correctly marked tentative in `data.py`;
  don't "fill them in" without a real source.
