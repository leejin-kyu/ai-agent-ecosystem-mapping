# GitHub AI Agent analysis v2 - revision addressing 15 review items
# (1) de-truncated data (v2) (2) k=2-30 sweep + dual macro/meso granularity (3) 20-seed + bootstrap stability
# (4) 4 baselines (LDA/NMF/TFIDF+KMeans/BERTopic) c_v + c_npmi + diversity (definition audited)
# (5) Binomial GLM (OR/yr, 95% CI, BH-FDR) + Emergent taxonomy (6) monthly/quarterly PELT + sensitivity (7) stars/archived sensitivity
import os, re, json
import numpy as np
import pandas as pd
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
if os.path.isdir(os.path.join(REPO, 'results')):   # replication repository layout (data/, results/)
    DATA = os.path.join(REPO, 'data', 'github_ai_agent_raw_v2.xlsx'); R = os.path.join(REPO, 'results')
else:                                              # original working layout
    DATA = os.path.join(BASE, 'data', 'github_ai_agent_raw_v2.xlsx'); R = os.path.join(BASE, 'results_github_v2')
os.makedirs(R, exist_ok=True)
def log(m): print(m, flush=True)

MACRO_K = 5
MESO_K = 12

# ─── 1. Load ───
df = pd.read_excel(DATA)
df['created_dt'] = pd.to_datetime(df['created_at'])
df['year'] = df['created_dt'].dt.year
df = df[(df['year'] >= 2016) & (df['year'] <= 2025)].copy()
name_txt = df['full_name'].str.split('/').str[1].str.replace(r'[-_]', ' ', regex=True)
df['text'] = (name_txt.fillna('') + '. ' + df['description'].fillna('') + '. ' +
              df['topics'].fillna('').str.replace(';', ' ', regex=False)).str.strip()
df['textlen'] = (df['description'].fillna('') + df['topics'].fillna('')).str.len()
df = df[df['textlen'] >= 10].reset_index(drop=True)
log(f'Number of documents: {len(df)}')
log(df['year'].value_counts().sort_index().to_string())

