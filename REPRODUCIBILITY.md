# Reproducibility Package: Open-Source AI-Agent Ecosystem Study

*(Prepared in response to review item 15. Final values are those in this document and in `results/`.)*

## 1. Data collection
- **API**: GitHub Search REST API, `X-GitHub-Api-Version: 2022-11-28`, authenticated (5,000 core requests/hour, 30 search requests/minute).
- **Collection dates**: initial collection 2026-08-08 (`scripts/github_collect.py` → `github_ai_agent_raw.xlsx`, not included in this repository because it is superseded by the v2 file); de-truncation re-collection 2026-08-08 (`scripts/github_collect_2025fix.py` → `data/github_ai_agent_raw_v2.xlsx`).
- **Queries (8, union, deduplicated by full_name)**: `topic:ai-agent`, `topic:ai-agents`, `topic:llm-agent`, `topic:llm-agents`, `topic:autonomous-agents`, `topic:agentic-ai`, `"ai agent" in:name,description`, `"llm agent" in:name,description`, each with `stars:>=5 created:YYYY-..` slices.
- **Slicing rule**: yearly slices 2016–2025; any slice with total_count > 1,000 re-sliced monthly; monthly slices > 1,000 re-sliced weekly (recursive). `incomplete_results` is logged per slice (`data/github_collect*.log`); the Search API excludes forks by default.
- **Fields**: full_name, description, topics, stargazers_count, forks_count, language, created_at, pushed_at, license.spdx_id, archived.
- **Checksums (SHA-256)** of the released data files (these files are byte-identical to the versions in the repository before the English-language renaming; only file names changed where applicable):

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `data/github_ai_agent_raw_v2.xlsx` | 1,433,689 | `a5412639621f95a128fd42c6bd1a1507410f76d1ed4b17b85d0086b19ccfe575` |
| `data/github_collect.log` | 6,760 | `76c24b48dccd2cb2b292acbbdca7b327ba787b2d2fb7bfee0d665d110eaf21fa` |
| `data/github_collect_2025fix.log` | 3,568 | `a43cec64db474c93348a608cde19150a329f0d8b7fb6aa99a8822eb2566b9452` |
| `results/embeddings.npy` | 39,325,824 | `dde3c473ee3b275799939227523979781f6180b384d585763c10ca7c00b75ea9` |
| `results/emb_keys.npy` | 276,059 | `b9365650d398fc1fa030a9699ff771161da5f5ed41a4c6ffb7e6a40c9dc83f68` |
| `results/document_cluster_assignments.xlsx` | 460,307 | `2ded874152d26dafc8d2e36724c89d00bce2922007475f3d9cfc9a7634d83387` |
| `results/domain_tagging.xlsx` | 497,058 | `92f9871f98eb771569b3de0b2a26f1132dc423d8f663035489a690b2b1095565` |

  On Windows: `certutil -hashfile <file> SHA256`; on Linux/macOS: `sha256sum <file>`.

## 2. Preprocessing
- Document text = repository name (dash/underscore → space) + description + topic tags; records with fewer than 10 characters of description + tags are excluded.
- Tokenization (count-based models): regex `[a-z][a-z0-9\-]{2,}`, lowercase.
- Stopwords: query-derived tokens (ai, agent(s), llm(s), including agentic variants) + generic English function words; full lists in `scripts/analysis_github_v2.py` (`STOP`, `EXTRA`).
- gensim Dictionary: no_below=3, no_above=0.1.

## 3. Models (local, Ollama)
| Role | Model | Digest (prefix) | Quant | Params |
|---|---|---|---|---|
| Embedding | bge-m3:latest | 7907646426070047a77 | F16 | 567M |
| Label generation | gemma3:12b | f4031aab637d1ffa37b | Q4_K_M | 12.2B |
| Specificity judge | llama3.1:8b | 46e0c10c039e0191193 | Q4_K_M | 8.0B |
| Audit classifier A | qwen2.5:7b | 845dbda0ea48ed749ca | Q4_K_M | 7.6B |
| Audit classifier B | llama3.1:8b | 46e0c10c039e0191193 | Q4_K_M | 8.0B |
- Generation options: temperature=0.2 (labels/refine), 0.0 (audit classification); other options are Ollama defaults. Full prompt texts: `scripts/analysis_github_v2.py` (`label_pipeline`), `scripts/audit_kit.py` (`PROMPT`), `scripts/analysis_domains.py` (`PROMPT`).

## 4. Analysis parameters
- KMeans: k=2..30, n_init=10, random_state=100 (main); stability = 20 seeds (1..20) + 20 × 80% subsampling (RandomState 42); silhouette on a fixed 5,000-document subsample (RandomState 0), cosine. The composite k-selection table of the manuscript (Table 3; `results/R1_revision/A_k_selection_composite.xlsx`) is produced by `scripts/analysis_r1_revision.py` with 10 seeds and 10 subsamples per k.
- Baselines: LDA (gensim, passes=10, random_state=100), NMF (init=nndsvda, max_iter=400, random_state=100), TF-IDF+KMeans (same KMeans parameters), BERTopic 0.17.4 (default UMAP/HDBSCAN, precomputed bge-m3 embeddings; outliers reported separately).
- Coherence: gensim CoherenceModel c_v & c_npmi, processes=1, topics restricted to dictionary tokens (≥3 valid terms).
- Diversity: unique / (k×10) over each method's raw top-10 terms (not filtered by the dictionary); definition fixed after a metric audit.
- GLM: per-topic Binomial GLM, endog=(count, N−count), predictor=(year−2016); OR/yr=exp(β1), 95% CI=exp(β1±1.96·SE); BH-FDR across non-emergent topics; taxonomy: Emergent if <5% of topic documents were created before 2023; otherwise growing/declining at q<0.05, else Stable. The 16-series FDR family and the four additional specifications are in `scripts/r11_reanalysis.py` and `scripts/analysis_r1_revision.py`.
- PELT (ruptures 1.1.10): monthly total counts (120 points, log1p), sensitivity grid model∈{l2, rbf} × pen∈{0.5, 1, 2, 3, 5} × min_size∈{2, 3, 6} = 30 configurations (as in `results/PELT_monthly_sensitivity.xlsx` and the manuscript); quarterly per-topic shares (40 points, l2, pen=0.02, min_size=4). The penalty loop in `scripts/analysis_github_v2.py` was corrected in v1.2-peerj to include pen=5, so the script now reproduces all 30 rows of the released table (the v1.1-peerj script listed only four penalties).
- Sensitivity: stars≥{5, 10, 50} × archived {excluded, included}; GLM/taxonomy re-estimated.

## 5. Environment
- Windows 11 Pro, NVIDIA RTX 3090 24 GB; Python 3.11.9; scikit-learn 1.8.0, gensim 4.4.0, statsmodels 0.14.6, ruptures 1.1.10, bertopic 0.17.4; other packages (pandas, numpy, scipy, matplotlib, openpyxl, patsy) are listed in `requirements.txt` (versions not recorded, unpinned).

## 6. Code & artifacts
- Collection: `scripts/github_collect.py`, `scripts/github_collect_2025fix.py` (+ logs in `data/`).
- Analysis: `scripts/analysis_github_v2.py` → `results/` (all xlsx tables; figures are produced by the `scripts/visuals_*.py` scripts into `figures/`).
- Corpus audit: `scripts/audit_kit.py` → `audit/` (stratified sample of 404, dual-LLM provisional labels, human rating sheet, `compute_alpha.py`).
- Draft build: `md_to_docx.py` (manuscript-drafting utility; not included in this repository and not needed for any result).
