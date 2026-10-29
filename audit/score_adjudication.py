# -*- coding: utf-8 -*-
"""Score the completed R11 adjudication kit (review item 2). Run after the sheets are filled in.
  Sheet ① files  R11_adjudication_sheets_rater*.xlsx  -> independent re-annotation under the codebook: precision per rater,
                                                 Krippendorff's alpha (binary and 3-class), pairwise Cohen's kappa
  Sheet ② file   R11_adjudication_sheets_consensus.xlsx -> adjudicated labels: unanimous items keep their original binary label,
                                                 the 40 non-unanimous items take the adjudicated class
Both precision figures are reported as the equal-allocation sample rate and as the cluster-size weighted estimate.
Output: R11_adjudication_result.txt
"""
import os, glob, itertools, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
HERE = os.path.dirname(os.path.abspath(__file__))
_flat = os.path.isdir(os.path.join(os.path.dirname(HERE), 'results'))
H = pd.read_pickle(os.path.join(os.path.dirname(HERE), 'results', 'R11', '_human120.pkl') if _flat else os.path.join(HERE, '..', '01_reanalysis', '_human120.pkl'))
Nc = pd.Series({0: 2233, 1: 1925, 2: 3476, 3: 1121, 4: 846}); W = Nc / Nc.sum()
out = open(os.path.join(HERE, 'R11_adjudication_result.txt'), 'w', encoding='utf-8')
def log(s): print(s); out.write(s + '\n')
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
def weighted(pos):
    d = H[['cluster']].assign(pos=pos.values.astype(float)); pc = d.groupby('cluster')['pos'].mean(); nc = d.groupby('cluster').size()
    est = float((W * pc).sum()); se = float(np.sqrt((W ** 2 * pc * (1 - pc) / (nc - 1) * (1 - nc / Nc)).sum())); return est, est - 1.96 * se, est + 1.96 * se
def kripp(mat):
    mat = np.asarray(mat, dtype=float); cats = np.unique(mat[~np.isnan(mat)]); idx = {c: i for i, c in enumerate(cats)}; O = np.zeros((len(cats),) * 2)
    for row in mat:
        r = row[~np.isnan(row)]; m = len(r)
        if m < 2: continue
        for i, a in enumerate(r):
            for j, b in enumerate(r):
                if i != j: O[idx[a], idx[b]] += 1 / (m - 1)
    n = O.sum(); nc_ = O.sum(1); D = 1 - np.eye(len(cats)); return 1 - (O * D).sum() / n / ((np.outer(nc_, nc_) * D).sum() / (n * (n - 1)))
def read(f, sheet):
    d = pd.read_excel(f, sheet_name=sheet); d = d[['item_no', 'Judgment (1/2/3)', 'Rule no.']].rename(columns={'Judgment (1/2/3)': 'cls', 'Rule no.': 'rule'})
    d['cls'] = pd.to_numeric(d['cls'], errors='coerce'); return d
# ① independent re-annotation
files = sorted(glob.glob(os.path.join(HERE, 'R11_adjudication_sheets_rater*.xlsx')))
log(f'[①] independent re-annotation files: {len(files)}')
if len(files) >= 1:
    R = H[['item_no', 'cluster']].copy()
    for i, f in enumerate(files, 1):
        d = read(f, '① Independent reannotation 120'); R = R.merge(d[['item_no', 'cls']].rename(columns={'cls': f'R{i}'}), on='item_no', how='left')
        done = R[f'R{i}'].notna().sum(); pos = (R[f'R{i}'] == 1)
        lo, hi = wilson(pos.sum(), len(R)); w, wlo, whi = weighted(pos)
        log(f'  R{i} ({os.path.basename(f)}): completed {done}/120 | sample precision {pos.mean():.3f} [{lo:.3f},{hi:.3f}] | weighted {w:.3f} [{wlo:.3f},{whi:.3f}]')
    rc = [c for c in R.columns if c.startswith('R') and c[1:].isdigit()]
    if len(rc) >= 2:
        log(f'  alpha 3-class {kripp(R[rc].values):.3f} | alpha binary {kripp((R[rc] == 1).astype(float).where(R[rc].notna()).values):.3f}')
        for a, b in itertools.combinations(rc, 2):
            m = R[[a, b]].dropna(); log(f'  kappa {a}-{b} binary {cohen_kappa_score(m[a] == 1, m[b] == 1):.3f} | 3-class {cohen_kappa_score(m[a], m[b]):.3f}')
# ② adjudication
f2 = os.path.join(HERE, 'R11_adjudication_sheets_consensus.xlsx')
if os.path.exists(f2):
    d = read(f2, '② Consensus adjudication 40'); A = H[['item_no', 'cluster', 'n_pos', 'disagree']].merge(d, on='item_no', how='left')
    miss = A.loc[A['disagree'] & A['cls'].isna(), 'item_no'].tolist()
    log(f'[②] adjudicated {int((A["disagree"] & A["cls"].notna()).sum())}/40; missing {miss}')
    final = np.where(A['disagree'], A['cls'] == 1, A['n_pos'] == 3)
    pos = pd.Series(final); lo, hi = wilson(pos.sum(), len(pos)); w, wlo, whi = weighted(pos)
    log(f'  adjudicated precision: sample {pos.mean():.3f} [{lo:.3f},{hi:.3f}] | cluster-size weighted {w:.3f} [{wlo:.3f},{whi:.3f}]')
    log('  by cluster: ' + str(A.assign(pos=pos.values).groupby('cluster')['pos'].mean().round(3).to_dict()))
    log('  rules used: ' + str(A.loc[A['disagree'], 'rule'].value_counts().to_dict()))
else:
    log('[②] R11_adjudication_sheets_consensus.xlsx not found')
out.close()
