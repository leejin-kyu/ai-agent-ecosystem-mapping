# Replication Package — Mapping the Open-Source AI-Agent Ecosystem on GitHub (2016–2025)

Replication package for the manuscript:

> **Mapping the Open-Source AI-Agent Ecosystem on GitHub: Topic Structure, Emergence, and Evolution (2016–2025)**
> Jinkyu Lee, Chang Soo Sung, Joo Yeon Park. Submitted to the *Journal of Systems and Software*.

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
