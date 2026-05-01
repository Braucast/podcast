# Braukast Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal dark single-page website for Braukast that lists all podcast episodes, driven by a GitHub Action that fetches the RSS feed and writes `episodes.json`.

**Architecture:** `index.html` fetches `episodes.json` at page load and renders the episode list with vanilla JS. A manually-triggered GitHub Action runs `scripts/fetch_episodes.py`, which parses the Anchor RSS feed (stdlib only) and writes `episodes.json`. GitHub Pages serves both files directly from `main` — no build step.

**Tech Stack:** HTML/CSS/JS (vanilla, no frameworks), Python 3 stdlib, GitHub Actions

---

## File Map

| File | Responsibility |
|------|----------------|
| `scripts/fetch_episodes.py` | Fetch RSS, parse XML, write `episodes.json` |
| `scripts/test_fetch_episodes.py` | Unit tests for parser functions |
| `.github/workflows/fetch-episodes.yml` | Manual-trigger GitHub Action |
| `episodes.json` | Episode data (generated); consumed by `index.html` |
| `index.html` | Single-page site — loads and renders `episodes.json` |
| `CNAME` | Custom domain `braukast.de` for GitHub Pages |
| `assets/logo.png` | Logo image (user drops in; `index.html` hides it gracefully if missing) |

---

### Task 1: Scaffold structure

**Files:**
- Create: `scripts/` directory
- Create: `.github/workflows/` directory
- Create: `assets/` directory
- Create: `episodes.json`
- Create: `CNAME`

- [ ] **Step 1: Create directories**

```bash
mkdir -p scripts .github/workflows assets
```

- [ ] **Step 2: Create seed `episodes.json`**

Create `episodes.json` with this content:

```json
{
  "description": "",
  "episodes": []
}
```

- [ ] **Step 3: Create `CNAME`**

Create `CNAME` with this content:

```
braukast.de
```

- [ ] **Step 4: Commit**

```bash
git add episodes.json CNAME
git commit -m "chore: scaffold site structure"
```

---

### Task 2: Write failing tests for the RSS parser

**Files:**
- Create: `scripts/test_fetch_episodes.py`

- [ ] **Step 1: Create `scripts/test_fetch_episodes.py`**

