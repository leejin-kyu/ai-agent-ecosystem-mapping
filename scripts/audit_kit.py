# 코퍼스 정합성 감사 키트 — 층화표본 400개 인간평가 시트 + LLM 이중분류(잠정 precision)
# 분류: Agent-framework / Agent-application / MCP-server / Tutorial-example / Awesome-resource / Paper-code / Non-agent / Other
import os, re, json
import numpy as np
import pandas as pd
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
if os.path.isdir(os.path.join(REPO, 'results')):   # replication repository layout (data/, results/, audit/)
    R = os.path.join(REPO, 'results'); AUD = os.path.join(REPO, 'audit'); RAW = os.path.join(REPO, 'data', 'github_ai_agent_raw_v2.xlsx')
else:                                              # original working layout
    R = os.path.join(BASE, '결과물_github_v2'); AUD = os.path.join(BASE, '감사_audit'); RAW = os.path.join(BASE, '데이터', 'github_ai_agent_raw_v2.xlsx')
os.makedirs(AUD, exist_ok=True)
CATS = ['Agent-framework', 'Agent-application', 'MCP-server', 'Tutorial-example',
        'Awesome-resource', 'Paper-code', 'Non-agent', 'Other']
AGENT_CATS = {'Agent-framework', 'Agent-application', 'MCP-server'}

def log(m): print(m, flush=True)

alloc = pd.read_excel(os.path.join(R, '문서_군집할당.xlsx'))
raw = pd.read_excel(RAW)
df = alloc.merge(raw[['full_name', 'description', 'topics']], on='full_name', how='left')
df['bucket'] = pd.cut(df['year'], bins=[2015, 2022, 2023, 2024, 2025], labels=['16-22', '23', '24', '25'])

# 층화표본 400 (cluster × year-bucket 비례, 최소 2)
N_S = 400
grp = df.groupby(['cluster', 'bucket'], observed=True)
sizes = (grp.size() / len(df) * N_S).round().astype(int).clip(lower=2)
samples = []
rs = np.random.RandomState(7)
for (c, b), n in sizes.items():
    g = grp.get_group((c, b))
    samples.append(g.sample(min(n, len(g)), random_state=rs))
smp = pd.concat(samples).drop_duplicates('full_name').reset_index(drop=True)
log(f'층화표본: {len(smp)}')

# LLM 이중분류
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

# Wilson 95% CI (합의 표본 기준 잠정 precision: 두 모델 모두 agent 계열)
n = len(smp); p = both_agent; z = 1.96
ci_lo = (p + z*z/(2*n) - z*np.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)
ci_hi = (p + z*z/(2*n) + z*np.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)
log(f'모델 간 일치율 {agree:.3f} | 잠정 precision(양모델 agent계열) {p:.3f} [{ci_lo:.3f},{ci_hi:.3f}] | either Non-agent {either_nonagent:.3f}')
pd.DataFrame([{'n': n, 'model_agreement': round(agree, 4), 'provisional_precision_bothagent': round(p, 4),
               'wilson_lo': round(ci_lo, 4), 'wilson_hi': round(ci_hi, 4),
               'either_nonagent': round(either_nonagent, 4)}]).to_excel(os.path.join(AUD, 'LLM이중분류_잠정지표.xlsx'), index=False)

# 인간평가 시트 (평가자 2인 컬럼 공란)
sheet = smp[['full_name', 'description', 'topics', 'stars', 'year', 'cluster', 'llm_qwen', 'llm_llama']].copy()
sheet['url'] = 'https://github.com/' + sheet['full_name']
sheet['rater1'] = ''; sheet['rater2'] = ''
with pd.ExcelWriter(os.path.join(AUD, '인간평가_층화표본400.xlsx')) as w:
    sheet.to_excel(w, sheet_name='sample', index=False)
    pd.DataFrame({'분류': CATS, '정의': [
        'AI 에이전트 구축용 라이브러리/프레임워크/SDK', 'AI 에이전트로 동작하는 실제 응용/제품/도구',
        'MCP 서버/클라이언트/연동', '교육용 예제·강좌·데모·스타터 템플릿',
        'awesome-list·링크 모음·큐레이션', '논문 동반 코드/벤치마크',
        'AI 에이전트와 무관', '판단 불가/기타']}).to_excel(w, sheet_name='guide', index=False)
log('인간평가 시트 저장')

# Krippendorff alpha 스크립트
open(os.path.join(AUD, 'compute_alpha.py'), 'w', encoding='utf-8').write('''# rater1/rater2 채운 뒤 실행: python compute_alpha.py
import pandas as pd, numpy as np
df = pd.read_excel('인간평가_층화표본400.xlsx', sheet_name='sample')
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
