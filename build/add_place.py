#!/usr/bin/env python3
"""
Add a new place to build/data.py and regenerate catalog.html, the KML, and
index.html. Splices the new entry into the source via `ast` (so only the new
text is added — nothing else in data.py gets reformatted), then validates the
result parses and imports cleanly before writing, rolling back on any failure.

Examples:

  # A plain sight — catalog + KML only, no Concert Monitor card
  python build/add_place.py --city linz --kind sight \\
    --name "Linz Castle" --latlon "48.3049,14.2843" \\
    --body "The Renaissance castle overlooking the Danube, with a small local-history museum."

  # A concert venue also tracked in the Concert Monitor
  python build/add_place.py --city vienna --kind concert \\
    --name "Wiener Musikverein — Brahms-Saal" --latlon "48.2006,16.3722" \\
    --body "The Musikverein's smaller recital hall." --link https://www.musikverein.at \\
    --status tentative \\
    --monitor-group Vienna --monitor-desc "Smaller-hall recitals sometimes slip in under the radar — worth checking directly." \\
    --monitor-badge-text "Worth checking" --monitor-badge-class purple \\
    --chip "Mar 2027|TBC"

Run from anywhere — paths are resolved relative to this file, not your cwd.
"""
import argparse
import ast
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BUILD_DIR)
DATA_PATH = os.path.join(BUILD_DIR, "data.py")