```python
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fetch_episodes import parse_duration, parse_date, spotify_url_from_uri, parse_feed

SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
  xmlns:spotify="http://www.spotify.com/ns/rss">
  <channel>
    <title>Braukast</title>
    <description>Der Podcast über Bier und Brauen</description>
    <item>
      <title>Folge 1 — Der Anfang</title>
      <pubDate>Thu, 01 Jan 2024 10:00:00 +0000</pubDate>
      <itunes:duration>45:30</itunes:duration>
      <itunes:episode>1</itunes:episode>
      <spotify:episodeUri>spotify:episode:abc123</spotify:episodeUri>
      <link>https://anchor.fm/braukast/episodes/folge-1</link>
    </item>
    <item>
      <title>Folge 2 — Hopfen</title>
      <pubDate>Thu, 15 Feb 2024 10:00:00 +0000</pubDate>
      <itunes:duration>1:12:05</itunes:duration>
      <itunes:episode>2</itunes:episode>
      <link>https://anchor.fm/braukast/episodes/folge-2</link>
    </item>
  </channel>
</rss>"""


class TestParseDuration(unittest.TestCase):
    def test_minutes_seconds(self):
        self.assertEqual(parse_duration('45:30'), '45 min')

    def test_hours_minutes_seconds(self):
        self.assertEqual(parse_duration('1:12:05'), '1h 12 min')

    def test_pure_seconds(self):
        self.assertEqual(parse_duration('3600'), '1h 0 min')

    def test_zero_hours(self):
        self.assertEqual(parse_duration('0:30:00'), '30 min')

    def test_none_input(self):
        self.assertIsNone(parse_duration(None))

    def test_empty_string(self):
        self.assertIsNone(parse_duration(''))


class TestParseDate(unittest.TestCase):
    def test_rfc2822_with_offset(self):
        self.assertEqual(parse_date('Thu, 01 Jan 2024 10:00:00 +0000'), '2024-01-01')

    def test_rfc2822_with_gmt(self):
        self.assertEqual(parse_date('Thu, 15 Feb 2024 10:00:00 GMT'), '2024-02-15')


class TestSpotifyUrlFromUri(unittest.TestCase):
    def test_converts_episode_uri(self):
        self.assertEqual(
            spotify_url_from_uri('spotify:episode:abc123'),
            'https://open.spotify.com/episode/abc123'
        )

    def test_none_returns_none(self):
        self.assertIsNone(spotify_url_from_uri(None))

    def test_non_episode_uri_returns_none(self):
        self.assertIsNone(spotify_url_from_uri('spotify:show:abc'))


class TestParseFeed(unittest.TestCase):
    def setUp(self):
        self.data = parse_feed(SAMPLE_RSS)

    def test_description_extracted(self):
        self.assertEqual(self.data['description'], 'Der Podcast über Bier und Brauen')

    def test_episode_count(self):
        self.assertEqual(len(self.data['episodes']), 2)

    def test_episodes_sorted_newest_first(self):
        self.assertEqual(self.data['episodes'][0]['number'], 2)
        self.assertEqual(self.data['episodes'][1]['number'], 1)

    def test_spotify_url_extracted_from_uri(self):
        ep1 = next(e for e in self.data['episodes'] if e['number'] == 1)
        self.assertEqual(ep1['url'], 'https://open.spotify.com/episode/abc123')

    def test_fallback_to_link_when_no_spotify_uri(self):
        ep2 = next(e for e in self.data['episodes'] if e['number'] == 2)
        self.assertEqual(ep2['url'], 'https://anchor.fm/braukast/episodes/folge-2')

    def test_duration_formatted(self):
        ep1 = next(e for e in self.data['episodes'] if e['number'] == 1)
        self.assertEqual(ep1['duration'], '45 min')

    def test_date_formatted_as_iso(self):
        ep1 = next(e for e in self.data['episodes'] if e['number'] == 1)
        self.assertEqual(ep1['date'], '2024-01-01')

    def test_episode_number_from_itunes_tag(self):
        ep2 = next(e for e in self.data['episodes'] if e['number'] == 2)
        self.assertEqual(ep2['number'], 2)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests — expect failure (module not found)**

```bash
cd scripts && python -m unittest test_fetch_episodes -v
```

Expected output: `ModuleNotFoundError: No module named 'fetch_episodes'`

- [ ] **Step 3: Commit the failing tests**

```bash
git add scripts/test_fetch_episodes.py
git commit -m "test: add RSS parser tests (red)"
```

---

### Task 3: Implement the RSS parser

**Files:**
- Create: `scripts/fetch_episodes.py`

- [ ] **Step 1: Create `scripts/fetch_episodes.py`**

```python
#!/usr/bin/env python3
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

RSS_URL = "https://anchor.fm/s/10038620/podcast/rss"
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'episodes.json')

ITUNES = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
SPOTIFY_NS = 'http://www.spotify.com/ns/rss'


def parse_duration(s):
    if not s:
        return None
    parts = s.strip().split(':')
    try:
        if len(parts) == 3:
            h, m = int(parts[0]), int(parts[1])
        elif len(parts) == 2:
            h, m = 0, int(parts[0])
        else:
            total = int(s)
            h, m = total // 3600, (total % 3600) // 60
    except ValueError:
        return None
    return f"{h}h {m} min" if h else f"{m} min"


