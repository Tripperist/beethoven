# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0, '.')
from data import SECTIONS, MONITOR_ONLY, MONITOR_GROUPS, MONITOR_META, CATALOG_URL, maps_url

ARROW_SVG = '<svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 10L10 2M5 2h5v5"/></svg>'

def build_entry_lookup():
    lookup = {}
    for sec in SECTIONS:
        for e in sec["entries"]:
            entry = dict(e)
            entry["_in_catalog"] = True
            lookup[e["id"]] = entry
    for e in MONITOR_ONLY:
        entry = dict(e)
        entry["_in_catalog"] = False
        lookup[e["id"]] = entry
    return lookup

ENTRY_BY_ID = build_entry_lookup()

def render_chip(chip):
    variant = chip.get("variant")
    cls = f"date-chip {variant}" if variant else "date-chip"
    return f'<span class="{cls}">{chip["text"]}</span>'

def render_card(entry_id):
    e = ENTRY_BY_ID[entry_id]
    mon = e["monitor"]

    card_class = f' {mon["card_class"]}' if mon.get("card_class") else ""

    meta_html = ""
    if mon.get("chips"):
        chips_html = "\n        ".join(render_chip(c) for c in mon["chips"])
        meta_html = f'''
      <div class="venue-meta">
        {chips_html}
      </div>'''

    links = []
    if e.get("link"):
        label = e["link"].replace("https://", "").replace("http://", "").rstrip("/")
        links.append(f'''<a class="venue-link" href="{e["link"]}" target="_blank" rel="noopener">
        {label}
        {ARROW_SVG}
      </a>''')
    if e.get("_in_catalog"):
        links.append(f'''<a class="venue-link" href="{CATALOG_URL}#{entry_id}" target="_blank" rel="noopener">
        Full catalog entry
        {ARROW_SVG}
      </a>''')
    if e.get("coords"):
        links.append(f'''<a class="venue-link" href="{maps_url(e["coords"])}" target="_blank" rel="noopener">
        View on Google Maps
        {ARROW_SVG}
      </a>''')
    links_html = "\n      ".join(links)

    badge = mon.get("badge")
    badge_html = f'<span class="badge badge-{badge["class"]}">{badge["text"]}</span>' if badge else ""

    return f'''
  <div class="venue-card{card_class}" id="{entry_id}">
    <div>
      <p class="venue-name">{e["name"]}</p>
      <p class="venue-desc">{mon["desc"]}</p>{meta_html}
      <div class="venue-links">
      {links_html}
      </div>
    </div>
    {badge_html}
  </div>'''

def render_group(group, is_first):
    divider_html = '\n  <hr class="section-divider">\n' if group.get("divider_before") and not is_first else ""
    dates_html = f'\n    <span class="section-dates">{group["dates"]}</span>' if group.get("dates") else ""
    cards_html = "\n".join(render_card(eid) for eid in group["entry_ids"])
    return f'''{divider_html}
  <div class="section-head">
    <span class="city-marker"><span class="city-dot {group["dot"]}"></span>{group["label"]}</span>
    <div class="section-rule"></div>{dates_html}
  </div>
{cards_html}'''

groups_html = "\n".join(render_group(g, i == 0) for i, g in enumerate(MONITOR_GROUPS))

updates_html = "\n      ".join(f"<li>{u}</li>" for u in MONITOR_META["updates"])

timeline_html = "\n\n      ".join(
    f'<span class="tl-date">{row["date"]}</span>\n      <p class="tl-action">{row["action"]}</p>'
    for row in MONITOR_META["timeline"]
)

CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --ink: #17120e;
    --ink-mid: #2b2018;
    --ink-soft: #4a3f35;
    --ink-faint-on-dark: #d8c7ab;
    --paper: #faf7f2;
    --paper-warm: #f2ece2;
    --paper-deep: #e7ddcd;
    --rule: #cbb89e;
    --rule-light: #e5dac6;
    --gold: #a97f2e;
    --gold-deep: #7a5a1e;
    --gold-light: #e0b862;
    --urgent: #8b2635;
    --urgent-bg: #fbeef0;
    --urgent-border: #edc3ca;
    --high: #7a5210;
    --high-bg: #fdf3df;
    --high-border: #f0dcac;
    --medium: #1f4d70;
    --medium-bg: #eaf3fa;
    --medium-border: #c3dcee;
    --watch: #2f5c2a;
    --watch-bg: #eef6ea;
    --watch-border: #c5e0ba;
    --purple: #4a3570;
    --purple-bg: #f1eefa;
    --purple-border: #d6cbee;
    --shadow: 220 25% 15%;
  }

  html { font-size: 17px; }
  body {
    background: var(--paper);
    color: var(--ink);
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 400;
    line-height: 1.7;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* ── HEADER ── */
  .header {
    background:
      radial-gradient(ellipse 80% 100% at 50% 0%, #2a2018 0%, transparent 60%),
      linear-gradient(180deg, var(--ink) 0%, #100c09 100%);
    color: var(--paper);
    text-align: center;
    padding: 4.5rem 2rem 3.75rem;
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 3px,
      rgba(255,255,255,0.015) 3px,
      rgba(255,255,255,0.015) 4px
    );
    pointer-events: none;
  }
  .header-eyebrow {
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 600;
    font-size: 0.74rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--gold-light);
    margin-bottom: 1.5rem;
  }
  .header h1 {
    font-family: 'IM Fell English', serif;
    font-weight: 400;
    font-size: clamp(2.4rem, 5.5vw, 3.9rem);
    line-height: 1.15;
    color: var(--paper);
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
    text-shadow: 0 2px 24px rgba(0,0,0,0.35);
  }
  .header h1 em {
    font-style: italic;
    color: var(--gold-light);
  }
  .header-subtitle {
    font-family: 'IM Fell English', serif;
    font-style: italic;
    font-size: 1.15rem;
    color: var(--ink-faint-on-dark);
    margin-bottom: 2.2rem;
  }
  .header-rule {
    width: 64px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-light), transparent);
    margin: 0 auto 1.5rem;
  }
  .header-meta {
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-faint-on-dark);
  }

  /* ── INTRO BAND ── */
  .intro-band {
    background: var(--ink-mid);
    color: var(--paper-warm);
    padding: 1.75rem 2rem;
    text-align: center;
  }
  .intro-band p {
    font-family: 'IM Fell English', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: var(--paper-warm);
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.7;
  }
  .intro-band strong {
    color: var(--gold-light);
    font-style: normal;
    font-weight: 600;
  }

  /* ── UPDATE BAND ── */
  .update-band {
    background: var(--watch-bg);
    border-top: 1px solid var(--watch-border);
    border-bottom: 1px solid var(--watch-border);
    padding: 1.6rem 2rem;
  }
  .update-inner {
    max-width: 900px;
    margin: 0 auto;
  }
  .update-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--watch);
    margin-bottom: 0.85rem;
    display: block;
  }
  .update-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }
  .update-list li {
    font-size: 0.92rem;
    color: var(--ink-soft);
    line-height: 1.6;
    padding-left: 1.1rem;
    position: relative;
  }
  .update-list li::before {
    content: '—';
    position: absolute;
    left: 0;
    color: var(--watch);
  }
  .update-list strong { font-weight: 700; color: var(--ink); }

  /* ── STRATEGY BOX ── */
  .strategy-band {
    background: var(--paper-deep);
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 1.6rem 2rem;
  }
  .strategy-inner {
    max-width: 900px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1rem 1.5rem;
    align-items: start;
  }
  .strategy-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold-deep);
    white-space: nowrap;
    padding-top: 0.15rem;
  }
  .strategy-text {
    font-size: 0.95rem;
    color: var(--ink-soft);
    line-height: 1.6;
  }
  .strategy-text strong { font-weight: 700; color: var(--ink); }

  /* ── MAIN LAYOUT ── */
  .main { max-width: 900px; margin: 0 auto; padding: 3rem 2rem 5rem; }

  /* ── SECTION HEADERS ── */
  .section-head {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 3.25rem 0 1.5rem;
  }
  .section-head:first-child { margin-top: 0; }
  .city-marker {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-soft);
    white-space: nowrap;
  }
  .city-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 0 3px color-mix(in srgb, currentColor 15%, transparent);
  }
  .dot-bonn    { background: #5a4a8a; color: #5a4a8a; }
  .dot-cologne { background: #1f7a52; color: #1f7a52; }
  .dot-linz    { background: #9a6a1a; color: #9a6a1a; }
  .dot-vienna  { background: #8a2a4a; color: #8a2a4a; }
  .dot-general { background: #5a5550; color: #5a5550; }
  .section-rule {
    flex: 1;
    height: 1px;
    background: var(--rule-light);
  }
  .section-dates {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--gold-deep);
    font-style: italic;
  }

  /* ── VENUE CARDS ── */
  .venue-card {
    background: white;
    border: 1px solid var(--rule-light);
    border-radius: 12px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 0.9rem;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.5rem 1.25rem;
    align-items: start;
    box-shadow: 0 1px 3px hsl(var(--shadow) / 0.05);
    transition: border-color 0.18s, box-shadow 0.18s;
    position: relative;
  }
  .venue-card:hover {
    border-color: var(--rule);
    box-shadow: 0 8px 20px hsl(var(--shadow) / 0.1);
  }
  .venue-card.urgent { border-left: 4px solid var(--urgent); }
  .venue-card.high   { border-left: 4px solid var(--gold); }

  .venue-name {
    font-family: 'Libre Baskerville', serif;
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.4rem;
    line-height: 1.3;
  }
  .venue-desc {
    font-size: 0.94rem;
    color: var(--ink-soft);
    line-height: 1.65;
    margin-bottom: 0.75rem;
  }
  .venue-desc strong { font-weight: 700; color: var(--ink); }
  .venue-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.6rem;
  }
  .date-chip {
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    background: var(--paper-deep);
    color: var(--ink-soft);
    border: 1px solid var(--rule-light);
    padding: 3px 10px;
    border-radius: 999px;
  }
  .date-chip.confirmed {
    background: var(--watch-bg);
    color: var(--watch);
    border-color: var(--watch-border);
  }
  .date-chip.flagship {
    background: var(--urgent-bg);
    color: var(--urgent);
    border-color: var(--urgent-border);
    font-weight: 700;
  }
  .venue-links { display: flex; flex-wrap: wrap; gap: 0.4rem 1.25rem; }
  .venue-link {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--gold-deep);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    letter-spacing: 0.02em;
    border-bottom: 1px solid transparent;
    transition: border-color 0.15s, color 0.15s;
  }
  .venue-link:hover { border-bottom-color: var(--gold); color: var(--gold); }
  .venue-link svg { flex-shrink: 0; }

  /* ── BADGES ── */
  .badge {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 999px;
    white-space: nowrap;
    align-self: start;
    margin-top: 3px;
  }
  .badge-urgent  { background: var(--urgent-bg);  color: var(--urgent);  border: 1px solid var(--urgent-border); }
  .badge-high    { background: var(--high-bg);    color: var(--high);    border: 1px solid var(--high-border); }
  .badge-medium  { background: var(--medium-bg);  color: var(--medium);  border: 1px solid var(--medium-border); }
  .badge-watch   { background: var(--watch-bg);   color: var(--watch);   border: 1px solid var(--watch-border); }
  .badge-purple  { background: var(--purple-bg);  color: var(--purple);  border: 1px solid var(--purple-border); }

  /* ── TIMELINE CALLOUT ── */
  .timeline-box {
    background: linear-gradient(160deg, var(--ink) 0%, #100c09 100%);
    color: var(--paper-warm);
    border-radius: 14px;
    padding: 2.25rem 2.25rem;
    margin: 2.75rem 0 0;
    box-shadow: 0 12px 28px hsl(var(--shadow) / 0.18);
  }
  .timeline-box h3 {
    font-family: 'IM Fell English', serif;
    font-weight: 400;
    font-size: 1.2rem;
    color: var(--gold-light);
    margin-bottom: 1.4rem;
    letter-spacing: 0.02em;
  }
  .timeline-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 1.25rem;
  }
  .tl-date {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--gold-light);
    white-space: nowrap;
    padding-top: 0.1rem;
    letter-spacing: 0.04em;
  }
  .tl-action {
    font-size: 0.92rem;
    color: var(--paper-warm);
    line-height: 1.55;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.09);
    margin-bottom: 0.1rem;
  }
  .tl-action:last-child { border-bottom: none; }
  .tl-action strong { color: white; font-weight: 700; }

  /* ── DIVIDER ── */
  hr.section-divider {
    border: none;
    border-top: 1px solid var(--rule-light);
    margin: 2rem 0 0;
  }

  /* ── FOOTER ── */
  footer {
    background: var(--ink-mid);
    color: var(--ink-faint-on-dark);
    text-align: center;
    padding: 2.25rem 2rem;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    line-height: 1.8;
  }
  footer em {
    font-family: 'IM Fell English', serif;
    font-style: italic;
    color: var(--gold-light);
    font-size: 0.98rem;
    display: block;
    margin-bottom: 0.5rem;
  }

  /* ── RESPONSIVE ── */
  @media (max-width: 600px) {
    .header { padding: 3rem 1.5rem 2.5rem; }
    .main { padding: 2rem 1.25rem 4rem; }
    .venue-card { grid-template-columns: 1fr; }
    .badge { align-self: auto; }
    .strategy-inner { grid-template-columns: 1fr; gap: 0.25rem; }
    .timeline-grid { grid-template-columns: 1fr; }
    .tl-date { font-size: 0.75rem; color: var(--gold-light); margin-top: 0.75rem; }
    .tl-date:first-child { margin-top: 0; }
  }

  @media (prefers-reduced-motion: no-preference) {
    .venue-card { transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s; }
    .venue-card:hover { transform: translateY(-1px); }
  }
