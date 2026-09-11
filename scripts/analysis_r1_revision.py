# -*- coding: utf-8 -*-
"""
R1 revision analyses (2026-09-08) responding to the IEEE comment (9/4):
  A. K-selection composite table (silhouette, CH, DB, 20-seed ARI, bootstrap ARI, balance, c_v)  -> comment 3
  B. GLM functional-form sensitivity: log-linear vs natural-spline(df=3) vs segmented(2023) vs 2023-25 window
     vs quarterly-resolution model                                                                   -> comment 7
  C. Survivorship / activity descriptives by creation cohort (pushed_at, archived, forks)         -> comment 5, minor
  D. Audit-sample precision by cluster and period + tutorial/awesome share                          -> comment 1, minor
  E. Representative repositories per macro/meso cluster (nearest centroid + top stars)              -> minor
Run from the paper root:  python 20_분석코드/analysis_r1_revision.py
Outputs -> 30_분석결과/R1_revision/
"""
import os, sys, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, '30_분석결과'); OUT = os.path.join(RES, 'R1_revision'); os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, '10_데이터수집'); AUD = os.path.join(ROOT, '40_감사_인간평가키트')
SNAPSHOT = pd.Timestamp('2026-08-08', tz='UTC')
def log(m): print(m, flush=True)

assign = pd.read_excel(os.path.join(RES, '문서_군집할당.xlsx'))
raw = pd.read_excel(os.path.join(DATA, 'github_ai_agent_raw_v2.xlsx'))
raw['created_at'] = pd.to_datetime(raw['created_at'], utc=True); raw['pushed_at'] = pd.to_datetime(raw['pushed_at'], utc=True)
df = assign.merge(raw[['full_name', 'created_at', 'pushed_at', 'forks', 'description', 'topics']], on='full_name', how='left')
assert df['created_at'].notna().all(), 'merge failed'
df['quarter'] = df['created_at'].dt.to_period('Q').astype(str)
df['month_idx'] = (df['created_at'].dt.year - 2016) * 12 + df['created_at'].dt.month - 1
log(f'corpus n={len(df)}')

# ───────────────────────── A. K-selection composite ─────────────────────────
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score
from sklearn.preprocessing import normalize
emb = np.load(os.path.join(RES, 'embeddings.npy')); keys = np.load(os.path.join(RES, 'emb_keys.npy'), allow_pickle=True)
key2idx = {k: i for i, k in enumerate(keys)}
idx = np.array([key2idx[k] for k in df['full_name']]); X = normalize(emb[idx])   # cosine geometry via L2-normalised vectors
rng = np.random.RandomState(100); sub = rng.choice(len(X), 5000, replace=False)
cv_sweep = pd.read_excel(os.path.join(RES, '본비교_k스윕.xlsx')); cv_bge = cv_sweep[cv_sweep['method'].str.startswith('BGE')].set_index('k')['c_v']
A_FILE = os.path.join(OUT, 'A_k_selection_composite.xlsx')
rows = []
K_GRID = list(range(2, 16)) + [20, 25, 30]
SEEDS = list(range(10))   # 10 seeds / 10 bootstraps for the k-sweep (paper's k=5 result used 20; identical grid available via SEEDS=range(20))
NI = 3
for k in (K_GRID if not os.path.exists(A_FILE) else []):
    ref = KMeans(k, n_init=10, random_state=100).fit(X); lab = ref.labels_
    sil = silhouette_score(X[sub], lab[sub], metric='cosine')
    ch = calinski_harabasz_score(X, lab); db = davies_bouldin_score(X, lab)
    sizes = np.bincount(lab); balance = sizes.min() / sizes.max(); smallest = sizes.min() / len(lab)
    seed_ari = [adjusted_rand_score(lab, KMeans(k, n_init=NI, random_state=s).fit(X).labels_) for s in SEEDS if s != 100]
    boot_ari = []
    for s in SEEDS:
        r = np.random.RandomState(1000 + s); bi = r.choice(len(X), int(0.8 * len(X)), replace=False)
        bl = KMeans(k, n_init=NI, random_state=s).fit(X[bi]).labels_
        boot_ari.append(adjusted_rand_score(lab[bi], bl))
    rows.append(dict(k=k, silhouette=round(sil, 4), calinski_harabasz=round(ch, 1), davies_bouldin=round(db, 3),
                     seed_ARI_median=round(np.median(seed_ari), 3), seed_ARI_min=round(min(seed_ari), 3),
                     boot_ARI_median=round(np.median(boot_ari), 3), boot_ARI_min=round(min(boot_ari), 3),
                     size_balance=round(balance, 3), smallest_share=round(smallest, 3), c_v=cv_bge.get(k, np.nan)))
    log(f'k={k} sil={sil:.4f} CH={ch:.0f} DB={db:.3f} seedARI={np.median(seed_ari):.3f} bootARI={np.median(boot_ari):.3f} bal={balance:.3f}')
