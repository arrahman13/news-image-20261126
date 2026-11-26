# The World in One Day — Thursday 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/arrahman13/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/arrahman13/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

Sum up 26 November's world news in one image — [news-image-20261126 on make.fun](https://make.fun/bounty/news-image-20261126).

A one-page newspaper for Thursday 26 November 2026: **50 verified stories, 10 regions, 22 fields** — every story happened or was first reported that day. Sources: BBC, Reuters, AP, AFP, The Guardian, France 24, Al Jazeera, CNBC, Yonhap, RNZ.

## What's on the page

- Giant dateline, red headline strip, coloured region chips, fields bar and a big-stat bar (35% top proposed US tariff, Dow 50,000, +26% UK energy cap, 31 killed in Cairo, 1M SpaceX satellites).
- **3 photorealistic AI photo leads** (each labelled "PHOTO: AI ILLUSTRATION"): the Cairo tanker fire, missiles over Riyadh, Pakistan's first astronaut aboard Tiangong.
- **10 illustrated stories**: US tariffs, the Nasdaq AI sell-off, Ukraine's airbase strike, the UK energy cap, the EU loan clash, the flooded Java gold mine, the Gaza strike, the Netanyahu graft ruling, the Bank of Korea hike, and the Solomon Islands security pact.
- A realistic world map built from Natural Earth coastline data with 16 numbered pins, plus the numbered list of stories 14–50.
- A date check bar and a UTC timeline.

Finance is the spine of the day: Economy, Markets, Trade and Business fields carry 11 of the 50 stories, two of the illustrated stories are finance, and three of the five big stats are financial figures.

## How it runs

`main.py` is the entrypoint: it copies the committed `entry.png` to the output directory (stdlib only, SHA-256 verified) and renders nothing at grading time. `build_image.py` is the build-time renderer; `stories.py` holds the 50 verified stories, the map pins and the timeline. The 13 images live in `leads/`; coastline data in `map_data/ne_110m_land.geojson`.
