# Selectazzz

Site for Carlo De Marchis's vinyl selector sets (Carlo's Turntables), served at
https://selectazzz.carlodemarchis.it (GitHub Pages from `docs/`).

## Add a date

Edit `gigs` in `data.json` (`date` is `YYYY-MM-DD`, or `YYYY-MM` / `YYYY` when the day is not known;
`src` is `medium` or `ig:<shortcode>` and becomes the row's link), then:

```bash
python3 build.py      # docs/index.html, copies site.css, favicon.svg, og.jpg, img/
```

Commit and push; Pages serves `docs/`. On CSS changes bump `css_version` in `site.json`.

## Sources

Everything on the page comes from two of Carlo's own pages (details in `research/SOURCES.md`):
- Medium, "Carlo's Turntables" (cdm.medium.com/carlos-turntable-playlists-2826ab98480c): the text,
  the dated list Oct 2022 to Oct 2024, and the photos in `img/`.
- Instagram @carlosturntables: Affini 7 Feb 2024, Banco Vini (posted 2 Apr 2025), and the Ddoce Casa
  release party at Tono Metzger, 12 Mar 2026 (announced in the post).

Carlo chose to leave out the Spotify set playlists and the booking email (2026-11-23).
The 2023 "Private open-air party" has no month on Medium, so it shows "—".

Design: palette from the Carlo's Turntables logo (navy, red, green, orange/yellow, blue/cyan), the
"Selectazzz" wordmark is three offset layers of Unbounded 900 (Google Fonts), text in Helvetica Neue.
`og.jpg` is a 1200x630 headless-Chrome screenshot of the hero.
