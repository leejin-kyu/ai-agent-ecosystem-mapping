# -*- coding: utf-8 -*-
"""Score survey_easy_version.xlsx (single annotator). Results: human precision, Wilson CI, per segment, human-vs-LLM kappa, mean label rating."""
import os, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
HERE = os.path.dirname(os.path.abspath(__file__))
sv = pd.read_excel(os.path.join(HERE, 'survey_easy_version.xlsx'), sheet_name='Repositories (120)')
key = pd.read_excel(os.path.join(HERE, 'survey_answer_key_do_not_open.xlsx'), sheet_name='repo_key')
d = sv.merge(key, on='item_no'); d['ans'] = d['▶ Judgment (choose from dropdown)'].astype(str).str[0]
d = d[d['ans'].isin(['1', '2', '3'])]
if len(d) == 0: raise SystemExit('No judgments yet.')
AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
d['human_agent'] = d['ans'] == '1'; d['llm_agent'] = d['llm_qwen'].isin(AG) & d['llm_llama'].isin(AG)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den; return c-h, c+h
n = len(d); k = d['human_agent'].sum(); lo, hi = wilson(k, n)
print(f'Judged {n} | human precision (AI agent yes) = {k/n:.3f}  Wilson95% [{lo:.3f}, {hi:.3f}]')
print(f'LLM consensus precision (same {n} items) = {d["llm_agent"].mean():.3f} | human-LLM agreement = {(d.human_agent==d.llm_agent).mean():.3f} | κ = {cohen_kappa_score(d.human_agent, d.llm_agent):.3f}')
print(f'Tutorial/resource list = {(d.ans=="2").mean():.3f} | No/not sure = {(d.ans=="3").mean():.3f}')
print('\nBy segment:'); print(d.groupby('cluster').agg(n=('ans','size'), human_prec=('human_agent','mean'), llm_prec=('llm_agent','mean')).round(3).to_string())
lab = pd.read_excel(os.path.join(HERE, 'survey_easy_version.xlsx'), sheet_name='Cluster labels (17)')
lk = pd.read_excel(os.path.join(HERE, 'survey_answer_key_do_not_open.xlsx'), sheet_name='label_key'); lab = lab.merge(lk, on='item_no')
for col, name in [('▶ Does the name fit? (dropdown)', 'label_fit'), ('▶ Do the terms form one topic? (dropdown)', 'coherence')]:
    v = pd.to_numeric(lab[col].astype(str).str[0], errors='coerce')
    if v.notna().any(): print(f'{name}: mean {v.mean():.2f}/3 (macro {v[lab.cid.str.startswith("T")].mean():.2f}, meso {v[lab.cid.str.startswith("M")].mean():.2f}), {v.notna().sum()} responses')
