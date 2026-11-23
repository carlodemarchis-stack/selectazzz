#!/usr/bin/env python3
"""Build the Selectazzz site into docs/ from data.json + site.json. Stdlib only.

One page laid out like a record sleeve: hero, about, the dates as a numbered
tracklist (residency first), photos, links.
"""
import json, pathlib, shutil, sys
from html import escape as e

ROOT = pathlib.Path(__file__).resolve().parent
# Each theme = site.css (shared layout) + themes/<name>.css (type, colour, hero treatment).
THEMES = {
    "paper": "IBM+Plex+Mono:wght@400;500",
    "kissa": "Fraunces:ital,opsz,wght@1,9..144,500;1,9..144,700&family=IBM+Plex+Mono:wght@400;500",
    "sleeve": "Anton&family=IBM+Plex+Mono:wght@400;500",
    "label": "Space+Mono:ital,wght@0,400;0,700;1,400",
    # tono: after the Tono Metzger flyers. Their display face is UT Modino Display (Uppercap Type,
    # commercial): the theme uses fonts/display.otf when a licensed copy is there, Righteous otherwise.
    "tono": "Righteous&family=IBM+Plex+Mono:wght@400;500",
}
DISC = """<svg class="disc" viewBox="0 0 200 200" aria-hidden="true">
  <circle cx="100" cy="100" r="99" fill="#0b0b0b"/>
  <g fill="none" stroke="#262626" stroke-width=".6">{grooves}</g>
  <circle cx="100" cy="100" r="38" class="lbl"/>
  <defs><path id="ring" d="M100,100 m-29,0 a29,29 0 1,1 58,0 a29,29 0 1,1 -58,0"/></defs>
  <text class="lt"><textPath href="#ring">SELECTAZZZ · CARLO DE MARCHIS · TORINO · SIDE A ·</textPath></text>
  <text x="100" y="122" class="lc" text-anchor="middle">33⅓</text>
  <circle cx="100" cy="100" r="2.6" fill="#0b0b0b"/>
</svg>""".replace("{grooves}", "".join(f'<circle cx="100" cy="100" r="{r}"/>' for r in range(44, 98, 3)))
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
// Dates Carlo has confirmed (residency.confirmed) are shown as "Next", the rest as "Next, usually".
(function () {{
  const confirmed = {json.dumps(r.get("confirmed", []))};
  const d = new Date(); d.setHours(0, 0, 0, 0);
  for (let i = 0; i < 21; i++, d.setDate(d.getDate() + 1)) {{
    if (d.getDay() === 4 && d.getDate() > 7) {{
      const iso = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      const el = document.getElementById('next');
      el.textContent = (confirmed.includes(iso) ? 'Next: ' : 'Next, usually: ') +
        d.toLocaleDateString('en-GB', {{weekday: 'short', day: 'numeric', month: 'short'}});
      el.hidden = false; return;
    }}
  }}
}})();
</script>"""


def page(theme):
    a, gigs = DATA["about"], DATA["gigs"]
    n_venues = len({g["venue"] for g in gigs if not g["venue"].lower().startswith("private")})
    first = min(g["date"][:4] for g in gigs)
    # residency.thursdays counts all regular Tono Thursdays (Carlo's figure); the ones with a
    # known date are already in gigs (flagged "residency"), so only the rest are added.
    n_res = max(DATA.get("residency", {}).get("thursdays", 0) - sum(1 for g in gigs if g.get("residency")), 0)
    n_sets = len(gigs) + n_res
    hero = DATA["photos"][0]
    rc = json.loads((ROOT / "records.json").read_text())
    rc_count, rc_date = rc["count"], rc["fetched"]
    fz = DATA.get("fanzine")
    fanzine = "" if not fz else "".join(
        f'<li><a class="r" href="{e(i["url"])}" target="_blank" rel="noopener"><span class="dt m">{i["date"][8:]}.{i["date"][5:7]}.{i["date"][2:4]}</span>'
        f'<span class="vn">{e(i["title"])}</span></a></li>' for i in fz["issues"])
    photos = "".join(f"""<figure{' class="contain"' if p.get('fit') == 'contain' else ''}>
  <img src="img/{p['file']}-1200.jpg" srcset="img/{p['file']}-600.jpg 600w, img/{p['file']}-1200.jpg 1200w" sizes="(max-width: 700px) 100vw, 33vw" alt="{e(p['alt'])}" loading="lazy">
  <figcaption class="m">{cap(p)}</figcaption>
