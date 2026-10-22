# 응용분야(도메인) 축 분석 — 사전 태깅(+General) → 분야별 Binomial GLM(OR/yr, CI, BH-FDR)+Emergent
# → 분기 추이 그림 → 층화표본 300 LLM 이중태깅 검증(일치율·κ)
import os, re, json
import numpy as np
import pandas as pd
import urllib.request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
if os.path.isdir(os.path.join(REPO, 'results')):   # replication repository layout (data/, results/)
    R = os.path.join(REPO, 'results'); RAW = os.path.join(REPO, 'data', 'github_ai_agent_raw_v2.xlsx')
else:                                              # original working layout
    R = os.path.join(BASE, '결과물_github_v2'); RAW = os.path.join(BASE, '데이터', 'github_ai_agent_raw_v2.xlsx')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
def log(m): print(m, flush=True)

DOM = {
 'Finance/Trading': r'trading|finance|financ|fintech|stock|crypto|invest|portfolio|defi|market analysis',
 'Healthcare/Medical': r'health|medical|clinic|patient|diagnos|biomed|drug|pharma',
 'Education': r'education|learning course|tutor|teaching|student|classroom|edtech',
 'Legal': r'\blegal\b|\blaw\b|contract review|compliance',
 'E-commerce/Sales': r'e-?commerce|shopify|sales|crm|marketing|customer support|shopping',
 'SoftwareDev/Coding': r'coding|code generation|developer tool|programming|devops|code review|software engineer',
 'Gaming': r'game|gaming|minecraft|npc',
 'Robotics/Embodied': r'robot|embodied|drone|autonomous driving|ros2?',
 'Research/Science': r'research assist|scientific|paper|literature|arxiv|lab\b',
 'Web/Browser automation': r'browser|web automation|scraping|crawler|selenium|playwright',
 'Data/Analytics': r'data analysis|analytics|sql|database agent|business intelligence|\bbi\b',
}
DOM_NAMES = list(DOM.keys())

df = pd.read_excel(RAW)
df['created_dt'] = pd.to_datetime(df['created_at']).dt.tz_localize(None)
df['year'] = df['created_dt'].dt.year
df = df[(df['year'] >= 2016) & (df['year'] <= 2025)].reset_index(drop=True)
txt = (df['full_name'].fillna('') + ' ' + df['description'].fillna('') + ' ' + df['topics'].fillna('')).str.lower()
for d, pat in DOM.items():
    df[d] = txt.str.contains(pat, regex=True)
df['General'] = ~df[DOM_NAMES].any(axis=1)
log('태깅 완료: ' + ', '.join(f'{d}={int(df[d].sum())}' for d in DOM_NAMES + ['General']))
df[['full_name', 'year'] + DOM_NAMES + ['General']].to_excel(os.path.join(R, '도메인_태깅.xlsx'), index=False)

# ── GLM(분야별 binary) + BH-FDR + Emergent ──
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
years = np.arange(2016, 2026)
N = df['year'].value_counts().reindex(years).fillna(0).values
rows = []
for d in DOM_NAMES + ['General']:
    cnt = df[df[d]]['year'].value_counts().reindex(years).fillna(0).values
    pre2023 = cnt[:7].sum() / max(cnt.sum(), 1)
    emergent = pre2023 < 0.05
    glm = sm.GLM(np.column_stack([cnt, N - cnt]), sm.add_constant(years - 2016),
                 family=sm.families.Binomial()).fit()
    b, se = glm.params[1], glm.bse[1]
    rows.append({'domain': d, 'n': int(cnt.sum()), 'pre2023_share': round(pre2023, 3),
                 'OR_per_year': round(np.exp(b), 3), 'CI_lo': round(np.exp(b - 1.96*se), 3),
                 'CI_hi': round(np.exp(b + 1.96*se), 3), 'p': glm.pvalues[1], 'emergent': emergent})
t = pd.DataFrame(rows)
mask = ~t['emergent']
t['q_BH'] = np.nan
t.loc[mask, 'q_BH'] = multipletests(t.loc[mask, 'p'], method='fdr_bh')[1]
def judge(r):
    if r['emergent']: return 'Emergent'
    if pd.isna(r['q_BH']) or r['q_BH'] >= 0.05: return 'Stable'
    return 'Growing' if r['OR_per_year'] > 1 else 'Declining'
