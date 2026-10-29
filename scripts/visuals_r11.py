# -*- coding: utf-8 -*-
"""R11 figures. Reuses the R5 figure style module and redraws only the two figures whose content changed:
  fig0_study_design.png  — '3 human annotators' (was 4), 'dual-LLM positive rate' (was 'precision'),
                           robustness box lists the misclassification scenarios and the 16-series FDR family
  fig3_model_selection.png — cluster labels 'coarse'/'exploratory' (was 'macro'/'meso'), matching the manuscript
  fig6_domain_trends.png — estimates on the analyzed 9,601-repository corpus (R10 used the 9,947-repository tag file);
                           colored = 95% CI excludes 1 and BH q < 0.05 across all 16 series (P8 of r11_reanalysis.py)
Outputs -> ./figures_R11/
"""
import os, sys, importlib.util
import numpy as np, pandas as pd, matplotlib
HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(HERE, 'visuals_jss_r5.py')):        # replication repository: scripts/
    REPO = os.path.dirname(HERE); V5 = os.path.join(HERE, 'visuals_jss_r5.py'); RAW = os.path.join(REPO, 'data', 'github_ai_agent_raw_v2.xlsx')
    XL = os.path.join(REPO, 'results', 'R11', 'R11_reanalysis.xlsx'); OUT = os.path.join(REPO, 'figures', 'R11')
else:                                                              # authors' working folder: 92_…/01_reanalysis/
    ROOT = os.path.dirname(os.path.dirname(HERE)); V5 = os.path.join(ROOT, '20_analysis_code', 'visuals_jss_r5.py'); RAW = os.path.join(ROOT, '10_data_collection', 'github_ai_agent_raw_v2.xlsx')
    XL = os.path.join(HERE, 'R11_reanalysis.xlsx'); OUT = os.path.join(HERE, 'figures_R11')
spec = importlib.util.spec_from_file_location('v5', V5); v5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v5)
plt, ticker, OI = v5.plt, v5.ticker, v5.OI
os.makedirs(OUT, exist_ok=True); v5.OUT = OUT
R = v5.R

