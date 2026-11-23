#!/usr/bin/env python3
"""Build the Selectazzz site into docs/ from data.json + site.json. Stdlib only.

One page laid out like a record sleeve: hero, about, the dates as a numbered
tracklist (residency first), photos, links.
"""
import json, pathlib, shutil
from html import escape as e

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text())
DATA = json.loads((ROOT / "data.json").read_text())


def when(d):
    """'2023-03-11' -> '11.03', '2025-04' -> '··.04', '2023' -> '··.··'."""
    p = d.split("-")
    return f"{p[2] if len(p) > 2 else '··'}.{p[1] if len(p) > 1 else '··'}"


def src_link(s):
    if s == "medium":
        return "https://cdm.medium.com/carlos-turntable-playlists-2826ab98480c"
    if s.startswith("ig:"):
        return f"https://www.instagram.com/p/{s[3:]}/"
    return ""  # "carlo": told by Carlo directly, nothing to link


def cap(p):
    """Photo caption, linked to the post it came from when there is one."""
    href = src_link(p["src"]) if p.get("src") else ""
    return f'<a href="{href}" target="_blank" rel="noopener">{e(p["caption"])}</a>' if href else e(p["caption"])


def umami():
    if not SITE.get("umami_id"):
        return ""
    return ("<!-- Umami -->"
            "<script>try{/[?&#]noumami\\b/.test(location.href)&&localStorage.setItem('umami.disabled','1')}catch(e){}</script>\n"
            f'<script defer src="https://m.aguywithascarf.com/k.js" data-website-id="{SITE["umami_id"]}" '
            f'data-domains="{SITE["host"]}"></script>\n<!-- /Umami -->')


def dates_section(gigs):
    """Every set numbered in order played (No. 001 = first), newest first, grouped by year.
    data.json keeps the sets in the order of the source list, which is chronological; a date
    without month (2023's second private open-air party) keeps its place from that list."""
    ordered = gigs
    num = {id(g): i + 1 for i, g in enumerate(ordered)}
    by_year = {}
    for g in reversed(ordered):
        by_year.setdefault(g["date"][:4], []).append(g)
    blocks = []
    for y, gs in by_year.items():
        rows = []
        for g in gs:
            note = f'<span class="nt">{e(g["note"])}</span>' if g.get("note") else ""
            href = src_link(g["src"])
            inner = (f'<span class="no m">{num[id(g)]:03d}</span>'
                     f'<span class="dt m">{when(g["date"])}</span>'
                     f'<span class="vn">{e(g["venue"])}{note}</span>'
                     f'<span class="pl">{e(g.get("place", ""))}</span>')
            rows.append(f'<li><a class="r" href="{href}" target="_blank" rel="noopener">{inner}</a></li>' if href
                        else f'<li><div class="r">{inner}</div></li>')
        n = len(gs)
        blocks.append(f"""<section class="year">
  <h3><span class="m">{y}</span><span class="m c">{n} {'set' if n == 1 else 'sets'}</span></h3>
  <ol>{''.join(rows)}</ol>
</section>""")
    return "".join(blocks)


def residency():
    r = DATA.get("residency")
    if not r:
        return ""
    return f"""<div class="res">
  <p class="m">Residency · since {e(r['since'])}</p>
  <p class="rv"><a href="{e(r['url'])}" target="_blank" rel="noopener">{e(r['venue'])}</a>, {e(r['place'])}</p>
  <p class="rr">{e(r['rule'])}</p>
  <p class="m nx" id="next" hidden></p>
</div>
<script>
// Next Thursday that is not the first Thursday of its month (the residency's usual pattern).
(function () {{
  const d = new Date(); d.setHours(0, 0, 0, 0);
  for (let i = 0; i < 21; i++, d.setDate(d.getDate() + 1)) {{
    if (d.getDay() === 4 && d.getDate() > 7) {{
      const el = document.getElementById('next');
      el.textContent = 'Next, usually: ' + d.toLocaleDateString('en-GB', {{weekday: 'short', day: 'numeric', month: 'short'}});
      el.hidden = false; return;
    }}
  }}
}})();
</script>"""


