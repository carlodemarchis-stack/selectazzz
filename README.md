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

Instagram photos come from Carlo's archive through the Graph API tokens in
`linkedin_instagram_automation/.env` (`_TURNTABLES`, `_CARLO`), read-only; Carlo picked them from a
contact sheet on 2026-11-23. Each caption links to its post. The download lives in `research/ig/` (not in git).
Told by Carlo, 2026-11-23 (`src: carlo`, no link): Tono Metzger residency since January 2026, every
Thursday except the first of the month on average; Casa delle Lampadine end-of-summer party in
September 2024, 2025 and 2026.

Carlo chose to leave out the Spotify set playlists and the booking email (2026-11-23).
The 2023 "Private open-air party" has no month on Medium, so it shows "—".

Copy: Carlo, 2026-11-23: "mostly vinyl", now also hybrid with digital versions of his own tracks
(NEOM Records) and new music. He asked to leave out the old Carlo's Turntables logo.

Design (second pass, Carlo asked for "cool and understated"): the back of a record sleeve. Paper
#ecebe6, black ink, one rust accent on hover; "selectazzz" in lowercase Helvetica Neue Bold with
tight tracking; IBM Plex Mono (Google Fonts) for credits, numbers and dates; sets numbered like a
catalogue in the order played. Hero photo in black and white.
`og.jpg` comes from `python3 tools/make_og.py` (Pillow, system Helvetica Neue + Menlo).
