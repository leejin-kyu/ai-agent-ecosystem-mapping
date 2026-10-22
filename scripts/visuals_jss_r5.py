# JSS 수준 출판용 Figure 6종 — 사용: python visuals_jss.py [1|2|3|4|5|6|all]
# 관례: 그림 내부 제목 없음(캡션은 원고), Okabe-Ito CVD-safe 팔레트, 직접 라벨, 300dpi,
#       constrained_layout으로 텍스트 잘림 방지, GLM은 forest plot.
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import ticker

BASE = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(os.path.dirname(BASE), 'results')):   # replication repository layout
    R = os.path.join(os.path.dirname(BASE), 'results'); RAW = os.path.join(os.path.dirname(BASE), 'data', 'github_ai_agent_raw_v2.xlsx')
    OUT = os.path.join(os.path.dirname(BASE), 'figures', 'R5')
else:                                                              # authors' working-folder layout
    R = os.path.join(os.path.dirname(BASE), '30_분석결과'); RAW = os.path.join(os.path.dirname(BASE), '10_데이터수집', 'github_ai_agent_raw_v2.xlsx')
    OUT = os.path.join(R, '논문그림_fig0-6', 'R5')
os.makedirs(OUT, exist_ok=True)

# ── 공통 스타일 ──
plt.rcParams.update({
    'font.family': ['Arial', 'DejaVu Sans'],
    'font.size': 8.5, 'axes.labelsize': 9, 'axes.titlesize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'axes.linewidth': 0.8, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.dpi': 100, 'savefig.dpi': 300,
    'axes.unicode_minus': False,
})
# Okabe-Ito (colorblind-safe, 출판 표준)
OI = {'blue': '#0072B2', 'vermillion': '#D55E00', 'green': '#009E73',
      'purple': '#CC79A7', 'orange': '#E69F00', 'sky': '#56B4E9',
      'yellow': '#F0E442', 'black': '#000000', 'gray': '#8A8A8A'}
GRID = dict(axis='y', color='#CCCCCC', lw=0.5, alpha=0.6, zorder=0)

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=300, bbox_inches='tight', pad_inches=0.03, facecolor='white')
    plt.close(fig)
    print('saved', p)

def load_alloc():
    alloc = pd.read_excel(os.path.join(R, '문서_군집할당.xlsx'))
    raw = pd.read_excel(RAW)
    raw['created_dt'] = pd.to_datetime(raw['created_at']).dt.tz_localize(None)
    return alloc.merge(raw[['full_name', 'created_dt']], on='full_name')

TOPIC_SHORT = {0: 'T0 Frameworks & dev tools', 1: 'T1 LangChain/LangGraph frameworks',
               2: 'T2 Orchestration & automation', 3: 'T3 MCP systems', 4: 'T4 Coding agents'}

