# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from data import SECTIONS, STYLE_FOR_KIND, CATALOG_URL, INDEX_URL, maps_url

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if s else s

def render_placemark(e):
    kind = e["kind"]
    style = STYLE_FOR_KIND[kind]
    anchor = f"{CATALOG_URL}#{e['id']}"
    name = e["name"]

    # description: short teaser (strip HTML tags for the teaser line) + status/date + link
    body = e["body"]
    event_line = ""
    if e.get("event_label"):
        badge = "CONFIRMED" if e.get("status") == "confirmed" else "TENTATIVE"
        event_line = f"<b>[{badge}] {e['event_label']}</b><br/><br/>\n        "
    elif e.get("status") == "tentative":
        event_line = "<b>[TENTATIVE — no confirmed date yet]</b><br/><br/>\n        "

    monitor_line = ""
    if e.get("monitor"):
        monitor_line = f'\n        <br/><a href="{INDEX_URL}#{e["id"]}">Booking status in the Concert Monitor →</a>'

    desc = f"""
        {event_line}{body}<br/><br/>
        <a href=\"{anchor}\">Full entry in the Beethoven Catalog →</a>
        <br/><a href=\"{maps_url(e['coords'])}\">View on Google Maps →</a>{monitor_line}
      """

    timestamp_block = ""
    dates = e.get("event_dates")
    if dates:
        if len(dates) == 1:
            timestamp_block = f"\n      <TimeStamp><when>{dates[0]}</when></TimeStamp>"
        else:
            # multiple event dates: use a TimeSpan covering first..last, list all in description already
            timestamp_block = f"\n      <TimeSpan><begin>{dates[0]}</begin><end>{dates[-1]}</end></TimeSpan>"

    return f"""    <Placemark>
      <name>{esc(name)}</name>
      <description><![CDATA[{desc}]]></description>
      <styleUrl>#{style}</styleUrl>{timestamp_block}
      <Point><coordinates>{e['coords']}</coordinates></Point>
    </Placemark>"""

STYLES_BLOCK = """    <!-- Core Beethoven sites (gold/blue) -->
    <Style id="core-pin">
      <IconStyle>
        <color>ffb8860b</color>
        <scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><scale>0.9</scale></LabelStyle>
    </Style>

    <!-- Extended / decompression / Wachau sites (green) -->
    <Style id="extended-pin">
      <IconStyle>
        <color>ff1f4e79</color>
        <scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><scale>0.9</scale></LabelStyle>
    </Style>

    <!-- Concert venues, no confirmed date yet (music note) -->
    <Style id="concert-pin">
      <IconStyle>
        <scale>1.3</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/music.png</href></Icon>
      </IconStyle>
    </Style>

    <!-- Confirmed flagship events / anniversary dates (red star) -->
    <Style id="anniversary-pin">
      <IconStyle>
        <scale>1.6</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon>
      </IconStyle>
    </Style>

    <!-- Off-route / wider anniversary network (gray) -->
    <Style id="network-pin">
      <IconStyle>
        <color>ff888888</color>
        <scale>1.0</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href></Icon>
      </IconStyle>
      <LabelStyle><scale>0.85</scale></LabelStyle>
    </Style>

    <!-- Pilgrimage route line -->
    <Style id="route">
      <LineStyle>
        <color>99ffaa00</color>
        <width>3</width>
      </LineStyle>
    </Style>"""

# route line: keep the original core-route waypoints (Bonn -> Cologne -> Drachenfels -> Koblenz -> Loreley -> Heidelberg -> Munich -> Salzburg -> Vienna)
ROUTE_COORDS = """          7.0982,50.7374,0
          6.9603,50.9413,0
          7.1908,50.6598,0
          7.6087,50.3641,0
          7.7233,50.1339,0
          8.7153,49.4102,0
          11.5800,48.1411,0
          13.0432,47.8003,0
          16.3725,48.2005,0"""

folders = []
for sec in SECTIONS:
    placemarks = "\n\n".join(render_placemark(e) for e in sec["entries"])
    folders.append(f"""    <!-- ═══════════════════════════════════════════════════════ -->
    <!--  {sec['title'].upper()}  -->
    <!-- ═══════════════════════════════════════════════════════ -->

{placemarks}""")

route_placemark = f"""    <Placemark>
      <name>Pilgrimage Route — Bonn to Vienna</name>
      <description><![CDATA[Indicative core route line. See the Beethoven Catalog (tripperist.github.io/beethoven/catalog.html) for the full, place-by-place breakdown of every stop, sight, and confirmed event.]]></description>
      <styleUrl>#route</styleUrl>
      <LineString>
        <tessellate>1</tessellate>
        <coordinates>
{ROUTE_COORDS}
        </coordinates>
      </LineString>
    </Placemark>"""

KML = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Beethoven Pilgrimage 2027 — Bonn to Vienna (Catalog Edition)</name>
    <description><![CDATA[
      A visual companion to the Beethoven Pilgrimage 2027 Catalog (tripperist.github.io/beethoven/catalog.html).
      Sights carry no fixed date — the itinerary order is flexible and subject to change.
      Concerts and performances carry their real, confirmed (or clearly marked tentative) event dates,
      not itinerary day numbers. Click through from any placemark to the full catalog entry.
    ]]></description>

    <!-- ═══════════════════════════════════════════════════════ -->
    <!--  STYLES                                                  -->
    <!-- ═══════════════════════════════════════════════════════ -->

{STYLES_BLOCK}

{chr(10).join(folders)}

    <!-- ═══════════════════════════════════════════════════════ -->
    <!--  ROUTE LINE                                              -->
    <!-- ═══════════════════════════════════════════════════════ -->

{route_placemark}

  </Document>
</kml>
"""

with open('beethoven_pilgrimage_2027_catalog.kml', 'w', encoding='utf-8') as f:
    f.write(KML)
print("KML written,", len(KML), "chars")

# Count placemarks for sanity
import re
n = len(re.findall(r'<Placemark>', KML))
print("Placemarks:", n)