t['taxonomy'] = t.apply(judge, axis=1)
t['p'] = t['p'].round(6); t['q_BH'] = t['q_BH'].round(6)
t = t.sort_values('n', ascending=False)
t.to_excel(os.path.join(R, '도메인_GLM_taxonomy.xlsx'), index=False)
log(t.to_string())

# ── 분기 추이 그림 (2023~2025, 분야별 비중) ──
q = df[df['created_dt'] >= '2022-01-01'].set_index('created_dt')
qidx = q.resample('QS').size()
fig, ax = plt.subplots(figsize=(9.5, 5.5))
top = t[t['domain'] != 'General'].head(8)['domain'].tolist()
colors = plt.cm.tab10(np.linspace(0, 1, len(top)))
for d, c in zip(top, colors):
    share = q[q[d]].resample('QS').size().reindex(qidx.index).fillna(0) / qidx
    ax.plot(share.index, share.values, lw=1.8, color=c)
    ax.text(share.index[-1], share.values[-1], f' {d}', color=c, fontsize=7.5, va='center')
ax.set_title('Figure 6. Quarterly application-domain shares, 2022–2025 (top-8 domains)')
ax.set_ylabel('Share of quarterly creations'); ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(pd.Timestamp('2022-01-01'), pd.Timestamp('2027-03-01'))
fig.tight_layout(); fig.savefig(os.path.join(R, '그림6_도메인_분기추이.png'), dpi=200); plt.close(fig)
log('그림6 저장')

# ── 검증: 층화표본 300 LLM 이중태깅 (스킬 원칙 9) ──
def ollama_gen(model, prompt):
    req = urllib.request.Request('http://localhost:11434/api/generate',
        data=json.dumps({'model': model, 'prompt': prompt, 'stream': False,
                         'options': {'temperature': 0.0}}).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())['response'].strip()

CATLIST = '\n'.join('- ' + d for d in DOM_NAMES + ['General (no specific application domain / generic framework)'])
PROMPT = """Which application domain does this AI-agent GitHub repository primarily target? Choose exactly ONE:
""" + CATLIST + """

Repository: {name}
Description: {desc}
Tags: {tags}

Answer with the domain name only."""

rs = np.random.RandomState(11)
strata = []
for d in DOM_NAMES:
    g = df[df[d]]
    strata.append(g.sample(min(18, len(g)), random_state=rs))
strata.append(df[df['General']].sample(102, random_state=rs))
smp = pd.concat(strata).drop_duplicates('full_name').reset_index(drop=True)
log(f'검증표본: {len(smp)}')

def norm(resp):
    r = resp.lower()
    for d in DOM_NAMES:
        if d.lower().split('/')[0] in r or d.lower() in r: return d
    return 'General'

for model, coln in [('qwen2.5:7b', 'llm_qwen'), ('llama3.1:8b', 'llm_llama')]:
    out = []
    for i, r in smp.iterrows():
        resp = ollama_gen(model, PROMPT.format(name=r.full_name, desc=str(r.description)[:300], tags=str(r.topics)[:200]))
        out.append(norm(resp))
        if i % 50 == 0: log(f'  {model} {i}/{len(smp)}')
    smp[coln] = out

def lex_match(row, llm_col):
    llm = row[llm_col]
    if llm == 'General': return bool(row['General'])
    return bool(row[llm])
smp['agree_models'] = smp['llm_qwen'] == smp['llm_llama']
smp['lex_vs_qwen'] = smp.apply(lambda r: lex_match(r, 'llm_qwen'), axis=1)
smp['lex_vs_llama'] = smp.apply(lambda r: lex_match(r, 'llm_llama'), axis=1)
# 합의 서브셋 기준 사전 태깅 정합
cons = smp[smp['agree_models']]
acc = cons.apply(lambda r: lex_match(r, 'llm_qwen'), axis=1).mean()
stats = {'n': len(smp), 'model_agreement': round(smp['agree_models'].mean(), 4),
         'lexicon_consistent_vs_consensus': round(acc, 4),
         'lexicon_vs_qwen': round(smp['lex_vs_qwen'].mean(), 4),
         'lexicon_vs_llama': round(smp['lex_vs_llama'].mean(), 4)}
log(str(stats))
pd.DataFrame([stats]).to_excel(os.path.join(R, '도메인_태깅검증.xlsx'), index=False)
smp[['full_name', 'description', 'year', 'llm_qwen', 'llm_llama'] + DOM_NAMES + ['General']].to_excel(
    os.path.join(R, '도메인_검증표본.xlsx'), index=False)
log('ALL DONE')
