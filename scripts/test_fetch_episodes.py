import unittest
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fetch_episodes import parse_duration, parse_date, spotify_url_from_uri, parse_feed

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
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
</rss>""".encode('utf-8')


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