if rows: pd.DataFrame(rows).to_excel(A_FILE, index=False)
else: log('A: reusing existing ' + A_FILE)

# ───────────────────────── B. GLM functional-form sensitivity ─────────────────────────
import statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
macro_lab = pd.read_excel(os.path.join(RES, 'GLM_taxonomy_macro.xlsx')).set_index('cluster')['label']
meso_lab = pd.read_excel(os.path.join(RES, 'GLM_taxonomy_meso.xlsx')).set_index('cluster')['label']

def yearly_counts(d, col, c):
    g = d.groupby('year').agg(N=('full_name', 'size'), y=(col, lambda s: (s == c).sum())).reset_index(); g['t'] = g['year'] - 2016; return g

def fit_forms(g, name):
    """Return dict of OR/yr (or slope) estimates under alternative functional forms."""
    out = dict(cluster=name)
    ep = g[['y', 'N']].copy(); ep['fail'] = ep['N'] - ep['y']; endog = ep[['y', 'fail']].values
    # 1 log-linear (baseline, identical to paper)
    m1 = sm.GLM(endog, sm.add_constant(g['t']), family=sm.families.Binomial()).fit()
    out['loglin_OR'] = np.exp(m1.params.iloc[1]); out['loglin_lo'], out['loglin_hi'] = np.exp(m1.conf_int().iloc[1]); out['loglin_p'] = m1.pvalues.iloc[1]
    # 2 natural cubic spline df=3 on t: report average marginal slope 2023-25 (finite-difference on logit) + LR test vs linear
    import patsy
    Xs = patsy.dmatrix('cr(t, df=3)', g, return_type='dataframe')
    m2 = sm.GLM(endog, Xs, family=sm.families.Binomial()).fit()
    pred = np.asarray(m2.predict(Xs)); logit = np.log(pred / (1 - pred))
    sel = g['year'].between(2023, 2025).values
    out['spline_avg_OR_2023_25'] = np.exp(np.mean(np.diff(logit[sel]))) if sel.sum() >= 2 else np.nan
    out['spline_avg_OR_full'] = np.exp((logit[-1] - logit[0]) / (len(logit) - 1))
    out['spline_LR_p_vs_linear'] = 1 - __import__('scipy').stats.chi2.cdf(2 * (m2.llf - m1.llf), Xs.shape[1] - 2)
    out['spline_monotone_2023_25'] = bool(np.all(np.sign(np.diff(logit[sel])) == np.sign(np.diff(logit[sel]))[0])) if sel.sum() >= 2 else None
    # 3 segmented at 2023 (knot: slope change allowed), report post-2023 slope
    g2 = g.copy(); g2['post'] = np.clip(g2['t'] - 7, 0, None)   # 2023 -> t=7
    m3 = sm.GLM(endog, sm.add_constant(g2[['t', 'post']]), family=sm.families.Binomial()).fit()
    b_pre, b_post = m3.params['t'], m3.params['t'] + m3.params['post']
    cov = m3.cov_params(); se_post = np.sqrt(cov.loc['t', 't'] + cov.loc['post', 'post'] + 2 * cov.loc['t', 'post'])
    out['seg_pre2023_OR'] = np.exp(b_pre); out['seg_post2023_OR'] = np.exp(b_post)
    out['seg_post_lo'], out['seg_post_hi'] = np.exp(b_post - 1.96 * se_post), np.exp(b_post + 1.96 * se_post)
    # 4 restricted window 2023-2025 log-linear
    gw = g[sel]; ew = np.column_stack([gw['y'], gw['N'] - gw['y']])
    m4 = sm.GLM(ew, sm.add_constant(gw['t']), family=sm.families.Binomial()).fit()
    out['win2325_OR'] = np.exp(m4.params.iloc[1]); out['win2325_lo'], out['win2325_hi'] = np.exp(m4.conf_int().iloc[1]); out['win2325_p'] = m4.pvalues.iloc[1]
    return out

def quarterly_form(d, col, c, name):
    """Quarterly-resolution binomial GLM 2023Q1-2025Q4 with natural spline df=4; report avg OR per year and sign consistency."""
    q = d[d['year'] >= 2023].groupby('quarter').agg(N=('full_name', 'size'), y=(col, lambda s: (s == c).sum())).reset_index()
    q['t'] = np.arange(len(q)) / 4.0   # in years
    endog = np.column_stack([q['y'], q['N'] - q['y']])
    mlin = sm.GLM(endog, sm.add_constant(q['t']), family=sm.families.Binomial()).fit()
    import patsy
    Xs = patsy.dmatrix('cr(t, df=4)', q, return_type='dataframe')
    msp = sm.GLM(endog, Xs, family=sm.families.Binomial()).fit(); pred = np.asarray(msp.predict(Xs)); lg = np.log(pred / (1 - pred))
    return dict(cluster=name, q_loglin_OR=np.exp(mlin.params.iloc[1]), q_loglin_lo=np.exp(mlin.conf_int().iloc[1, 0]), q_loglin_hi=np.exp(mlin.conf_int().iloc[1, 1]),
                q_spline_avg_OR=np.exp((lg[-1] - lg[0]) / (q['t'].iloc[-1] - q['t'].iloc[0])),
                q_spline_share_first=pred[0], q_spline_share_last=pred[-1], n_quarters=len(q))

