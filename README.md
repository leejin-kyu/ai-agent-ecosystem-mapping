# Mapping public AI-agent repositories on GitHub: clusters and creation-year composition (replication package)

## Description

This repository is the replication package for the manuscript:

> **Mapping public AI-agent repositories on GitHub: clusters and creation-year composition**
> Jinkyu Lee, Chang Soo Sung, Joo Yeon Park. Manuscript submitted to *PeerJ Computer Science* (2026).

Earlier drafts of the manuscript used the title *Mapping AI-Agent Repositories on GitHub: Clusters, Emergence, and Composition Trends (2016–2025)*.

The study analyzes 9,601 public GitHub repositories related to AI agents (stars ≥ 5, created 2016–2025). The repositories were collected with the GitHub Search API using a procedure that avoids the API's 1,000-result cap, embedded with BGE-M3, and clustered with K-means at two granularities (a stable coarse solution with k = 5 and an exploratory finer solution with k = 12). The clustering is compared with LDA, NMF, TF-IDF + K-means, and BERTopic. Creation-year composition is analyzed with binomial generalized linear models (GLMs) under five model specifications with Benjamini–Hochberg false-discovery-rate (BH-FDR) control across 16 series, an emergence taxonomy, and PELT change-point detection. Corpus relevance is audited by two local language models (n = 404) and three human annotators (n = 120). A keyword-based application-domain axis with 11 domains is analyzed in the same way.

All text in this repository (code comments, docstrings, printed messages, file names, spreadsheet sheet names and headers, and documentation) is in English. The human-annotation instruments were originally presented to the annotators in Korean; the copies in this repository contain an English translation of that text (see `DATA_CODEBOOK.md`).

## Dataset Information

| Item | Value |
|---|---|
| Source | Public GitHub repository metadata from the official GitHub Search REST API (`X-GitHub-Api-Version: 2022-11-28`) |
| Collection date | 8 August 2026 |
| Queries | 8 (union, deduplicated by `full_name`): `topic:ai-agent`, `topic:ai-agents`, `topic:llm-agent`, `topic:llm-agents`, `topic:autonomous-agents`, `topic:agentic-ai`, `"ai agent" in:name,description`, `"llm agent" in:name,description`; each with `stars:>=5` and a creation-date range from 2016 through 2025 |
| Raw corpus | `data/github_ai_agent_raw_v2.xlsx`: 9,947 unique repositories |
| Analyzed corpus | 9,601 repositories (346 removed because their combined description and topic-tag text was shorter than 10 characters) |
| Fields | `full_name`, `description`, `topics`, `stars`, `forks`, `language`, `created_at`, `pushed_at`, `license`, `archived`, `year` |
| Embeddings | `results/embeddings.npy` (9,601 × 1,024 float32, BGE-M3); row keys (`full_name`) in `results/emb_keys.npy` |
| Personal data | None beyond public repository owner names embedded in repository full names |

Folder overview:

| Path | Contents |
|---|---|
| `data/` | Raw collected corpus and collection logs (per-slice `total_count` and `incomplete_results`) |
| `results/` | Derived tables: cluster assignments, model selection, method comparison, cluster labels, GLM/taxonomy estimates (coarse, fine-grained, domain), PELT sensitivity, stability, sensitivity analyses, embedding matrix |
| `results/R1_revision/` | Revision analyses: k-selection composite, model-specification sensitivity, activity by creation year, audit precision by stratum, representative repositories, false-positive robustness |
| `results/R11/` | Cluster-size weighting, 16-series FDR family, misclassification and tipping-point analysis, stability of TF-IDF + K-means, reproduction check |
| `audit/` | Relevance-audit sample with both models' labels, human annotation sheets with all three annotators' judgments, answer key, codebook, adjudication sheets, scoring scripts |
| `figures/` | Figures (300 dpi); `figures/R1/` and `figures/R11/` hold the revised versions used in the manuscript |
| `scripts/` | Collection, analysis, figure, and manuscript-wording utilities |

Every data and result file (sheet names, columns, categorical values) is documented in `DATA_CODEBOOK.md`. Fifteen repository descriptions in the raw corpus are written in Korean by their GitHub owners; they are kept unchanged because the embeddings and clusters were computed from them, and English translations are given in `DATA_CODEBOOK.md`.

## Code Information

All scripts resolve paths relative to this repository (`data/`, `results/`, `audit/`, `figures/`); no path constants need editing. Some scripts also contain a fallback branch for the authors' original working-folder layout (for example `30_analysis_results/`); that branch is not used in this repository.

