# -*- coding: utf-8 -*-
"""설문지_초간단.xlsx 채점 (O 체크 방식, 1인). 정답키 = 설문지_정답키(열지마세요).xlsx"""
import os, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
HERE = os.path.dirname(os.path.abspath(__file__))
sv = pd.read_excel(os.path.join(HERE, '설문지_초간단_작성.xlsx'), sheet_name='① 프로젝트 120개')
sv.columns = ['번호', 'desc', 'link', 'a1', 'a2', 'a3']
def pick(r):
    m = [str(r[c]).strip().upper().rstrip('.0') in ('O', '', 'V', 'X', '✓', 'ㅇ', '○', 'Ο') and str(r[c]).strip() not in ('', 'nan', 'None') for c in ('a1', 'a2', 'a3')]
    return str(m.index(True) + 1) if sum(m) == 1 else None
sv['ans'] = sv.apply(pick, axis=1)
key = pd.read_excel(os.path.join(HERE, '설문지_정답키(열지마세요).xlsx'), sheet_name='repo_key')
d = sv.merge(key, on='번호'); d = d[d['ans'].notna()]
if len(d) == 0: raise SystemExit('아직 O 표시가 없습니다.')
AG = {'Agent-framework', 'Agent-application', 'MCP-server'}
d['human_agent'] = d['ans'] == '1'; d['llm_agent'] = d['llm_qwen'].isin(AG) & d['llm_llama'].isin(AG)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den; return c-h, c+h
n = len(d); k = d['human_agent'].sum(); lo, hi = wilson(k, n)
print(f'판정 {n}건 (미응답/중복표시 {120-n}건) | 인간 정밀도 = {k/n:.3f}  Wilson95% [{lo:.3f}, {hi:.3f}]')
print(f'LLM 합의 정밀도(같은 {n}건) = {d["llm_agent"].mean():.3f} | 인간↔LLM 일치 = {(d.human_agent==d.llm_agent).mean():.3f} | κ = {cohen_kappa_score(d.human_agent, d.llm_agent):.3f}')
print(f'자료모음/튜토리얼 = {(d.ans=="2").mean():.3f} | 아님/모름 = {(d.ans=="3").mean():.3f}')
print('\n세그먼트별:'); print(d.groupby('cluster').agg(n=('ans', 'size'), human_prec=('human_agent', 'mean'), llm_prec=('llm_agent', 'mean')).round(3).to_string())
lab = pd.read_excel(os.path.join(HERE, '설문지_초간단_작성.xlsx'), sheet_name='② 그룹 이름 17개'); lab.columns = ['번호', 'terms', 'label', 'b3', 'b2', 'b1']
def pick2(r):
    m = [str(r[c]).strip().upper().rstrip('.0') in ('O', '', 'V', 'X', '✓', 'ㅇ', '○', 'Ο') and str(r[c]).strip() not in ('', 'nan', 'None') for c in ('b3', 'b2', 'b1')]
    return [3, 2, 1][m.index(True)] if sum(m) == 1 else np.nan
lab['fit'] = lab.apply(pick2, axis=1); lk = pd.read_excel(os.path.join(HERE, '설문지_정답키(열지마세요).xlsx'), sheet_name='label_key'); lab = lab.merge(lk, on='번호')
if lab['fit'].notna().any(): print(f"\n라벨 적합도 평균 {lab['fit'].mean():.2f}/3 (macro {lab[lab.cid.str.startswith('T')]['fit'].mean():.2f}, meso {lab[lab.cid.str.startswith('M')]['fit'].mean():.2f}), 응답 {lab['fit'].notna().sum()}건")