MONITOR_BADGE_CLASSES = {"urgent", "high", "medium", "watch", "purple"}
MONITOR_CARD_CLASSES = {"urgent", "high"}
KINDS = ["sight", "museum", "tavern", "extended", "concert", "flagship", "network"]


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def pq(s):
    """Quote a string as a Python double-quoted literal, matching data.py's style."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_data_module():
    sys.path.insert(0, BUILD_DIR)
    import data as data_module
    return data_module


def parse_args():
    p = argparse.ArgumentParser(
        description="Add a new place to the Beethoven catalog and regenerate catalog.html/.kml/index.html.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--city", required=True, help="Existing SECTIONS city id, e.g. 'vienna', 'linz', 'cologne'")
    p.add_argument("--name", required=True, help="Display name for the place")
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--latlon", required=True, help="'LAT,LON' — human order; stored internally as KML's lon,lat")
    p.add_argument("--body", required=True, help="Catalog description (HTML allowed, e.g. <b>...</b>)")
    p.add_argument("--id", help="Override the auto-generated id (default: slug of city+name)")
    p.add_argument("--link", help="Official website URL")
    p.add_argument("--status", choices=["confirmed", "tentative"])
    p.add_argument("--event-date", action="append", default=[], metavar="YYYY-MM-DD", help="Repeatable")
    p.add_argument("--event-label", help="Human-readable event label")
    p.add_argument("--route-tag", help="e.g. 'Version B route'")
    p.add_argument("--monitor-group", help="Existing Concert Monitor group label to add this venue to, e.g. 'Vienna'")
    p.add_argument("--monitor-desc", help="Booking-focused description for the Concert Monitor card")
    p.add_argument("--monitor-card-class", choices=sorted(MONITOR_CARD_CLASSES))
    p.add_argument("--monitor-badge-text", help="Badge label, e.g. '★ Book now'")
    p.add_argument("--monitor-badge-class", choices=sorted(MONITOR_BADGE_CLASSES))
    p.add_argument("--chip", action="append", default=[], metavar="TEXT[|variant]",
                    help="Date chip; variant is 'confirmed' or 'flagship'. Repeatable.")
    p.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    p.add_argument("--no-regen", action="store_true", help="Skip running the generators after adding")
    return p.parse_args()


def offset(source, lineno, col):
    lines = source.splitlines(keepends=True)
    return sum(len(l) for l in lines[: lineno - 1]) + col


def find_sections_list(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SECTIONS" for t in node.targets
        ):
            return node.value
    raise SystemExit("Could not find SECTIONS in data.py — has the file structure changed?")


def find_dict_value(dict_node, key):
    for k, v in zip(dict_node.keys, dict_node.values):
        if isinstance(k, ast.Constant) and k.value == key:
            return v
    return None


def render_monitor_source(monitor):
    parts = []
    if monitor.get("card_class"):
        parts.append(f'"card_class":"{monitor["card_class"]}"')
    parts.append(f'"desc":{pq(monitor["desc"])}')
    if monitor.get("chips"):
        chip_strs = []
        for c in monitor["chips"]:
            if "variant" in c:
                chip_strs.append(f'{{"text":{pq(c["text"])},"variant":"{c["variant"]}"}}')
            else:
                chip_strs.append(f'{{"text":{pq(c["text"])}}}')
        parts.append(f'"chips":[{",".join(chip_strs)}]')
    badge = monitor["badge"]
    parts.append(f'"badge":{{"text":{pq(badge["text"])},"class":"{badge["class"]}"}}')
    return "{" + ",".join(parts) + "}"


def render_entry_source(entry_id, args, coords, monitor):
    lines = [f'      {{"id":"{entry_id}","name":{pq(args.name)},"kind":"{args.kind}",']
    lines.append(f'       "coords":"{coords}",')
    if args.status:
        lines.append(f'       "status":"{args.status}",')
    if args.route_tag:
        lines.append(f'       "route_tag":{pq(args.route_tag)},')
    if args.event_date:
        dates_src = ",".join(f'"{d}"' for d in args.event_date)
        lines.append(f'       "event_dates":[{dates_src}],')
    if args.event_label:
        lines.append(f'       "event_label":{pq(args.event_label)},')

    last = f'       "body":{pq(args.body)}'
    if args.link:
        last += f',\n       "link":{pq(args.link)}'
    if monitor:
        last += f',\n       "monitor":{render_monitor_source(monitor)}'
    last += "},"
    lines.append(last)
    return "\n".join(lines)


def splice_entry(source, city, entry_src):
    tree = ast.parse(source)
    sections_list = find_sections_list(tree)

    target_section = None
    for section_dict in sections_list.elts:
        id_node = find_dict_value(section_dict, "id")
        if isinstance(id_node, ast.Constant) and id_node.value == city:
            target_section = section_dict
            break
    if target_section is None:
        raise SystemExit(f"Could not locate section '{city}' while splicing (unexpected).")

    entries_node = find_dict_value(target_section, "entries")
    if entries_node is None:
        raise SystemExit(f"Section '{city}' has no 'entries' list (unexpected).")

    # Insert at the start of the line holding the closing "]" of the entries
    # list, so the new entry lands as its own line(s) just above it.
    insert_pos = offset(source, entries_node.end_lineno, 0)
    return source[:insert_pos] + entry_src + "\n" + source[insert_pos:]


def splice_monitor_group_id(source, group_label, entry_id):
    tree = ast.parse(source)
    groups_assign = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MONITOR_GROUPS" for t in n.targets)
    )
    groups_list = groups_assign.value

    target_group = None
    for group_dict in groups_list.elts:
        label_node = find_dict_value(group_dict, "label")
        if isinstance(label_node, ast.Constant) and label_node.value == group_label:
            target_group = group_dict
            break
    if target_group is None:
        raise SystemExit(f"Could not locate monitor group '{group_label}' while splicing (unexpected).")

    entry_ids_node = find_dict_value(target_group, "entry_ids")
    insert_pos = offset(source, entry_ids_node.end_lineno, entry_ids_node.end_col_offset - 1)
    return source[:insert_pos] + f',"{entry_id}"' + source[insert_pos:]


def run(cmd, **kw):
    return subprocess.run(cmd, **kw)


def main():
    args = parse_args()
    data_module = load_data_module()

    section = next((s for s in data_module.SECTIONS if s["id"] == args.city), None)
    if section is None:
        valid = ", ".join(s["id"] for s in data_module.SECTIONS)
        sys.exit(
            f"Unknown --city '{args.city}'. Existing cities: {valid}\n"
            f"(Adding a brand-new city section isn't automated by this script — edit data.py directly for that.)"
        )

    all_ids = {e["id"] for s in data_module.SECTIONS for e in s["entries"]}
    all_ids |= {e["id"] for e in data_module.MONITOR_ONLY}
    entry_id = args.id or slugify(f"{args.city}-{args.name}")
    if entry_id in all_ids:
        sys.exit(f"id '{entry_id}' already exists — pass --id to override.")

    try:
        lat_s, lon_s = [p.strip() for p in args.latlon.split(",")]
        lat, lon = float(lat_s), float(lon_s)
    except ValueError:
        sys.exit(f"--latlon must be 'LAT,LON' (two numbers), got: {args.latlon!r}")
    coords = f"{lon},{lat},0"

    monitor = None
    group = None
    if args.monitor_group:
        group = next(
            (g for g in data_module.MONITOR_GROUPS if g["label"].lower() == args.monitor_group.lower()), None
        )
        if group is None:
            valid = ", ".join(g["label"] for g in data_module.MONITOR_GROUPS)
            sys.exit(f"Unknown --monitor-group '{args.monitor_group}'. Existing groups: {valid}")
        if not (args.monitor_desc and args.monitor_badge_text and args.monitor_badge_class):
            sys.exit("--monitor-group requires --monitor-desc, --monitor-badge-text, and --monitor-badge-class.")
        chips = []
        for c in args.chip:
            if "|" in c:
                text, variant = c.split("|", 1)
                chips.append({"text": text, "variant": variant})
            else:
                chips.append({"text": c})
        monitor = {"desc": args.monitor_desc, "badge": {"text": args.monitor_badge_text, "class": args.monitor_badge_class}}
        if args.monitor_card_class:
            monitor["card_class"] = args.monitor_card_class
        if chips:
            monitor["chips"] = chips
    elif args.chip or args.monitor_desc or args.monitor_badge_text:
        sys.exit("--chip/--monitor-desc/--monitor-badge-text require --monitor-group.")

    entry_src = render_entry_source(entry_id, args, coords, monitor)

    source = open(DATA_PATH, encoding="utf-8").read()
    new_source = splice_entry(source, args.city, entry_src)
    if monitor is not None:
        new_source = splice_monitor_group_id(new_source, group["label"], entry_id)

    try:
        ast.parse(new_source)
    except SyntaxError as e:
        sys.exit(f"Generated data.py would not parse: {e}")

    if args.dry_run:
        print(f"Would add id={entry_id!r} to city={args.city!r}" + (f", monitor group={group['label']!r}" if monitor else ""))
        print(entry_src)
        return

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(new_source)

    check = run([sys.executable, "-c", "import data"], cwd=BUILD_DIR, capture_output=True, text=True)
    if check.returncode != 0:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            f.write(source)
        sys.exit(f"data.py failed to import after edit — reverted.\n{check.stderr}")

    print(f"Added '{args.name}' as id={entry_id!r} to '{args.city}'" + (f" (Concert Monitor: {group['label']})" if monitor else "") + ".")

    if not args.no_regen:
        for script in ["gen_catalog.py", "gen_kml.py", "gen_index.py"]:
            r = run([sys.executable, os.path.join("build", script)], cwd=REPO_ROOT)
            if r.returncode != 0:
                sys.exit(f"{script} failed — check output above. data.py already has the new entry; fix and rerun the generators manually.")
        print("Regenerated catalog.html, the KML, and index.html.")


if __name__ == "__main__":
    main()