# ═══ Figure 1: 연도별 생성 레포 수 (막대 + 값 라벨) ═══
def fig1():
    alloc = pd.read_excel(os.path.join(R, '문서_군집할당.xlsx'))
    cnt = alloc['year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5.6, 2.9), layout='constrained')
    ax.grid(**GRID)
    bars = ax.bar(cnt.index.astype(str), cnt.values, width=0.62,
                  color=OI['blue'], edgecolor='none', zorder=3)
    for b, v in zip(bars, cnt.values):
        ax.annotate(f'{v:,}', (b.get_x() + b.get_width() / 2, v),
                    xytext=(0, 2), textcoords='offset points',
                    ha='center', va='bottom', fontsize=7.5, color='#333333')
    ax.set_ylabel('Repositories created')
    ax.set_xlabel('Creation year')
    ax.set_ylim(0, cnt.max() * 1.09)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.tick_params(length=3)
    save(fig, 'fig1_creation_years.png')

# ═══ Figure 2: 월별 시계열(로그) + PELT 변화점 ═══
def fig2():
    df = load_alloc()
    mon = df.set_index('created_dt').resample('MS').size().reindex(
        pd.date_range('2016-01-01', '2025-12-01', freq='MS')).fillna(0)
    fig, ax = plt.subplots(figsize=(6.4, 2.9), layout='constrained')
    ax.grid(**GRID)
    ax.plot(mon.index, mon.values + 1, color=OI['blue'], lw=1.4, zorder=3)
    ax.set_yscale('log')
    ax.set_ylabel('Repositories created per month + 1')
    ax.set_xlabel('Month of creation')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    # 변화점: 2023-02 (30/30 robust), 2018-12 (secondary)
    cps = [('2023-02-01', OI['vermillion'], 'Feb 2023\n(30/30 configurations)', '-'),
           ('2018-12-01', OI['gray'], 'Dec 2018\n(secondary)', (0, (4, 3)))]
    for d, c, lbl, ls in cps:
        x = pd.Timestamp(d)
        ax.axvline(x, color=c, lw=1.1, ls=ls, zorder=2)
        ax.annotate(lbl, (x, ax.get_ylim()[1]), xytext=(4, -4),
                    textcoords='offset points', ha='left', va='top',
                    fontsize=7.5, color=c)
    # ChatGPT 출시 참조 마커 (정합, 비인과)
    x = pd.Timestamp('2022-11-30')
    ax.annotate('ChatGPT release (Nov 2022)', (x, 1.32), xytext=(-8, 0),
                textcoords='offset points', ha='right', va='center',
                fontsize=7.5, color='#555555')
    ax.plot([x], [1.32], marker='>', color='#555555', ms=4.5, zorder=4, clip_on=False)
    ax.tick_params(length=3)
    save(fig, 'fig2_monthly_changepoints.png')

# ═══ Figure 3: (a) 실루엣 k-선정 + (b) 방법별 c_v 스윕 ═══
def fig3():
    fig = plt.figure(figsize=(7.0, 3.2))
    ga = fig.add_axes([0.065, 0.145, 0.255, 0.76])
    gb = fig.add_axes([0.40, 0.145, 0.40, 0.76])
    # (a) 실루엣
    sil = pd.read_excel(os.path.join(R, '군집_k선정_실루엣_2to30.xlsx'))
    ga.grid(**GRID)
    ga.plot(sil['k'], sil['silhouette'], '-', lw=1.4, color=OI['blue'],
            marker='o', ms=2.6, mec='none', zorder=3)
    g2 = sil[sil.k == 2].iloc[0]; g5 = sil[sil.k == 5].iloc[0]; g12 = sil[sil.k == 12].iloc[0]
    for r, lbl, dx, dy, ha in [(g2, 'k=2 (global max)', 2, 8, 'left'),
                               (g5, 'k=5 (macro)', 7, -3, 'left'),
                               (g12, 'k=12 (meso)', 5, 5, 'left')]:
        ga.plot([r.k], [r.silhouette], marker='o', ms=6, mfc='white', mec=OI['vermillion'],
                mew=1.4, zorder=4)
        ga.annotate(lbl, (r.k, r.silhouette), xytext=(dx, dy), textcoords='offset points',
                    ha=ha, fontsize=7.2, color=OI['vermillion'])
    ga.set_xlabel('Number of clusters k')
    ga.set_ylabel('Cosine silhouette')
    ga.set_xticks([2, 5, 12, 20, 30])
    ga.set_title('(a) Cluster-number selection', fontsize=8.5, loc='left')
    ga.margins(y=0.12); ga.tick_params(length=3)
    # (b) c_v 스윕
    sw = pd.read_excel(os.path.join(R, '본비교_k스윕.xlsx'))
    order = ['TF-IDF+KMeans', 'BGE-M3+KMeans (proposed)', 'NMF (TF-IDF)', 'LDA (gensim)']
    disp = {'TF-IDF+KMeans': 'TF-IDF + K-means', 'BGE-M3+KMeans (proposed)': 'BGE-M3 + K-means',
            'NMF (TF-IDF)': 'NMF', 'LDA (gensim)': 'LDA'}
    cols = {'TF-IDF+KMeans': OI['vermillion'], 'BGE-M3+KMeans (proposed)': OI['blue'],
            'NMF (TF-IDF)': OI['green'], 'LDA (gensim)': OI['gray']}
    gb.grid(**GRID)
    for m in order:
        g = sw[sw.method == m].sort_values('k')
        gb.plot(g['k'], g['c_v'], '-', lw=1.4, color=cols[m], zorder=3,
                marker='o', ms=2.4, mec='none')
        best = g.loc[g.c_v.idxmax()]
        gb.plot([best.k], [best.c_v], marker='o', ms=6, mfc='white', mec=cols[m],
                mew=1.4, zorder=4)
        gb.annotate(f'{disp[m]}  ({best.c_v:.3f}, k={int(best.k)})',
                    (30, g[g.k == 30].c_v.iloc[0]), xytext=(5, 0),
                    textcoords='offset points', va='center', fontsize=7.3, color=cols[m])
    gb.set_xlabel('Number of topics k')
    gb.set_ylabel('Coherence $c_v$')
    gb.set_xlim(1.5, 30.5)
    gb.set_xticks([2, 5, 10, 15, 20, 25, 30])
    gb.set_title('(b) Coherence by method', fontsize=8.5, loc='left')
    gb.margins(y=0.08); gb.tick_params(length=3)
    save(fig, 'fig3_model_selection.png')

# ═══ Figure 4: 토픽×연도 비중 히트맵 ═══
def fig4():
    share = pd.read_excel(os.path.join(R, '연도별_토픽비중.xlsx'), index_col=0)
    share.columns = share.columns.astype(int)
    M = share.T.reindex(range(5)).values  # topic × year
    fig, ax = plt.subplots(figsize=(6.2, 2.5), layout='constrained')
    im = ax.imshow(M, aspect='auto', cmap='Blues', vmin=0, vmax=np.nanmax(M))
    ax.set_xticks(range(share.shape[0]))
    ax.set_xticklabels(share.index)
    ax.set_yticks(range(5))
    ax.set_yticklabels([TOPIC_SHORT[t] for t in range(5)], fontsize=8)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=7,
                    color='white' if v > np.nanmax(M) * 0.55 else '#333333')
    ax.set_xlabel('Creation year')
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, shrink=0.9, pad=0.015)
    cb.set_label('Cluster share', fontsize=8)
    cb.ax.tick_params(labelsize=7.5, length=2)
    cb.outline.set_linewidth(0.6)
    save(fig, 'fig4_topic_year_heatmap.png')

