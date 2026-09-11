# -*- coding: utf-8 -*-
"""R9: 제목·초록 전수 DF(선행연구 27편, 기준 ≥3편) 재검사 후 미달 용어 치환 + 본문 잔여어. 사용: python apply_terms_r9.py <tex>
출력: 치환 로그, 초록 내용어 DF<3 잔여 목록, 본문 저빈도 복합어 상위."""
import re, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_분석결과', '용어검토')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    return sum(1 for d in docs.values() if any(p in d for p in pats))
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
REPL = [
 ('To overcome the GitHub Search API\'s 1,000-result limit, queries were recursively partitioned by creation date.', 'To overcome the 1,000-result limit of the GitHub Search API, queries were partitioned by creation date.'),
 ('the analysis characterizes the creation-year composition of repositories that remained publicly visible at collection rather than the historical repository population.', 'the analysis describes the composition by creation year of repositories that remained publicly visible at collection rather than the historical repository population.'),
 ('support a five-cluster coarse solution; a 12-cluster solution is treated as exploratory.', 'support a coarse solution with five clusters; a solution with 12 clusters is treated as exploratory.'),
 ('Relevance auditing of 404 repositories with two local language models estimated corpus precision', 'Relevance was assessed on 404 repositories with two local language models, which estimated corpus precision'),
 ('Game repositories also decline, while the apparent full-period decline of the largest orchestration-and-automation cluster does not persist within 2023--2025.', 'Game repositories also decrease, while the decrease of the largest orchestration and automation cluster estimated over the full period does not persist within 2023--2025.'),
 ('Overall, the results provide a reproducible repository-level characterization of recent compositional shifts in currently visible AI-agent repositories on GitHub.', 'Overall, the results provide a reproducible description, at the repository level, of recent shifts in the composition of currently visible AI-agent repositories on GitHub.'),
]
for a, b in REPL:
    n = s.count(a); s = s.replace(a, b); print(f'{n} | {a[:60]} -> {b[:60]}')
open(p, 'w', encoding='utf-8').write(s)
ab = s[s.index('\\begin{abstract}') + 16:s.index('\\end{abstract}')].replace('\\', '')
title = re.search(r'\\title\{(.*?)\}', s).group(1)
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must using use used rather but while'.split())
def audit(text, name):
    seen = []; low = []
    for w in re.findall(r"[a-z][a-z0-9\-]+", text.lower()):
        if w in STOP or len(w) < 3 or w in seen: continue
        seen.append(w); d = df(w)
        if d < 3: low.append((w, d))
    print(f'{name}: content words {len(seen)} | DF<3: {low}')
audit(title, 'TITLE'); audit(ab, 'ABSTRACT'); print('abstract words', len(ab.split()))
