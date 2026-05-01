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