def parse_date(s):
    for fmt in ('%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S GMT'):
        try:
            return datetime.strptime(s.strip(), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return s[:10] if s else None


def spotify_url_from_uri(uri):
    if uri and uri.startswith('spotify:episode:'):
        return 'https://open.spotify.com/episode/' + uri.split(':')[-1]
    return None


def parse_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    channel = root.find('channel')
    description = (channel.findtext('description') or '').strip()

    items = channel.findall('item')
    episodes = []
    for i, item in enumerate(reversed(items)):  # oldest first → number starts at 1
        title = (item.findtext('title') or '').strip()
        date = parse_date(item.findtext('pubDate') or '')
        duration = parse_duration(item.findtext(f'{{{ITUNES}}}duration'))
        ep_tag = item.findtext(f'{{{ITUNES}}}episode')
        number = int(ep_tag) if ep_tag and ep_tag.isdigit() else i + 1
        spotify_uri = item.findtext(f'{{{SPOTIFY_NS}}}episodeUri')
        url = spotify_url_from_uri(spotify_uri) or item.findtext('link') or ''
        episodes.append({
            'number': number,
            'title': title,
            'date': date,
            'duration': duration,
            'url': url,
        })

    episodes.sort(key=lambda e: e['number'], reverse=True)
    return {'description': description, 'episodes': episodes}


def main():
    print(f"Fetching {RSS_URL} ...")
    with urllib.request.urlopen(RSS_URL, timeout=30) as resp:
        xml_bytes = resp.read()
    data = parse_feed(xml_bytes)
    print(f"Found {len(data['episodes'])} episodes.")
    out = os.path.abspath(OUTPUT)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written to {out}")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run tests — expect all pass**

```bash
cd scripts && python -m unittest test_fetch_episodes -v
```

Expected: `OK` with all tests passing.

- [ ] **Step 3: Commit**

```bash
git add scripts/fetch_episodes.py
git commit -m "feat: implement RSS parser and episode fetch script"
```

---

### Task 4: GitHub Action

**Files:**
- Create: `.github/workflows/fetch-episodes.yml`

- [ ] **Step 1: Create `.github/workflows/fetch-episodes.yml`**

```yaml
name: Fetch Episodes

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Fetch episodes from RSS
        run: python scripts/fetch_episodes.py

      - name: Commit episodes.json if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add episodes.json
          if git diff --staged --quiet; then
            echo "No changes to episodes.json"
          else
            git commit -m "chore: update episodes.json"
            git push
          fi
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/fetch-episodes.yml
git commit -m "ci: add manual episode fetch workflow"
```

---

### Task 5: Generate real episodes.json locally

- [ ] **Step 1: Run script from repo root**

```bash
python scripts/fetch_episodes.py
```

Expected output:
```
Fetching https://anchor.fm/s/10038620/podcast/rss ...
Found N episodes.
Written to /path/to/podcast/episodes.json
```

- [ ] **Step 2: Verify the JSON**

```bash
python -c "
import json
d = json.load(open('episodes.json'))
print('Description:', d['description'][:60])
print('Episodes:', len(d['episodes']))
print('First:', d['episodes'][0])
"
```

Expected: episode count > 0, each entry has `number`, `title`, `date`, `duration`, `url`.

- [ ] **Step 3: Commit**

```bash
git add episodes.json
git commit -m "chore: seed episodes.json from live RSS feed"
```

---

### Task 6: Create index.html

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create `index.html`**

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Braukast</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #0f0f0f;
      color: #e8e8e8;
      font-family: -apple-system, 'Segoe UI', sans-serif;
      min-height: 100vh;
    }
    a { color: inherit; text-decoration: none; }

    /* ── Header ── */
    header {
      padding: 32px 40px 24px;
      border-bottom: 1px solid #1a1a1a;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }
    .brand { display: flex; align-items: center; gap: 14px; }
    .logo { width: 44px; height: 44px; border-radius: 8px; }
    .brand-text h1 { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
    .brand-text p  { color: #4ade80; font-size: 11px; margin-top: 2px; opacity: 0.8; }

    /* ── Platform badges ── */
    .platforms { display: flex; gap: 8px; flex-wrap: wrap; }
    .badge {
      font-size: 10px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 20px;
    }
    .badge-spotify  { background: #1DB954; color: #fff; }
    .badge-secondary { background: #1a1a1a; color: #aaa; border: 1px solid #2a2a2a; }

    /* ── Episode list ── */
    main { padding: 24px 40px; }
    .section-label {
      color: #2d2d2d;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      margin-bottom: 16px;
    }
    .episode {
      display: flex;
      align-items: baseline;
      gap: 16px;
      padding: 14px 0;
      border-bottom: 1px solid #161616;
    }
    .ep-num   { color: #4ade80; font-size: 12px; font-weight: 700; min-width: 28px; opacity: 0.9; flex-shrink: 0; }
    .ep-info  { flex: 1; min-width: 0; }
    .ep-title { font-size: 13px; font-weight: 500; }
    .ep-meta  { color: #3a3a3a; font-size: 11px; margin-top: 3px; }
    .ep-link  { color: #4ade80; font-size: 10px; opacity: 0.7; white-space: nowrap; flex-shrink: 0; }
    .ep-link:hover { opacity: 1; }

    /* ── Footer ── */
    footer { padding: 16px 40px; border-top: 1px solid #161616; }
    footer p { color: #2a2a2a; font-size: 10px; }

    /* ── States ── */
    .state-msg { color: #3a3a3a; font-size: 12px; padding: 40px 0; }
    .state-msg.error { color: #ef4444; }

    /* ── Mobile ── */
    @media (max-width: 600px) {
      header, main, footer { padding-left: 20px; padding-right: 20px; }
      header { flex-direction: column; align-items: flex-start; }
    }
  </style>
</head>
<body>

<header>
  <div class="brand">
    <img class="logo" src="assets/logo.png" alt="Braukast"
         onerror="this.style.display='none'">
    <div class="brand-text">
      <h1>Braukast</h1>
      <p id="tagline"></p>
    </div>
  </div>
  <nav class="platforms">
    <a class="badge badge-spotify"
       href="https://open.spotify.com/show/1i8txBkDNEeDaKPsgbxToD"
       target="_blank" rel="noopener">▶ Spotify</a>
    <a class="badge badge-secondary"
       href="https://anchor.fm/s/10038620/podcast/rss"
       target="_blank" rel="noopener">RSS</a>
  </nav>
</header>

<main>
  <div class="section-label">ALLE FOLGEN</div>
  <div id="episodes">
    <p class="state-msg">Lädt…</p>
  </div>
</main>

<footer>
  <p>© <span id="year"></span> Braukast</p>
</footer>

<script>
  const MONTHS = [
    'Januar','Februar','März','April','Mai','Juni',
    'Juli','August','September','Oktober','November','Dezember'
  ];

  function formatDate(iso) {
    const [y, m, d] = iso.split('-').map(Number);
    return `${d}. ${MONTHS[m - 1]} ${y}`;
  }

  function renderEpisode(ep) {
    const row = document.createElement('div');
    row.className = 'episode';

    const num = document.createElement('span');
    num.className = 'ep-num';
    num.textContent = `#${ep.number}`;

    const info = document.createElement('div');
    info.className = 'ep-info';

    const title = document.createElement('div');
    title.className = 'ep-title';
    title.textContent = ep.title;

    const meta = document.createElement('div');
    meta.className = 'ep-meta';
    meta.textContent = formatDate(ep.date) + (ep.duration ? ' · ' + ep.duration : '');

    info.appendChild(title);
    info.appendChild(meta);

    const link = document.createElement('a');
    link.className = 'ep-link';
    link.href = ep.url;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = 'Anhören ↗';

    row.appendChild(num);
    row.appendChild(info);
    row.appendChild(link);
    return row;
  }

  document.getElementById('year').textContent = new Date().getFullYear();

  fetch('episodes.json')
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => {
      const tagline = document.getElementById('tagline');
      if (data.description) tagline.textContent = data.description;

      const container = document.getElementById('episodes');
      container.innerHTML = '';
      if (!data.episodes.length) {
        container.innerHTML = '<p class="state-msg">Noch keine Folgen.</p>';
        return;
      }
      data.episodes.forEach(ep => container.appendChild(renderEpisode(ep)));
    })
    .catch(() => {
      document.getElementById('episodes').innerHTML =
        '<p class="state-msg error">Episoden konnten nicht geladen werden.</p>';
    });
</script>

</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat: add single-page podcast site"
```

---

### Task 7: Test locally

- [ ] **Step 1: Start a local HTTP server from repo root**

```bash
python -m http.server 8000
```

- [ ] **Step 2: Open http://localhost:8000 in your browser**

Verify:
- Episodes list loads and renders correctly (titles, dates, durations, "Anhören ↗" links)
- Tagline appears in green under the logo
- "Anhören ↗" links open in a new tab pointing to Spotify

- [ ] **Step 3: Verify mobile layout**

Narrow the browser to ~375px. Verify:
- Header stack: brand on top, badges below
- Episode rows don't overflow horizontally

- [ ] **Step 4: Stop the server**

Press `Ctrl+C` in the terminal running the server.

---

### Task 8: Push to GitHub and enable Pages

- [ ] **Step 1: Push all commits to GitHub**

```bash
git push -u origin main
```

- [ ] **Step 2: Enable GitHub Pages in the repo settings**

In the GitHub UI:
1. Go to `https://github.com/Braucast/podcast` → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)`
4. Click **Save**

GitHub will show the Pages URL (e.g. `https://braucast.github.io/podcast/`) while the custom domain propagates.

- [ ] **Step 3: Add DNS records for braukast.de**

At your DNS provider, add:
```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
CNAME www  braucast.github.io.
```

- [ ] **Step 4: Set custom domain in GitHub Pages settings**

In **Settings → Pages → Custom domain**, enter `braukast.de` and click Save. Enable "Enforce HTTPS" once the cert is issued (can take up to 24h).

- [ ] **Step 5: Trigger the GitHub Action for the first time**

In the GitHub UI: **Actions → Fetch Episodes → Run workflow → Run workflow**

Verify the action completes successfully and `episodes.json` is committed.

---

### Task 9: Add logo

- [ ] **Step 1: Drop your logo file into `assets/logo.png`**

Any format works if you rename it to `logo.png`. Recommended: square, at least 88×88px.

- [ ] **Step 2: Commit and push**

```bash
git add assets/logo.png
git commit -m "feat: add podcast logo"
git push
```