</figure>""" for p in DATA["photos"][1:])
    links = "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener"><span class="m">{e(l["label"])}</span>'
                    f'<span>{e(l["handle"])}</span><span class="ar">↗</span></a></li>' for l in DATA["links"])
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    stores = "".join(f"<li>{e(s)}</li>" for s in a["stores"])
    title = "Selectazzz · Carlo De Marchis"
    desc = f"Selectazzz: Carlo De Marchis's selector sets, mostly vinyl, now hybrid. {n_sets} sets since {first}."
    url = f"https://{SITE['host']}/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1b1613">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={THEMES[theme]}&display=swap">
<link rel="stylesheet" href="site.css?v={SITE['css_version']}">
<link rel="stylesheet" href="themes/{theme}.css?v={SITE['css_version']}">
{umami()}
</head>
<body class="t-{theme}">
<header class="bar">
  <a class="logo" href="./">selectazzz</a>
  <nav class="m"><a href="#about">About</a><a href="#sets">Sets</a><a href="#records">Records</a><a href="#photos">Photos</a><a href="#links">Links</a></nav>
</header>
<main>
<section class="hero">
  <div class="ht">
    <p class="m kick">Carlo De Marchis · Selector · Torino</p>
    <h1>selectazzz</h1>
    <p class="con">with Carlo De Marchis</p>
    <p class="tag">{e(a['tagline'])}</p>
    <dl class="stats m">
      <div><dt>Sets</dt><dd>{n_sets}</dd></div>
      <div><dt>Venues</dt><dd>{n_venues}</dd></div>
      <div><dt>Records</dt><dd>2,000+</dd></div>
      <div><dt>Since</dt><dd>{first}</dd></div>
    </dl>
  </div>
  {DISC}
  <p class="stamp" aria-hidden="true">Mostly vinyl</p>
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
    <p class="lede m">{n_sets} sets: {len(gigs)} dated ones, numbered in the order played, plus about {n_res} more Thursdays of the residency. Most link to where they were posted.</p>
    {residency()}
    {dates_section(gigs)}
  </div>
</section>

<section id="records" class="sec">
  <h2 class="m"><span>03</span>Records</h2>
  <div class="body wide">
    <p class="lede m">A selection of his records: the {rc_count:,} catalogued on Discogs ({rc_date}), the same list behind the daily record on @carlosturntables. Each one opens its Discogs page.</p>
    <div class="rc-tools">
      <input type="search" id="rc-q" placeholder="Search artist, title, label" aria-label="Search the records">
      <select id="rc-sort" aria-label="Sort the records">
        <option value="added">Recently added</option><option value="artist">Artist A–Z</option>
        <option value="new">Year, newest</option><option value="old">Year, oldest</option>
      </select>
    </div>
    <div class="rc-chips m" id="rc-chips"></div>
    <p class="m rc-n" id="rc-n"></p>
    <ul class="rc-grid" id="rc-grid"></ul>
    <button type="button" class="rc-more m" id="rc-more" hidden>Show more</button>
  </div>
</section>
<script>
// Records: loaded from records.json (tools/fetch_discogs.py), drawn 60 at a time.
(function () {{
  const STEP = 60, grid = document.getElementById('rc-grid'), more = document.getElementById('rc-more'),
        q = document.getElementById('rc-q'), sort = document.getElementById('rc-sort'),
        chips = document.getElementById('rc-chips'), n = document.getElementById('rc-n');
  let all = [], list = [], shown = 0, genre = '';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}})[c]);
  function draw(reset) {{
    if (reset) {{ grid.innerHTML = ''; shown = 0; }}
    const html = list.slice(shown, shown + STEP).map(r =>
      `<li><a href="https://www.discogs.com/release/${{r.id}}" target="_blank" rel="noopener">` +
      (r.thumb ? `<img src="${{esc(r.thumb)}}" alt="" loading="lazy" width="150" height="150">` : '<span class="nocover"></span>') +
      `<span class="ra">${{esc(r.artist)}}</span><span class="rt">${{esc(r.title)}}</span>` +
      `<span class="ry m">${{r.year || ''}}${{r.year && r.label ? ' · ' : ''}}${{esc(r.label)}}</span></a></li>`).join('');
    grid.insertAdjacentHTML('beforeend', html);
    shown = Math.min(shown + STEP, list.length);
    more.hidden = shown >= list.length;
    n.textContent = list.length === all.length ? `${{all.length.toLocaleString('en')}} records` :
      `${{list.length.toLocaleString('en')}} of ${{all.length.toLocaleString('en')}} records`;
  }}
  function apply() {{
    const t = q.value.trim().toLowerCase();
    list = all.filter(r => (!genre || r.genres.includes(genre)) &&
      (!t || (r.artist + ' ' + r.title + ' ' + r.label + ' ' + r.styles.join(' ')).toLowerCase().includes(t)));
    const s = sort.value;
    if (s === 'artist') list.sort((a, b) => a.artist.localeCompare(b.artist));
    else if (s === 'new') list.sort((a, b) => (b.year || 0) - (a.year || 0));
    else if (s === 'old') list.sort((a, b) => (a.year || 9999) - (b.year || 9999));
    draw(true);
  }}
  fetch('records.json').then(r => r.json()).then(d => {{
    all = d.records; list = all.slice();
    const g = {{}}; all.forEach(r => r.genres.forEach(x => g[x] = (g[x] || 0) + 1));
    chips.innerHTML = '<button type="button" class="on" data-g="">All</button>' +
      Object.entries(g).sort((a, b) => b[1] - a[1]).slice(0, 8)
        .map(([k, v]) => `<button type="button" data-g="${{esc(k)}}">${{esc(k)}} <i>${{v}}</i></button>`).join('');
    chips.addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      chips.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
      genre = b.dataset.g; apply();
    }});
    q.addEventListener('input', apply); sort.addEventListener('change', apply);
    more.addEventListener('click', () => draw(false));
    draw(true);
  }});
}})();
</script>

<section id="photos" class="sec">
  <h2 class="m"><span>04</span>Photos</h2>
  <div class="body grid">{photos}</div>
</section>

<section id="fanzine" class="sec">
  <h2 class="m"><span>05</span>Fanzine</h2>
  <div class="body">
    <p>{e(fz['intro']) if fz else ''} <a href="{e(fz['url']) if fz else ''}" target="_blank" rel="noopener">{e(fz['name']) if fz else ''} ↗</a></p>
    <ol class="fz year">{fanzine}</ol>
  </div>
</section>

<section id="links" class="sec">
  <h2 class="m"><span>06</span>Links</h2>
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


def build(out, theme):
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(theme))
    for f in ("site.css", "favicon.svg", "og.jpg", "records.json"):
        shutil.copy(ROOT / f, out / f)
    shutil.copytree(ROOT / "themes", out / "themes", dirs_exist_ok=True)
    shutil.copytree(ROOT / "img", out / "img", dirs_exist_ok=True)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":  # every theme into <dir>/<theme>/
        for t in THEMES:
            build(pathlib.Path(sys.argv[2]) / t, t)
        print("preview:", ", ".join(THEMES))
        return
    build(DOCS, SITE["theme"])
    (DOCS / "CNAME").write_text(SITE["host"] + "\n")
    print(f"built docs/index.html ({SITE['theme']}): {len(DATA['gigs'])} sets, {len(DATA['photos'])} photos")

if __name__ == "__main__":
    main()