| Script | Purpose | Main inputs → outputs |
|---|---|---|
| `scripts/github_collect.py` | Initial collection: 8 queries × yearly slices 2016–2025, `stars:>=5` (requires an authenticated GitHub CLI `gh`) | GitHub API → `github_ai_agent_raw.xlsx`, `github_collect.log` |
| `scripts/github_collect_2025fix.py` | Re-collects the three truncated 2025 query slices by month, re-split by week when a month exceeds 1,000 results, and merges | `github_ai_agent_raw.xlsx` → `github_ai_agent_raw_v2.xlsx`, `github_collect_2025fix.log` |
| `scripts/analysis_github_v2.py` | Main pipeline: text construction and filtering, BGE-M3 embeddings, K-means k = 2–30 sweep, seed/bootstrap stability, 4 baselines, Gemma-3-12B labels + Self-Refine, binomial GLM + taxonomy, PELT, stars/archived sensitivity | `data/github_ai_agent_raw_v2.xlsx` → `results/*.xlsx`, `results/embeddings.npy`, `results/emb_keys.npy` |
| `scripts/analysis_domains.py` | Application-domain axis: keyword tagging (11 domains + General), GLM, dual-LLM validation on 300 repositories | raw data → `results/domain_*.xlsx` |
| `scripts/audit_kit.py` | Relevance audit: stratified sample, dual-LLM classification (Qwen2.5-7B, Llama-3.1-8B), human rating sheet | `results/document_cluster_assignments.xlsx` → `audit/human_eval_stratified_sample_400.xlsx`, `audit/llm_dual_classification_provisional_metrics.xlsx`, `audit/compute_alpha.py` |
| `scripts/analysis_r1_revision.py` | Stability-based model selection, model-specification sensitivity (spline, segmented, 2023–2025 window, quarterly), activity by creation year, audit precision by stratum, representative repositories | → `results/R1_revision/A–E*` |
| `scripts/analysis_r2_precision_robustness.py` | Robustness to false positives: precision-weighted GLM, conservative corpus (n = 8,256), Monte-Carlo removal (200 draws) | → `results/R1_revision/F_precision_robustness.xlsx` |
| `scripts/analysis_r8_strict_rater_B.py` | Same, weighted by the strictest human annotator's cluster-level precision | → `results/R1_revision/F3_precision_robustness_strict_raterB.xlsx` |
| `scripts/r11_reanalysis.py` | Cluster-size weighted relevance-positive rate and human estimates, BH-FDR across 16 series under every specification, misclassification scenarios and tipping points, TF-IDF + K-means stability | → `results/R11/R11_reanalysis.xlsx`, `results/R11/R11_reanalysis_log.txt`, `results/R11/_human120.pkl` |
| `scripts/repro_compare.py` | Compares regenerated outputs with the released files | → `R11_repro_check.txt` |
| `scripts/visuals_jss.py`, `visuals_jss_r1.py`, `visuals_jss_r5.py`, `visuals_r11.py` | Publication figures (successive revisions; `visuals_r11.py` reuses `visuals_jss_r5.py`) | → `figures/`, `figures/R1/`, `figures/R5/` (created on first run), `figures/R11/` |
| `audit/make_easy_survey.py`, `make_simplest_survey.py`, `make_friend_survey.py`, `make_label_eval_kit.py`, `make_adjudication_kit.py` | Generators of the annotation, label-rating, and adjudication sheets | → `audit/*.xlsx` |
| `audit/score_three_annotators.py` | Scores the three annotators (precision, Cohen's κ, Krippendorff's α, majority vote, agreement with the models) | → printed statistics, archived in `audit/human_eval_three_annotators_results_260910.txt` |
| `audit/score_easy_survey.py`, `score_simplest.py`, `score_label_eval.py`, `score_adjudication.py`, `compute_alpha.py` | Scoring of the individual sheets and of the adjudication kit | → printed statistics / `R11_adjudication_result.txt` |
| `scripts/term_*.py`, `scripts/apply_*.py`, `scripts/abstract_term_audit_r6.py` | Manuscript-wording utilities that compare terminology with 27 prior-work full texts (document-frequency rule ≥ 3); the full texts are not redistributed and these scripts are not needed to reproduce any result | — |

## Usage Instructions

1. Clone or download this repository (or the Zenodo archive) and open a terminal in its root folder.
2. Create a Python 3.11 environment and install the dependencies: `pip install -r requirements.txt`.
3. CPU-only reproduction of every table in the manuscript from the released files (about 15 minutes; uses `results/embeddings.npy` and `results/emb_keys.npy`, no GPU needed):

