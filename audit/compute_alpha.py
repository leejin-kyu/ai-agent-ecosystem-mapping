# rater1/rater2 채운 뒤 실행: python compute_alpha.py
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
