# -*- coding: utf-8 -*-
"""Score the filled-in cluster_label_human_eval_blind_sheet.xlsx: mean ratings per level, Krippendorff's alpha (interval) across raters,
word-intrusion accuracy per rater and majority. Also scores human_eval_stratified_sample_400.xlsx (rater1/rater2 vs LLMs) if filled.
Usage: python score_label_eval.py
"""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))

def kripp_alpha(mat, metric='interval'):
    """mat: items x raters (NaN allowed). Krippendorff's alpha, interval or nominal."""
    mat = np.asarray(mat, dtype=float); vals = mat[~np.isnan(mat)]
    if len(vals) < 2: return np.nan
    cats = np.unique(vals); idx = {c: i for i, c in enumerate(cats)}
    O = np.zeros((len(cats), len(cats)))
    for row in mat:
        r = row[~np.isnan(row)]; m = len(r)
        if m < 2: continue
        for a in r:
            for b in r:
                if a is not b: pass
        for i, a in enumerate(r):
            for j, b in enumerate(r):
                if i != j: O[idx[a], idx[b]] += 1.0 / (m - 1)
    n = O.sum(); nc = O.sum(1)
    if metric == 'interval': D = (cats[:, None] - cats[None, :]) ** 2
    else: D = 1 - np.eye(len(cats))
    Do = (O * D).sum() / n; De = (np.outer(nc, nc) * D).sum() / (n * (n - 1))
    return 1 - Do / De if De > 0 else np.nan

f = os.path.join(HERE, 'cluster_label_human_eval_blind_sheet.xlsx')
if os.path.exists(f):
    cr = pd.read_excel(f, sheet_name='cluster_rating'); key = pd.read_excel(f, sheet_name='key'); wi = pd.read_excel(f, sheet_name='word_intrusion')
    cr = cr.merge(key, on='item_id')
    for dim in ['coherence', 'label_fit', 'distinctness']:
        cols = [c for c in cr.columns if c.endswith('_' + dim)]; M = cr[cols].apply(pd.to_numeric, errors='coerce')
        if M.notna().sum().sum() == 0: print(f'{dim}: not filled'); continue
        print(f'{dim}: mean={np.nanmean(M.values):.2f}  macro={np.nanmean(M[cr.level=="macro"].values):.2f}  meso={np.nanmean(M[cr.level=="meso"].values):.2f}  alpha(interval)={kripp_alpha(M.values):.3f}  n_raters_filled={int((M.notna().sum()>0).sum())}')
    wi = wi.merge(key[['item_id', 'intruder']], on='item_id')
    for rc in [c for c in wi.columns if c.endswith('_pick')]:
        p = pd.to_numeric(wi[rc], errors='coerce')
        if p.notna().sum() == 0: continue
        picked = [wi.loc[i, f'term{int(v)}'] if not np.isnan(v) else None for i, v in enumerate(p)]
        acc = np.mean([a == b for a, b in zip(picked, wi['intruder']) if a is not None]); print(f'word-intrusion {rc}: accuracy={acc:.3f} (chance=0.167)')
f2 = os.path.join(HERE, 'human_eval_stratified_sample_400.xlsx')
if os.path.exists(f2):
    s = pd.read_excel(f2, sheet_name='sample'); AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
    if s['rater1'].notna().any():
        cats = sorted(set(s['llm_qwen']) | set(s['llm_llama']) | set(s['rater1'].dropna()) | set(s['rater2'].dropna())); cid = {c: i for i, c in enumerate(cats)}
        M = s[['rater1', 'rater2']].apply(lambda col: col.map(cid)); print(f"human-human alpha(nominal, 8 cat)={kripp_alpha(M.values, 'nominal'):.3f}")
        hb = s['rater1'].isin(AG) & s['rater2'].isin(AG); lb = s['llm_qwen'].isin(AG) & s['llm_llama'].isin(AG)
        print(f"human precision(both agent)={hb.mean():.3f}  LLM precision={lb.mean():.3f}  human-LLM binary agreement={(hb==lb).mean():.3f}")
        from sklearn.metrics import cohen_kappa_score; print(f"kappa(human consensus vs LLM consensus, binary)={cohen_kappa_score(hb, lb):.3f}")
    else: print('human_eval_stratified_sample_400: rater columns empty')
