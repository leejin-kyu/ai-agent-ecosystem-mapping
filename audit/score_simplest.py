# -*- coding: utf-8 -*-
"""Score survey_simplest.xlsx (O-mark format, single annotator). Answer key = survey_answer_key_do_not_open.xlsx"""
import os, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
HERE = os.path.dirname(os.path.abspath(__file__))
sv = pd.read_excel(os.path.join(HERE, 'survey_simplest_completed.xlsx'), sheet_name='① Projects (120)')
sv.columns = ['item_no', 'desc', 'link', 'a1', 'a2', 'a3']
def pick(r):
    m = [str(r[c]).strip().upper().rstrip('.0') in ('O', '', 'V', 'X', '✓', '\u3147', '○', 'Ο') and str(r[c]).strip() not in ('', 'nan', 'None') for c in ('a1', 'a2', 'a3')]  # '\u3147' = Korean letter ieung (looks like O), accepted as a check mark
    return str(m.index(True) + 1) if sum(m) == 1 else None
sv['ans'] = sv.apply(pick, axis=1)
key = pd.read_excel(os.path.join(HERE, 'survey_answer_key_do_not_open.xlsx'), sheet_name='repo_key')
d = sv.merge(key, on='item_no'); d = d[d['ans'].notna()]
if len(d) == 0: raise SystemExit('No O marks yet.')
AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
d['human_agent'] = d['ans'] == '1'; d['llm_agent'] = d['llm_qwen'].isin(AG) & d['llm_llama'].isin(AG)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den; return c-h, c+h
n = len(d); k = d['human_agent'].sum(); lo, hi = wilson(k, n)
print(f'Judged {n} (unanswered/multiple marks {120-n}) | human precision = {k/n:.3f}  Wilson95% [{lo:.3f}, {hi:.3f}]')
print(f'LLM consensus precision (same {n} items) = {d["llm_agent"].mean():.3f} | human-LLM agreement = {(d.human_agent==d.llm_agent).mean():.3f} | κ = {cohen_kappa_score(d.human_agent, d.llm_agent):.3f}')
print(f'Resource list/tutorial = {(d.ans=="2").mean():.3f} | No/not sure = {(d.ans=="3").mean():.3f}')
print('\nBy segment:'); print(d.groupby('cluster').agg(n=('ans', 'size'), human_prec=('human_agent', 'mean'), llm_prec=('llm_agent', 'mean')).round(3).to_string())
lab = pd.read_excel(os.path.join(HERE, 'survey_simplest_completed.xlsx'), sheet_name='② Group names (17)'); lab.columns = ['item_no', 'terms', 'label', 'b3', 'b2', 'b1']
def pick2(r):
    m = [str(r[c]).strip().upper().rstrip('.0') in ('O', '', 'V', 'X', '✓', '\u3147', '○', 'Ο') and str(r[c]).strip() not in ('', 'nan', 'None') for c in ('b3', 'b2', 'b1')]  # '\u3147' = Korean letter ieung (looks like O)
    return [3, 2, 1][m.index(True)] if sum(m) == 1 else np.nan
lab['fit'] = lab.apply(pick2, axis=1); lk = pd.read_excel(os.path.join(HERE, 'survey_answer_key_do_not_open.xlsx'), sheet_name='label_key'); lab = lab.merge(lk, on='item_no')
if lab['fit'].notna().any(): print(f"\nMean label fit {lab['fit'].mean():.2f}/3 (macro {lab[lab.cid.str.startswith('T')]['fit'].mean():.2f}, meso {lab[lab.cid.str.startswith('M')]['fit'].mean():.2f}), {lab['fit'].notna().sum()} responses")
