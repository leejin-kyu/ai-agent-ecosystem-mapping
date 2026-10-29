# -*- coding: utf-8 -*-
"""Generate the term-standardization report xlsx. A = term used in the paper (R4), B = term commonly used in prior work (DF), C = changed term (R5), D = prior-work DF (old/new), E = rationale/notes, F = where applied.
Sheet 2: DF of every word in the title and abstract. Sheet 3: top DF of technical terms in the body (review evidence). Output: 30_analysis_results/term_review/term_standardization_report_260910.xlsx"""
import json, re, os, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_analysis_results', 'term_review')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, 'prior_work_fulltext.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    hit = [k for k, d in docs.items() if any(p in d for p in pats)]; return len(hit), ', '.join(sorted(h[:4] + ' ' + h.split('_')[1][:12] for h in hit))
def wdf(phrase):  # minimum DF over the constituent words
    ws = [w for w in re.findall(r"[a-z][a-z\-]+", phrase.lower()) if len(w) > 2 and w not in ('and', 'the', 'of', 'by', 'to', 'not', 'with', 'for')]
    return min((df(w)[0] for w in ws), default=0)
R4 = open(os.path.join(ROOT, '84_submission2_IEEEAccess_R4_260910_four_rater_eval', 'typesetting_tex', 'main.tex'), encoding='utf-8').read().lower()
R5 = open(os.path.join(ROOT, '85_submission2_IEEEAccess_R5_260910_term_standardization', 'typesetting_tex', 'main.tex'), encoding='utf-8').read().lower()
rows = [
 ('title', 'Semantic Segments', 'clusters (Blei 2003; Grootendorst 2022; Angelov 2020; Wang 2023 GoalEx and others, 13 papers)', 'Clusters', 'No prior work calls clustering outputs "segments". The common name for K-means outputs is cluster'),
 ('title', 'Creation-Time Composition', 'composition (16 papers) / trends (13 papers)', 'Composition Trends', '"creation-time" appears in 0 prior-work papers. Change over time is commonly called trend(s)'),
 ('title', 'Emergence', 'emergence (5 papers: Xi 2023, Wang 2023, Gu 2024, and others)', 'Emergence (retained)', 'DF 5 ≥ 3, retained'),
 ('title', 'Mapping AI-Agent Repositories on GitHub', 'mapping (10 papers), AI agent (7 papers), repositories (6 papers)', '(retained)', 'All words DF ≥ 3'),
 ('abstract', 'semantic repository segments', 'clusters / clustering (13 papers, 10 papers)', 'repository clusters', 'Same as above'),
 ('abstract', 'creation-time composition', 'composition (16), over time (13), creation (12)', 'composition of currently visible repositories by creation year', 'Spelled out using prior-work wording'),
 ('abstract', 'temporal construct', 'construct (22) - but the combination "temporal construct" appears in 0 papers', 'measured quantity', 'Research-methodology term replaced by plain wording'),
 ('abstract', 'recursive date slicing', 'partition (6 papers)', 'recursive partition of each query by creation date', '"slicing" 0 papers'),
 ('abstract', 'twelve-segment solution', 'cluster (13)', '12-cluster solution', 'Same as above'),
 ('abstract', 'macro segments', 'coarse (4) / fine-grained (11)', 'coarse clusters', '"macro" 2 papers, "meso" 0 papers -> coarse / fine-grained'),
 ('abstract', 'stratified relevance audit', 'stratified (3), relevance (17), sample (many)', 'Relevance was checked on a stratified sample', '"audit" in 4 papers, but the combination "relevance audit" in 0 papers'),
 ('abstract', 'locally hosted language-model classifiers', 'language model (many), local (many); "classifier" 1 paper', 'local language models', '"classifiers" 1 paper'),
 ('abstract', 'provisional corpus precision', 'precision (9), estimate (many)', 'estimate corpus precision', '"provisional" 0 papers'),
 ('abstract', 'blind human raters', 'annotators (12), human-annotated (5), blind (8)', 'human annotators blind to the model labels', '"raters" 2 papers, "human raters" 0 papers'),
 ('abstract', 'spline, segmented, restricted-window, and quarterly models', 'model (many), specification(s) (5/3), alternative (many)', 'alternative model specifications', 'Individual statistical model names are defined in the body; the abstract uses common terms'),
 ('abstract', 'relevance-weighted, conservative-corpus, and Monte-Carlo re-estimation', 'robustness (13), weighted (6), filtering (11)', 'robustness checks that weight or filter the corpus', 'Compound terms 0 papers'),
 ('abstract', 'repository share', 'proportion (15)', 'proportion', '"share" alone 18 papers, but "repository share" 0 papers'),
 ('abstract', 'Model Context Protocol infrastructure', 'Model Context Protocol (3), MCP server (2), server (many)', 'Model Context Protocol (MCP) servers', '"infrastructure" 7 papers, but its combination with MCP 0 papers'),
 ('abstract', 'coding-focused agents', 'code generation (5), programming (12)', 'code-generation agents', '"coding agent(s)" 0 papers'),
 ('abstract', 'game agents', 'game (11)', 'game repositories', '"game agent" 1 paper'),
 ('abstract', 'robust to functional form and to corpus impurity', 'robust (19), false positive (8)', 'robust (detailed in the body as model specification / false positives)', '"functional form" 0 papers, "impurity" 0 papers'),
 ('abstract', 'full-window declines', 'period (14), decrease (many)', 'decreases estimated over the full period', '"full-window" 0 papers'),
 ('abstract', 'regime change', 'change point (Killick 2012; standard term)', 'change point', '"regime" 2 papers (different meaning). change point is the formal term of the cited reference'),
 ('abstract', 'reported as a temporal correlate, not a cause', 'aligned with (9), coincide (4)', 'is aligned with several events but not attributed to a cause', '"temporal correlate" 0 papers'),
 ('body', 'segment / segments / segmentation (84 occurrences)', 'cluster / clusters / clustering', 'cluster / clusters / clustering', 'The PELT "minimum segment size" is an algorithm parameter and is retained (1 occurrence)'),
 ('body', 'macro / meso (18 occurrences)', 'coarse / fine-grained', 'coarse / fine-grained', 'Same as above'),
 ('body', 'functional form / form-robust (18 occurrences)', 'specification (5)', 'model specification / specification-robust', 'The combination "model specification" appears in 0 papers but is a standard statistical term; the alternative "functional form" appears in 0 papers'),
 ('body', 'regime change / regime boundary / changes regime (8 occurrences)', 'change point', 'change point / has a change point', 'Same as above'),
 ('body', 'temporal correlate(s) / temporal alignment(s) (7 occurrences)', 'coincide (4), aligned with (9), correlate (7)', 'coinciding event(s) / coincidence in time', 'Section VI-B title "Coinciding Events, Not Causes"'),
 ('body', 'corpus impurity / impurity (6 occurrences)', 'false positive(s) (8/7), noise (10)', 'false positives / false-positive rate', 'Section V-D title "Robustness to False Positives"'),
 ('body', 'lexicon / lexicon-defined / lexicon-tagged (19 occurrences)', 'keyword (11), keyword-based (2)', 'keyword list / keyword-based / keyword-tagged', '"lexicon" 0 papers'),
 ('body', 'rater(s) / Rater / inter-rater reliability (50 occurrences)', 'annotator(s) (12), agreement (9), human-annotated (5)', 'annotator(s) / inter-annotator agreement', '"rater" 5 papers, "raters" 2 papers'),
 ('body', 'cohort(s) (24 occurrences)', 'created (14), creation (12), year', 'creation-year group(s) / repositories by creation year', '"cohort" 0 papers'),
 ('body', 'snapshot (9 occurrences)', 'data collection (9), collected (11)', 'collection time / collection', '"snapshot" 2 papers'),
 ('body', 'survivor set (5 occurrences)', 'surviv- (4)', 'set of surviving repositories', '"survivorship" retained for lack of an alternative (0 papers, noted)'),
 ('body', 'coding agents / coding-agent (18 occurrences)', 'code generation (5)', 'code-generation agents', 'Same as above'),
 ('body', 'MCP infrastructure (11 occurrences)', 'MCP server (2), Model Context Protocol (3)', 'MCP servers and tools', 'Same as above'),
 ('body', 'recursive date slicing / truncation-free', 'partition (6), truncation (4)', 'recursive partitioning by creation date / without truncation', 'Same as above'),
 ('body', 'corpus-scale', 'large-scale (17)', 'large-scale', '"corpus-scale" 0 papers'),
 ('body', 'dormant', 'active/inactive (18/2)', 'inactive', '"dormant" 0 papers'),
 ('body', 'tooling', 'tools', 'tools', '"tooling" 2 papers'),
 ('body', 'present-day metadata', 'metadata (7), data collection (9)', 'metadata at collection time', 'Same as above'),
 ('retained', 'adjusted Rand index / silhouette / binomial / odds ratio / spline / false discovery rate / Krippendorff', '(standard statistical terms; the 27 prior-work papers are not statistics papers, hence DF 0-1)', 'retained', 'Standard statistical terms of the field. No alternative. Recorded as a note only'),
 ('retained', 'change point / PELT', 'Killick 2012 (formal term of the cited reference)', 'retained', 'DF 1, but the term of the cited original'),
 ('retained', 'survivorship', '(no alternative)', 'retained', 'Customary term in the MSR field. Prior-work DF 0 - noted'),
 ('retained', 'exploratory / stability / reproducible / coherence / diversity / coverage / embedding / K-means / TF-IDF / LDA / NMF / BERTopic', 'DF 3-15', 'retained', 'All DF ≥ 3'),
]
rep = []
for sec, old, prior, new, note in rows:
    d_old = df(old)[0] if len(old.split()) <= 4 and '/' not in old else wdf(old); d_new = df(new)[0] if len(new.split()) <= 3 and '/' not in new and '(' not in new else wdf(new)
    rep.append({'Section': sec, 'A. Term used in the paper (R4)': old, 'B. Term commonly used in prior work (number of papers)': prior, 'C. Changed term (R5)': new, 'D. Prior-work DF: A -> C (minimum over constituent words)': f'{d_old} → {d_new}', 'E. Rationale / notes': note})
