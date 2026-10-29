# GitHub AI Agent repository collection - query x year slices to work around the 1,000-result cap, stars>=5
# Output: github_ai_agent_raw.xlsx (full_name, description, topics, stars, forks, language, created, pushed, license)
import subprocess, json, time, sys, os
import pandas as pd

TOKEN = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'github_ai_agent_raw.xlsx')
LOG = os.path.join(BASE, 'github_collect.log')

QUERIES = [
    'topic:ai-agent', 'topic:ai-agents', 'topic:llm-agent', 'topic:llm-agents',
    'topic:autonomous-agents', 'topic:agentic-ai',
    '"ai agent" in:name,description', '"llm agent" in:name,description',
]
YEARS = list(range(2016, 2026))
STARS = 'stars:>=5'

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

def search(q, page):
    url = ('https://api.github.com/search/repositories?q=' +
           urllib.parse.quote(q) + f'&per_page=100&page={page}&sort=stars&order=desc')
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                remaining = int(r.headers.get('X-RateLimit-Remaining', 1))
                data = json.loads(r.read().decode())
                if remaining <= 1:
                    time.sleep(30)
                return data
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                wait = int(e.headers.get('Retry-After', 60) or 60)
                log(f'  rate-limited, sleep {wait}s')
                time.sleep(wait)
            else:
                log(f'  HTTP {e.code} on {q} p{page}')
                return None
        except Exception as ex:
            log(f'  err {ex}, retry')
            time.sleep(10)
    return None

repos = {}
for q in QUERIES:
    for y in YEARS:
        full_q = f'{q} {STARS} created:{y}-01-01..{y}-12-31'
        page, total = 1, None
        while page <= 10:
            data = search(full_q, page)
            if not data or 'items' not in data:
                break
            if total is None:
                total = data.get('total_count', 0)
                log(f'{full_q} -> total {total}')
                if total > 1000:
                    log(f'  WARN: >1000, truncated to top-star 1000')
            for it in data['items']:
                repos[it['full_name']] = {
                    'full_name': it['full_name'],
                    'description': it.get('description') or '',
                    'topics': ';'.join(it.get('topics') or []),
                    'stars': it.get('stargazers_count', 0),
                    'forks': it.get('forks_count', 0),
                    'language': it.get('language') or '',
                    'created_at': it.get('created_at', ''),
                    'pushed_at': it.get('pushed_at', ''),
                    'license': (it.get('license') or {}).get('spdx_id', ''),
                    'archived': it.get('archived', False),
                }
            if len(data['items']) < 100:
                break
            page += 1
            time.sleep(2.2)  # search 30/min
        time.sleep(2.2)
    # Intermediate save
    pd.DataFrame(repos.values()).to_excel(OUT, index=False)
    log(f'== query done: {q} | cumulative unique repos: {len(repos)}')

df = pd.DataFrame(repos.values())
df['year'] = df['created_at'].str[:4]
df.to_excel(OUT, index=False)
log(f'ALL DONE — unique repos: {len(df)}')
log(str(df['year'].value_counts().sort_index()))
