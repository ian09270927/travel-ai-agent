import copy
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('travel_weekly_collector', HERE / 'collect_weekly.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
FIXTURE = json.loads((HERE / 'fixtures/attractions.json').read_text(encoding='utf-8'))
TEST_ROOT = m.ROOT / '.build' / 'actions-demo' / 'tests'
TEST_ROOT.mkdir(parents=True, exist_ok=True)


def rows():
    return m.normalize(copy.deepcopy(FIXTURE), True, '2026-10-19T09:00:00+08:00')[0]


class CollectorTests(unittest.TestCase):
    def test_timezone_and_monday(self):
        utc = dt.datetime(2026, 10, 19, 1, 0, tzinfo=dt.timezone.utc)
        local = utc.astimezone(m.TAIPEI)
        self.assertEqual((local.weekday(), local.hour, local.minute), (0, 9, 0))

    def test_fixture_no_network_and_pending_only(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp, patch.object(m, 'fetch_public', side_effect=AssertionError('no network')):
            out = Path(temp) / 'draft'
            code, s = m.run('fixture', out)
            self.assertEqual(code, 0)
            self.assertEqual((s['raw_count'], s['accepted_count'], s['duplicate_count'], s['rejected_count']), (6, 3, 2, 1))
            self.assertEqual(s['review_status'], 'pending_review')
            self.assertEqual(s['ai_call'], 'not_used')
            self.assertEqual(s['website_update'], 'not_attempted')
            data = json.loads((out / 'candidates.json').read_text(encoding='utf-8'))
            self.assertTrue(all(r['is_mock'] and r['source_url'] is None and r['price'] is None for r in data['records']))
            text = (out / 'weekly-report.pending.md').read_text(encoding='utf-8')
            self.assertIn('離線測試資料', text)
            self.assertNotIn('<script>', text)

    def test_newest_duplicate_and_alias(self):
        kept, duplicates = m.deduplicate(rows())
        self.assertEqual(len(kept), 3)
        self.assertIn('新版', next(r for r in kept if r['id'] == 'FIX-001')['description_excerpt'])
        self.assertTrue(any(d['reason'] == 'same_name_city_address' for d in duplicates))
        self.assertEqual(m.deduplicate(list(reversed(rows()))), (kept, duplicates))

    def test_shared_homepage_not_a_dedup_key(self):
        r = rows()[0]
        a, b = copy.deepcopy(r), copy.deepcopy(r)
        a['id'], b['id'] = 'DISTINCT-A', 'DISTINCT-B'
        b['name'], b['street_address'] = '另一景點', '另一地址'
        a['website_url'] = b['website_url'] = 'https://example.org/'
        self.assertEqual(len(m.deduplicate([a, b])[0]), 2)

    def test_missing_address_does_not_merge_different_ids(self):
        a, b = copy.deepcopy(rows()[0]), copy.deepcopy(rows()[0])
        a['street_address'] = b['street_address'] = None
        a['id'], b['id'] = 'A', 'B'
        self.assertEqual(len(m.deduplicate([a, b])[0]), 2)

    def test_bad_rows_and_empty_upstream(self):
        for data in ({}, [], {'Attractions': []}, {'Attractions': [None]}, {'Attractions': [{}]}):
            with self.assertRaises(m.PipelineError):
                m.normalize(data, False, '2026-10-19T09:00:00+08:00')

    def test_url_validation(self):
        for value in ('javascript:alert(1)', 'https://name:secret@example.org', 'https://x.invalid/\ncommand', None, 'https://x.invalid/<script>'):
            self.assertIsNone(m.safe_url(value))
        self.assertEqual(m.safe_url('https://EXAMPLE.org/test#fragment'), 'https://example.org/test')

    def test_allowlist(self):
        with self.assertRaises(m.PipelineError):
            m.fetch_public('http://127.0.0.1/', 10, lambda *a, **k: None)
        with self.assertRaises(m.PipelineError):
            m.AllowedRedirect().redirect_request(None, None, 302, '', {}, 'https://unreviewed.invalid/')

    def test_metadata_license_and_resource(self):
        good = ('政府資料開放授權條款-第1版 免費 <a href="' + m.CONFIG['download_url'] + '">JSON</a>').encode()
        m.check_metadata(good)
        for bad in (b'copyright all rights reserved', '政府資料開放授權條款-第1版 免費'.encode()):
            with self.assertRaises(m.PipelineError):
                m.check_metadata(bad)

    def test_zip_member_not_extracted(self):
        blob = io.BytesIO()
        with zipfile.ZipFile(blob, 'w') as z:
            z.writestr('../not-extracted.txt', 'unused')
            z.writestr('AttractionList.json', json.dumps(FIXTURE))
        self.assertEqual(len(m.parse_archive(blob.getvalue())['Attractions']), 6)

    def test_zip_schema_drift(self):
        blob = io.BytesIO()
        with zipfile.ZipFile(blob, 'w') as z:
            z.writestr('unexpected.json', '{}')
        with self.assertRaises(m.PipelineError):
            m.parse_archive(blob.getvalue())

    def test_failure_records_without_fake_draft(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp, patch.object(m, 'fetch_public', side_effect=m.PipelineError('source unavailable')):
            out = Path(temp) / 'failed'
            code, s = m.run('live', out)
            self.assertEqual(code, 1)
            self.assertEqual(s['review_status'], 'blocked')
            self.assertFalse((out / 'weekly-report.pending.md').exists())
            self.assertTrue((out / 'events.ndjson').exists())

    def test_no_overwrite_or_product_output(self):
        for target in (m.ROOT, m.ROOT / 'site' / 'generated', m.ROOT / 'docs' / 'new'):
            with self.assertRaises(m.PipelineError):
                m.prepare_output(target)
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp:
            path = Path(temp) / 'draft'
            m.run('fixture', path)
            with self.assertRaises(m.PipelineError):
                m.run('fixture', path)

    def test_success_live_with_stubbed_public_source(self):
        metadata = ('政府資料開放授權條款-第1版 免費 <a href="' + m.CONFIG['download_url'] + '">JSON</a>').encode()
        blob = io.BytesIO()
        with zipfile.ZipFile(blob, 'w') as z:
            z.writestr('AttractionList.json', json.dumps(FIXTURE))
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as temp, patch.object(m, 'fetch_public', side_effect=[metadata, blob.getvalue()]):
            code, s = m.run('live', Path(temp) / 'live')
            self.assertEqual(code, 0)
            self.assertIn('download_and_json_checked', s['source_check'])
            self.assertTrue(s['draft_generated'])
            # Mocked transport is structural testing, never evidence of a live request.

    def test_http_200_rejection_page_stops_without_retry(self):
        class Response:
            status = 200
            headers = {'Content-Type': 'text/html'}
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def geturl(self): return m.CONFIG['download_url']
            def read(self, cap): return b'<html>Request Rejected</html>'
        class Opener:
            def __init__(self): self.calls = 0
            def open(self, *args, **kwargs): self.calls += 1; return Response()
        opener = Opener()
        with patch.object(m.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(m.PipelineError, 'without bypass'):
                m.fetch_public(m.CONFIG['download_url'], 1000, lambda *a, **k: None)
        self.assertEqual(opener.calls, 1)


if __name__ == '__main__':
    unittest.main()
