# Re-collect the 3 truncated 2025 slices month by month and merge into the existing xlsx (re-split by week if a month has >1000)
import json, time, os, subprocess, calendar
import urllib.request, urllib.parse
import pandas as pd

TOKEN = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'github_ai_agent_raw.xlsx')
OUT = os.path.join(BASE, 'github_ai_agent_raw_v2.xlsx')
LOG = os.path.join(BASE, 'github_collect_2025fix.log')

TRUNCATED = ['topic:ai-agents', 'topic:agentic-ai', '"ai agent" in:name,description']
STARS = 'stars:>=5'

def log(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(m + '\n')
    print(m, flush=True)

def search(q, page):
    url = ('https://api.github.com/search/repositories?q=' + urllib.parse.quote(q) +
           f'&per_page=100&page={page}&sort=stars&order=desc')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}',
        'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    for _ in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(int(e.headers.get('Retry-After', 60) or 60))
            else:
                log(f'HTTP {e.code} {q} p{page}'); return None
        except Exception as ex:
            log(f'err {ex}'); time.sleep(10)
    return None

def collect_range(q, d1, d2, repos):
    full_q = f'{q} {STARS} created:{d1}..{d2}'
    data = search(full_q, 1)
    if not data: return
    total = data.get('total_count', 0)
    incomplete = data.get('incomplete_results', False)
    log(f'{full_q} -> {total} (incomplete={incomplete})')
    if total > 1000:
        # Re-split by week
        days = pd.date_range(d1, d2, freq='7D').strftime('%Y-%m-%d').tolist()
        bounds = days + [d2]
        for a, b in zip(bounds[:-1], bounds[1:]):
            collect_range(q, a, b, repos)
        return
    page = 1
    while page <= 10:
        if page > 1:
            data = search(full_q, page)
            if not data or 'items' not in data: break
        for it in data.get('items', []):
            repos[it['full_name']] = {
                'full_name': it['full_name'], 'description': it.get('description') or '',
                'topics': ';'.join(it.get('topics') or []), 'stars': it.get('stargazers_count', 0),
                'forks': it.get('forks_count', 0), 'language': it.get('language') or '',
                'created_at': it.get('created_at', ''), 'pushed_at': it.get('pushed_at', ''),
                'license': (it.get('license') or {}).get('spdx_id', ''), 'archived': it.get('archived', False)}
        if len(data.get('items', [])) < 100: break
        page += 1; time.sleep(2.2)
    time.sleep(2.2)

repos = {}
for q in TRUNCATED:
    for m in range(1, 13):
        last = calendar.monthrange(2025, m)[1]
        collect_range(q, f'2025-{m:02d}-01', f'2025-{m:02d}-{last}', repos)
    log(f'== {q} done, cumulative new-pool: {len(repos)}')

new = pd.DataFrame(repos.values())
old = pd.read_excel(RAW)
merged = pd.concat([old, new]).drop_duplicates(subset='full_name', keep='last').reset_index(drop=True)
merged['year'] = merged['created_at'].str[:4]
merged.to_excel(OUT, index=False)
log(f'ALL DONE — old {len(old)} + newly-fetched {len(new)} -> merged unique {len(merged)}')
log(str(merged['year'].value_counts().sort_index()))