def fig0():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(7.6, 3.7), layout='constrained')
    ax.set_xlim(0, 100); ax.set_ylim(15, 101); ax.axis('off')
    C_DATA, C_TOPIC, C_TREND, C_VAL = '#EAF1F7', '#EAF4EE', '#FBF0E6', '#F4F4F4'
    EDGE = '#6B7B8C'; LH, TH, GAP = 3.0, 2.6, 1.2
    def box(x, y, w, h, title, lines, fc, fs=8.0, tfs=9.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2', fc=fc, ec=EDGE, lw=0.8, zorder=2))
        total = TH + GAP + LH * len(lines); top = y + h / 2 + total / 2
        ax.text(x + w / 2, top, title, ha='center', va='top', fontsize=tfs, fontweight='bold', color='#222222', zorder=3)
        ax.text(x + w / 2, top - TH - GAP, '\n'.join(lines), ha='center', va='top', fontsize=fs, color='#333333', zorder=3, linespacing=1.35)
    def arrow(x1, y1, x2, y2, style='-|>'):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=9, lw=0.9, color='#555555', zorder=1))
    def rq(x, y, label):
        ax.text(x, y, label, ha='center', va='center', fontsize=7.6, fontweight='bold', color='#FFFFFF', zorder=4,
                bbox=dict(boxstyle='round,pad=0.28', fc='#4878A8', ec='none'))
    H4 = TH + GAP + LH * 4 + 2.4
    r1, r2, r3 = 98 - H4, 98 - H4 - 7 - H4, 98 - 2 * (H4 + 7) - H4
    box(2, r1, 27, H4, 'Data collection', ['GitHub Search API (2026-08-08)', '8-query union, stars ≥ 5', 'recursive year→month→week slicing', '(all slices < 1,000 results)'], C_DATA)
    box(36, r1, 25, H4, 'Corpus', ['9,947 unique repositories', '→ 9,601 analyzed (2016–2025)', 'name + description + topic tags'], C_DATA)
    box(68, r1, 30, H4, 'Relevance audit', ['stratified sample n = 404', 'dual-LLM positive rate 81.7%', '(70–90% by cluster)', '3 human annotators (n = 120)'], C_VAL)
    m1 = r1 + H4 / 2; arrow(29, m1, 35.4, m1); arrow(61, m1, 67.4, m1)
    box(2, r2, 34, H4, 'Semantic clustering (technology axis)', ['BGE-M3 embeddings + K-means', 'k = 2–30: silhouette + stability rule → k=5', 'k=12 exploratory (seed ARI 0.63)', 'LLM labels + Self-Refine (measured)'], C_TOPIC)
    box(41, r2, 26, H4, 'Baselines', ['LDA · NMF', 'TF-IDF + K-means', 'BERTopic', 'metrics: $c_v$, NPMI, diversity'], C_TOPIC)
    box(72, r2, 26, H4, 'Domain axis', ['11-domain keyword list', '(+ General, multi-label)', 'dual-LLM validation (n = 300)'], C_TOPIC)
    t2 = r2 + H4
    arrow(48.5, r1 - 0.6, 19, t2 + 0.6); arrow(48.5, r1 - 0.6, 54, t2 + 0.6); arrow(48.5, r1 - 0.6, 85, t2 + 0.6)
    m2 = r2 + H4 / 2; arrow(36.6, m2, 40.4, m2, style='<|-|>')
    box(2, r3, 46, H4, 'Trend, model specification, change points', ['binomial GLM: OR/yr, 95% CI', 'BH-FDR across 16 series', 'log-linear / spline / segmented / window / quarterly', 'PELT, 30-configuration sensitivity grid'], C_TREND)
    box(55, r3, 43, H4, 'Robustness', ['stars ≥ {5, 10, 50} × archived incl./excl.', 'seed and subsampling stability', 'active-24-month restriction',
                                     'misclassification scenarios + tipping point'], C_VAL)
    t3 = r3 + H4
    arrow(19, r2 - 0.6, 19, t3 + 0.6); arrow(85, r2 - 0.6, 42, t3 + 0.8)
    m3 = r3 + H4 / 2; arrow(48, m3, 54.4, m3); ax.set_ylim(r3 - 2, 101)
    rq(6, t2 + 0.3, 'RQ1'); rq(45, t2 + 0.3, 'RQ3'); rq(76, t2 + 0.3, 'RQ4'); rq(6, t3 + 0.3, 'RQ2')
    v5.save(fig, 'fig0_study_design.png')

