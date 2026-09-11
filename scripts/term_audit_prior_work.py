# -*- coding: utf-8 -*-
"""원고 용어 ↔ 선행연구 27편 전문 대조.
  1) 원고 tex → 평문(LaTeX 제거)  2) 제목·초록: 모든 내용어 1~3-gram 전수  3) 본문: 빈도≥2 전문용어 n-gram
  4) 각 용어의 선행연구 문서빈도(DF, 27편 중 몇 편)·총출현  → 30_분석결과/용어검토/용어DF_전수.csv
사용: python term_audit_prior_work.py <main.tex>
"""
import re, sys, os, json, collections, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_분석결과', '용어검토')
corpus = json.load(open(os.path.join(OUT, '선행연구_전문텍스트.json'), encoding='utf-8'))
norm = lambda s: re.sub(r'[\u2010-\u2015]', '-', s.lower())
docs = {k: norm(v) for k, v in corpus.items()}
tex = open(sys.argv[1], encoding='utf-8').read()
def plain(t):
    t = re.sub(r'%.*', '', t); t = re.sub(r'\\(cite|ref|label|url|includegraphics|caption|xdef|setlength)\{[^}]*\}', ' ', t)
    t = re.sub(r'\\begin\{(table\*?|figure\*?|tabular|equation|keywords|IEEEbiography)\}.*?\\end\{\1\}', ' ', t, flags=re.S)
    t = re.sub(r'\$[^$]*\$', ' ', t); t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', t); t = re.sub(r'[{}~]', ' ', t); t = t.replace('--', '-').replace("''", '').replace('``', '')
    return re.sub(r'\s+', ' ', t)
title = re.search(r'\\title\{(.*?)\}', tex, re.S).group(1); abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
body = plain(tex.split('\\maketitle')[1].split('\\section*{Acknowledgment}')[0])
STOP = set('a an the and or of to in on for with by from as at is are was were be been being that this these those we our it its their which who whom whose than then there here not no nor so such into over under between among within without through per each all any both either neither more most less least very also only own same other another such if when where while whether because since until against about above below off out up down once here again further ever never each few some many much several both every one two three four five six seven eight nine ten first second third do does did doing has have had having may might can could would should will shall must i you he she they them his her him us me my your yours ours theirs itself themselves whereas rather however therefore thus hence moreover instead still yet even often always sometimes already just around across along before after during'.split())
def ngrams(text, nmax=3, minfreq=1):
    toks = re.findall(r"[a-z][a-z0-9\-/\.]*[a-z0-9]|[a-z]", norm(text)); c = collections.Counter()
    for n in range(1, nmax + 1):
        for i in range(len(toks) - n + 1):
            g = toks[i:i + n]
            if g[0] in STOP or g[-1] in STOP: continue
            if all(w in STOP for w in g): continue
            c[' '.join(g)] += 1
    return {k: v for k, v in c.items() if v >= minfreq}
def df(term):
    t = norm(term); pats = [t, t.replace('-', ' '), t.replace(' ', '-')]
    if not t.endswith('s'): pats += [p + 's' for p in pats]
    hit = {k for k, d in docs.items() if any(p in d for p in set(pats))}
    tot = sum(sum(d.count(p) for p in set(pats)) for d in docs.values())
    return len(hit), tot, sorted(h.split('_')[1] if '_' in h else h for h in hit)
rows = []
for sec, text, minf in [('제목', title, 1), ('초록', abstract, 1), ('본문', body, 2)]:
    for term, freq in ngrams(text, 3, minf).items():
        if sec == '본문' and (len(term) < 4 or re.fullmatch(r'[\d\.\-/]+', term)): continue
        d, tot, hits = df(term); rows.append(dict(section=sec, term=term, manuscript_freq=freq, prior_DF=d, prior_total=tot, prior_docs=', '.join(hits)[:200]))
res = pd.DataFrame(rows).drop_duplicates('term', keep='first').sort_values(['section', 'prior_DF', 'manuscript_freq'], ascending=[True, True, False])
res.to_csv(os.path.join(OUT, '용어DF_전수.csv'), index=False, encoding='utf-8-sig'); print('terms:', len(res), '| by section:', res['section'].value_counts().to_dict())
print(res[res.section != '본문'][['section', 'term', 'manuscript_freq', 'prior_DF']].to_string())
