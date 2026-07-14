# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0, '.')
from data import SECTIONS, ROOT, CATALOG_URL

KIND_LABEL = {
    "sight": "Sight",
    "museum": "Museum",
    "tavern": "Tavern &amp; Rest",
    "extended": "Wachau / Extended",
    "concert": "Concert",
    "flagship": "★ Confirmed Event",
    "network": "Beyond the Route",
}
KIND_CLASS = {
    "sight": "tag-sight",
    "museum": "tag-museum",
    "tavern": "tag-tavern",
    "extended": "tag-extended",
    "concert": "tag-concert",
    "flagship": "tag-flagship",
    "network": "tag-network",
}

def render_entry(e):
    kind = e["kind"]
    tag_label = KIND_LABEL[kind]
    tag_class = KIND_CLASS[kind]
    status = e.get("status")
    status_html = ""
    if status == "confirmed":
        status_html = '<span class="status-chip status-confirmed">Confirmed</span>'
    elif status == "tentative":
        status_html = '<span class="status-chip status-tentative">Tentative / not yet announced</span>'
    event_html = ""
    if e.get("event_label"):
        event_html = f'<p class="entry-event">{e["event_label"]}</p>'
    route_html = ""
    if e.get("route_tag"):
        route_html = f'<span class="tag route-tag">{e["route_tag"]}</span>'
    link_html = ""
    if e.get("link"):
        link_html = f'''<a class="entry-link" href="{e["link"]}" target="_blank" rel="noopener">{e["link"].replace("https://","").replace("http://","").rstrip("/")}
        <svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 10L10 2M5 2h5v5"/></svg></a>'''
    return f'''
  <div class="entry" id="{e["id"]}">
    <div class="entry-head">
      <span class="tag {tag_class}">{tag_label}</span>
      {route_html}
      {status_html}
    </div>
    <p class="entry-name">{e["name"]}</p>
    {event_html}
    <p class="entry-body">{e["body"]}</p>
    {link_html}
  </div>'''

def render_section(sec):
    entries_html = "\n".join(render_entry(e) for e in sec["entries"])
    return f'''
  <section class="city-section" id="{sec["id"]}">
    <div class="section-head">
      <h2>{sec["title"]}</h2>
      <span class="section-sub">{sec["subtitle"]}</span>
    </div>
    {entries_html}
  </section>'''

def render_toc():
    items = []
    for sec in SECTIONS:
        items.append(f'<a href="#{sec["id"]}">{sec["title"]}</a>')
    return "\n      ".join(items)