def fig6():
    P8 = pd.read_excel(XL, sheet_name='P8_FDR16')
    dom = P8[~P8['series'].str.startswith('T')].sort_values('full_OR')
    alloc = pd.read_excel(os.path.join(R, 'document_cluster_assignments.xlsx'))
    tag = pd.read_excel(os.path.join(R, 'domain_tagging.xlsx')); tag = tag[tag['full_name'].isin(alloc['full_name'])]
    raw = pd.read_excel(RAW); raw['created_dt'] = pd.to_datetime(raw['created_at']).dt.tz_localize(None)
    tag = tag.merge(raw[['full_name', 'created_dt']], on='full_name'); assert len(tag) == 9601
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.4), layout='constrained', gridspec_kw={'width_ratios': [1, 1.15]})
    a.grid(axis='x', color='#CCCCCC', lw=0.5, alpha=0.6, zorder=0)
    for i, r in enumerate(dom.itertuples()):
        sig = ((r.full_lo > 1) or (r.full_hi < 1)) and r.full_q16 < 0.05
        c = (OI['vermillion'] if r.full_OR > 1 else OI['blue']) if sig else OI['gray']
        a.plot([r.full_lo, r.full_hi], [i, i], color=c, lw=1.4, zorder=3); a.plot([r.full_OR], [i], 'o', ms=4.6, color=c, zorder=4)
    a.axvline(1.0, color='#555555', lw=0.8, ls=(0, (4, 3)), zorder=2)
    a.set_yticks(range(len(dom))); a.set_yticklabels([f'{r.series}  (n={r.n:,})' for r in dom.itertuples()], fontsize=7.6)
    a.set_xlabel('Odds ratio per year (95% CI)'); a.set_title('(a) Domain-share trends, 2016–2025 (GLM)', fontsize=8.5, loc='left')
    a.set_xscale('log'); a.set_xticks([0.7, 1.0, 1.5]); a.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    a.xaxis.set_minor_formatter(ticker.NullFormatter()); a.xaxis.set_minor_locator(ticker.NullLocator()); a.tick_params(length=3)
    picks = ['SoftwareDev/Coding', 'Web/Browser automation', 'Gaming', 'Robotics/Embodied', 'Finance/Trading', 'Data/Analytics']
    colmap = {'SoftwareDev/Coding': OI['vermillion'], 'Web/Browser automation': OI['orange'], 'Gaming': OI['blue'], 'Robotics/Embodied': OI['sky'], 'Finance/Trading': OI['green'], 'Data/Analytics': OI['purple']}
    tq = tag[tag['created_dt'] >= '2022-01-01'].set_index('created_dt'); tot = tq.resample('QS').size()
    gs = b.get_subplotspec().subgridspec(4, 2, hspace=0.45, wspace=0.30, height_ratios=[0.16, 1, 1, 1]); b.remove()
    hdr = fig.add_subplot(gs[0, :]); hdr.axis('off'); hdr.text(0, 0.1, '(b) Quarterly shares of selected domains, 2022–2025', fontsize=8.5, transform=hdr.transAxes)
    short = {'SoftwareDev/Coding': 'Software dev / coding', 'Web/Browser automation': 'Web / browser automation', 'Gaming': 'Gaming',
             'Robotics/Embodied': 'Robotics / embodied', 'Finance/Trading': 'Finance / trading', 'Data/Analytics': 'Data / analytics'}
    for i, d in enumerate(picks):
        axi = fig.add_subplot(gs[1 + i // 2, i % 2]); share = tq[tq[d]].resample('QS').size().reindex(tot.index).fillna(0) / tot
        axi.plot(share.index, share.values, lw=1.3, color=colmap[d], zorder=3); axi.grid(axis='y', color='#DDDDDD', lw=0.4, alpha=0.6, zorder=0)
        axi.set_title(short[d], fontsize=7.2, loc='left', pad=2); axi.set_ylim(0, 0.16); axi.set_yticks([0, 0.05, 0.10, 0.15]); axi.set_yticklabels(['0', '.05', '.10', '.15'])
        axi.tick_params(labelsize=6.3, length=2); axi.spines[['top', 'right']].set_visible(False)
        axi.xaxis.set_major_locator(matplotlib.dates.YearLocator()); axi.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("'%y"))
        if i < 4: axi.set_xticklabels([])
        if i == 2: axi.set_ylabel('Quarterly domain share', fontsize=7.5)
    v5.save(fig, 'fig6_domain_trends.png')

def fig3():
    """R5 fig3 with the manuscript's terms: 'k=5 (coarse)', 'k=12 (exploratory)', x-axis 'Number of topics or clusters k'."""
    import inspect
    src = inspect.getsource(v5.fig3)
    for a, b in [("'k=5 (macro)'", "'k=5 (coarse)'"), ("'k=12 (meso)'", "'k=12 (exploratory)'"), ("'Number of topics k'", "'Number of topics or clusters k'")]:
        assert a in src, a; src = src.replace(a, b)
    ns = vars(v5); exec(compile(src, 'fig3_r11', 'exec'), ns); ns['fig3']()

if __name__ == '__main__':
    fig0(); fig3(); fig6()