# ═══ Figure 5: (a) 분기별 토픽 비중 + (b) GLM OR forest ═══
def fig5():
    df = load_alloc()
    glm = pd.read_excel(os.path.join(R, 'GLM_taxonomy_macro.xlsx'))
    q = df.set_index('created_dt').groupby([pd.Grouper(freq='QS'), 'cluster']).size().unstack(fill_value=0)
    qs = q.div(q.sum(axis=1), axis=0)
    qs = qs[qs.index >= '2022-01-01']
    cols = {0: OI['gray'], 1: OI['purple'], 2: OI['blue'], 3: OI['vermillion'], 4: OI['green']}
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.0), layout='constrained',
                               gridspec_kw={'width_ratios': [1.45, 1]})
    # (a) 분기 추이
    a.grid(**GRID)
    for t in range(5):
        y = qs[t]
        a.plot(y.index, y.values, lw=1.5, color=cols[t], zorder=3)
    # 직접 라벨 (겹침 방지 수동 오프셋)
    endx = qs.index[-1]
    offs = {0: 0, 1: 0, 2: 0, 3: 0.012, 4: -0.012}
    for t in range(5):
        a.annotate(f'T{t}', (endx, qs[t].iloc[-1] + offs[t]), xytext=(4, 0),
                   textcoords='offset points', va='center', fontsize=8,
                   color=cols[t], fontweight='bold')
    a.set_ylabel('Quarterly cluster share')
    a.set_xlabel('Quarter of creation')
    a.set_title('(a) Cluster shares, 2022–2025', fontsize=8.5, loc='left')
    a.tick_params(length=3, axis='x', labelrotation=0)
    a.xaxis.set_major_locator(matplotlib.dates.YearLocator())
    a.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
    # (b) forest plot
    b.grid(axis='x', color='#CCCCCC', lw=0.5, alpha=0.6, zorder=0)
    glm2 = glm.sort_values('OR_per_year')
    ypos = np.arange(len(glm2))
    for i, r in enumerate(glm2.itertuples()):
        c = cols[r.cluster]
        b.plot([r.CI_lo, r.CI_hi], [i, i], color=c, lw=1.4, zorder=3)
        b.plot([r.OR_per_year], [i], 'o', ms=5, color=c, zorder=4)
    b.axvline(1.0, color='#555555', lw=0.8, ls=(0, (4, 3)), zorder=2)
    b.set_yticks(ypos)
    b.set_yticklabels([TOPIC_SHORT[r.cluster] for r in glm2.itertuples()], fontsize=7.8)
    b.set_xlabel('Odds ratio per year (95% CI)')
    b.set_title('(b) Cluster-share trends (log-linear GLM)', fontsize=8.5, loc='left')
    b.set_xscale('log')
    b.set_xticks([0.75, 1.0, 1.5, 2.0])
    b.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    b.tick_params(length=3)
    save(fig, 'fig5_topic_trends_forest.png')