B_rows, Q_rows = [], []
for c in sorted(df['cluster'].unique()):
    B_rows.append({'level': 'macro', **fit_forms(yearly_counts(df, 'cluster', c), f'T{c} {macro_lab[c]}')})
    Q_rows.append({'level': 'macro', **quarterly_form(df, 'cluster', c, f'T{c} {macro_lab[c]}')})
for c in sorted(df['cluster_meso'].unique()):
    B_rows.append({'level': 'meso', **fit_forms(yearly_counts(df, 'cluster_meso', c), f'M{c} {meso_lab[c]}')})
    Q_rows.append({'level': 'meso', **quarterly_form(df, 'cluster_meso', c, f'M{c} {meso_lab[c]}')})
# domains
dom = pd.read_excel(os.path.join(RES, '도메인_태깅.xlsx')); dom = dom[dom['full_name'].isin(df['full_name'])].merge(df[['full_name', 'created_at', 'quarter']], on='full_name')
DOMS = [c for c in dom.columns if c not in ('full_name', 'year', 'General', 'created_at', 'quarter')]
for dname in DOMS:
    dd = dom.copy(); dd['flag'] = dd[dname].astype(int)
    B_rows.append({'level': 'domain', **fit_forms(yearly_counts(dd, 'flag', 1), dname)})
    Q_rows.append({'level': 'domain', **quarterly_form(dd, 'flag', 1, dname)})
B = pd.DataFrame(B_rows); Q = pd.DataFrame(Q_rows)
def sgn(x): return np.sign(np.log(x))
B['direction_consistent'] = (sgn(B['loglin_OR']) == sgn(B['spline_avg_OR_2023_25'])) & (sgn(B['loglin_OR']) == sgn(B['seg_post2023_OR'])) & (sgn(B['loglin_OR']) == sgn(B['win2325_OR']))
B = B.merge(Q[['cluster', 'q_loglin_OR', 'q_loglin_lo', 'q_loglin_hi', 'q_spline_avg_OR', 'q_spline_share_first', 'q_spline_share_last']], on='cluster')
B['direction_consistent_incl_quarterly'] = B['direction_consistent'] & (sgn(B['loglin_OR']) == sgn(B['q_loglin_OR']))
for c in B.columns:
    if B[c].dtype == float: B[c] = B[c].round(4)
B.to_excel(os.path.join(OUT, 'B_glm_functional_form_sensitivity.xlsx'), index=False)
log(B[['cluster', 'loglin_OR', 'spline_avg_OR_2023_25', 'seg_post2023_OR', 'win2325_OR', 'q_loglin_OR', 'direction_consistent_incl_quarterly']].to_string())

# ───────────────────────── C. Survivorship / activity by cohort ─────────────────────────
df['days_since_push'] = (SNAPSHOT - df['pushed_at']).dt.days
df['active_12m'] = df['days_since_push'] <= 365; df['active_24m'] = df['days_since_push'] <= 730
coh = df.groupby('year').agg(n=('full_name', 'size'), archived_pct=('archived', lambda s: 100 * s.mean()),
                             active_12m_pct=('active_12m', lambda s: 100 * s.mean()), active_24m_pct=('active_24m', lambda s: 100 * s.mean()),
                             median_stars=('stars', 'median'), median_forks=('forks', 'median'),
                             median_days_since_push=('days_since_push', 'median')).reset_index()
coh = coh.round(1); coh.to_excel(os.path.join(OUT, 'C_cohort_activity_survivorship.xlsx'), index=False); log(coh.to_string())
# per-cluster activity (macro)
clu_act = df.groupby('cluster').agg(n=('full_name', 'size'), archived_pct=('archived', lambda s: 100 * s.mean()), active_12m_pct=('active_12m', lambda s: 100 * s.mean()), median_stars=('stars', 'median')).round(1).reset_index()
clu_act['label'] = clu_act['cluster'].map(macro_lab); clu_act.to_excel(os.path.join(OUT, 'C_cluster_activity.xlsx'), index=False)
# Sensitivity: trends restricted to repositories active within 24 months (reduces "abandoned" repos)
act = df[df['active_24m']]
S_rows = []
for c in sorted(df['cluster'].unique()):
    r = fit_forms(yearly_counts(act, 'cluster', c), f'T{c}'); S_rows.append(dict(cluster=f'T{c} {macro_lab[c]}', n_active24m=int((act['cluster'] == c).sum()), OR_active24m=round(r['loglin_OR'], 3), lo=round(r['loglin_lo'], 3), hi=round(r['loglin_hi'], 3)))
