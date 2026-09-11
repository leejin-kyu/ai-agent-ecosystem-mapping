# -*- coding: utf-8 -*-
"""용어 표준화 결과보고 xlsx 생성. A=논문에 쓰인 용어(R4), B=선행연구에서 통용되는 용어(DF), C=바꾼 용어(R5), D=선행연구 DF(구/신), E=근거·비고, F=적용 위치.
시트2: 제목·초록 전수 단어 DF. 시트3: 본문 전문용어 DF 상위(검토 근거). 출력: 30_분석결과/용어검토/용어표준화_결과보고_260910.xlsx"""
import json, re, os, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_분석결과', '용어검토')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    hit = [k for k, d in docs.items() if any(p in d for p in pats)]; return len(hit), ', '.join(sorted(h[:4] + ' ' + h.split('_')[1][:12] for h in hit))
def wdf(phrase):  # 구성 단어별 DF 최소값
    ws = [w for w in re.findall(r"[a-z][a-z\-]+", phrase.lower()) if len(w) > 2 and w not in ('and', 'the', 'of', 'by', 'to', 'not', 'with', 'for')]
    return min((df(w)[0] for w in ws), default=0)
R4 = open(os.path.join(ROOT, '84_투고2_IEEEAccess_R4_260910_4인평가', '조판작업용_tex', 'main.tex'), encoding='utf-8').read().lower()
R5 = open(os.path.join(ROOT, '85_투고2_IEEEAccess_R5_260910_용어표준화', '조판작업용_tex', 'main.tex'), encoding='utf-8').read().lower()
rows = [
 ('제목', 'Semantic Segments', 'clusters (Blei 2003; Grootendorst 2022; Angelov 2020; Wang 2023 GoalEx 등 13편)', 'Clusters', '군집 산출물을 "segment"로 부르는 선행연구 없음. K-means 산출물의 통용 명칭은 cluster'),
 ('제목', 'Creation-Time Composition', 'composition (16편) / trends (13편)', 'Composition Trends', '"creation-time"은 선행연구 0편. 시간 변화는 trend(s)가 통용'),
 ('제목', 'Emergence', 'emergence (5편: Xi 2023, Wang 2023, Gu 2024 등)', 'Emergence (유지)', 'DF 5 ≥ 3, 유지'),
 ('제목', 'Mapping AI-Agent Repositories on GitHub', 'mapping (10편), AI agent (7편), repositories (6편)', '(유지)', '모든 단어 DF ≥ 3'),
 ('초록', 'semantic repository segments', 'clusters / clustering (13편·10편)', 'repository clusters', '동일'),
 ('초록', 'creation-time composition', 'composition (16), over time (13), creation (12)', 'composition of currently visible repositories by creation year', '선행연구 표현으로 풀어씀'),
 ('초록', 'temporal construct', 'construct (22) — 단, "temporal construct" 조합 0편', 'measured quantity', '연구방법론 용어를 일반어로'),
 ('초록', 'recursive date slicing', 'partition (6편)', 'recursive partition of each query by creation date', '"slicing" 0편'),
 ('초록', 'twelve-segment solution', 'cluster (13)', '12-cluster solution', '동일'),
 ('초록', 'macro segments', 'coarse (4) / fine-grained (11)', 'coarse clusters', '"macro" 2편, "meso" 0편 → coarse / fine-grained'),
 ('초록', 'stratified relevance audit', 'stratified (3), relevance (17), sample (다수)', 'Relevance was checked on a stratified sample', '"audit" 4편이나 "relevance audit" 조합 0편'),
 ('초록', 'locally hosted language-model classifiers', 'language model (다수), local (다수); "classifier" 1편', 'local language models', '"classifiers" 1편'),
 ('초록', 'provisional corpus precision', 'precision (9), estimate (다수)', 'estimate corpus precision', '"provisional" 0편'),
 ('초록', 'blind human raters', 'annotators (12), human-annotated (5), blind (8)', 'human annotators blind to the model labels', '"raters" 2편, "human raters" 0편'),
 ('초록', 'spline, segmented, restricted-window, and quarterly models', 'model (다수), specification(s) (5/3), alternative (다수)', 'alternative model specifications', '개별 통계모형명은 본문에서 정의; 초록은 통용어로'),
 ('초록', 'relevance-weighted, conservative-corpus, and Monte-Carlo re-estimation', 'robustness (13), weighted (6), filtering (11)', 'robustness checks that weight or filter the corpus', '조합어 0편'),
 ('초록', 'repository share', 'proportion (15)', 'proportion', '"share" 단독 18편이나 "repository share" 0편'),
 ('초록', 'Model Context Protocol infrastructure', 'Model Context Protocol (3), MCP server (2), server (다수)', 'Model Context Protocol (MCP) servers', '"infrastructure" 7편이나 MCP와의 조합 0편'),
 ('초록', 'coding-focused agents', 'code generation (5), programming (12)', 'code-generation agents', '"coding agent(s)" 0편'),
 ('초록', 'game agents', 'game (11)', 'game repositories', '"game agent" 1편'),
 ('초록', 'robust to functional form and to corpus impurity', 'robust (19), false positive (8)', 'robust (본문에서 model specification·false positives로 상술)', '"functional form" 0편, "impurity" 0편'),
 ('초록', 'full-window declines', 'period (14), decrease (다수)', 'decreases estimated over the full period', '"full-window" 0편'),
 ('초록', 'regime change', 'change point (Killick 2012; 표준 용어)', 'change point', '"regime" 2편 (다른 의미). change point는 인용 문헌의 정식 용어'),
 ('초록', 'reported as a temporal correlate, not a cause', 'aligned with (9), coincide (4)', 'is aligned with several events but not attributed to a cause', '"temporal correlate" 0편'),
 ('본문', 'segment / segments / segmentation (84회)', 'cluster / clusters / clustering', 'cluster / clusters / clustering', 'PELT의 "minimum segment size"는 알고리즘 파라미터라 유지(1회)'),
 ('본문', 'macro / meso (18회)', 'coarse / fine-grained', 'coarse / fine-grained', '동일'),
 ('본문', 'functional form / form-robust (18회)', 'specification (5)', 'model specification / specification-robust', '"model specification" 조합은 0편이나 통계학 표준 용어; 대안 "functional form"은 0편'),
 ('본문', 'regime change / regime boundary / changes regime (8회)', 'change point', 'change point / has a change point', '동일'),
 ('본문', 'temporal correlate(s) / temporal alignment(s) (7회)', 'coincide (4), aligned with (9), correlate (7)', 'coinciding event(s) / coincidence in time', '§VI-B 제목 "Coinciding Events, Not Causes"'),
 ('본문', 'corpus impurity / impurity (6회)', 'false positive(s) (8/7), noise (10)', 'false positives / false-positive rate', '§V-D 제목 "Robustness to False Positives"'),
 ('본문', 'lexicon / lexicon-defined / lexicon-tagged (19회)', 'keyword (11), keyword-based (2)', 'keyword list / keyword-based / keyword-tagged', '"lexicon" 0편'),
 ('본문', 'rater(s) / Rater / inter-rater reliability (50회)', 'annotator(s) (12), agreement (9), human-annotated (5)', 'annotator(s) / inter-annotator agreement', '"rater" 5편·"raters" 2편'),
 ('본문', 'cohort(s) (24회)', 'created (14), creation (12), year', 'creation-year group(s) / repositories by creation year', '"cohort" 0편'),
 ('본문', 'snapshot (9회)', 'data collection (9), collected (11)', 'collection time / collection', '"snapshot" 2편'),
 ('본문', 'survivor set (5회)', 'surviv- (4)', 'set of surviving repositories', '"survivorship"은 대안 부재로 유지(0편, 비고)'),
 ('본문', 'coding agents / coding-agent (18회)', 'code generation (5)', 'code-generation agents', '동일'),
 ('본문', 'MCP infrastructure (11회)', 'MCP server (2), Model Context Protocol (3)', 'MCP servers and tools', '동일'),
 ('본문', 'recursive date slicing / truncation-free', 'partition (6), truncation (4)', 'recursive partitioning by creation date / without truncation', '동일'),
 ('본문', 'corpus-scale', 'large-scale (17)', 'large-scale', '"corpus-scale" 0편'),
 ('본문', 'dormant', 'active/inactive (18/2)', 'inactive', '"dormant" 0편'),
 ('본문', 'tooling', 'tools', 'tools', '"tooling" 2편'),
 ('본문', 'present-day metadata', 'metadata (7), data collection (9)', 'metadata at collection time', '동일'),
 ('유지', 'adjusted Rand index / silhouette / binomial / odds ratio / spline / false discovery rate / Krippendorff', '(통계 표준 용어; 선행연구 27편은 통계 논문이 아니라 DF 0~1)', '유지', '분야 표준 통계 용어. 대안 없음. 비고로만 기록'),
 ('유지', 'change point / PELT', 'Killick 2012 (인용 문헌의 정식 용어)', '유지', 'DF 1이지만 인용 원문 용어'),
 ('유지', 'survivorship', '(대안 없음)', '유지', 'MSR 분야 관용어. 선행연구 DF 0 — 비고'),
 ('유지', 'exploratory / stability / reproducible / coherence / diversity / coverage / embedding / K-means / TF-IDF / LDA / NMF / BERTopic', 'DF 3~15', '유지', '모두 DF ≥ 3'),
]
rep = []
for sec, old, prior, new, note in rows:
    d_old = df(old)[0] if len(old.split()) <= 4 and '/' not in old else wdf(old); d_new = df(new)[0] if len(new.split()) <= 3 and '/' not in new and '(' not in new else wdf(new)
    rep.append({'구분': sec, 'A. 논문에 쓰인 용어 (R4)': old, 'B. 선행연구에서 통용되는 용어 (문서 수)': prior, 'C. 바꾼 용어 (R5)': new, 'D. 선행연구 DF: A → C (구성 단어 최소값)': f'{d_old} → {d_new}', 'E. 근거·비고': note})
