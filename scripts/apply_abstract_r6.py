# -*- coding: utf-8 -*-
"""R6: 검토 완료 초록(R6_abstract_final.txt)을 main.tex에 적용하고 LangChain-centered→LangChain-based, 초록 단어 DF 재검증."""
import re, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tex = sys.argv[1]
A = open(os.path.join(ROOT, '30_분석결과', '용어검토', 'R6_abstract_final.txt'), encoding='utf-8').read().strip()
s = open(tex, encoding='utf-8').read()
i = s.index('\\begin{abstract}') + len('\\begin{abstract}'); j = s.index('\\end{abstract}')
s = s[:i] + '\n' + A + '\n' + s[j:]
s = s.replace('LangChain-centered', 'LangChain-based')
open(tex, 'w', encoding='utf-8').write(s)
print('abstract words', len(A.split()), '| control', sum(1 for c in s if ord(c) < 32 and c not in '\n'), '| centered left', s.count('LangChain-centered'))
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(ROOT, '30_분석결과', '용어검토', '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    return sum(1 for d in docs.values() if any(p in d for p in pats))
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must using use used rather'.split())
seen = []; low = []
for w in re.findall(r"[a-z][a-z0-9\-]+", A.replace('\\', '').lower()):
    if w in STOP or len(w) < 3 or w in seen: continue
    seen.append(w); d = df(w)
    if d < 3: low.append((w, d))
print('content words', len(seen), '| DF<3:', low)