# ═══ Figure 6: (a) 도메인 OR forest + (b) 분기 비중 small multiples ═══
def fig6():
    dom = pd.read_excel(os.path.join(R, '도메인_GLM_taxonomy.xlsx'))
    dom = dom[dom.domain != 'General'].sort_values('OR_per_year')
    tag = pd.read_excel(os.path.join(R, '도메인_태깅.xlsx'))
    raw = pd.read_excel(RAW)
    raw['created_dt'] = pd.to_datetime(raw['created_at']).dt.tz_localize(None)
    tag = tag.merge(raw[['full_name', 'created_dt']], on='full_name')
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 3.4), layout='constrained',
                               gridspec_kw={'width_ratios': [1, 1.15]})
    # (a) forest
    a.grid(axis='x', color='#CCCCCC', lw=0.5, alpha=0.6, zorder=0)
    for i, r in enumerate(dom.itertuples()):
        sig = (r.CI_lo > 1) or (r.CI_hi < 1)
        c = (OI['vermillion'] if r.OR_per_year > 1 else OI['blue']) if sig else OI['gray']
        a.plot([r.CI_lo, r.CI_hi], [i, i], color=c, lw=1.4, zorder=3)
        a.plot([r.OR_per_year], [i], 'o', ms=4.6, color=c, zorder=4)
    a.axvline(1.0, color='#555555', lw=0.8, ls=(0, (4, 3)), zorder=2)
    a.set_yticks(range(len(dom)))
    a.set_yticklabels([f'{r.domain}  (n={r.n:,})' for r in dom.itertuples()], fontsize=7.6)
    a.set_xlabel('Odds ratio per year (95% CI)')
    a.set_title('(a) Domain-share trends (GLM)', fontsize=8.5, loc='left')
    a.set_xscale('log')
    a.set_xticks([0.7, 1.0, 1.5])
    a.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    a.xaxis.set_minor_formatter(ticker.NullFormatter())
    a.xaxis.set_minor_locator(ticker.NullLocator())
    a.tick_params(length=3)
    # (b) small multiples: 분기 비중 (선정 6개 도메인)
    picks = ['SoftwareDev/Coding', 'Web/Browser automation', 'Gaming',
             'Robotics/Embodied', 'Finance/Trading', 'Data/Analytics']
    colmap = {'SoftwareDev/Coding': OI['vermillion'], 'Web/Browser automation': OI['orange'],
              'Gaming': OI['blue'], 'Robotics/Embodied': OI['sky'],
              'Finance/Trading': OI['green'], 'Data/Analytics': OI['purple']}
    tq = tag[tag['created_dt'] >= '2022-01-01'].set_index('created_dt')
    tot = tq.resample('QS').size()
    gs = b.get_subplotspec().subgridspec(4, 2, hspace=0.45, wspace=0.30,
                                        height_ratios=[0.16, 1, 1, 1])
    b.remove()
    hdr = fig.add_subplot(gs[0, :]); hdr.axis('off')
    hdr.text(0, 0.1, '(b) Quarterly shares of selected domains, 2022–2025',
             fontsize=8.5, transform=hdr.transAxes)
    short = {'SoftwareDev/Coding': 'Software dev / coding',
             'Web/Browser automation': 'Web / browser automation',
             'Gaming': 'Gaming', 'Robotics/Embodied': 'Robotics / embodied',
             'Finance/Trading': 'Finance / trading', 'Data/Analytics': 'Data / analytics'}
    for i, d in enumerate(picks):
        axi = fig.add_subplot(gs[1 + i // 2, i % 2])
        share = tq[tq[d]].resample('QS').size().reindex(tot.index).fillna(0) / tot
        axi.plot(share.index, share.values, lw=1.3, color=colmap[d], zorder=3)
        axi.grid(axis='y', color='#DDDDDD', lw=0.4, alpha=0.6, zorder=0)
        axi.set_title(short[d], fontsize=7.2, loc='left', pad=2)
        axi.set_ylim(0, 0.16)
        axi.set_yticks([0, 0.05, 0.10, 0.15])
        axi.set_yticklabels(['0', '.05', '.10', '.15'])
        axi.tick_params(labelsize=6.3, length=2)
        axi.spines[['top', 'right']].set_visible(False)
        axi.xaxis.set_major_locator(matplotlib.dates.YearLocator())
        axi.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("'%y"))
        if i < 4:
            axi.set_xticklabels([])
        if i == 2:
            axi.set_ylabel('Quarterly domain share', fontsize=7.5)
    save(fig, 'fig6_domain_trends.png')


# ═══ Figure 0: 연구 설계 개요도 (Method 서두) ═══
def fig0():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(7.6, 3.7), layout='constrained')
    ax.set_xlim(0, 100); ax.set_ylim(15, 101); ax.axis('off')
    C_DATA, C_TOPIC, C_TREND, C_VAL = '#EAF1F7', '#EAF4EE', '#FBF0E6', '#F4F4F4'
    EDGE = '#6B7B8C'
    LH = 3.0    # 본문 1행 높이(데이터 단위)
    TH = 2.6    # 제목 높이
    GAP = 1.2   # 제목-본문 간격

    def box(x, y, w, h, title, lines, fc, fs=8.0, tfs=9.0):
        """텍스트 블록(제목+본문)을 상자 안에서 수직 중앙 정렬 → 상자 하단 공백 제거"""
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2',
                                    fc=fc, ec=EDGE, lw=0.8, zorder=2))
        total = TH + GAP + LH * len(lines)
        top = y + h/2 + total/2
        ax.text(x + w/2, top, title, ha='center', va='top', fontsize=tfs,
                fontweight='bold', color='#222222', zorder=3)
        ax.text(x + w/2, top - TH - GAP, '\n'.join(lines), ha='center', va='top',
                fontsize=fs, color='#333333', zorder=3, linespacing=1.35)

    def arrow(x1, y1, x2, y2, style='-|>'):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                     mutation_scale=9, lw=0.9, color='#555555', zorder=1))

    def rq(x, y, label):
        ax.text(x, y, label, ha='center', va='center', fontsize=7.6, fontweight='bold',
                color='#FFFFFF', zorder=4,
                bbox=dict(boxstyle='round,pad=0.28', fc='#4878A8', ec='none'))

    # 1행: 수집 → 코퍼스 → 감사
    # 상자 높이 = 4행 텍스트 블록에 여백 최소로 맞춤(H4), 행 간격 7
    H4 = TH + GAP + LH * 4 + 2.4
    r1, r2, r3 = 98 - H4, 98 - H4 - 7 - H4, 98 - 2 * (H4 + 7) - H4
    box(2, r1, 27, H4, 'Data collection',
        ['GitHub Search API (2026-08-08)', '8-query union, stars ≥ 5',
         'recursive year→month→week slicing', '(all slices < 1,000 results)'], C_DATA)
    box(36, r1, 25, H4, 'Corpus',
        ['9,947 unique repositories', '→ 9,601 analyzed (2016–2025)',
         'name + description + topic tags'], C_DATA)
    box(68, r1, 30, H4, 'Relevance audit',
        ['stratified sample n = 404', 'dual-LLM classification',
         'precision 81.7% [77.6, 85.2]', 'by cluster 70–90%; 4 human annotators'], C_VAL)
    m1 = r1 + H4 / 2
    arrow(29, m1, 35.4, m1); arrow(61, m1, 67.4, m1)

    # 2행: 토픽 축 + 베이스라인
    box(2, r2, 34, H4, 'Semantic clustering (technology axis)',
        ['BGE-M3 embeddings + K-means', 'k = 2–30: silhouette + stability rule → k=5',
         'k=12 exploratory (seed ARI 0.63)', 'LLM labels + Self-Refine (measured)'], C_TOPIC)
    box(41, r2, 26, H4, 'Baselines',
        ['LDA · NMF', 'TF-IDF + K-means', 'BERTopic',
         'metrics: $c_v$, NPMI, diversity'], C_TOPIC)
    box(72, r2, 26, H4, 'Domain axis',
        ['11-domain keyword lexicon', '(+ General, multi-label)',
         'dual-LLM validation (n = 300)'], C_TOPIC)
    t2 = r2 + H4
    arrow(48.5, r1 - 0.6, 19, t2 + 0.6)   # corpus -> topic
    arrow(48.5, r1 - 0.6, 54, t2 + 0.6)   # corpus -> baselines
    arrow(48.5, r1 - 0.6, 85, t2 + 0.6)   # corpus -> domain
    m2 = r2 + H4 / 2
    arrow(36.6, m2, 40.4, m2, style='<|-|>')  # topic <-> baselines 비교

    # 3행: 추이 분석 → 민감도
    box(2, r3, 46, H4, 'Trend, functional form, change points',
        ['binomial GLM: OR/yr, 95% CI, BH-FDR', 'spline / segmented / window / quarterly specs',
         'PELT on monthly series,', '30-configuration sensitivity grid'], C_TREND)
    box(55, r3, 43, H4, 'Robustness',
        ['stars ≥ {5, 10, 50} × archived incl./excl.', 'seed and subsampling stability',
         'active-24-month restriction; cohort activity', 'Self-Refine pre/post ablation'], C_VAL)
    t3 = r3 + H4
    arrow(19, r2 - 0.6, 19, t3 + 0.6)    # topic -> trend
    arrow(85, r2 - 0.6, 42, t3 + 0.8)    # domain -> trend (도메인도 동일 GLM/taxonomy)
    m3 = r3 + H4 / 2
    arrow(48, m3, 54.4, m3)  # trend -> robustness
    ax.set_ylim(r3 - 2, 101)

    # RQ 태그
    rq(6, t2 + 0.3, 'RQ1'); rq(45, t2 + 0.3, 'RQ3'); rq(76, t2 + 0.3, 'RQ4'); rq(6, t3 + 0.3, 'RQ2')
    save(fig, 'fig0_study_design.png')

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    fns = {'0': fig0, '1': fig1, '2': fig2, '3': fig3, '4': fig4, '5': fig5, '6': fig6}
    if arg == 'all':
        for f in fns.values(): f()
    else:
        fns[arg]()