pd.DataFrame(S_rows).to_excel(os.path.join(OUT, 'C_glm_active24m_sensitivity.xlsx'), index=False); log(pd.DataFrame(S_rows).to_string())

# ───────────────────────── D. Audit precision by stratum ─────────────────────────
aud = pd.read_excel(os.path.join(AUD, '인간평가_층화표본400.xlsx'), sheet_name='sample')
AGENT = {'Agent-framework', 'Agent-application', 'MCP-server'}
aud['both_agent'] = aud['llm_qwen'].isin(AGENT) & aud['llm_llama'].isin(AGENT)
aud['either_agent'] = aud['llm_qwen'].isin(AGENT) | aud['llm_llama'].isin(AGENT)
aud['agree'] = aud['llm_qwen'] == aud['llm_llama']
aud['period'] = np.where(aud['year'] <= 2022, '2016-2022', aud['year'].astype(str))
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (c - h, c + h)
def strat(g):
    n = len(g); k = g['both_agent'].sum(); lo, hi = wilson(k, n)
    return pd.Series(dict(n=n, precision_both=round(k / n, 3), wilson_lo=round(lo, 3), wilson_hi=round(hi, 3), precision_either=round(g['either_agent'].mean(), 3), model_agreement=round(g['agree'].mean(), 3),
                          tutorial_or_awesome_either=round((g['llm_qwen'].isin(['Tutorial-example', 'Awesome-resource']) | g['llm_llama'].isin(['Tutorial-example', 'Awesome-resource'])).mean(), 3),
                          nonagent_either=round((g['llm_qwen'].eq('Non-agent') | g['llm_llama'].eq('Non-agent')).mean(), 3)))
by_cluster = aud.groupby('cluster').apply(strat).reset_index(); by_cluster['label'] = by_cluster['cluster'].map(macro_lab)
by_period = aud.groupby('period').apply(strat).reset_index()
overall = strat(aud).to_frame().T; overall.insert(0, 'stratum', 'ALL')
# category distribution per model
cat = pd.concat([aud['llm_qwen'].value_counts(normalize=True).rename('qwen'), aud['llm_llama'].value_counts(normalize=True).rename('llama')], axis=1).round(3)
with pd.ExcelWriter(os.path.join(OUT, 'D_audit_precision_by_stratum.xlsx')) as w:
    overall.to_excel(w, 'overall', index=False); by_cluster.to_excel(w, 'by_cluster', index=False); by_period.to_excel(w, 'by_period', index=False); cat.to_excel(w, 'category_dist')
log(by_cluster.to_string()); log(by_period.to_string()); log(cat.to_string())
# Cohen's kappa between the two LLMs (8 categories) for reporting
from sklearn.metrics import cohen_kappa_score
log(f"LLM-LLM Cohen kappa (8 cat) = {cohen_kappa_score(aud['llm_qwen'], aud['llm_llama']):.3f}; binary agent/non-agent kappa = {cohen_kappa_score(aud['llm_qwen'].isin(AGENT), aud['llm_llama'].isin(AGENT)):.3f}")
json.dump(dict(kappa8=float(cohen_kappa_score(aud['llm_qwen'], aud['llm_llama'])), kappa_bin=float(cohen_kappa_score(aud['llm_qwen'].isin(AGENT), aud['llm_llama'].isin(AGENT)))), open(os.path.join(OUT, 'D_llm_kappa.json'), 'w'))

# ───────────────────────── E. Representative repositories ─────────────────────────
def reps(col, k, labmap, tag):
    rows = []
    for c in range(k):
        m = df[col].values == c; cen = X[m].mean(0); cen /= np.linalg.norm(cen)
        sims = X[m] @ cen; sub_df = df[m].copy(); sub_df['sim'] = sims
        near = sub_df.sort_values('sim', ascending=False).head(3)['full_name'].tolist()
        top = sub_df.sort_values('stars', ascending=False).head(3)['full_name'].tolist()
        rows.append(dict(cluster=f'{tag}{c}', label=labmap[c], n=int(m.sum()), nearest_centroid=' ; '.join(near), most_starred=' ; '.join(top)))
    return pd.DataFrame(rows)
E = pd.concat([reps('cluster', 5, macro_lab, 'T'), reps('cluster_meso', 12, meso_lab, 'M')]); E.to_excel(os.path.join(OUT, 'E_representative_repos.xlsx'), index=False); log(E.to_string())
log('DONE -> ' + OUT)