# ─── 2. Embeddings ───
def ollama(endpoint, payload, timeout=600):
    req = urllib.request.Request(f'http://localhost:11434/api/{endpoint}',
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

EMB_NPY = os.path.join(R, 'embeddings.npy'); KEY_NPY = os.path.join(R, 'emb_keys.npy')
if os.path.exists(EMB_NPY) and os.path.exists(KEY_NPY) and \
   list(np.load(KEY_NPY, allow_pickle=True)) == df['full_name'].tolist():
    emb = np.load(EMB_NPY); log('Loaded cached embeddings')
else:
    embs = []
    for i in range(0, len(df), 64):
        embs.extend(ollama('embed', {'model': 'bge-m3', 'input': df['text'].iloc[i:i+64].tolist()})['embeddings'])
        if i % 1280 == 0: log(f'  embedding {i}/{len(df)}')
    emb = np.array(embs, dtype=np.float32)
    np.save(EMB_NPY, emb); np.save(KEY_NPY, np.array(df['full_name'].tolist(), dtype=object))
emb_n = emb / np.linalg.norm(emb, axis=1, keepdims=True)
log(f'Embeddings {emb.shape}')

# ─── 3. Tokenization and dictionary (shared) ───
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
STOP = set('ai agent agents llm llms based using with your for the and this that http https github com an of to in on a is are it by or as at be can you use from'.split())
tok = [[w for w in re.findall(r'[a-z][a-z0-9\-]{2,}', t.lower()) if w not in STOP] for t in df['text']]
dic = corpora.Dictionary(tok)
dic.filter_extremes(no_below=3, no_above=0.1)
corpus = [dic.doc2bow(t) for t in tok]

def coh(topics_words, kind='c_v'):
    tw = [[w for w in ws if w in dic.token2id][:10] for ws in topics_words]
    tw = [ws for ws in tw if len(ws) >= 3]
    if not tw: return float('nan')
    return CoherenceModel(topics=tw, texts=tok, dictionary=dic, coherence=kind, processes=1).get_coherence()

def diversity(topics_words):
    # Definition audit: each topic's raw top-10 words (without dictionary filtering) - unique / (k*10)
    allw = [w for ws in topics_words for w in ws[:10]]
    return len(set(allw)) / len(allw)

# ─── 4. Proposed method: KMeans k=2-30 sweep ───
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.feature_extraction.text import TfidfVectorizer

tv = TfidfVectorizer(max_features=8000, stop_words='english', token_pattern=r'[a-zA-Z][a-zA-Z0-9\-]{2,}')
X = tv.fit_transform(df['text'].str.lower())
vocab = np.array(tv.get_feature_names_out())
EXTRA = STOP | {'ai-agents', 'ai-agent', 'llm-agents', 'llm-agent', 'agentic-ai', 'agentic'}

def cluster_topwords(labels_, k):
    tws = []
    for c in range(k):
        mask = (labels_ == c)
        if mask.sum() == 0: tws.append([]); continue
        mt = np.asarray(X[mask].mean(axis=0)).ravel()
        tws.append([w for w in vocab[mt.argsort()[::-1]] if w not in EXTRA][:10])
    return tws

sil_rows = []
rng_idx = np.random.RandomState(0).choice(len(df), min(5000, len(df)), replace=False)
kms = {}
for k in range(2, 31):
    km = KMeans(n_clusters=k, random_state=100, n_init=10).fit(emb_n)
    s = silhouette_score(emb_n[rng_idx], km.labels_[rng_idx], metric='cosine')
    sil_rows.append({'k': k, 'silhouette': round(float(s), 4)})
    kms[k] = km
    log(f'k={k} sil={s:.4f}')
pd.DataFrame(sil_rows).to_excel(os.path.join(R, 'cluster_k_selection_silhouette_2to30.xlsx'), index=False)

km_macro, km_meso = kms[MACRO_K], kms[MESO_K]
df['cluster'] = km_macro.labels_
df['cluster_meso'] = km_meso.labels_

# 20-seed stability + bootstrap (80% subsample x20)
seed_aris = []
for seed in range(1, 21):
    km2 = KMeans(n_clusters=MACRO_K, random_state=seed, n_init=10).fit(emb_n)
    seed_aris.append(adjusted_rand_score(km_macro.labels_, km2.labels_))
boot_aris = []
rs = np.random.RandomState(42)
for b in range(20):
    idx = rs.choice(len(df), int(0.8 * len(df)), replace=False)
    kmb = KMeans(n_clusters=MACRO_K, random_state=100, n_init=10).fit(emb_n[idx])
    boot_aris.append(adjusted_rand_score(km_macro.labels_[idx], kmb.labels_))
stab = pd.DataFrame({
    'analysis': ['20-seed ARI', 'bootstrap80 ARI'],
    'median': [np.median(seed_aris), np.median(boot_aris)],
    'IQR_lo': [np.percentile(seed_aris, 25), np.percentile(boot_aris, 25)],
    'IQR_hi': [np.percentile(seed_aris, 75), np.percentile(boot_aris, 75)],
    'min': [min(seed_aris), min(boot_aris)], 'max': [max(seed_aris), max(boot_aris)]}).round(4)
stab.to_excel(os.path.join(R, 'stability_seed_bootstrap.xlsx'), index=False)
log(stab.to_string())

# ─── 5. Main comparison: 4 baselines + proposed method (k=2-30 sweep, report k with best c_v) ───
from sklearn.decomposition import NMF
results = []
sweep_rows = []

def eval_method(name, get_topics, ks):
    best = (None, -1, None)
    for k in ks:
        tws = get_topics(k)
        cv = coh(tws, 'c_v')
        sweep_rows.append({'method': name, 'k': k, 'c_v': round(cv, 4)})
        log(f'{name} k={k} c_v={cv:.4f}')
        if cv > best[1]: best = (k, cv, tws)
    k, cv, tws = best
    results.append({'method': name, 'best_k': k, 'c_v': round(cv, 4),
                    'c_npmi': round(coh(tws, 'c_npmi'), 4), 'diversity': round(diversity(tws), 4)})
    return best

KS = list(range(2, 31, 2)) + [5, 15]  # limit computation: even k plus 5 and 15
KS = sorted(set(KS))
# Proposed method (BGE+KMeans)
eval_method('BGE-M3+KMeans (proposed)', lambda k: cluster_topwords(kms[k].labels_, k) if k in kms
            else cluster_topwords(KMeans(n_clusters=k, random_state=100, n_init=10).fit(emb_n).labels_, k), KS)
# Also record metrics at the fixed macro/meso granularities
for kk, tag in [(MACRO_K, 'macro'), (MESO_K, 'meso')]:
    tws = cluster_topwords(kms[kk].labels_, kk)
    results.append({'method': f'BGE-M3+KMeans ({tag} k={kk})', 'best_k': kk, 'c_v': round(coh(tws, 'c_v'), 4),
                    'c_npmi': round(coh(tws, 'c_npmi'), 4), 'diversity': round(diversity(tws), 4)})
# TF-IDF+KMeans
def tfidf_km(k):
    lab = KMeans(n_clusters=k, random_state=100, n_init=10).fit(X).labels_
    return cluster_topwords(lab, k)
eval_method('TF-IDF+KMeans', tfidf_km, KS)
# NMF
def nmf_topics(k):
    W = NMF(n_components=k, random_state=100, init='nndsvda', max_iter=400).fit(X)
    return [[w for w in vocab[H.argsort()[::-1]] if w not in EXTRA][:10] for H in W.components_]
eval_method('NMF (TF-IDF)', nmf_topics, KS)
# LDA
def lda_topics(k):
    lda = LdaModel(corpus, num_topics=k, id2word=dic, random_state=100, passes=10)
    return [[w for w, _ in lda.show_topic(t, 15)][:10] for t in range(k)]
eval_method('LDA (gensim)', lda_topics, KS)
# BERTopic (native k, with and without outliers)
try:
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    bt = BERTopic(calculate_probabilities=False, verbose=False)
    bt_topics, _ = bt.fit_transform(df['text'].tolist(), embeddings=emb)
    ti = bt.get_topic_info()
    n_out = int((np.array(bt_topics) == -1).sum())
    tws_bt = [[w for w, _ in bt.get_topic(t)][:10] for t in ti['Topic'] if t != -1]
    results.append({'method': f'BERTopic (native k={len(tws_bt)}, outliers n={n_out})', 'best_k': len(tws_bt),
                    'c_v': round(coh(tws_bt, 'c_v'), 4), 'c_npmi': round(coh(tws_bt, 'c_npmi'), 4),
                    'diversity': round(diversity(tws_bt), 4)})
    log(f'BERTopic native topics={len(tws_bt)} outliers={n_out}')
except Exception as e:
    log(f'BERTopic failed: {e}')
pd.DataFrame(sweep_rows).to_excel(os.path.join(R, 'main_comparison_k_sweep.xlsx'), index=False)
pd.DataFrame(results).to_excel(os.path.join(R, 'main_comparison_metrics_v2.xlsx'), index=False)
log(pd.DataFrame(results).to_string())

# ─── 6. LLM labels + Self-Refine (macro & meso) ───
def gen(model, prompt, temp=0.2):
    return ollama('generate', {'model': model, 'prompt': prompt, 'stream': False,
                               'options': {'temperature': temp}})['response'].strip()

def label_pipeline(col, k, tag):
    ck_rows, reps = [], {}
    km = kms[k]
    for c in range(k):
        mask = df[col] == c
        mt = np.asarray(X[mask.values].mean(axis=0)).ravel()
        top = [w for w in vocab[mt.argsort()[::-1]] if w not in EXTRA][:12]
        d = emb_n[mask.values] @ km.cluster_centers_[c] / np.linalg.norm(km.cluster_centers_[c])
        rep_idx = df[mask].index[np.argsort(-d)[:8]]
        reps[c] = df.loc[rep_idx, ['full_name', 'description']]
        ck_rows.append({'cluster': c, 'n_docs': int(mask.sum()), 'top_terms': ', '.join(top),
                        'rep_repos': '; '.join(df.loc[rep_idx[:5], 'full_name'])})
    ck = pd.DataFrame(ck_rows)
    l0, l1 = {}, {}
    for c in range(k):
        rep_txt = '\n'.join(f"- {r.full_name}: {str(r.description)[:180]}" for r in reps[c].itertuples())
        l0[c] = gen('gemma3:12b',
            f"You are labeling clusters of GitHub repositories about AI agents.\nTop TF-IDF terms: {ck.top_terms[c]}\n"
            f"Representative repos:\n{rep_txt}\n\nGive ONE concise English topic label (4-8 words). Label only.").strip('"*. ')
    all0 = '\n'.join(f'T{c}: {l0[c]}' for c in range(k))
    for c in range(k):
        resp = gen('gemma3:12b',
            f"Cluster labels:\n{all0}\n\nCritique label T{c} (terms: {ck.top_terms[c]}): specific, grounded, "
            f"non-overlapping? Output improved label (4-8 words). Final line exactly: LABEL: <label>")
        m = re.search(r'LABEL:\s*(.+)', resp)
        l1[c] = (m.group(1) if m else l0[c]).strip('"*. ')
        log(f'[{tag}] T{c}: {l0[c]}  ->  {l1[c]}')
    def dup(lbl):
        E = np.array(ollama('embed', {'model': 'bge-m3', 'input': [lbl[c] for c in range(k)]})['embeddings'])
        E = E / np.linalg.norm(E, axis=1, keepdims=True); S = E @ E.T
        return float((S.sum() - k) / (k * (k - 1)))
    def spec(lbl):
        sc = []
        for c in range(k):
            r = gen('llama3.1:8b',
                f"Rate specificity/groundedness of this topic label for a cluster whose top terms are: "
                f"{ck.top_terms[c]}\nLabel: \"{lbl[c]}\"\nScore 1 (vague) to 5 (specific, grounded). One digit only.")
            m = re.search(r'[1-5]', r); sc.append(int(m.group()) if m else np.nan)
        return float(np.nanmean(sc)), sc
    d0, d1_ = dup(l0), dup(l1); s0m, s0 = spec(l0); s1m, s1 = spec(l1)
    ck['label_initial'] = [l0[c] for c in range(k)]; ck['label_refined'] = [l1[c] for c in range(k)]
    ck['spec_initial'] = s0; ck['spec_refined'] = s1
    ck.to_excel(os.path.join(R, f'topic_{tag}_k{k}.xlsx'), index=False)
    pd.DataFrame([{'granularity': tag, 'dup_init': round(d0, 4), 'dup_refined': round(d1_, 4),
                   'spec_init': round(s0m, 2), 'spec_refined': round(s1m, 2)}]
                 ).to_excel(os.path.join(R, f'SelfRefine_{tag}.xlsx'), index=False)
    log(f'[{tag}] SelfRefine dup {d0:.4f}->{d1_:.4f} spec {s0m:.2f}->{s1m:.2f}')
    return {c: l1[c] for c in range(k)}

labels_macro = label_pipeline('cluster', MACRO_K, 'macro')
labels_meso = label_pipeline('cluster_meso', MESO_K, 'meso')

# ─── 7. GLM(Binomial) + BH-FDR + Emergent taxonomy ───
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

def glm_table(dfin, col, k, labels, tag):
    years = np.arange(2016, 2026)
    N = dfin['year'].value_counts().reindex(years).fillna(0).values
    rows = []
    for c in range(k):
        cnt = dfin[dfin[col] == c]['year'].value_counts().reindex(years).fillna(0).values
        pre2023 = cnt[:7].sum() / max(cnt.sum(), 1)
        emergent = pre2023 < 0.05
        ok = N > 0
        try:
            glm = sm.GLM(np.column_stack([cnt[ok], N[ok] - cnt[ok]]),
                         sm.add_constant(years[ok] - 2016), family=sm.families.Binomial()).fit()
            b, se = glm.params[1], glm.bse[1]
            OR = np.exp(b); lo, hi = np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)
            p = glm.pvalues[1]
        except Exception:
            OR, lo, hi, p = np.nan, np.nan, np.nan, np.nan
        rows.append({'cluster': c, 'label': labels[c], 'n': int(cnt.sum()), 'pre2023_share': round(pre2023, 3),
                     'OR_per_year': round(OR, 3), 'CI_lo': round(lo, 3), 'CI_hi': round(hi, 3),
                     'p': p, 'emergent': emergent})
    t = pd.DataFrame(rows)
    mask = ~t['emergent'] & t['p'].notna()
    t['q_BH'] = np.nan
    if mask.sum():
        t.loc[mask, 'q_BH'] = multipletests(t.loc[mask, 'p'], method='fdr_bh')[1]
    def judge(r):
        if r['emergent']: return 'Emergent'
        if pd.isna(r['q_BH']) or r['q_BH'] >= 0.05: return 'Stable'
        return 'Established-growing' if r['OR_per_year'] > 1 else 'Established-declining'
    t['taxonomy'] = t.apply(judge, axis=1)
    t['p'] = t['p'].round(5); t['q_BH'] = t['q_BH'].round(5)
    t.to_excel(os.path.join(R, f'GLM_taxonomy_{tag}.xlsx'), index=False)
    log(t.to_string())
    return t

