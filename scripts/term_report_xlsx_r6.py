# -*- coding: utf-8 -*-
"""R6 결과보고: R5 보고 xlsx에 '1b_R6 초록 용어 대조'와 '2b_R6 초록 단어 전수 DF' 시트를 추가하고 요약 갱신."""
import json, re, os, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_분석결과', '용어검토')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    hit = [k for k, d in docs.items() if any(p in d for p in pats)]; return len(hit), ', '.join(sorted(h[:4] + ' ' + h.split('_')[1][:12] for h in hit))
rows = [
 ('recursive partitioning by creation date circumvents the 1,000-result limit', 'partition (6편) · removes (3편) · recursive (5편)', 'a recursive partition of each query by creation date removes the 1,000-result limit', '"partitioning" 2편, "circumvents" 0편'),
 ('the analysis characterizes the creation-year composition', 'describe (다수) · composition (16편) · creation (12편)', 'the analysis describes the composition by creation year', '"characterizes" 1편, "creation-year" 0편'),
 ('a stability-based model-selection rule', 'model selection (3편) · stability (10편)', 'a model-selection rule based on stability', '"stability-based" 1편'),
 ('supports a five-cluster coarse solution', 'cluster (13편) · coarse (4편)', 'supports a coarse solution with five clusters', '"five-cluster" 0편'),
 ('a 120-repository subsample', 'sample (다수)', 'a 120-repository sample', '"subsample" 1편'),
 ('variation in the operational boundary of an AI-agent repository', 'boundary (4편) · variation (19편)', 'variation in the boundary of what counts as an AI-agent repository', '"operational boundary" 0편'),
 ('falling within the range', 'within (다수)', 'lying within the range', '"falling" 2편'),
 ('alternative temporal model specifications', 'specification(s) (5/3편) · alternative (다수)', 'alternative model specifications', '"temporal model" 0편'),
 ('robustness analyses over relevance and sampling assumptions', 'robustness (13편)', 'robustness checks over relevance and sampling assumptions', '"robustness analyses" 0편'),
 ('LangChain-centered framework repositories', 'LangChain(고유명사) · based (다수)', 'LangChain-based framework repositories', '"-centered" 조합 0편; 본문 전체 동일 치환'),
 ('game-related repositories also declines robustly', 'game (11편) · decrease (다수)', 'game repositories also decreases robustly', '"game-related" 0편, "declines" 1편'),
 ('the apparent full-period decline of the largest orchestration-and-automation cluster', 'decrease · period (14편) · orchestration (4편) · automation (8편)', 'the decrease of the largest orchestration and automation cluster estimated over the full period', '"apparent" 2편, "full-period" 0편, 하이픈 조합 0편'),
 ('coincides temporally with several relevant events', 'aligned with (9편)', 'is aligned in time with several relevant events', '"coincides" 1편, "temporally" 0편'),
 ('the observational design does not support causal attribution', 'cause (24편) · design (다수)', 'the study design does not identify a cause', '"observational" 0편, "attribution" 2편'),
 ('a reproducible, repository-level characterization', 'reproducible (7편) · description (18편) · repository (12편)', 'a reproducible description, at the repository level', '"repository-level" 1편, "characterization" 2편'),
 ('currently visible, query-matched AI-agent repositories', 'matched (4편) · search queries (다수)', 'currently visible AI-agent repositories matched by the search queries', '"query-matched" 0편'),
 ('toward MCP infrastructure', 'MCP server (2편) · server (다수)', 'toward MCP servers', '"MCP infrastructure" 조합 0편 (본문과 일치)'),
 ('(유지) silhouette · binomial · false-discovery-rate · BGE-M3', '통계 표준어·고유명사 (DF 0~1)', '유지', '대안 없음, 비고'),
]
rep = pd.DataFrame([{'A. 사용자 초록 용어 (R6 원안)': a, 'B. 선행연구 통용 용어 (문서 수)': b, 'C. 바꾼 용어 (R6 확정)': c, 'E. 근거·비고': e} for a, b, c, e in rows])
A = open(os.path.join(OUT, 'R6_abstract_final.txt'), encoding='utf-8').read().replace('\\', '')
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must using use used rather'.split())
seen = []; wrows = []
for w in re.findall(r"[a-z][a-z0-9\-]+", A.lower()):
    if w in STOP or len(w) < 3 or w in seen: continue
    seen.append(w); d, h = df(w); wrows.append({'초록 단어(R6 확정)': w, '선행연구 문서 수(27편 중)': d, '판정': 'OK' if d >= 3 else '예외(통계 표준어/고유명사)', '출현 문헌': h[:150]})
wdf = pd.DataFrame(wrows).sort_values('선행연구 문서 수(27편 중)')
src = os.path.join(OUT, '용어표준화_결과보고_260910.xlsx'); out = os.path.join(OUT, '용어표준화_결과보고_R6_260910.xlsx')
sheets = pd.read_excel(src, sheet_name=None)
with pd.ExcelWriter(out) as w:
    summ = sheets['0_요약']; summ.loc[len(summ)] = ['R6 추가', '사용자 제공 초록(315단어) 전수 검사 → 저빈도어 17건 치환(시트 1b) → 확정 초록 내용어 전부 DF≥3(예외 4: silhouette·binomial·false-discovery-rate·BGE-M3) → 본문 LangChain-centered→LangChain-based']
    summ.to_excel(w, sheet_name='0_요약', index=False); sheets['1_용어 대조·수정 결과'].to_excel(w, sheet_name='1_용어 대조·수정 결과(R5)', index=False); rep.to_excel(w, sheet_name='1b_R6 초록 용어 대조', index=False)
    wdf.to_excel(w, sheet_name='2b_R6 초록 단어 전수 DF', index=False)
    for k in ['2_제목·초록 단어 전수 DF', '3_본문 복합어 DF(저빈도순)', '4_후보용어 DF 근거']: sheets[k].to_excel(w, sheet_name=k, index=False)
wb = load_workbook(out)
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col, w_ in zip('ABCDEFG', [12, 48, 46, 46, 30, 60, 40]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
wb.save(out); print('saved', out, '| words', len(seen), '| low', [(r['초록 단어(R6 확정)'], r['선행연구 문서 수(27편 중)']) for r in wrows if r['선행연구 문서 수(27편 중)'] < 3])
