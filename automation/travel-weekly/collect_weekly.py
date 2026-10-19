"""Public open-data -> deterministic, pending-review draft. Standard library only."""
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TAIPEI = dt.timezone(dt.timedelta(hours=8), 'Asia/Taipei')
CONFIG = json.loads((HERE / 'sources.json').read_text(encoding='utf-8'))
PROTECTED = ('site', 'research', 'docs', 'video', 'skills', '.github', '.git', 'automation')


class PipelineError(Exception):
    pass


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_url(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if any(ord(c) < 33 for c in value) or any(c in value for c in '<>"`'):
        return None
    try:
        p = urllib.parse.urlsplit(value)
        if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
            return None
        return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', p.query, ''))
    except ValueError:
        return None


class AllowedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if newurl not in CONFIG['allowed_urls']:
            raise PipelineError('Redirect outside reviewed source allowlist')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_public(url, cap, log):
    if url not in CONFIG['allowed_urls'] or not url.startswith('https://'):
        raise PipelineError('Unreviewed download URL')
    opener = urllib.request.build_opener(AllowedRedirect())
    for attempt in range(1, 3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'travel-ai-agent-weekly-review/1.0 (public open-data teaching demo)',
                'Accept': 'application/zip,application/json,text/html;q=0.8',
            })
            with opener.open(req, timeout=40) as response:
                if response.status != 200 or response.geturl() not in CONFIG['allowed_urls']:
                    raise PipelineError('Unexpected HTTP status or final URL')
                body = response.read(cap + 1)
                if len(body) > cap:
                    raise PipelineError('Source exceeds byte limit')
                log('fetch', url=url, attempt=attempt, http_status=200, bytes=len(body),
                    sha256=sha(body), content_type=response.headers.get('Content-Type'), retrieved_at_utc=utc_now())
                if url == CONFIG['download_url'] and not body.startswith(b'PK\x03\x04'):
                    log('source_rejected_or_unexpected_content', url=url, retry=False)
                    raise PipelineError('Expected ZIP but source returned a rejection page or other content; stop without bypass or fixture fallback')
                return body
        except urllib.error.HTTPError as exc:
            log('fetch_error', url=url, attempt=attempt, http_status=exc.code)
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise PipelineError(f'HTTP {exc.code}; no fixture fallback') from exc
            retry_after = exc.headers.get('Retry-After')
            if retry_after and (not retry_after.isdigit() or int(retry_after) > 5):
                raise PipelineError('Server asks for longer retry; defer to next manual/scheduled run') from exc
            time.sleep(max(2, int(retry_after or '0')))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            log('fetch_error', url=url, attempt=attempt, error_type=type(exc).__name__)
            if attempt == 2:
                raise PipelineError('Source unavailable; no fixture fallback') from exc
            time.sleep(2)


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.text = [], []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))
    def handle_data(self, data):
        self.text.append(data)


def check_metadata(body):
    parser = MetadataParser()
    parser.feed(body.decode('utf-8-sig'))
    text = unicodedata.normalize('NFKC', ''.join(parser.text))
    compact = re.sub(r'[\s\-－—–]', '', text)
    if '政府資料開放授權條款第1版' not in compact or '免費' not in compact:
        raise PipelineError('Expected public license/free access statement not found; manual review required')
    if CONFIG['download_url'] not in parser.links:
        raise PipelineError('Reviewed resource link changed; manual source review required')


def reject_constant(value):
    raise ValueError('Nonstandard JSON number')


