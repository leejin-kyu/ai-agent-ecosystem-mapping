# -*- coding: utf-8 -*-
"""R6 초록(사용자 제공) 단어·구 전수 DF 검사. 출력: 단어별 DF, DF<3 목록, 후보 대체어 DF."""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(ROOT, '30_분석결과', '용어검토', '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    return sum(1 for d in docs.values() if any(p in d for p in pats))
ABS = open(os.path.join(ROOT, '30_분석결과', '용어검토', 'R6_abstract_user.txt'), encoding='utf-8').read()
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must at using use used than rather'.split())
words = [w for w in re.findall(r"[a-z][a-z0-9\-]+", ABS.lower()) if w not in STOP and len(w) > 2]
seen = []; print('=== 단어별 DF (DF<3만 표시)')
for w in words:
    if w in seen: continue
    seen.append(w); d = df(w)
    if d < 3: print(f'  {w:28s} DF {d}')
print('총 내용어', len(seen))
print('\n=== 구(phrase) DF')
for ph in ['recursive partitioning', 'creation date', 'circumvent', 'result limit', 'collection time', 'creation-year', 'publicly visible', 'historical population', 'repository cluster', 'model-selection', 'model selection', 'random-seed', 'random seed', 'reproducibility', 'bootstrap', 'five-cluster', 'coarse', 'exploratory', 'relevance', 'stratified sample', 'local language model', 'corpus precision', 'human annotation', 'subsample', 'operational boundary', 'operational definition', 'temporal model', 'model specification', 'robustness analyses', 'robustness analysis', 'sampling assumptions', 'proportion', 'framework repositories', 'mcp servers', 'code-generation', 'game-related', 'orchestration', 'change point', 'coincides temporally', 'coincide', 'observational', 'causal attribution', 'causal', 'reproducible', 'repository-level', 'query-matched', 'shifted', 'infrastructure', 'consistently', 'persist', 'apparent', 'yielding', 'assessed', 'assessment', 'revealed', 'substantial', 'variation', 'circumvents', 'boundary', 'automation']:
    print(f'  {ph:28s} DF {df(ph)}')
