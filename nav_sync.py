#!/usr/bin/env python3
"""
nav_sync.py  —  Regenerate AUTO-NAV blocks in every pages/*.qmd
Can be run from any directory — always works relative to this script's location.

Tab order: all regular pages alphabetically, then flashcard/game pages pinned at the end.
"""
import os, re, glob

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

pages_dir = "pages"
qmd_files = sorted(glob.glob(os.path.join(pages_dir, "*.qmd")))

if not qmd_files:
    print("  ⚠  No .qmd files found in pages/")
    exit(0)

# Pages to pin at the far right of the nav bar (in this order)
PINNED_LAST = ["flashcards"]

tabs = []
for path in qmd_files:
    key = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
    title = m.group(1) if m else key.title()
    tabs.append((key, title, path))

# Sort: regular pages first (alpha), pinned pages at the end in defined order
def sort_key(tab):
    key = tab[0]
    if key in PINNED_LAST:
        return (1, PINNED_LAST.index(key))
    return (0, key)

tabs.sort(key=sort_key)

NAV_COMMENT = "<!-- AUTO-NAV-START -->"
NAV_END     = "<!-- AUTO-NAV-END -->"

updated = 0
skipped = 0
for current_key, _, current_path in tabs:
    tab_lines = ""
    for key, title, _ in tabs:
        active = ' class="nav-tab active"' if key == current_key else ' class="nav-tab"'
        tab_lines += f'    <a{active} href="{key}.html">{title}</a>\n'

    new_nav = (
        f'{NAV_COMMENT}\n'
        f'<div id="nav-tabs">\n'
        f'{tab_lines}'
        f'</div>\n'
        f'{NAV_END}'
    )

    with open(current_path, encoding="utf-8") as f:
        content = f.read()

    if NAV_COMMENT in content and NAV_END in content:
        content = re.sub(
            re.escape(NAV_COMMENT) + r'.*?' + re.escape(NAV_END),
            new_nav,
            content,
            flags=re.DOTALL
        )
        with open(current_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ nav updated: {os.path.basename(current_path)}")
        updated += 1
    else:
        print(f"  ⚠  no AUTO-NAV markers in {os.path.basename(current_path)} — skipping")
        skipped += 1

print(f"\n  {updated} page(s) updated, {skipped} skipped.")
