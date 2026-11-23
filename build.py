#!/usr/bin/env python3
"""Build the Selectazzz site into docs/ from data.json + site.json. Stdlib only.

One page: hero, about, dates (grouped by year, most-played venues), photos, links.
"""
import json, pathlib, shutil
from collections import Counter
from html import escape as e

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text())
DATA = json.loads((ROOT / "data.json").read_text())
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
# Palette lifted from the Carlo's Turntables logo, one colour per year.
YEAR_COLOURS = ["#f68d04", "#2a9fd8", "#d0103f", "#13894b", "#f5b400"]


def when(d):
    """'2023-03-11' -> '11 Mar', '2025-04' -> 'Apr', '2023' -> 'date n/a'."""
    p = d.split("-")
    if len(p) == 3:
        return f"{int(p[2])} {MONTHS[int(p[1]) - 1]}"
    if len(p) == 2:
        return MONTHS[int(p[1]) - 1]
    return "—"


def src_link(s):
    if s == "medium":
        return "https://cdm.medium.com/carlos-turntable-playlists-2826ab98480c"
    if s.startswith("ig:"):
        return f"https://www.instagram.com/p/{s[3:]}/"
    return ""


def umami():
    if not SITE.get("umami_id"):
        return ""
    return ("<!-- Umami -->"
            "<script>try{/[?&#]noumami\\b/.test(location.href)&&localStorage.setItem('umami.disabled','1')}catch(e){}</script>\n"
            f'<script defer src="https://m.aguywithascarf.com/k.js" data-website-id="{SITE["umami_id"]}" '
            f'data-domains="{SITE["host"]}"></script>\n<!-- /Umami -->')


def wordmark(text, cls):
    """Layered wordmark: two offset back layers and a translucent front, like the logo."""
    t = e(text)
    return (f'<span class="{cls}" aria-label="{t}"><span class="l1" aria-hidden="true">{t}</span>'
            f'<span class="l2" aria-hidden="true">{t}</span><span class="l3" aria-hidden="true">{t}</span></span>')


def dates_section(gigs):
    by_year = {}
    for g in gigs:
        by_year.setdefault(g["date"][:4], []).append(g)
    years = sorted(by_year, reverse=True)
    blocks = []
    for i, y in enumerate(years):
        rows = []
        for g in sorted(by_year[y], key=lambda g: g["date"], reverse=True):
            note = f'<span class="nt">{e(g["note"])}</span>' if g.get("note") else ""
            place = f'<span class="pl">{e(g["place"])}</span>' if g.get("place") else ""
            star = ' class="away"' if "New York" in g.get("place", "") else ""
            rows.append(f'<li{star}><a href="{src_link(g["src"])}" target="_blank" rel="noopener">'
                        f'<span class="dt">{when(g["date"])}</span>'
                        f'<span class="vn">{e(g["venue"])}{note}</span>{place}</a></li>')
        n = len(by_year[y])
        blocks.append(f"""<section class="year" style="--c:{YEAR_COLOURS[i % len(YEAR_COLOURS)]}">
  <h3 class="d"><span>{y}</span><small>{n} {'date' if n == 1 else 'dates'}</small></h3>
  <ol>{''.join(rows)}</ol>
</section>""")
    return "".join(blocks)


def venues(gigs):
    """Most-played venues (2+ dates), as bars."""
    c = Counter(g["venue"] for g in gigs if not g["venue"].lower().startswith("private"))
    top = [(v, n) for v, n in c.most_common() if n > 1]
    mx = top[0][1]
    rows = "".join(f'<li><span class="vn">{e(v)}</span><span class="vb" style="--w:{n / mx:.3f}"></span>'
                   f'<span class="n">{n}</span></li>' for v, n in top)
    return f'<ul class="venues">{rows}</ul>'


def page():
    a, gigs = DATA["about"], DATA["gigs"]
    n_venues = len({g["venue"] for g in gigs if not g["venue"].lower().startswith("private")})
    first = min(g["date"][:4] for g in gigs)
    photos = "".join(f"""<figure{' class="contain"' if p.get('fit') == 'contain' else ''}>
  <img src="img/{p['file']}-1200.jpg" srcset="img/{p['file']}-600.jpg 600w, img/{p['file']}-1200.jpg 1200w" sizes="(max-width: 700px) 100vw, 50vw" alt="{e(p['alt'])}" loading="lazy">
  <figcaption>{e(p['caption'])}</figcaption>
</figure>""" for p in DATA["photos"])
    links = "".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener"><span class="k">{e(l["label"])}</span>'
                    f'<span class="d">{e(l["handle"])} ↗</span></a>' for l in DATA["links"])
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    stores = " · ".join(e(s) for s in a["stores"])
    title = "Selectazzz · Carlo's Turntables"
    desc = f"Selectazzz: Carlo De Marchis's all-vinyl selector sets. {len(gigs)} dates since {first}, Torino to New York."
    url = f"https://{SITE['host']}/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#01003c">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{url}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;900&display=swap">
<link rel="stylesheet" href="site.css?v={SITE['css_version']}">
{umami()}
</head>
<body>
<header class="bar">
  <a class="logo d" href="./">Selectazzz</a>
  <nav class="k"><a href="#about">About</a><a href="#dates">Dates</a><a href="#photos">Photos</a><a href="#links">Links</a></nav>
</header>
<main>
<section class="hero">
  <h1 class="d">{wordmark('Selectazzz', 'wm')}</h1>
  <p class="strap d">{wordmark("Carlo's Turntables", 'wm sub')}</p>
  <p class="tag">{e(a['tagline'])}</p>
  <ul class="stats k"><li><b>{len(gigs)}</b> dates</li><li><b>{n_venues}</b> venues</li><li><b>2,000+</b> records</li><li>since <b>{first}</b></li></ul>
</section>

<section id="about" class="about">
  <h2 class="d">About</h2>
  <div class="cols">
    <div class="txt">{paras}<p class="stores"><span class="k">{e(a['stores_intro'])}</span> {stores}</p></div>
    <figure class="logo-img"><img src="img/ct-logo-1200.jpg" alt="The Carlo's Turntables logo: overlapping rounded letters in orange, red, green and blue on navy" loading="lazy"></figure>
  </div>
</section>

<section id="dates" class="dates">
  <div class="sh"><h2 class="d">Dates</h2><span class="k">{len(gigs)} sets · each links to its source</span></div>
  <div class="most"><h3 class="k">Most played</h3>{venues(gigs)}</div>
  <div class="years">{dates_section(gigs)}</div>
</section>

<section id="photos" class="photos">
  <div class="sh"><h2 class="d">Photos</h2></div>
  <div class="grid">{photos}</div>
</section>

<section id="links" class="links">
  <div class="sh"><h2 class="d">Links</h2></div>
  <div class="lk">{links}</div>
</section>
</main>
<footer class="k">
  <span>© Carlo De Marchis · Selectazzz</span>
  <span><a href="https://carlodemarchis.it/">carlodemarchis.it</a></span>
</footer>
</body>
</html>
"""


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page())
    for f in ("site.css", "favicon.svg", "og.jpg"):
        shutil.copy(ROOT / f, DOCS / f)
    shutil.copytree(ROOT / "img", DOCS / "img", dirs_exist_ok=True)
    (DOCS / "CNAME").write_text(SITE["host"] + "\n")
    print(f"built docs/index.html: {len(DATA['gigs'])} dates, {len(DATA['photos'])} photos")


if __name__ == "__main__":
    main()