rep = pd.DataFrame(rep)
ta = pd.read_csv(os.path.join(OUT, '용어DF_전수.csv'), encoding='utf-8-sig'); ta = ta[ta.section != '본문']
ta1 = ta[~ta.term.str.contains(' ')].sort_values(['section', 'prior_DF'])[['section', 'term', 'manuscript_freq', 'prior_DF', 'prior_docs']]; ta1.columns = ['구분', '단어(제목·초록, R5 기준)', '원고 빈도', '선행연구 문서 수(27편 중)', '출현 문헌']
body = pd.read_csv(os.path.join(OUT, '용어DF_전수.csv'), encoding='utf-8-sig'); body = body[(body.section == '본문') & (body.term.str.contains(' '))].sort_values(['prior_DF', 'manuscript_freq'], ascending=[True, False]).head(300)[['term', 'manuscript_freq', 'prior_DF', 'prior_docs']]; body.columns = ['본문 복합어(R5 기준)', '원고 빈도', '선행연구 문서 수', '출현 문헌']
cand = pd.read_csv(os.path.join(OUT, '후보용어DF.csv'), encoding='utf-8-sig'); cand.columns = ['용어군', '후보 용어', '선행연구 문서 수', '총 출현', '출현 문헌']
out = os.path.join(OUT, '용어표준화_결과보고_260910.xlsx')
with pd.ExcelWriter(out) as w:
    rep.to_excel(w, sheet_name='1_용어 대조·수정 결과', index=False); ta1.to_excel(w, sheet_name='2_제목·초록 단어 전수 DF', index=False); body.to_excel(w, sheet_name='3_본문 복합어 DF(저빈도순)', index=False); cand.to_excel(w, sheet_name='4_후보용어 DF 근거', index=False)
    pd.DataFrame({'항목': ['대조 대상', '기준', '선행연구', '방법', '결과', '유지(비고)', '산출물'], '내용': ['R4 원고 전체(제목·초록 전수 단어, 본문 전문용어)', '선행연구 27편 중 3편 이상에서 쓰인 용어만 통용어로 인정', '60_선행연구_PDF28편 (Blei 2003 … Menzen 2025; 1편은 텍스트 추출 실패로 27편)', 'PDF 전문 추출 → 용어 문서빈도(DF) 계산 → DF<3 용어를 DF≥3 통용어로 치환 → 재조판·수치 대조', '제목 2어 변경, 초록 전면 재작성(250단어, 모든 내용어 DF≥3; 예외=통계 표준어 4개·고유명사), 본문 20개 용어군 약 300회 치환', '통계 표준어(adjusted Rand index·silhouette·binomial·odds ratio·spline·FDR·Krippendorff)와 인용 원문 용어(change point·PELT)·survivorship은 대안 부재로 유지', '85_투고2_IEEEAccess_R5_260910_용어표준화/']}).to_excel(w, sheet_name='0_요약', index=False)
wb = load_workbook(out)
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col, w_ in zip('ABCDEFG', [10, 42, 48, 42, 22, 60, 40]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
wb.move_sheet('0_요약', offset=-4); wb.save(out); print('saved', out, len(rep), 'rows')
