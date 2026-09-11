# Replication Package — Mapping AI-Agent Repositories on GitHub: Clusters, Emergence, and Composition Trends (2016–2025)

Replication package for the manuscript:

> **Mapping AI-Agent Repositories on GitHub: Clusters, Emergence, and Composition Trends (2016–2025)**
> Jinkyu Lee, Chang Soo Sung, Joo Yeon Park. Submitted to *IEEE Access* (2026).

The study analyzes 9,601 public GitHub repositories related to AI agents (stars ≥ 5, created 2016–2025), collected with a truncation-free procedure, clustered with BGE-M3 embeddings + K-means at two granularities, compared against LDA/NMF/TF-IDF+K-means/BERTopic, and analyzed with binomial GLM trend models (BH-FDR), an emergence taxonomy, and PELT change-point detection with a 30-configuration sensitivity grid.

## Contents

| Path | Description |
|---|---|
| `REPRODUCIBILITY.md` | Full parameter documentation: queries, slicing rules, model digests/quantization, prompts, seeds, PELT grid, library versions |
| `scripts/github_collect.py` | Initial collection (8-query union, yearly slices, GitHub Search API) |
| `scripts/github_collect_2025fix.py` | De-truncation re-collection (recursive monthly/weekly slicing) |
| `scripts/analysis_github_v2.py` | Main pipeline: embeddings, k=2–30 sweep, stability, 4 baselines, LLM labeling + Self-Refine, GLM + taxonomy, PELT, sensitivity |
| `scripts/analysis_domains.py` | Application-domain axis: lexicon tagging, GLM, dual-LLM validation |
| `scripts/audit_kit.py` | Corpus relevance audit: stratified sample, dual-LLM classification, human rating sheets |
| `scripts/visuals_jss.py` | Publication figures (Figures 1–6) |
| `data/github_ai_agent_raw_v2.xlsx` | Raw collected corpus (9,947 unique repositories; public GitHub metadata only) |
| `data/*.log` | Collection logs incl. per-slice `total_count` and `incomplete_results` |
| `results/` | Derived tables: method comparison, GLM/taxonomy estimates (macro/meso/domain), PELT sensitivity, stability, topic labels, sensitivity analyses |
| `audit/` | Relevance-audit sample with dual-LLM labels, human rating sheet, Krippendorff's α script |
| `figures/` | Figures 1–6 (300 dpi) |

Note: the 38 MB embedding cache (`embeddings.npy`) is excluded; it is regenerated deterministically by `analysis_github_v2.py` from the raw data via bge-m3.

## Revision materials (2026-09-08 to 2026-09-10)

| Path | Description |
|---|---|
| `scripts/analysis_r1_revision.py` | Stability-based model selection (silhouette + seed/bootstrap ARI for k=2–30), model-specification sensitivity of trends (spline, segmented, 2023–2025 window, quarterly), activity by creation year, audit precision by stratum, representative repositories → `results/R1_revision/A–E*.xlsx` |
| `scripts/analysis_r2_precision_robustness.py` | Robustness to false positives: precision-weighted GLM, conservative corpus (n=8,256), Monte-Carlo worst case (200 draws) → `results/R1_revision/F_precision_robustness.xlsx` |
| `scripts/analysis_r8_strict_rater_B.py` | Same, weighted by the strictest human annotator's cluster-level precision → `results/R1_revision/F3_precision_robustness_strict_raterB.xlsx` |
| `audit/설문지_*_작성.xlsx`, `audit/score_three_annotators.py`, `audit/인간평가_3인_결과_260910.txt` | Blind human annotation by three annotators (A = author; B, C = external volunteers, anonymized) of a stratified 120-repository subsample and of the 17 cluster labels; scoring (precision, Cohen's κ, Krippendorff's α, majority vote) |
| `audit/make_*_survey.py`, `audit/설문지_한글번역.json` | Annotation kit generators (Korean-language sheets) |
| `scripts/term_*.py`, `scripts/apply_term*.py` | Terminology audit against 27 prior-work full texts (document-frequency rule ≥3) used to standardize the manuscript vocabulary |
| `scripts/visuals_jss_r1.py`, `scripts/visuals_jss_r5.py`, `figures/R1/`, `figures/R5/` | Regenerated Figures 1–6 with cluster wording |

Terminology note: the manuscript calls the K-means units *repository clusters* (earlier drafts used *segments* or *topics*); result file names retain the original `토픽`/`segment` wording.

## Environment

- Python 3.11.9; scikit-learn 1.8.0, gensim 4.4.0, statsmodels 0.14.6, ruptures 1.1.10, bertopic 0.17.4, pandas, numpy
- [Ollama](https://ollama.com) with models: `bge-m3` (F16), `gemma3:12b` (Q4_K_M), `llama3.1:8b` (Q4_K_M), `qwen2.5:7b` (Q4_K_M) — exact digests in `REPRODUCIBILITY.md`
- GitHub CLI (`gh`) authenticated, for collection scripts

## Reproducing the analysis

```bash
# 1. Collect (or skip and use data/github_ai_agent_raw_v2.xlsx)
python scripts/github_collect.py
python scripts/github_collect_2025fix.py

# 2. Main pipeline (embeddings -> clustering -> baselines -> GLM -> PELT -> sensitivity)
python scripts/analysis_github_v2.py

# 3. Application-domain axis
python scripts/analysis_domains.py

# 4. Corpus relevance audit
python scripts/audit_kit.py

# 5. Figures
python scripts/visuals_jss.py all
```

Scripts expect the directory layout used in the paper (`데이터/`, `결과물_github_v2/`); adjust the path constants at the top of each script if you use this repository's flat layout.

## Data statement

The dataset contains only public GitHub repository metadata (name, description, topic tags, star/fork counts, timestamps, license identifiers) collected via the official GitHub Search API on 2026-08-08. No personal data beyond public repository owner names embedded in repository full names is included.

## License

MIT (see `LICENSE`). The collected metadata remains subject to GitHub's Terms of Service.