rep = pd.DataFrame(rep)
ta = pd.read_csv(os.path.join(OUT, 'term_DF_full.csv'), encoding='utf-8-sig'); ta = ta[ta.section != 'body']
ta1 = ta[~ta.term.str.contains(' ')].sort_values(['section', 'prior_DF'])[['section', 'term', 'manuscript_freq', 'prior_DF', 'prior_docs']]; ta1.columns = ['Section', 'Word (title/abstract, as of R5)', 'Manuscript frequency', 'Prior-work papers (of 27)', 'Papers where it occurs']
body = pd.read_csv(os.path.join(OUT, 'term_DF_full.csv'), encoding='utf-8-sig'); body = body[(body.section == 'body') & (body.term.str.contains(' '))].sort_values(['prior_DF', 'manuscript_freq'], ascending=[True, False]).head(300)[['term', 'manuscript_freq', 'prior_DF', 'prior_docs']]; body.columns = ['Body compound term (as of R5)', 'Manuscript frequency', 'Prior-work papers', 'Papers where it occurs']
cand = pd.read_csv(os.path.join(OUT, 'candidate_term_DF.csv'), encoding='utf-8-sig'); cand.columns = ['Term group', 'Candidate term', 'Prior-work papers', 'Total occurrences', 'Papers where it occurs']
out = os.path.join(OUT, 'term_standardization_report_260910.xlsx')
with pd.ExcelWriter(out) as w:
    rep.to_excel(w, sheet_name='1_Term comparison and edits', index=False); ta1.to_excel(w, sheet_name='2_Title-abstract word DF', index=False); body.to_excel(w, sheet_name='3_Body compound DF (low first)', index=False); cand.to_excel(w, sheet_name='4_Candidate term DF evidence', index=False)
    pd.DataFrame({'Item': ['Compared material', 'Criterion', 'Prior work', 'Method', 'Result', 'Retained (notes)', 'Output'], 'Content': ['Entire R4 manuscript (every word of the title and abstract, technical terms of the body)', 'Only terms used in at least 3 of the 27 prior-work papers are accepted as common terms', '60_prior_work_PDFs_28 (Blei 2003 … Menzen 2025; text extraction failed for 1 paper, hence 27)', 'Extract PDF full texts -> compute term document frequency (DF) -> replace terms with DF<3 by common terms with DF≥3 -> re-typeset and check numbers', 'Title: 2 words changed; abstract fully rewritten (250 words, all content words DF≥3; exceptions = 4 standard statistical terms and proper nouns); body: about 300 replacements in 20 term groups', 'Standard statistical terms (adjusted Rand index, silhouette, binomial, odds ratio, spline, FDR, Krippendorff), terms of cited originals (change point, PELT) and survivorship are retained for lack of an alternative', '85_submission2_IEEEAccess_R5_260910_term_standardization/']}).to_excel(w, sheet_name='0_Summary', index=False)
wb = load_workbook(out)
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col, w_ in zip('ABCDEFG', [10, 42, 48, 42, 22, 60, 40]): ws.column_dimensions[col].width = w_
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
wb.move_sheet('0_Summary', offset=-4); wb.save(out); print('saved', out, len(rep), 'rows')
