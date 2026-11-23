#!/usr/bin/env python3
"""records.json: Carlo's whole Discogs collection (user carlodemarchis, folder 0 = All), the same
public endpoint linkedin_instagram_automation/discogs_stories.py reads. No token needed: the
collection is public. Stdlib only. Run again whenever the collection changes, then build.py."""
import json, pathlib, re, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://api.discogs.com/users/carlodemarchis/collection/folders/0/releases?per_page=100&sort=added&sort_order=desc&page={}"
clean = lambda n: re.sub(r"\s\(\d+\)$", "", n).strip()   # "Nightmares On Wax (2)" -> "Nightmares On Wax"

out, page, pages = [], 1, 1
while page <= pages:
    req = urllib.request.Request(URL.format(page), headers={"User-Agent": "Selectazzz/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    pages = d["pagination"]["pages"]
    for rel in d["releases"]:
        b = rel["basic_information"]
        artist = "".join(clean(a["name"]) + (f" {a['join']} " if a.get("join") and a["join"] != "," else (", " if a.get("join") == "," else ""))
                         for a in b.get("artists", [])).strip().rstrip(",")
        fmt = b.get("formats", [{}])[0]
        out.append({
            "id": b["id"], "artist": artist, "title": b["title"], "year": b.get("year") or None,
            "label": clean(b["labels"][0]["name"]) if b.get("labels") else "",
            "catno": b["labels"][0].get("catno", "") if b.get("labels") else "",
            "format": ", ".join([fmt.get("name", "")] + fmt.get("descriptions", [])[:2]).strip(", "),
            "genres": b.get("genres", []), "styles": b.get("styles", [])[:4],
            "thumb": b.get("thumb", ""), "added": rel["date_added"][:10],
        })
    print(f"page {page}/{pages}: {len(out)}")
    page += 1
    time.sleep(1.2)  # Discogs allows 25 unauthenticated requests a minute
(ROOT / "records.json").write_text(json.dumps({"fetched": time.strftime("%Y-%m-%d"), "count": len(out), "records": out},
                                              ensure_ascii=False, separators=(",", ":")))
print("records.json:", len(out), "records")
