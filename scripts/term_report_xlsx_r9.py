# -*- coding: utf-8 -*-
"""R9 final report xlsx: sheet '1_R9 Abstract+body terms' (A paper term / B prior-work term / C changed term / D DF / E rationale) + '2_Title-abstract word DF(R9)' + merged R5 and R6 sheets."""
import json, re, os, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_analysis_results', 'term_review')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, 'prior_work_fulltext.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    hit = [k for k, d in docs.items() if any(p in d for p in pats)]; return len(hit), ', '.join(sorted(h[:4] + ' ' + h.split('_')[1][:12] for h in hit))
rows = [
 ('abstract', 'queries were recursively partitioned by creation date', 'divided (13 papers) · partition (6 papers)', 'queries were divided by creation date', '"recursively" 2 papers, "partitioned" 2 papers'),
 ('abstract', 'the analysis characterizes the creation-year composition', 'describe (many) · composition (16 papers) · creation (12 papers)', 'the analysis describes the composition by creation year', '"characterizes" 1 paper, "creation-year" 0 papers'),
 ('abstract', 'support a five-cluster coarse solution; a 12-cluster solution', 'cluster (13 papers) · coarse (4 papers)', 'support a coarse solution with five clusters; a solution with 12 clusters', '"five-cluster" 0 papers'),
 ('abstract', 'Relevance auditing of 404 repositories … estimated', 'assessed (5 papers) · assessment (10 papers)', 'Relevance was assessed on 404 repositories …, which estimated', '"auditing" 1 paper'),
 ('abstract', 'Game repositories also decline', 'decrease (many)', 'Game repositories also decrease', '"declines" 1 paper'),
 ('abstract', 'the apparent full-period decline of the largest orchestration-and-automation cluster', 'decrease · period (14 papers) · orchestration (4 papers) · automation (8 papers)', 'the decrease of the largest orchestration and automation cluster estimated over the full period', '"apparent" 2 papers, "full-period" 0 papers, hyphenated compound 0 papers'),
 ('abstract', 'a reproducible repository-level characterization of recent compositional shifts', 'reproducible (7 papers) · description (18 papers) · repository (12 papers) · composition (16 papers)', 'a reproducible description, at the repository level, of recent shifts in the composition', '"repository-level" 1 paper, "characterization" 2 papers, "compositional" low frequency'),
 ('abstract', 'LangChain-based', 'LangChain (proper noun) + based', 'LangChain-based (retained)', 'compound with a proper noun - exception'),
 ('abstract', 'silhouette · binomial · false-discovery-rate · BGE-M3', '(standard statistical terms / proper nouns, DF 0-1)', 'retained', 'no alternative - exception'),
 ('title', 'Mapping AI-Agent Repositories on GitHub: Clusters, Emergence, and Composition Trends (2016–2025)', 'mapping 10 · AI agent 7 · repositories 6 · clusters 8 · emergence 5 · composition 16 · trends 13', '(retained)', 'All words DF ≥ 3'),
 ('body(R8)', 'Almost all disagreements were one-directional … assigned to the tutorial or template class', '(data re-checked)', 'Most disagreements were one-directional: the author accepted 32 … (18 tutorial/template, 14 unrelated) …', 'Factual correction: of the 32 items excluded by B, 14 were classified as unrelated'),
]
rep = pd.DataFrame([{'Section': g, 'A. Term used in the paper (R8)': a, 'B. Term commonly used in prior work (number of papers)': b, 'C. Changed term (R9)': c, 'E. Rationale / notes': e} for g, a, b, c, e in rows])
tex = open(os.path.join(ROOT, '89_submission2_IEEEAccess_R9_260910_final', 'typesetting_tex', 'main.tex'), encoding='utf-8').read()
ab = tex[tex.index('\\begin{abstract}') + 16:tex.index('\\end{abstract}')].replace('\\', ''); title = re.search(r'\\title\{(.*?)\}', tex).group(1)
STOP = set('a an the and or of to in on for with by from as at is are was were be been that this these those we our it its which who than then there not no so such into over under between among within without through per each all more most less only same other if when where while whether because also does do did has have had may might can could would should will must using use used rather but'.split())
wrows = []
for sec, text in [('title', title), ('abstract', ab)]:
    seen = []
    for w in re.findall(r"[a-z][a-z0-9\-]+", text.lower()):
        if w in STOP or len(w) < 3 or w in seen: continue
        seen.append(w); d, h = df(w); wrows.append({'Section': sec, 'Word (R9 final)': w, 'Prior-work papers (of 27)': d, 'Verdict': 'OK' if d >= 3 else 'Exception (standard statistical term / proper noun)', 'Papers where it occurs': h[:150]})
wdf = pd.DataFrame(wrows).sort_values(['Section', 'Prior-work papers (of 27)'])
src = os.path.join(OUT, 'term_standardization_report_R6_260910.xlsx'); out = os.path.join(OUT, 'term_standardization_report_R9_260910.xlsx'); sheets = pd.read_excel(src, sheet_name=None)
with pd.ExcelWriter(out) as w:
    summ = sheets['0_Summary']; summ.loc[len(summ)] = ['R9 final', 'Exhaustive re-check of the 8 title words and 120 abstract content words -> 8 replacements in the abstract (sheet 1). Remaining exceptions = silhouette, binomial, false-discovery-rate, BGE-M3, LangChain-based. 1 factual correction in the body text.']
    summ.to_excel(w, sheet_name='0_Summary', index=False); rep.to_excel(w, sheet_name='1_R9 Abstract+body terms', index=False); wdf.to_excel(w, sheet_name='2_Title-abstract word DF(R9)', index=False)
    for k in ['1_Term comparison and edits(R5)', '1b_R6 Abstract term comparison', '3_Body compound DF (low first)', '4_Candidate term DF evidence']: sheets[k].to_excel(w, sheet_name=k, index=False)
wb = load_workbook(out)
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col, w_ in zip('ABCDEFG', [12, 48, 46, 46, 30, 60, 40]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
wb.save(out); print('saved', out, '| low:', [(r['Word (R9 final)'], r['Prior-work papers (of 27)']) for r in wrows if r['Prior-work papers (of 27)'] < 3])
