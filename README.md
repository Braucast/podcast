# Braukast

Ein Hobbybrau-Podcast — wir reden über Bier, Brauen und alles was dazugehört.

🎙️ [braukast.de](https://braukast.de) · [Spotify](https://open.spotify.com/show/1i8txBkDNEeDaKPsgbxToD) · [RSS](https://anchor.fm/s/10038620/podcast/rss)

---

## Folgen

| # | Titel | Datum | Dauer |
|---|-------|-------|-------|
| 12 | [BC012 - CO₂](https://podcasters.spotify.com/pod/show/braucast/episodes/BC012---CO-e3i1qnj) | 17.04.2026 | 1h 40 min |
| 11 | [BC011 - Reinigung](https://podcasters.spotify.com/pod/show/braucast/episodes/BC011---Reinigung-e2ep9l1) | 22.01.2024 | 1h 28 min |
| 10 | [BC010 - Bier & Brot](https://podcasters.spotify.com/pod/show/braucast/episodes/BC010---Bier--Brot-e1ioav5) | 19.05.2022 | 1h 32 min |
| 9 | [BC009 - Rohfrucht](https://podcasters.spotify.com/pod/show/braucast/episodes/BC009---Rohfrucht-e1879dm) | 03.10.2021 | 1h 33 min |
| 8 | [BC008 - Von Labels und Etikettiermaschinen](https://podcasters.spotify.com/pod/show/braucast/episodes/BC008---Von-Labels-und-Etikettiermaschinen-eoligh) | 07.01.2021 | 1h 30 min |
| 7 | [BC007 - Bier Etiketten](https://podcasters.spotify.com/pod/show/braucast/episodes/BC007---Bier-Etiketten-ekqdna) | 09.10.2020 | 1h 29 min |
| 6 | [BC006 - How to serve a craft](https://podcasters.spotify.com/pod/show/braucast/episodes/BC006---How-to-serve-a-craft-ed1k4n) | 21.04.2020 | 1h 22 min |
| 5 | [BC005 – Berliner Weisse](https://podcasters.spotify.com/pod/show/braucast/episodes/BC005--Berliner-Weisse-e8g9o5) | 14.10.2019 | 2h 28 min |
| 4 | [BC004 – Grisette](https://podcasters.spotify.com/pod/show/braucast/episodes/BC004--Grisette-e8g9o4) | 22.11.2018 | 47 min |
| 3 | [BC003 – Maischen](https://podcasters.spotify.com/pod/show/braucast/episodes/BC003--Maischen-e8g9o7) | 15.10.2018 | 1h 54 min |
| 2 | [BC002 – Dry Hopping](https://podcasters.spotify.com/pod/show/braucast/episodes/BC002--Dry-Hopping-e8g9o6) | 05.04.2018 | 1h 29 min |
| 1 | [BC001 – Die Gose im Laufe der Zeit](https://podcasters.spotify.com/pod/show/braucast/episodes/BC001--Die-Gose-im-Laufe-der-Zeit-e8g9o8) | 25.10.2017 | 1h 18 min |

---

## Wie die Website funktioniert

Die Seite unter [braukast.de](https://braukast.de) ist ein einfaches statisches HTML-File das über GitHub Pages ausgeliefert wird. Keine Frameworks, kein Build-Step.

### Datenfluss

```
Spotify for Podcasters (Anchor)
        │
        │  RSS-Feed
        ▼
scripts/fetch_episodes.py
        │
        │  schreibt
        ▼
episodes.json  ──────────────────►  index.html (lädt JSON im Browser)
```

`episodes.json` enthält alle Folgen mit Titel, Datum, Dauer und Link. `index.html` lädt diese Datei beim Seitenaufruf und rendert die Liste.

### Neue Folge veröffentlichen

1. Folge auf Spotify for Podcasters veröffentlichen
2. Auf GitHub: **Actions → Fetch Episodes → Run workflow**
3. Der Workflow holt den RSS-Feed, aktualisiert `episodes.json` und pusht den Commit
4. GitHub Pages deployt automatisch — die Seite ist nach ~1 Minute aktuell

### Lokale Entwicklung

```bash
# Episodendaten aktualisieren
python scripts/fetch_episodes.py

# Seite lokal testen
python -m http.server 8000
# → http://localhost:8000

# Tests
cd scripts && python -m unittest test_fetch_episodes -v
```

### Dateistruktur

```
├── index.html                        # Die Website
├── episodes.json                     # Episodendaten (generiert)
├── assets/
│   └── logo.png                      # Podcast-Logo
├── scripts/
│   ├── fetch_episodes.py             # RSS → episodes.json
│   └── test_fetch_episodes.py        # Tests für den Parser
└── .github/workflows/
    └── fetch-episodes.yml            # Manueller GitHub Action Trigger
```
