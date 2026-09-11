# -*- coding: utf-8 -*-
"""3인 평가자(A=저자, B·C=외부) — 정밀도·쌍별 κ·Krippendorff α(nominal)·다수결 합의·LLM 대비. 출력: 인간평가_3인_결과_260910.txt"""
import os, itertools, pandas as pd, numpy as np
from sklearn.metrics import cohen_kappa_score
HERE=os.path.dirname(os.path.abspath(__file__))
FILES={'A':'설문지_초간단_작성.xlsx','B':'설문지_친구용_2차평가자_작성.xlsx','C':'설문지_친구용_3차평가자_작성.xlsx'}
MARK=lambda v: str(v).strip() not in ('','nan','None') and str(v).strip().upper().rstrip('.0') in ('O','','V','X','✓','ㅇ','○','Ο')
def load(f):
    d=pd.read_excel(os.path.join(HERE,f),sheet_name='① 프로젝트 120개'); d.columns=['번호','desc','link','a1','a2','a3']; d['번호']=range(1,len(d)+1)
    d['ans']=d.apply(lambda r: (str([MARK(r.a1),MARK(r.a2),MARK(r.a3)].index(True)+1) if sum([MARK(r.a1),MARK(r.a2),MARK(r.a3)])==1 else None),axis=1)
    l=pd.read_excel(os.path.join(HERE,f),sheet_name='② 그룹 이름 17개'); l.columns=['번호','t','lab','b3','b2','b1']; l['번호']=range(1,len(l)+1)
    l['fit']=l.apply(lambda r: ([3,2,1][[MARK(r.b3),MARK(r.b2),MARK(r.b1)].index(True)] if sum([MARK(r.b3),MARK(r.b2),MARK(r.b1)])==1 else np.nan),axis=1)
    try:
        info=pd.read_excel(os.path.join(HERE,f),sheet_name='시작 전 읽기',header=None); exp=str(info.iloc[-1,1])
    except Exception: exp='?'
    return d[['번호','ans']],l[['번호','fit']],exp
def wilson(k,n,z=1.96):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return c-h,c+h
def kripp_nominal(mat):
    mat=np.asarray(mat,dtype=float); vals=mat[~np.isnan(mat)]; cats=np.unique(vals); idx={c:i for i,c in enumerate(cats)}; O=np.zeros((len(cats),)*2)
    for row in mat:
        r=row[~np.isnan(row)]; m=len(r)
        if m<2: continue
        for i,a in enumerate(r):
            for j,b in enumerate(r):
                if i!=j: O[idx[a],idx[b]]+=1/(m-1)
    n=O.sum(); nc=O.sum(1); D=1-np.eye(len(cats)); Do=(O*D).sum()/n; De=(np.outer(nc,nc)*D).sum()/(n*(n-1)); return 1-Do/De
R={k:load(v) for k,v in FILES.items()}
for k in R: print(f'{k}: answered {R[k][0].ans.notna().sum()} | dist {R[k][0].ans.value_counts().to_dict()} | exp={R[k][2]}')
m=R['A'][0].rename(columns={'ans':'A'})
for k in 'BC': m=m.merge(R[k][0].rename(columns={'ans':k}),on='번호')
m=m.dropna()
key=pd.read_excel(os.path.join(HERE,'설문지_정답키(열지마세요).xlsx'),sheet_name='repo_key'); m=m.merge(key,on='번호')
AG={'Agent-framework','Agent-application','MCP-server'}; m['llm']=m.llm_qwen.isin(AG)&m.llm_llama.isin(AG); n=len(m)
bin_={k:(m[k]=='1') for k in 'ABC'}
print(f'\nn={n}')
for k in 'ABC': lo,hi=wilson(bin_[k].sum(),n); print(f'  {k} precision {bin_[k].mean():.3f} [{lo:.3f},{hi:.3f}] | agree w/ LLM {(bin_[k]==m.llm).mean():.3f} | kappa(k,LLM) {cohen_kappa_score(bin_[k],m.llm):.3f}')
for a,b in itertools.combinations('ABC',2): print(f'  {a}-{b}: agree3 {(m[a]==m[b]).mean():.3f} | agreeBin {(bin_[a]==bin_[b]).mean():.3f} | kappa3 {cohen_kappa_score(m[a],m[b]):.3f} | kappaBin {cohen_kappa_score(bin_[a],bin_[b]):.3f}')
M3=np.array([[float(x) for x in m[k]] for k in 'ABC']).T; MB=np.array([bin_[k].astype(float).values for k in 'ABC']).T
print(f'  Krippendorff alpha nominal: 3-class {kripp_nominal(M3):.3f} | binary {kripp_nominal(MB):.3f}')
cnt=sum(bin_[k].astype(int) for k in 'ABC'); maj=cnt>=2; allr=cnt==3; anyr=cnt>=1
print(f'  votes: 3/3 {(cnt==3).mean():.3f} | 2/3 {(cnt==2).mean():.3f} | 1/3 {(cnt==1).mean():.3f} | 0/3 {(cnt==0).mean():.3f}')
for nm,v in [('majority(>=2 of 3)',maj),('unanimous',allr),('any',anyr)]:
    lo,hi=wilson(v.sum(),n); print(f'  {nm} precision {v.mean():.3f} [{lo:.3f},{hi:.3f}] | kappa(vs LLM) {cohen_kappa_score(v,m.llm):.3f} | agree {(v==m.llm).mean():.3f}')
print('\nper segment:'); print(m.assign(A=bin_['A'],B=bin_['B'],C=bin_['C'],maj=maj).groupby('cluster')[['A','B','C','maj','llm']].mean().round(3).to_string())
print('\n3-class distribution:', {k:m[k].value_counts().to_dict() for k in 'ABC'})
# labels
L=R['A'][1].rename(columns={'fit':'A'})
for k in 'BC': L=L.merge(R[k][1].rename(columns={'fit':k}),on='번호')
L=L.dropna()
lk=pd.read_excel(os.path.join(HERE,'설문지_정답키(열지마세요).xlsx'),sheet_name='label_key'); L=L.merge(lk,on='번호'); L['mean']=L[['A','B','C']].mean(1)
print(f"\nlabels n={len(L)} | means A {L.A.mean():.2f} B {L.B.mean():.2f} C {L.C.mean():.2f} | pooled {L['mean'].mean():.2f} | all-identical {(L[['A','B','C']].nunique(1)==1).mean():.3f} | Krippendorff alpha(interval) {1-((L[['A','B','C']].values[:,:,None]-L[['A','B','C']].values[:,None,:])**2).sum()/ (3*2*len(L)) / (np.var(L[['A','B','C']].values)*1.0+1e-12):.3f}")
print('by level:', L.groupby(L.cid.str[0])['mean'].mean().round(2).to_dict()); print('lowest:', L.sort_values('mean').head(3)[['cid','label_refined','A','B','C']].to_string(index=False))
print('share of ratings = fits(3):', (L[['A','B','C']].values==3).mean().round(3))