def page():
    a, gigs = DATA["about"], DATA["gigs"]
    n_venues = len({g["venue"] for g in gigs if not g["venue"].lower().startswith("private")})
    first = min(g["date"][:4] for g in gigs)
    hero = DATA["photos"][0]
    photos = "".join(f"""<figure{' class="contain"' if p.get('fit') == 'contain' else ''}>
  <img src="img/{p['file']}-1200.jpg" srcset="img/{p['file']}-600.jpg 600w, img/{p['file']}-1200.jpg 1200w" sizes="(max-width: 700px) 100vw, 33vw" alt="{e(p['alt'])}" loading="lazy">
  <figcaption class="m">{cap(p)}</figcaption>
</figure>""" for p in DATA["photos"][1:])
    links = "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener"><span class="m">{e(l["label"])}</span>'
                    f'<span>{e(l["handle"])}</span><span class="ar">↗</span></a></li>' for l in DATA["links"])
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    stores = "".join(f"<li>{e(s)}</li>" for s in a["stores"])
    title = "Selectazzz · Carlo De Marchis"
    desc = f"Selectazzz: Carlo De Marchis's selector sets, mostly vinyl, now hybrid. {len(gigs)} sets since {first}."
    url = f"https://{SITE['host']}/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ecebe6">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="site.css?v={SITE['css_version']}">
{umami()}
</head>
<body>
<header class="bar">
  <a class="logo" href="./">selectazzz</a>
  <nav class="m"><a href="#about">About</a><a href="#sets">Sets</a><a href="#photos">Photos</a><a href="#links">Links</a></nav>
</header>
<main>
<section class="hero">
  <div class="ht">
    <p class="m kick">Carlo De Marchis · Selector · Torino</p>
    <h1>selectazzz</h1>
    <p class="tag">{e(a['tagline'])}</p>
    <dl class="stats m">
      <div><dt>Sets</dt><dd>{len(gigs)}</dd></div>
      <div><dt>Venues</dt><dd>{n_venues}</dd></div>
      <div><dt>Records</dt><dd>2,000+</dd></div>
      <div><dt>Since</dt><dd>{first}</dd></div>
    </dl>
  </div>
  <figure class="hp"><img src="img/{hero['file']}-1200.jpg" srcset="img/{hero['file']}-600.jpg 600w, img/{hero['file']}-1200.jpg 1200w" sizes="(max-width: 860px) 100vw, 42vw" alt="{e(hero['alt'])}"><figcaption class="m">{cap(hero)}</figcaption></figure>
</section>

<section id="about" class="sec">
  <h2 class="m"><span>01</span>About</h2>
  <div class="body">
    {paras}
    <div class="stores"><p class="m">{e(a['stores_intro'])}</p><ul>{stores}</ul></div>
  </div>
</section>

<section id="sets" class="sec">
  <h2 class="m"><span>02</span>Sets</h2>
  <div class="body">
    <p class="lede m">{len(gigs)} dated sets, numbered in the order played, plus the Thursday residency. Most link to where they were posted.</p>
    {residency()}
    {dates_section(gigs)}
  </div>
</section>

<section id="photos" class="sec">
  <h2 class="m"><span>03</span>Photos</h2>
  <div class="body grid">{photos}</div>
</section>

<section id="links" class="sec">
  <h2 class="m"><span>04</span>Links</h2>
  <div class="body"><ul class="lk">{links}</ul></div>
</section>
</main>
<footer class="m">
  <span>© Carlo De Marchis</span>
  <a href="https://carlodemarchis.it/">carlodemarchis.it</a>
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
    print(f"built docs/index.html: {len(DATA['gigs'])} sets, {len(DATA['photos'])} photos")


if __name__ == "__main__":
    main()