```bash
python audit/score_three_annotators.py               # human annotation statistics
python scripts/analysis_r1_revision.py               # model selection, specification sensitivity, activity, audit by stratum
python scripts/analysis_r2_precision_robustness.py   # precision-weighted and conservative-corpus scenarios
python scripts/analysis_r8_strict_rater_B.py         # strictest-annotator weights
python scripts/r11_reanalysis.py                     # weighting, 16-series FDR family, misclassification, TF-IDF stability
python scripts/visuals_r11.py                        # revised figures -> figures/R11/
```

4. Optional full pipeline from collection (requires an authenticated GitHub CLI `gh`, [Ollama](https://ollama.com) running on `localhost:11434` with the models listed under Requirements, and a GPU). The collection scripts write their output next to the script; copy `github_ai_agent_raw_v2.xlsx` to `data/` before continuing, or skip collection and use the released `data/github_ai_agent_raw_v2.xlsx`:

```bash
python scripts/github_collect.py
python scripts/github_collect_2025fix.py
python scripts/analysis_github_v2.py      # embeddings -> clustering -> baselines -> labels -> GLM -> PELT
python scripts/analysis_domains.py        # application-domain axis + dual-LLM validation
python scripts/audit_kit.py               # relevance audit sample + dual-LLM labels
python scripts/visuals_jss_r5.py all      # figures -> figures/R5/
```

5. Loading the data in Python:

```python
import numpy as np, pandas as pd
raw = pd.read_excel('data/github_ai_agent_raw_v2.xlsx')                      # 9,947 repositories
assign = pd.read_excel('results/document_cluster_assignments.xlsx')          # 9,601 analyzed repositories with cluster ids
emb = np.load('results/embeddings.npy')                                      # 9,601 x 1,024
keys = np.load('results/emb_keys.npy', allow_pickle=True)                    # full_name of each embedding row
```

6. To check a re-run against the released files: `python scripts/repro_compare.py <fresh_copy_root> <released_repo_root> <R11_reanalysis.xlsx> <run_log>`.

Step 3 was re-run on 2026-10-15 in a fresh copy of this repository: all regenerated tables matched the released files exactly, except one K-means stability median (BGE-M3, k = 5: 0.9717 vs 0.9725) that varies in the fourth decimal with multithreaded floating-point order; every value reported in the manuscript is unchanged (see `results/R11/R11_repro_check.txt`). That check was run before the English-language renaming of files, sheets, and columns in this version; only names and text changed, not numerical values or code logic.

## Requirements

- Python 3.11.9 with the packages in `requirements.txt`: scikit-learn 1.8.0, gensim 4.4.0, statsmodels 0.14.6, ruptures 1.1.10, BERTopic 0.17.4, plus pandas, numpy, scipy, matplotlib, openpyxl, and patsy (versions of these were not recorded and are left unpinned).
- Steps that use language models or the embedding model: [Ollama](https://ollama.com) with the following local models (digest prefixes):

| Role | Ollama tag | Digest (prefix) | Quantization | Parameters |
|---|---|---|---|---|
| Embedding | `bge-m3:latest` | 7907646426070047a77 | F16 | 567M |
| Label generation | `gemma3:12b` | f4031aab637d1ffa37b | Q4_K_M | 12.2B |
| Label specificity judge; audit classifier B | `llama3.1:8b` | 46e0c10c039e0191193 | Q4_K_M | 8.0B |
| Audit classifier A | `qwen2.5:7b` | 845dbda0ea48ed749ca | Q4_K_M | 7.6B |

- Hardware and OS used by the authors: Windows 11 Pro (build 10.0.26300), 13th Gen Intel Core i5-13600K, 32 GB RAM, one NVIDIA GeForce RTX 3090 (24 GB). Local models were served with Ollama 0.6.8 (installed version at the time of release). All steps after the embedding and LLM steps run on a CPU.
- Collection only: GitHub CLI (`gh`) authenticated (the scripts read the token with `gh auth token`).

## Methodology

1. **Collection** (`github_collect.py`, `github_collect_2025fix.py`): union of 8 queries with `stars:>=5`, partitioned by creation year and, for slices that exceeded 1,000 results, by month and week, so that every final slice returned fewer than 1,000 results; forks are excluded by the API default; deduplication by `full_name` (9,947 unique repositories).
2. **Preprocessing** (`analysis_github_v2.py`): repositories created 2016–2025 are kept; the document text is the repository name (owner removed, `-`/`_` replaced by spaces) + description + topic tags; repositories whose description plus tags is shorter than 10 characters are removed (9,601 remain). For count-based models, text is lowercased and tokenized with `[a-z][a-z0-9\-]{2,}`, query-derived words (ai, agent(s), llm(s)) and generic function words are removed, and the gensim dictionary keeps tokens that occur in at least 3 documents and in at most 10% of documents.
3. **Embedding and clustering**: BGE-M3 embeddings (1,024 dimensions, L2-normalized) and K-means (n_init = 10, random_state = 100) for k = 2–30. k is selected by a stability rule (median seed ARI and subsampling ARI both > 0.95, then highest cosine silhouette), giving k = 5; k = 12 is reported as an exploratory finer view.
4. **Labeling**: representative TF-IDF terms (query-derived terms removed) and the 8 repositories nearest each centroid are given to Gemma-3-12B; one Self-Refine round; label redundancy and Llama-3.1-8B specificity ratings are recorded.
5. **Baselines**: LDA, NMF, TF-IDF + K-means (k = 2–30) and BERTopic (native k, on the BGE-M3 embeddings), compared with c_v, NPMI coherence, and topic diversity.
6. **Relevance audit**: stratified sample of 404 repositories classified by Qwen2.5-7B and Llama-3.1-8B (temperature 0) into 8 categories; 120 of them judged by three human annotators blind to the model labels; codebook and adjudication sheets for the contested boundary.
7. **Trends**: per-series binomial GLM of yearly share (OR per year) under five specifications (log-linear, natural cubic spline, segmented at 2023, 2023–2025 window, quarterly), BH-FDR across 16 series (5 clusters + 11 domains), emergence taxonomy (Emergent if < 5% of a series predates 2023); PELT change points on the monthly log(1+x) series over a 30-configuration grid and on quarterly cluster shares.
8. **Robustness**: stars/archived subsets, precision weighting, conservative corpus, random and year-concentrated misclassification, tipping-point analysis.
9. **Application domains** (`analysis_domains.py`): case-insensitive keyword patterns over full name, description, and tags assign 11 domains (multi-label; General if none), validated on 300 repositories by the two LLMs.

Full parameter documentation (seeds, prompts, stopword lists, PELT grid) is in `REPRODUCIBILITY.md`.

## Citations

If you use this dataset or code, please cite the manuscript and the archived package:

- Lee, J., Sung, C. S., & Park, J. Y. (2026). *Mapping public AI-agent repositories on GitHub: clusters and creation-year composition*. Manuscript submitted to PeerJ Computer Science.
- Lee, J., Sung, C. S., & Park, J. Y. (2026). *Replication package: Mapping public AI-agent repositories on GitHub: clusters and creation-year composition* [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.23555408 (all versions; resolves to the latest). This English-language version is release v1.3-peerj. Releases v1.1-peerj and v1.2-peerj contain the earlier Korean-named version with identical numerical content (v1.2-peerj was tagged before the English-language commit and duplicates v1.1-peerj).

Methods and tools used:

- Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). M3-Embedding: Multi-linguality, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. *Findings of ACL 2024*, 2318–2335. https://doi.org/10.18653/v1/2024.findings-acl.137
- Killick, R., Fearnhead, P., & Eckley, I. A. (2012). Optimal detection of changepoints with a linear computational cost. *Journal of the American Statistical Association*, 107(500), 1590–1598.
- Madaan, A., et al. (2023). Self-Refine: Iterative refinement with self-feedback. *NeurIPS 2023*.
- Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. arXiv:2203.05794.
- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. *Journal of Machine Learning Research*, 3, 993–1022.
- Röder, M., Both, A., & Hinneburg, A. (2015). Exploring the space of topic coherence measures. *WSDM 2015*, 399–408.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.

## License & Contribution Guidelines

- **License**: MIT License, Copyright (c) 2026 Jinkyu Lee, Chang Soo Sung, Joo Yeon Park (see `LICENSE`). The collected metadata remains subject to the GitHub Terms of Service.
- **Contributions**: this repository is the frozen replication package of a manuscript. Please report problems (errors, reproduction failures, unclear documentation) through GitHub Issues. Pull requests that fix documentation or portability are welcome; changes to released data or results will not be merged, so that the package continues to match the published analysis. Corrections, if any, are released as new tagged versions and archived on Zenodo.
- **Contact**: Jinkyu Lee (see the manuscript for contact details).
