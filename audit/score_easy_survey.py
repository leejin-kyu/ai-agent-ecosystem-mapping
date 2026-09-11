# -*- coding: utf-8 -*-
"""설문지_쉬운버전.xlsx 채점 (1인 평가자용). 결과: 인간 정밀도·Wilson CI·세그먼트별·인간↔LLM κ·라벨 평균."""
import os, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
HERE = os.path.dirname(os.path.abspath(__file__))
sv = pd.read_excel(os.path.join(HERE, '설문지_쉬운버전.xlsx'), sheet_name='리포지토리 120건')
key = pd.read_excel(os.path.join(HERE, '설문지_정답키(열지마세요).xlsx'), sheet_name='repo_key')
d = sv.merge(key, on='번호'); d['ans'] = d['▶ 판정 (드롭다운 선택)'].astype(str).str[0]
d = d[d['ans'].isin(['1', '2', '3'])]
if len(d) == 0: raise SystemExit('아직 판정이 없습니다.')
AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
d['human_agent'] = d['ans'] == '1'; d['llm_agent'] = d['llm_qwen'].isin(AG) & d['llm_llama'].isin(AG)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den; return c-h, c+h
n = len(d); k = d['human_agent'].sum(); lo, hi = wilson(k, n)
print(f'판정 {n}건 | 인간 정밀도(에이전트 맞음) = {k/n:.3f}  Wilson95% [{lo:.3f}, {hi:.3f}]')
print(f'LLM 합의 정밀도(같은 {n}건) = {d["llm_agent"].mean():.3f} | 인간↔LLM 일치 = {(d.human_agent==d.llm_agent).mean():.3f} | κ = {cohen_kappa_score(d.human_agent, d.llm_agent):.3f}')
print(f'튜토리얼/자료모음 = {(d.ans=="2").mean():.3f} | 아님/모름 = {(d.ans=="3").mean():.3f}')
print('\n세그먼트별:'); print(d.groupby('cluster').agg(n=('ans','size'), human_prec=('human_agent','mean'), llm_prec=('llm_agent','mean')).round(3).to_string())
lab = pd.read_excel(os.path.join(HERE, '설문지_쉬운버전.xlsx'), sheet_name='군집 라벨 17건')
lk = pd.read_excel(os.path.join(HERE, '설문지_정답키(열지마세요).xlsx'), sheet_name='label_key'); lab = lab.merge(lk, on='번호')
for col, name in [('▶ 이름이 잘 맞나요? (드롭다운)', 'label_fit'), ('▶ 단어들이 한 주제로 보이나요? (드롭다운)', 'coherence')]:
    v = pd.to_numeric(lab[col].astype(str).str[0], errors='coerce')
    if v.notna().any(): print(f'{name}: 평균 {v.mean():.2f}/3 (macro {v[lab.cid.str.startswith("T")].mean():.2f}, meso {v[lab.cid.str.startswith("M")].mean():.2f}), 응답 {v.notna().sum()}건')