glm_macro = glm_table(df, 'cluster', MACRO_K, labels_macro, 'macro')
glm_meso = glm_table(df, 'cluster_meso', MESO_K, labels_meso, 'meso')

# ─── 8. PELT monthly/quarterly + sensitivity ───
import ruptures as rpt
mon = df.set_index('created_dt').resample('MS').size().reindex(
    pd.date_range('2016-01-01', '2025-12-01', freq='MS')).fillna(0)
sens = []
for model_ in ('l2', 'rbf'):
    for pen in (0.5, 1, 2, 3, 5):  # 2 models x 5 penalties x 3 min sizes = 30 configurations (see results/PELT_monthly_sensitivity.xlsx)
        for ms in (2, 3, 6):
            try:
                cps = rpt.Pelt(model=model_, min_size=ms).fit(np.log1p(mon.values)).predict(pen=pen)
                sens.append({'series': 'monthly_total(log1p)', 'model': model_, 'pen': pen, 'min_size': ms,
                             'changepoints': str([mon.index[i].strftime('%Y-%m') for i in cps[:-1]])})
            except Exception as e:
                sens.append({'series': 'monthly_total(log1p)', 'model': model_, 'pen': pen, 'min_size': ms,
                             'changepoints': f'err {e}'})
q = df.set_index('created_dt').groupby([pd.Grouper(freq='QS'), 'cluster']).size().unstack(fill_value=0)
qs = q.div(q.sum(axis=1), axis=0).reindex(pd.date_range('2016-01-01', '2025-10-01', freq='QS')).fillna(0)
for c in range(MACRO_K):
    cps = rpt.Pelt(model='l2', min_size=4).fit(qs[c].values).predict(pen=0.02)
    sens.append({'series': f'quarterly_share_T{c}', 'model': 'l2', 'pen': 0.02, 'min_size': 4,
                 'changepoints': str([qs.index[i].strftime('%Y-Q%q').replace('%q', str(qs.index[i].quarter)) for i in cps[:-1]])})
