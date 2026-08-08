# Reproducibility Package — Open-Source AI-Agent Ecosystem Study

*(리뷰 항목 15 대응. 최종 수치는 v2 분석 완료 후 이 문서와 결과물_github_v2/에서 확정.)*

## 1. Data collection
- **API**: GitHub Search REST API, `X-GitHub-Api-Version: 2022-11-28`, authenticated (5,000 core/hr, 30 search/min).
- **Collection dates**: initial 2026-08-08 (`데이터/github_collect.py` → `github_ai_agent_raw.xlsx`); de-truncation re-collection 2026-08-08 (`github_collect_2025fix.py` → `github_ai_agent_raw_v2.xlsx`).
- **Queries (8, union, dedup by full_name)**: `topic:ai-agent`, `topic:ai-agents`, `topic:llm-agent`, `topic:llm-agents`, `topic:autonomous-agents`, `topic:agentic-ai`, `"ai agent" in:name,description`, `"llm agent" in:name,description` — each with `stars:>=5 created:YYYY-..` slices.
- **Slicing rule**: yearly slices 2016–2025; any slice with total_count > 1,000 re-sliced monthly; monthly slices > 1,000 re-sliced weekly (recursive). `incomplete_results` logged per slice (`github_collect*.log`); Search API default excludes forks.
- **Fields**: full_name, description, topics, stargazers_count, forks_count, language, created_at, pushed_at, license.spdx_id, archived.
- **Checksums**: 산출 후 `certutil -hashfile ... SHA256` 기록 예정 `[분석 확정 후 기입]`.

## 2. Preprocessing
- Document text = repo name (dash/underscore→space) + description + topic tags; records with <10 chars of description+tags excluded.
- Tokenization (count-based models): regex `[a-z][a-z0-9\-]{2,}`, lowercase.
- Stopwords: query-derived tokens (ai, agent(s), llm(s), agentic 파생 포함) + generic English function words — full list in `analysis_github_v2.py` (STOP, EXTRA).
- gensim Dictionary: no_below=3, no_above=0.1.

## 3. Models (local, Ollama)
| Role | Model | Digest (prefix) | Quant | Params |
|---|---|---|---|---|
| Embedding | bge-m3:latest | 7907646426070047a77 | F16 | 567M |
| Label generation | gemma3:12b | f4031aab637d1ffa37b | Q4_K_M | 12.2B |
| Specificity judge | llama3.1:8b | 46e0c10c039e0191193 | Q4_K_M | 8.0B |
| Audit classifier A | qwen2.5:7b | 845dbda0ea48ed749ca | Q4_K_M | 7.6B |
| Audit classifier B | llama3.1:8b | 46e0c10c039e0191193 | Q4_K_M | 8.0B |
- Generation options: temperature=0.2 (labels/refine), 0.0 (audit classification); other options Ollama defaults. Prompt full texts: `analysis_github_v2.py`(label_pipeline), `audit_kit.py`(PROMPT).

## 4. Analysis parameters
- KMeans: k=2..30, n_init=10, random_state=100 (main); stability = 20 seeds (1..20) + 20×80% subsampling (RandomState 42); silhouette on 5,000-doc fixed subsample (RandomState 0), cosine.
- Baselines: LDA (gensim, passes=10, random_state=100), NMF (init=nndsvda, max_iter=400, random_state=100), TF-IDF+KMeans (same KMeans params), BERTopic 0.17.4 (default UMAP/HDBSCAN, precomputed bge-m3 embeddings; outliers reported separately).
- Coherence: gensim CoherenceModel c_v & c_npmi, processes=1, topics restricted to dictionary tokens (≥3 valid terms).
- Diversity: unique / (k×10) over each method's raw top-10 terms (dictionary-unfiltered) — definition fixed after metric audit.
- GLM: per-topic Binomial GLM, endog=(count, N−count), predictor=(year−2016); OR/yr=exp(β1), 95% CI=exp(β1±1.96·SE); BH-FDR across non-emergent topics; taxonomy: Emergent if <5% of topic docs created before 2023; else growing/declining at q<0.05 else Stable.
- PELT (ruptures 1.1.10): monthly total counts (120 pts, log1p) — sensitivity grid model∈{l2,rbf} × pen∈{0.5,1,2,3} × min_size∈{2,3,6}; quarterly per-topic shares (40 pts, l2, pen=0.02, min_size=4).
- Sensitivity: stars≥{5,10,50} × archived {excl, incl} — GLM/taxonomy 재계산.

## 5. Environment
- Windows 11 Pro, RTX 3090 24GB; Python 3.11.9; scikit-learn 1.8.0, gensim 4.4.0, statsmodels 0.14.6, ruptures 1.1.10, bertopic 0.17.4, pandas/numpy per requirements `[freeze 예정]`.

## 6. Code & artifacts
- Collection: `데이터/github_collect.py`, `데이터/github_collect_2025fix.py` (+logs)
- Analysis: `analysis_github_v2.py` → `결과물_github_v2/` (all xlsx/figures)
- Corpus audit: `audit_kit.py` → `감사_audit/` (stratified 400 sample, dual-LLM provisional labels, human rating sheets, `compute_alpha.py`)
- Draft build: `초안/md_to_docx.py`
