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
| `build/data.py` | **Single source of truth** for everything in `catalog.html` and the `.kml` |
| `build/gen_catalog.py` | Reads `data.py` → writes `catalog.html` |
| `build/gen_kml.py` | Reads `data.py` → writes the `.kml` |
| `LICENSE` | MIT |

## Critical rule: regenerate, don't hand-edit

`catalog.html` and the `.kml` are both generated from `build/data.py`. Every entry in
`data.py` has an `id` that is used as **both** the HTML anchor (`catalog.html#that-id`)
**and** the link target inside the corresponding KML placemark's description. If you
edit `catalog.html` or the `.kml` directly, the two will silently drift apart and the
map's "Full entry in the Beethoven Catalog →" links will break.

**Workflow for any content change:** edit `build/data.py` → run
`python3 build/gen_catalog.py && python3 build/gen_kml.py` from the `build/` directory
→ commit all three changed files together (`data.py`, `catalog.html`, the `.kml`).

`index.html` (the concert monitor) is currently hand-maintained separately and is
*not* generated from `data.py`. That's a known inconsistency — worth deciding at some
point whether it should be folded into the same data model, but no rush.

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

## Known open items

- The original day-by-day itinerary docx and the earlier (pre-catalog) merged KML
  exist in project history but are superseded by `catalog.html` / the new KML —
  confirm with the user whether those should stay in the repo for reference or be
  removed.
- Several event dates are still genuinely unconfirmed (Konzerthaus Vienna, Cologne,
  Munich, Salzburg concerts) — these are correctly marked tentative in `data.py`;
  don't "fill them in" without a real source.
- `index.html` and `catalog.html`/`data.py` are not yet cross-linked with nav — no
  way to get from one to the other on the page itself yet.