pd.DataFrame(sens).to_excel(os.path.join(R, 'PELT_monthly_sensitivity.xlsx'), index=False)
log(pd.DataFrame(sens).head(30).to_string())

# ─── 9. stars/archived sensitivity ───
sens2 = []
for th in (5, 10, 50):
    for arch in (False, True):
        sub = df[(df['stars'] >= th) & ((df['archived'] == False) if not arch else True)]
        t = glm_table(sub, 'cluster', MACRO_K, labels_macro, f'sens_s{th}_arch{arch}')
        for r in t.itertuples():
            sens2.append({'stars>=': th, 'incl_archived': arch, 'cluster': r.cluster, 'label': r.label,
                          'n': r.n, 'OR': r.OR_per_year, 'CI': f'[{r.CI_lo},{r.CI_hi}]', 'q': r.q_BH, 'tax': r.taxonomy})
pd.DataFrame(sens2).to_excel(os.path.join(R, 'sensitivity_stars_archived.xlsx'), index=False)

# ─── 10. Save shares by year and assignments ───
pd.crosstab(df['year'], df['cluster'], normalize='index').to_excel(os.path.join(R, 'topic_share_by_year.xlsx'))
df[['full_name', 'stars', 'language', 'license', 'archived', 'year', 'cluster', 'cluster_meso']].to_excel(
    os.path.join(R, 'document_cluster_assignments.xlsx'), index=False)
log('ALL DONE')
