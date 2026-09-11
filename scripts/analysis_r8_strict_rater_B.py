# -*- coding: utf-8 -*-
"""R4 strict variant: weights = Rater C precision. Original docstring: R2 (2026-09-10): corpus-relevance robustness without human labels.
  F1 precision-weighted GLM  — each repository weighted by the LLM-audit precision of its segment (T0..T4),
                               so segments with more suspected non-agent repositories count less.
  F2 conservative-corpus GLM — drop the audit-sample repositories that at least one LLM called Non-agent /
                               Tutorial / Awesome / Paper-code / Other, and additionally drop, corpus-wide,
                               repositories whose metadata match a tutorial/awesome/paper lexicon.
  F3 worst-case reassignment — Monte-Carlo: in each of 200 draws, randomly flag (1 - precision_segment) of each
                               segment's repositories as non-agent and refit; report share of draws with same sign.
Outputs -> 30_분석결과/R1_revision/F_precision_robustness.xlsx
"""
import os, re, numpy as np, pandas as pd, statsmodels.api as sm
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, '30_분석결과'); OUT = os.path.join(RES, 'R1_revision'); AUD = os.path.join(ROOT, '40_감사_인간평가키트'); DATA = os.path.join(ROOT, '10_데이터수집')
df = pd.read_excel(os.path.join(RES, '문서_군집할당.xlsx'))
raw = pd.read_excel(os.path.join(DATA, 'github_ai_agent_raw_v2.xlsx'))[['full_name', 'description', 'topics']]
df = df.merge(raw, on='full_name', how='left')
prec = pd.Series({0: 0.750, 1: 0.417, 2: 0.750, 3: 0.792, 4: 0.792})   # strictest retained annotator (B) per-segment precision, 2026-09-10 (C excluded)
lab = pd.read_excel(os.path.join(RES, 'GLM_taxonomy_macro.xlsx')).set_index('cluster')['label']
dom = pd.read_excel(os.path.join(RES, '도메인_태깅.xlsx')); dom = dom[dom['full_name'].isin(df['full_name'])]
DOMS = ['Gaming', 'SoftwareDev/Coding', 'Web/Browser automation']

def glm(d, flag, w=None, window=None):
    """binomial GLM of flag share on year (weights optional). window=(a,b) restricts years."""
    w = np.ones(len(d)) if w is None else np.asarray(w, dtype=float)
    if window is not None:
        mask = d['year'].between(*window).values; d = d[mask]; w = w[mask]
    g = pd.DataFrame({'year': d['year'].values, 'y': d[flag].values * w, 'N': w}).groupby('year').sum().reset_index()
    m = sm.GLM(np.column_stack([g['y'], g['N'] - g['y']]), sm.add_constant(g['year'] - 2016), family=sm.families.Binomial()).fit()
    lo, hi = np.exp(m.conf_int().iloc[1]); return np.exp(m.params.iloc[1]), lo, hi

def series(d):
    out = {}
    for c in range(5): d[f'T{c}'] = (d['cluster'] == c).astype(int); out[f'T{c} {lab[c]}'] = f'T{c}'
    dd = d.merge(dom[['full_name'] + DOMS], on='full_name', how='left')
    for x in DOMS: dd[x] = dd[x].fillna(False).astype(int); out[x] = x
    return dd, out

base, names = series(df.copy())
rows = []
# F1 weights
w = base['cluster'].map(prec).values
# F2 conservative corpus
aud = pd.read_excel(os.path.join(AUD, '인간평가_층화표본400.xlsx'), sheet_name='sample'); AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
bad_aud = set(aud[~(aud['llm_qwen'].isin(AG) & aud['llm_llama'].isin(AG))]['full_name'])
lex = re.compile(r'\b(tutorial|tutorials|course|courses|lecture|awesome|curated|collection of|list of|cheat ?sheet|paper|papers|official (code|implementation)|implementation of|reproduc|homework|assignment|example[s]?|demo[s]?|template[s]?|boilerplate|starter)\b', re.I)
txt = (base['full_name'].fillna('') + ' ' + base['description'].fillna('') + ' ' + base['topics'].fillna('')).str.replace(';', ' ')
lex_flag = txt.str.contains(lex) | base['full_name'].str.lower().str.contains('awesome|tutorial|example|course|paper', regex=True)
cons = base[~base['full_name'].isin(bad_aud) & ~lex_flag].reset_index(drop=True)
print(f'conservative corpus: {len(cons)} of {len(base)} (lexicon-flagged {lex_flag.sum()}, audit-flagged {len(bad_aud)})')
rng = np.random.RandomState(42)
for name, col in names.items():
    r = {'series': name}
    r['full_OR'], r['full_lo'], r['full_hi'] = glm(base, col)
    r['win_OR'], r['win_lo'], r['win_hi'] = glm(base, col, window=(2023, 2025))
    r['pw_full_OR'], r['pw_full_lo'], r['pw_full_hi'] = glm(base, col, w=w)
    r['pw_win_OR'], r['pw_win_lo'], r['pw_win_hi'] = glm(base, col, w=w, window=(2023, 2025))
    r['cons_n'] = len(cons)
    r['cons_full_OR'], r['cons_full_lo'], r['cons_full_hi'] = glm(cons, col)
    r['cons_win_OR'], r['cons_win_lo'], r['cons_win_hi'] = glm(cons, col, window=(2023, 2025))
    # F3 Monte-Carlo worst case: drop (1-prec) share of each segment at random, 200 draws, window 2023-25 and full
    signs_full, signs_win = [], []
    for _ in range(200):
        keep = np.ones(len(base), bool)
        for c in range(5):
            idx = np.where(base['cluster'].values == c)[0]; k = int(round((1 - prec[c]) * len(idx)))
            keep[rng.choice(idx, k, replace=False)] = False
        sub = base[keep].reset_index(drop=True)
        signs_full.append(np.sign(np.log(glm(sub, col)[0]))); signs_win.append(np.sign(np.log(glm(sub, col, window=(2023, 2025))[0])))
    ref_full = np.sign(np.log(r['full_OR'])); ref_win = np.sign(np.log(r['win_OR']))
    r['mc_same_sign_full'] = float(np.mean(np.array(signs_full) == ref_full)); r['mc_same_sign_win'] = float(np.mean(np.array(signs_win) == ref_win))
    rows.append(r); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
res = pd.DataFrame(rows).round(3); res.to_excel(os.path.join(OUT, 'F3_precision_robustness_strict_raterB.xlsx'), index=False); print('saved')