def parse_archive(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        entries = [i for i in archive.infolist() if i.filename == CONFIG['archive_member']]
        if len(entries) != 1 or entries[0].file_size > CONFIG['max_uncompressed_bytes']:
            raise PipelineError('Unexpected archive layout or size')
        # Read this member only; never extract archive paths to the filesystem.
        body = archive.read(entries[0])
        if len(body) > CONFIG['max_uncompressed_bytes']:
            raise PipelineError('Decompressed payload exceeds byte limit')
        return json.loads(body.decode('utf-8-sig'), parse_constant=reject_constant)


def clean_text(value):
    if not isinstance(value, str):
        return ''
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', value)).strip()


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.replace(tzinfo=TAIPEI) if parsed.tzinfo is None else parsed
    except ValueError:
        return None


def normalize(data, fixture, queried_at):
    if not isinstance(data, dict) or not isinstance(data.get('Attractions'), list) or not data['Attractions']:
        raise PipelineError('Expected nonempty Attractions array; upstream schema may have changed')
    records, rejected = [], []
    for i, item in enumerate(data['Attractions']):
        if not isinstance(item, dict):
            rejected.append({'index': i, 'reason': 'not an object'}); continue
        address = item.get('PostalAddress')
        if not isinstance(address, dict):
            address = {}
        rid, name, city, description = map(clean_text, (
            item.get('AttractionID'), item.get('AttractionName'), address.get('City'), item.get('Description')))
        if not all((rid, name, city, description)) or len(rid) > 200 or len(name) > 200:
            rejected.append({'index': i, 'reason': 'missing or invalid ID/name/city/description'}); continue
        record = {
            'id': rid, 'name': name, 'city': city, 'district': clean_text(address.get('Town')) or None,
            'street_address': clean_text(address.get('StreetAddress')) or None,
            'description_excerpt': description[:180], 'is_mock': fixture,
            'source_id': 'fixture-only' if fixture else CONFIG['id'],
            'source_url': None if fixture else CONFIG['metadata_url'],
            'queried_at': queried_at, 'source_updated_at': item.get('UpdateTime') if timestamp(item.get('UpdateTime')) else None,
            'website_url': safe_url(item.get('WebsiteURL')), 'website_check': 'syntax_only_not_fetched',
            'price': None, 'opening_hours': None, 'transport_schedule': None, 'activity_dates': None,
            'audience_assessment': '尚未分類；待人工依孩子年齡、共同興趣、步行及休息條件審查',
            'review_status': 'pending_review',
        }
        record['content_sha256'] = sha(json.dumps({k: record[k] for k in ('name', 'city', 'district', 'street_address', 'description_excerpt', 'source_updated_at')}, sort_keys=True, ensure_ascii=False).encode())
        records.append(record)
    if not records:
        raise PipelineError('No valid records; do not produce an empty-success draft')
    return records, rejected


def deduplicate(records):
    # Newest valid provider timestamp wins; SHA/ID supply deterministic tie breaks.
    floor = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    ranked = sorted(records, key=lambda r: (timestamp(r['source_updated_at']) or floor, r['content_sha256'], r['id']), reverse=True)
    ids, identities, kept, duplicates = {}, {}, [], []
    for r in ranked:
        identity = tuple(clean_text(r.get(k) or '').casefold() for k in ('name', 'city', 'street_address'))
        prior = ids.get(r['id'])
        reason = 'same_id'
        if prior is None and r['street_address']:
            prior = identities.get(identity); reason = 'same_name_city_address'
        if prior is not None:
            duplicates.append({'dropped_id': r['id'], 'kept_id': prior['id'], 'reason': reason,
                               'conflicting_content': r['content_sha256'] != prior['content_sha256']})
            # Remember dropped aliases so later duplicate IDs cannot reappear.
            ids[r['id']] = prior
            continue
        kept.append(r); ids[r['id']] = r
        if r['street_address']:
            identities[identity] = r
    return sorted(kept, key=lambda r: r['id']), duplicates


def markdown(value):
    value = html.escape(str(value or '待確認'))
    return re.sub(r'([\\`*_{}\[\]()#+.!|>])', r'\\\1', value)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepare_output(output):
    output = Path(output).resolve()
    if output == ROOT or any(output == ROOT / p or ROOT / p in output.parents for p in PROTECTED):
        raise PipelineError('Refusing to write inside product/source directories')
    if output.exists() and any(output.iterdir()):
        raise PipelineError('Output must be new or empty; use a new run directory')
    output.mkdir(parents=True, exist_ok=True)
    return output


def draft_report(records, summary):
    date = dt.datetime.fromisoformat(summary['started_at_taipei']).date()
    monday = date - dt.timedelta(days=date.weekday())
    chosen = records[:CONFIG['target_records']]
    lines = ['# 旅遊情報週報｜待人工審核', '', '**狀態：pending_review；未發布、未核價、未更新網站。**',
             f"模式：{summary['mode']}；週別 {monday}～{monday + dt.timedelta(days=6)}；執行日 {date}（Asia/Taipei）。",
             '本週指本次整理週別，不代表景點於本週新開幕或資訊本週才更新。', '', '## 本次資料摘要',
             f"原始 {summary['raw_count']} 筆，無效排除 {summary['rejected_count']} 筆，重複排除 {summary['duplicate_count']} 筆，保留 {len(records)} 筆；以下取 ID 排序前 {len(chosen)} 筆作審稿示範，非最佳行程推薦。", '']
    if summary['mode'] == 'fixture':
        lines += ['**全份為離線測試資料，非真實旅遊推薦；未連網查證、沒有官方來源。**', '']
    else:
        lines += [f"資料來源：[交通部觀光署／景點資料集]({CONFIG['metadata_url']})；[下載來源]({CONFIG['download_url']})。",
                  f"授權：[政府資料開放授權條款第 1 版]({CONFIG['license_url']})。",
                  f"顯名：交通部觀光署 {date.year} 景點－觀光資訊資料庫（觀光資料標準 V2.1）；依政府資料開放授權條款進行公眾釋出。", '']
    lines += ['## 景點候選與來源摘錄', '摘錄來自來源描述，尚未逐筆核對營運現況；不能把摘錄中出現的價格、時間、交通說法直接當成已驗證承諾。', '']
    for r in chosen:
        lines += [f"### {markdown(r['name'])}", f"- 紀錄 ID：{markdown(r['id'])}；地區：{markdown(r['city'])}／{markdown(r['district'])}。",
                  f"- 來源描述摘錄：{markdown(r['description_excerpt'])}", f"- 來源明示更新時間：{markdown(r['source_updated_at'])}；本次擷取時間：{markdown(r['queried_at'])}。",
                  '- 親子／情侶／熟齡適合度：待人工分類，不等同官方認證。', '- 費用、開放、交通班次、活動日期：未核對，不填示範報價。', '']
    lines += ['## 三個待審核行銷切入點',
              '1. 依旅伴興趣與步行條件挑選候選；這是編輯提案，不是市場統計。',
              '2. 以官方資料與查詢時間解釋推薦理由，避免以來源摘錄承諾服務。',
              '3. 邀請旅客整理日期、預算與偏好，再由業務查價及確認交通。', '',
              '## 旅客 FAQ（審稿模板）',
              '- 現在可以預訂或保證開放嗎？本草稿沒有庫存、訂位或現場狀態查核。',
              '- 價格包含哪些服務？本流程不產生報價，待旅行社核定。',
              '- 熟齡或兒童一定適合嗎？需依年齡、興趣、坡度、步行與休息條件另評估。', '',
              '## 人工審核與發布檢查',
              '- [ ] 逐筆比對官方來源，核對有效性、名稱及地區；個別官網網址目前僅檢查語法，沒有逐一抓取。',
              '- [ ] 審查去重衝突、被排除資料與來源更新時間，不把未知當免費或全年開放。',
              '- [ ] 編輯親子、情侶、熟齡分類，補充有證據的限制與備案。',
              '- [ ] 若增活動，另建活動來源及日期驗證；本流程只下載景點資料，未實作活動介接。',
              '- [ ] 審查來源原文與可能的過時營運說法，刪修不應宣傳內容。',
              '- [ ] 審稿人另行提出內容變更、覆核並合併；此流程不自動部署。', '']
    return '\n'.join(lines)


def run(mode, output, fixture_path=None):
    output = prepare_output(output)
    started = dt.datetime.now(TAIPEI)
    summary = {'status': 'running', 'review_status': 'pending_review', 'mode': mode,
               'started_at_taipei': started.isoformat(), 'started_at_utc': started.astimezone(dt.timezone.utc).isoformat(),
               'event_name': os.environ.get('GITHUB_EVENT_NAME', 'local'),
               'github_run_id': os.environ.get('GITHUB_RUN_ID'), 'github_run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
               'commit_sha': os.environ.get('GITHUB_SHA'), 'source_id': CONFIG['id'] if mode == 'live' else 'fixture-only',
               'source_check': 'not_started', 'ai_call': 'not_used', 'website_update': 'not_attempted',
               'publication': 'not_attempted', 'draft_generated': False, 'stage': 'source'}
    def log(event, **fields):
        with (output / 'events.ndjson').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'at_utc': utc_now(), 'event': event, **fields}, ensure_ascii=False) + '\n')
    try:
        if mode == 'fixture':
            data = json.loads(Path(fixture_path or HERE / 'fixtures/attractions.json').read_text(encoding='utf-8-sig'), parse_constant=reject_constant)
            if data.get('is_mock') is not True:
                raise PipelineError('Fixture must explicitly declare is_mock=true')
            summary['source_check'] = 'fixture_no_network'
            log('fixture_loaded', note='Synthetic data, no official source checked')
        elif mode == 'live':
            metadata = fetch_public(CONFIG['metadata_url'], 2000000, log)
            check_metadata(metadata)
            summary['metadata_sha256'] = sha(metadata)
            summary['source_check'] = 'metadata_license_and_link_checked_only'
            payload = fetch_public(CONFIG['download_url'], CONFIG['max_download_bytes'], log)
            summary['payload_sha256'] = sha(payload)
            summary['stage'] = 'parse'
            data = parse_archive(payload)
            summary['source_check'] = 'metadata_license_link_download_and_json_checked'
        else:
            raise PipelineError('Unsupported mode')
        summary['stage'] = 'normalize'
        records, rejected = normalize(data, mode == 'fixture', started.isoformat())
        summary['raw_count'] = len(data['Attractions'])
        summary['source_updated_at'] = data.get('UpdateTime')
        summary['stage'] = 'deduplicate'
        kept, duplicates = deduplicate(records)
        summary.update({'accepted_count': len(kept), 'rejected_count': len(rejected), 'duplicate_count': len(duplicates),
                        'draft_count': min(len(kept), CONFIG['target_records']), 'target_count': CONFIG['target_records']})
        write_json(output / 'candidates.json', {'data_mode': mode, 'is_mock': mode == 'fixture', 'review_status': 'pending_review', 'records': kept})
        write_json(output / 'quality.json', {'duplicates': duplicates, 'rejected': rejected,
                    'dedup_scope': 'current input batch only; no cross-run baseline',
                    'warnings': ['個別官網未逐一抓取；來源摘要未作營運現況查核'] + (['資料少於目標筆數，未補造資料'] if len(kept) < CONFIG['target_records'] else [])})
        summary['stage'] = 'draft'
        (output / 'weekly-report.pending.md').write_text(draft_report(kept, summary), encoding='utf-8')
        sources = ('# 測試來源\n全份為 synthetic fixture，未查官方來源。\n' if mode == 'fixture' else
                   f"# 本次來源檢查\n\n提供機關：{CONFIG['publisher']}\n\n資料集：{CONFIG['metadata_url']}\n\n下載：{CONFIG['download_url']}\n\n授權：{CONFIG['license_name']} {CONFIG['license_url']}\n\n擷取時間：{started.isoformat()}\n\n只驗證詮釋資料授權文字、下載連結、HTTP、大小、ZIP/JSON 結構；不代表每個景點現場資訊已核對。\n")
        (output / 'sources.md').write_text(sources, encoding='utf-8')
        summary.update({'status': 'success', 'stage': 'complete', 'draft_generated': True})
        log('complete', accepted_count=len(kept), review_status='pending_review')
        code = 0
    except Exception as exc:
        summary.update({'status': 'failed', 'review_status': 'blocked', 'error_type': type(exc).__name__,
                        'error': str(exc) if isinstance(exc, PipelineError) else 'Invalid/unavailable source; inspect stage and error_type'})
        log('failed', stage=summary['stage'], error_type=type(exc).__name__)
        code = 1
    summary['finished_at_utc'] = utc_now()
    write_json(output / 'run-summary.json', summary)
    return code, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['fixture', 'live'], default='fixture')
    parser.add_argument('--output', default='review-output')
    parser.add_argument('--fixture', type=Path)
    args = parser.parse_args()
    try:
        code, summary = run(args.mode, args.output, args.fixture)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return code
    except PipelineError as exc:
        print(json.dumps({'status': 'blocked_before_write', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
