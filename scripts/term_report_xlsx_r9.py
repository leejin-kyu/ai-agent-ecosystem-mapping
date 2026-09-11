# -*- coding: utf-8 -*-
"""R9 최종 결과보고 xlsx: 시트 '1_R9 초록 용어 대조'(A 논문 용어/B 선행연구 용어/C 바꾼 용어/D DF/E 근거) + '2_제목·초록 단어 전수 DF(R9)' + R5·R6 시트 병합."""
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
 ('초록', 'queries were recursively partitioned by creation date', 'divided (13편) · partition (6편)', 'queries were divided by creation date', '"recursively" 2편, "partitioned" 2편'),
 ('초록', 'the analysis characterizes the creation-year composition', 'describe (다수) · composition (16편) · creation (12편)', 'the analysis describes the composition by creation year', '"characterizes" 1편, "creation-year" 0편'),
 ('초록', 'support a five-cluster coarse solution; a 12-cluster solution', 'cluster (13편) · coarse (4편)', 'support a coarse solution with five clusters; a solution with 12 clusters', '"five-cluster" 0편'),
 ('초록', 'Relevance auditing of 404 repositories … estimated', 'assessed (5편) · assessment (10편)', 'Relevance was assessed on 404 repositories …, which estimated', '"auditing" 1편'),
 ('초록', 'Game repositories also decline', 'decrease (다수)', 'Game repositories also decrease', '"declines" 1편'),
 ('초록', 'the apparent full-period decline of the largest orchestration-and-automation cluster', 'decrease · period (14편) · orchestration (4편) · automation (8편)', 'the decrease of the largest orchestration and automation cluster estimated over the full period', '"apparent" 2편, "full-period" 0편, 하이픈 복합어 0편'),
 ('초록', 'a reproducible repository-level characterization of recent compositional shifts', 'reproducible (7편) · description (18편) · repository (12편) · composition (16편)', 'a reproducible description, at the repository level, of recent shifts in the composition', '"repository-level" 1편, "characterization" 2편, "compositional" 저빈도'),
 ('초록', 'LangChain-based', 'LangChain(고유명사) + based', 'LangChain-based (유지)', '고유명사 복합어 — 예외'),
 ('초록', 'silhouette · binomial · false-discovery-rate · BGE-M3', '(통계 표준어·고유명사, DF 0~1)', '유지', '대안 없음 — 예외'),
 ('제목', 'Mapping AI-Agent Repositories on GitHub: Clusters, Emergence, and Composition Trends (2016–2025)', 'mapping 10 · AI agent 7 · repositories 6 · clusters 8 · emergence 5 · composition 16 · trends 13', '(유지)', '모든 단어 DF ≥ 3'),
 ('본문(R8)', 'Almost all disagreements were one-directional … assigned to the tutorial or template class', '(데이터 재검산)', 'Most disagreements were one-directional: the author accepted 32 … (18 tutorial/template, 14 unrelated) …', '사실 정정: B 제외 32건 중 14건은 무관 분류'),
]
rep = pd.DataFrame([{'구분': g, 'A. 논문에 쓰인 용어 (R8)': a, 'B. 선행연구에서 통용되는 용어 (문서 수)': b, 'C. 바꾼 용어 (R9)': c, 'E. 근거·비고': e} for g, a, b, c, e in rows])
tex = open(os.path.join(ROOT, '89_투고2_IEEEAccess_R9_260910_최종', '조판작업용_tex', 'main.tex'), encoding='utf-8').read()
ab = tex[tex.index('\\begin{abstract}') + 16:tex.index('\\end{abstract}')].replace('\\', ''); title = re.search(r'\\title\{(.*?)\}', tex).group(1)
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must using use used rather but'.split())
wrows = []
for sec, text in [('제목', title), ('초록', ab)]:
    seen = []
    for w in re.findall(r"[a-z][a-z0-9\-]+", text.lower()):
        if w in STOP or len(w) < 3 or w in seen: continue
        seen.append(w); d, h = df(w); wrows.append({'구분': sec, '단어 (R9 확정)': w, '선행연구 문서 수 (27편 중)': d, '판정': 'OK' if d >= 3 else '예외(통계 표준어/고유명사)', '출현 문헌': h[:150]})
wdf = pd.DataFrame(wrows).sort_values(['구분', '선행연구 문서 수 (27편 중)'])
src = os.path.join(OUT, '용어표준화_결과보고_R6_260910.xlsx'); out = os.path.join(OUT, '용어표준화_결과보고_R9_260910.xlsx'); sheets = pd.read_excel(src, sheet_name=None)
with pd.ExcelWriter(out) as w:
    summ = sheets['0_요약']; summ.loc[len(summ)] = ['R9 최종', '제목 8단어·초록 120 내용어 전수 재검사 → 초록 8건 치환(시트 1). 잔여 예외=silhouette·binomial·false-discovery-rate·BGE-M3·LangChain-based. 본문 서술 1건 사실 정정.']
    summ.to_excel(w, sheet_name='0_요약', index=False); rep.to_excel(w, sheet_name='1_R9 초록·본문 용어 대조', index=False); wdf.to_excel(w, sheet_name='2_제목·초록 단어 전수 DF(R9)', index=False)
    for k in ['1_용어 대조·수정 결과(R5)', '1b_R6 초록 용어 대조', '3_본문 복합어 DF(저빈도순)', '4_후보용어 DF 근거']: sheets[k].to_excel(w, sheet_name=k, index=False)
wb = load_workbook(out)
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col, w_ in zip('ABCDEFG', [12, 48, 46, 46, 30, 60, 40]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
wb.save(out); print('saved', out, '| low:', [(r['단어 (R9 확정)'], r['선행연구 문서 수 (27편 중)']) for r in wrows if r['선행연구 문서 수 (27편 중)'] < 3])
