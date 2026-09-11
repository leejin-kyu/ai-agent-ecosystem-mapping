# -*- coding: utf-8 -*-
"""현행 용어 + 표준 후보 용어의 선행연구 DF 계산 → 30_분석결과/용어검토/후보용어DF.csv"""
import json, re, os, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '30_분석결과', '용어검토')
docs = {k: re.sub(r'[‐-―]', '-', v.lower()) for k, v in json.load(open(os.path.join(OUT, '선행연구_전문텍스트.json'), encoding='utf-8')).items()}
def df(t):
    t = t.lower(); pats = {t, t.replace('-', ' '), t.replace(' ', '-')}
    if not t.endswith('s'): pats |= {p + 's' for p in list(pats)}
    hit = [k[:4] + '_' + k.split('_')[1][:10] for k, d in docs.items() if any(p in d for p in pats)]
    return len(hit), sum(sum(d.count(p) for p in pats) for d in docs.values()), hit
groups = {
'segment/cluster': ['semantic repository segment', 'semantic segment', 'segment', 'cluster', 'clusters', 'semantic cluster', 'topic', 'topics', 'theme', 'category', 'categories', 'group'],
'composition/time': ['creation-time composition', 'composition', 'temporal distribution', 'over time', 'distribution over time', 'evolution', 'trend', 'trends', 'temporal trend', 'temporal dynamics', 'emergence', 'emerging', 'emergent', 'growth', 'longitudinal', 'time series'],
'regime/changepoint': ['regime change', 'regime', 'change point', 'changepoint', 'change-point detection', 'structural change', 'structural break', 'breakpoint'],
'correlate': ['temporal correlate', 'correlate', 'coincide', 'coincides with', 'temporal association', 'correlation', 'association', 'aligned with', 'alignment'],
'share': ['repository share', 'share', 'proportion', 'percentage', 'fraction', 'relative frequency', 'prevalence', 'relative share'],
'impurity/precision': ['corpus impurity', 'impurity', 'noise', 'noisy', 'false positive', 'false positives', 'precision', 'relevance', 'relevant', 'irrelevant', 'misclassification', 'misclassified'],
'audit': ['relevance audit', 'audit', 'manual inspection', 'manual validation', 'manual labeling', 'manual annotation', 'human annotation', 'human labeling', 'annotate', 'annotation', 'annotator', 'annotators', 'human evaluator', 'human evaluators', 'human raters', 'raters', 'rater', 'human judges', 'human judgment', 'human evaluation', 'coder', 'coders', 'inter-rater', 'inter-annotator', 'agreement', 'cohen', 'kappa', 'krippendorff', 'fleiss', 'majority vote', 'majority voting', 'blind', 'blinded', 'ground truth', 'gold standard'],
'functional form': ['functional form', 'model specification', 'specification', 'log-linear', 'loglinear', 'spline', 'splines', 'segmented regression', 'piecewise', 'generalized linear model', 'glm', 'binomial', 'logistic regression', 'odds ratio', 'confidence interval', 'false discovery rate', 'benjamini', 'multiple comparison', 'multiple comparisons', 'multiple testing', 'sensitivity analysis', 'sensitivity analyses', 'robustness check', 'robustness', 'robust', 'monte carlo', 'bootstrap', 'permutation'],
'collection': ['recursive date slicing', 'date slicing', 'slicing', 'partition', 'partitioned', 'time window', 'time windows', 'result limit', '1,000 results', 'api limit', 'rate limit', 'pagination', 'truncation', 'truncation-free', 'snapshot', 'crawl', 'crawled', 'collected', 'data collection', 'mining software repositories', 'msr', 'github search api', 'search api', 'github api', 'rest api', 'graphql'],
'lexicon': ['lexicon-defined', 'lexicon', 'keyword-based', 'keyword', 'keywords', 'keyword matching', 'regular expression', 'regex', 'dictionary', 'application domain', 'application domains', 'domain', 'vertical', 'use case', 'use cases'],
'granularity': ['macro', 'meso', 'coarse-grained', 'fine-grained', 'coarse', 'granularity', 'granularities', 'hierarchical', 'two levels', 'level of granularity'],
'stability': ['stability', 'stable', 'seed', 'seeds', 'random seed', 'random initialization', 'initialization', 'reproducib', 'adjusted rand index', 'rand index', 'ari', 'silhouette', 'coherence', 'npmi', 'diversity', 'topic diversity', 'outlier', 'outliers', 'coverage', 'k-means', 'kmeans', 'embedding', 'embeddings', 'sentence embedding', 'umap', 'hdbscan', 'elbow'],
'agents': ['ai agent', 'ai agents', 'llm agent', 'llm agents', 'llm-based agent', 'llm-based agents', 'autonomous agent', 'autonomous agents', 'agentic', 'agent framework', 'agent frameworks', 'agentic application', 'agentic applications', 'agent application', 'multi-agent', 'orchestration', 'workflow', 'framework', 'frameworks', 'tool use', 'tool-use', 'tool calling', 'function calling', 'model context protocol', 'mcp', 'mcp server', 'coding agent', 'coding agents', 'code agent', 'code generation', 'coding assistant', 'software engineering agent', 'programming', 'developer tool', 'developer tools', 'game', 'games', 'gaming', 'game agent', 'web automation', 'browser automation', 'browser agent', 'web agent'],
'repos': ['repository', 'repositories', 'github repositories', 'open-source', 'open source', 'oss', 'star', 'stars', 'stargazers', 'fork', 'forks', 'popularity', 'popular', 'archived', 'active', 'activity', 'commit', 'commits', 'pushed', 'maintained', 'abandoned', 'dormant', 'survivorship', 'survivorship bias', 'selection bias', 'sampling bias', 'creation date', 'created', 'creation'],
'study': ['empirical study', 'large-scale', 'corpus-scale', 'corpus', 'characteriz', 'characterization', 'characterize', 'mapping', 'landscape', 'ecosystem', 'population', 'taxonomy', 'composition', 'structure', 'construct', 'construct validity', 'internal validity', 'external validity', 'conclusion validity', 'threats to validity', 'operationaliz', 'proxy', 'metadata', 'description', 'descriptions', 'readme', 'topic tag', 'topic tags', 'github topics', 'tags'],
'methods': ['self-refine', 'lda', 'latent dirichlet allocation', 'nmf', 'non-negative matrix factorization', 'tf-idf', 'bertopic', 'top2vec', 'bge', 'bge-m3', 'llm-as-a-judge', 'llm judge', 'label', 'labels', 'labeling', 'labelling', 'specificity', 'redundancy', 'representative', 'representative terms', 'top terms', 'top words'],
}
rows = []
for g, terms in groups.items():
    for t in terms:
        d, tot, h = df(t); rows.append((g, t, d, tot, ', '.join(h)[:120])); print(f'{g:18s} | {t:32s} | DF {d:2d} | total {tot:5d}')
pd.DataFrame(rows, columns=['group', 'term', 'prior_DF', 'prior_total', 'docs']).to_csv(os.path.join(OUT, '후보용어DF.csv'), index=False, encoding='utf-8-sig')
