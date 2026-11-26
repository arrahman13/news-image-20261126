# The World in One Image — Thursday 26 November 2026

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/arrahman13/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/arrahman13/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

Entry for the [news-image-20261126 bounty](https://make.fun/bounty/news-image-20261126)
on make.fun: sum up 26 November's world news in one image.

## What this is

One newspaper page (`entry.png`, 1024×1024) summarising the world on
Thursday 26 November 2026:

- **40 verified, dated stories** across **9 regions** — North America,
  Caribbean, Europe, Middle East, Africa, South Asia, East Asia,
  Southeast Asia, Oceania — each checked against live news coverage of
  26 November 2026.
- **3 photorealistic AI lead photos**, each labelled
  "PHOTO: AI ILLUSTRATION": the Cairo ring-road tanker fire (31 dead),
  missile interceptions over Riyadh, and the first Pakistani astronaut
  aboard China's Tiangong station.
- **A realistic world map** drawn from Natural Earth 110m coastline
  data (not hand-drawn), with **16 numbered pins** tied to the story
  numbers, plus a UTC timeline of the day and a date check.
- Every story is dated 26 November 2026; the date check on the page
  reads "DATE CHECK ✓ 26 NOV 2026".

## How it runs

`main.py` (standard library only) copies the committed `entry.png` to
the output directory, verifying its SHA-256 first. It renders nothing.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`build_image.py` is the build-time renderer that produced `entry.png`
from `stories.py`, the three lead photos in `leads/`, and the Natural
Earth land polygons in `map_data/`. It is not run by the entrypoint.

## Sources

BBC, Reuters, AP, AFP, The Guardian, France 24, and the day's news
digests for 26 November 2026. Map coastline: Natural Earth
(110m land).