sections_html = "\n".join(render_section(s) for s in SECTIONS)
toc_html = render_toc()

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beethoven Pilgrimage 2027 — The Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --ink: #1a1410; --ink-mid: #3d3028; --ink-muted: #7a6b5e; --ink-faint: #b8a898;
    --paper: #f7f3ed; --paper-warm: #f0ebe2; --paper-deep: #e8e0d4;
    --rule: #c8b8a8; --rule-light: #ddd4c8;
    --gold: #9a7c3a; --gold-light: #c4a55a;
    --urgent: #7a2020; --urgent-bg: #fdf0f0;
    --high: #6b4a10; --high-bg: #fdf6e8;
    --medium: #1a4a6b; --medium-bg: #eef4fb;
    --watch: #3a5a2a; --watch-bg: #f0f7ec;
    --purple: #4a3a6b; --purple-bg: #f2f0f8;
    --teal: #1a6b5e; --teal-bg: #eaf6f3;
  }}
  html {{ font-size: 16px; scroll-behavior: smooth; }}
  body {{ background: var(--paper); color: var(--ink); font-family: 'Source Sans 3', sans-serif; font-weight: 300; line-height: 1.7; }}

  .header {{ background: var(--ink); color: var(--paper); text-align: center; padding: 4rem 2rem 3rem; }}
  .header-eyebrow {{ font-size: 0.72rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold-light); margin-bottom: 1.4rem; }}
  .header h1 {{ font-family: 'IM Fell English', serif; font-weight: 400; font-size: clamp(2.2rem, 5vw, 3.6rem); line-height: 1.15; margin-bottom: 0.5rem; }}
  .header h1 em {{ font-style: italic; color: var(--gold-light); }}
  .header-subtitle {{ font-family: 'IM Fell English', serif; font-style: italic; font-size: 1.1rem; color: var(--ink-faint); margin-bottom: 2rem; }}
  .header-rule {{ width: 60px; height: 1px; background: var(--gold); margin: 0 auto 1.5rem; }}
  .header-meta {{ font-size: 0.8rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-faint); }}

  .intro-band {{ background: var(--ink-mid); color: var(--paper-warm); padding: 1.6rem 2rem; text-align: center; }}
  .intro-band p {{ font-family: 'IM Fell English', serif; font-style: italic; font-size: 1.05rem; max-width: 760px; margin: 0 auto; line-height: 1.7; }}
  .intro-band strong {{ color: var(--gold-light); font-style: normal; font-weight: 400; }}

  .legend-band {{ background: var(--paper-deep); border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); padding: 1.25rem 2rem; }}
  .legend-inner {{ max-width: 900px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 0.6rem 1rem; align-items: center; justify-content: center; }}
  .legend-note {{ font-size: 0.82rem; color: var(--ink-muted); width: 100%; text-align: center; margin-bottom: 0.4rem; }}

  .toc-band {{ background: var(--paper); border-bottom: 1px solid var(--rule-light); padding: 1.25rem 2rem; position: sticky; top: 0; z-index: 10; backdrop-filter: blur(6px); background: rgba(247,243,237,0.94); }}
  .toc-inner {{ max-width: 900px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; justify-content: center; }}
  .toc-inner a {{ font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink-muted); text-decoration: none; border-bottom: 1px solid transparent; padding-bottom: 2px; }}
  .toc-inner a:hover {{ color: var(--gold); border-bottom-color: var(--gold-light); }}

  .main {{ max-width: 900px; margin: 0 auto; padding: 3rem 2rem 5rem; }}

  .city-section {{ margin-bottom: 3.5rem; scroll-margin-top: 4.5rem; }}
  .section-head {{ display: flex; align-items: baseline; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--gold); padding-bottom: 0.6rem; flex-wrap: wrap; }}
  .section-head h2 {{ font-family: 'IM Fell English', serif; font-weight: 400; font-size: 1.7rem; color: var(--ink); }}
  .section-sub {{ font-size: 0.82rem; color: var(--ink-muted); font-style: italic; }}

  .entry {{ background: white; border: 1px solid var(--rule-light); border-radius: 2px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; scroll-margin-top: 4.5rem; }}
  .entry-head {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.6rem; align-items: center; }}
  .tag {{ font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 9px; border-radius: 2px; white-space: nowrap; }}
  .tag-sight {{ background: var(--medium-bg); color: var(--medium); border: 1px solid #b8d0e8; }}
  .tag-museum {{ background: var(--purple-bg); color: var(--purple); border: 1px solid #c8c0e0; }}
  .tag-tavern {{ background: var(--high-bg); color: var(--high); border: 1px solid #e8d4a0; }}
  .tag-extended {{ background: var(--watch-bg); color: var(--watch); border: 1px solid #c0d8b8; }}
  .tag-concert {{ background: var(--teal-bg); color: var(--teal); border: 1px solid #b8ddd2; }}
  .tag-flagship {{ background: var(--urgent-bg); color: var(--urgent); border: 1px solid #e8c0c0; }}
  .tag-network {{ background: var(--paper-deep); color: var(--ink-muted); border: 1px solid var(--rule-light); }}
  .route-tag {{ background: none; color: var(--ink-faint); border: 1px dashed var(--rule); }}
  .status-chip {{ font-size: 0.66rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 3px 9px; border-radius: 2px; }}
  .status-confirmed {{ background: var(--watch-bg); color: var(--watch); border: 1px solid #c8dfc0; }}
  .status-tentative {{ background: var(--paper-deep); color: var(--ink-muted); border: 1px solid var(--rule-light); }}

  .entry-name {{ font-family: 'Libre Baskerville', serif; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.3rem; }}
  .entry-event {{ font-size: 0.82rem; color: var(--urgent); font-weight: 600; margin-bottom: 0.5rem; }}
  .entry-body {{ font-size: 0.9rem; color: var(--ink-mid); line-height: 1.65; margin-bottom: 0.6rem; }}
  .entry-body b {{ font-weight: 600; color: var(--ink); }}
  .entry-link {{ font-size: 0.78rem; color: var(--gold); text-decoration: none; display: inline-flex; align-items: center; gap: 4px; border-bottom: 1px solid transparent; }}
  .entry-link:hover {{ border-bottom-color: var(--gold-light); }}

  footer {{ background: var(--ink-mid); color: var(--ink-faint); text-align: center; padding: 2rem; font-size: 0.78rem; letter-spacing: 0.05em; line-height: 1.8; }}
  footer em {{ font-family: 'IM Fell English', serif; font-style: italic; color: var(--gold-light); font-size: 0.92rem; display: block; margin-bottom: 0.5rem; }}

  @media (max-width: 600px) {{
    .header {{ padding: 3rem 1.5rem 2.5rem; }}
    .main {{ padding: 2rem 1.25rem 4rem; }}
  }}
</style>
</head>
<body>

<header class="header">
  <p class="header-eyebrow">The Catalog · Bonn to Vienna and beyond</p>
  <h1>Beethoven <em>Pilgrimage</em> 2027</h1>
  <p class="header-subtitle">Every sight, museum, tavern, and confirmed performance — organized by place, not by date</p>
  <div class="header-rule"></div>
  <p class="header-meta">Companion to the Concert Monitor · tripperist.github.io/beethoven</p>
</header>

<div class="intro-band">
  <p>This is the full catalog behind the pilgrimage — every Beethoven site, museum, and performance we've found worth knowing about, whether or not it's on the current itinerary. <strong>All dates are subject to change.</strong> Where a concert or performance has a real, confirmed date we say so plainly; where it's still a placeholder, we say that too. The companion KML map links directly into this page — click through from any pin to read the full entry here.</p>
</div>

<div class="legend-band">
  <div class="legend-inner">
    <span class="legend-note">Entry types, at a glance:</span>
    <span class="tag tag-sight">Sight</span>
    <span class="tag tag-museum">Museum</span>
    <span class="tag tag-tavern">Tavern &amp; Rest</span>
    <span class="tag tag-extended">Wachau / Extended</span>
    <span class="tag tag-concert">Concert</span>
    <span class="tag tag-flagship">★ Confirmed Event</span>
    <span class="tag tag-network">Beyond the Route</span>
  </div>
</div>

<div class="toc-band">
  <div class="toc-inner">
      {toc_html}
  </div>
</div>

<main class="main">
{sections_html}
</main>

<footer>
  <em>"Music is a higher revelation than all wisdom and philosophy."</em>
  Beethoven Pilgrimage 2027 · The Catalog · Updated 14 July 2026 · Companion to the Concert Monitor
</footer>

</body>
</html>
'''

with open('catalog.html', 'w', encoding='utf-8') as f:
    f.write(HTML)
print("catalog.html written,", len(HTML), "chars")