"""

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beethoven Pilgrimage 2027 — Concert Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">

<style>
{CSS}
</style>
</head>
<body>

<header class="header">
  <p class="header-eyebrow">Concert Monitor · {MONITOR_META["date_range"]}</p>
  <h1>Beethoven <em>Pilgrimage</em> 2027</h1>
  <p class="header-subtitle">{MONITOR_META["header_subtitle"]}</p>
  <div class="header-rule"></div>
  <p class="header-meta">{MONITOR_META["header_meta"]}</p>
</header>

<div class="intro-band">
  <p>{MONITOR_META["intro"]}</p>
</div>

<div class="update-band">
  <div class="update-inner">
    <span class="update-label">Update · {MONITOR_META["updated"]}</span>
    <ul class="update-list">
      {updates_html}
    </ul>
  </div>
</div>

<div class="strategy-band">
  <div class="strategy-inner">
    <span class="strategy-label">Strategy</span>
    <p class="strategy-text">{MONITOR_META["strategy"]}</p>
  </div>
</div>

<main class="main">
{groups_html}

  <!-- ── TIMELINE ── -->
  <div class="timeline-box">
    <h3>When to act</h3>
    <div class="timeline-grid">
      {timeline_html}
    </div>
  </div>

</main>

<footer>
  <em>"Music is a higher revelation than all wisdom and philosophy."</em>
  Beethoven Pilgrimage 2027 · Prepared {MONITOR_META["prepared"]} · Updated {MONITOR_META["updated"]} · {MONITOR_META["travelers"]} · Bonn to Vienna
</footer>

</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(HTML)
print("index.html written,", len(HTML), "chars")

n = len(re.findall(r'class="venue-card', HTML))
print("Venue cards:", n)
