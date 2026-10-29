# Corpus relevance audit kit: human rating sheet for a stratified sample of 400 + dual LLM classification (provisional precision)
# Categories: Agent-framework / Agent-application / MCP-server / Tutorial-example / Awesome-resource / Paper-code / Non-agent / Other
import os, re, json
import numpy as np
import pandas as pd
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
if os.path.isdir(os.path.join(REPO, 'results')):   # replication repository layout (data/, results/, audit/)
    R = os.path.join(REPO, 'results'); AUD = os.path.join(REPO, 'audit'); RAW = os.path.join(REPO, 'data', 'github_ai_agent_raw_v2.xlsx')
else:                                              # original working layout
    R = os.path.join(BASE, 'results_github_v2'); AUD = os.path.join(BASE, 'audit'); RAW = os.path.join(BASE, 'data', 'github_ai_agent_raw_v2.xlsx')
os.makedirs(AUD, exist_ok=True)
CATS = ['Agent-framework', 'Agent-application', 'MCP-server', 'Tutorial-example',
        'Awesome-resource', 'Paper-code', 'Non-agent', 'Other']
AGENT_CATS = {'Agent-framework', 'Agent-application', 'MCP-server'}

def log(m): print(m, flush=True)

alloc = pd.read_excel(os.path.join(R, 'document_cluster_assignments.xlsx'))
raw = pd.read_excel(RAW)
df = alloc.merge(raw[['full_name', 'description', 'topics']], on='full_name', how='left')
df['bucket'] = pd.cut(df['year'], bins=[2015, 2022, 2023, 2024, 2025], labels=['16-22', '23', '24', '25'])

# Stratified sample of 400 (proportional to cluster x year-bucket, minimum 2)
N_S = 400
grp = df.groupby(['cluster', 'bucket'], observed=True)
sizes = (grp.size() / len(df) * N_S).round().astype(int).clip(lower=2)
samples = []
rs = np.random.RandomState(7)
for (c, b), n in sizes.items():
    g = grp.get_group((c, b))
    samples.append(g.sample(min(n, len(g)), random_state=rs))
smp = pd.concat(samples).drop_duplicates('full_name').reset_index(drop=True)
log(f'Stratified sample: {len(smp)}')

# Dual LLM classification
def ollama_gen(model, prompt):
    req = urllib.request.Request('http://localhost:11434/api/generate',
        data=json.dumps({'model': model, 'prompt': prompt, 'stream': False,
                         'options': {'temperature': 0.0}}).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())['response'].strip()

PROMPT = """Classify this GitHub repository into exactly ONE category:
- Agent-framework: a library/framework/SDK for building AI agents
- Agent-application: a working application/product/tool that operates as an AI agent
- MCP-server: a Model Context Protocol server/client/integration
- Tutorial-example: educational examples, courses, demos, starter templates
- Awesome-resource: awesome-lists, link collections, curated resources
- Paper-code: code accompanying a research paper / benchmarks
- Non-agent: not actually about AI agents
- Other: none of the above

Repository: {name}
Description: {desc}
Tags: {tags}

Answer with the category name only."""

def classify(model):
    out = []
    for i, r in smp.iterrows():
        resp = ollama_gen(model, PROMPT.format(name=r.full_name, desc=str(r.description)[:300], tags=str(r.topics)[:200]))
        cat = next((c for c in CATS if c.lower() in resp.lower()), 'Other')
        out.append(cat)
        if i % 50 == 0: log(f'  {model} {i}/{len(smp)}')
    return out

smp['llm_qwen'] = classify('qwen2.5:7b')
smp['llm_llama'] = classify('llama3.1:8b')
agree = (smp['llm_qwen'] == smp['llm_llama']).mean()
both_agent = ((smp['llm_qwen'].isin(AGENT_CATS)) & (smp['llm_llama'].isin(AGENT_CATS))).mean()
either_nonagent = ((smp['llm_qwen'] == 'Non-agent') | (smp['llm_llama'] == 'Non-agent')).mean()

# Wilson 95% CI (provisional precision on the consensus sample: both models assign an agent category)
n = len(smp); p = both_agent; z = 1.96
ci_lo = (p + z*z/(2*n) - z*np.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)
ci_hi = (p + z*z/(2*n) + z*np.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)
log(f'Inter-model agreement {agree:.3f} | provisional precision (both models agent category) {p:.3f} [{ci_lo:.3f},{ci_hi:.3f}] | either Non-agent {either_nonagent:.3f}')
pd.DataFrame([{'n': n, 'model_agreement': round(agree, 4), 'provisional_precision_bothagent': round(p, 4),
               'wilson_lo': round(ci_lo, 4), 'wilson_hi': round(ci_hi, 4),
               'either_nonagent': round(either_nonagent, 4)}]).to_excel(os.path.join(AUD, 'llm_dual_classification_provisional_metrics.xlsx'), index=False)

# Human rating sheet (columns for 2 raters left blank)
sheet = smp[['full_name', 'description', 'topics', 'stars', 'year', 'cluster', 'llm_qwen', 'llm_llama']].copy()
sheet['url'] = 'https://github.com/' + sheet['full_name']
sheet['rater1'] = ''; sheet['rater2'] = ''
with pd.ExcelWriter(os.path.join(AUD, 'human_eval_stratified_sample_400.xlsx')) as w:
    sheet.to_excel(w, sheet_name='sample', index=False)
    pd.DataFrame({'Category': CATS, 'Definition': [
        'Library/framework/SDK for building AI agents', 'Actual application/product/tool that operates as an AI agent',
        'MCP server/client/integration', 'Educational example, course, demo, or starter template',
        'awesome-list, link collection, curation', 'Code or benchmark accompanying a paper',
        'Unrelated to AI agents', 'Cannot judge / other']}).to_excel(w, sheet_name='guide', index=False)
log('Human rating sheet saved')

# Krippendorff alpha script
open(os.path.join(AUD, 'compute_alpha.py'), 'w', encoding='utf-8').write('''# Run after filling in rater1/rater2: python compute_alpha.py
import pandas as pd, numpy as np
df = pd.read_excel('human_eval_stratified_sample_400.xlsx', sheet_name='sample')
d = df[(df.rater1 != '') & (df.rater2 != '')][['rater1', 'rater2']].dropna()
cats = sorted(set(d.rater1) | set(d.rater2))
o = pd.crosstab(d.rater1, d.rater2).reindex(index=cats, columns=cats, fill_value=0).values
n = o.sum(); po = np.trace(o) / n
marg = (o.sum(0) + o.sum(1)) / (2 * n); pe = (marg ** 2).sum()
print(f'n={n}  %agree={po:.3f}  kappa/alpha(nominal)~{(po - pe) / (1 - pe):.3f}')
AGENT = {'Agent-framework', 'Agent-application', 'MCP-server'}
prec = d.apply(lambda r: r.rater1 in AGENT and r.rater2 in AGENT, axis=1).mean()
print(f'human precision (both agent-related) = {prec:.3f}')
''')
log('ALL DONE')
