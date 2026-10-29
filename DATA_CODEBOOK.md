# Data Codebook (English)

Replication package: *Mapping public AI-agent repositories on GitHub: clusters and creation-year composition* (Lee, Sung, Park).

This codebook documents every data and result file in the repository (`.xlsx`, `.npy`, `.pkl`, `.log`, `.txt`, `.json`): its purpose, the script that produces it, the scripts that read it, and the meaning of every sheet and column. In the English-language version of the repository, all file names, sheet names, column headers, and categorical values that were in Korean have been translated; the Korean original is given in the column "Korean original" for traceability with earlier releases (v1.1-peerj and before).

Conventions used throughout:

- `full_name`: GitHub repository identifier `owner/name`.
- `cluster`: coarse K-means cluster id (k = 5), 0–4, also written T0–T4. `cluster_meso`: exploratory fine-grained cluster id (k = 12), 0–11, also written M0–M11. "macro" = coarse (k = 5), "meso" = fine-grained (k = 12).
- Coarse cluster names used in the manuscript: T0 Agent frameworks and development tools; T1 LangChain/LangGraph/OpenAI-centered (LangChain-based) frameworks; T2 Orchestration and automation; T3 MCP servers and tools; T4 Code-generation agents.
- `OR`, `OR_per_year`: odds ratio per year from a binomial GLM of a series' yearly share; `lo`/`hi`, `CI_lo`/`CI_hi`: 95% confidence limits; `p`: p-value; `q`, `q_BH`: Benjamini–Hochberg adjusted p-value.
- `emergent`: True if fewer than 5% of the series' repositories were created before 2023. `taxonomy`/`tax`: Emergent, Established-growing, Established-declining, Stable (domains: Emergent, Growing, Declining, Stable).
- Audit categories (`llm_qwen`, `llm_llama` in the audit files): Agent-framework, Agent-application, MCP-server, Tutorial-example, Awesome-resource, Paper-code, Non-agent, Other. "Agent" = one of the first three.
- Application domains (11, multi-label): Finance/Trading, Healthcare/Medical, Education, Legal, E-commerce/Sales, SoftwareDev/Coding, Gaming, Robotics/Embodied, Research/Science, Web/Browser automation, Data/Analytics; `General` = none of these.
- Boolean columns are stored as TRUE/FALSE.

## 1. File renames (Korean original → English)

| New path | Korean original path | English meaning of the original |
|---|---|---|
| `audit/cluster_label_human_eval_blind_sheet.xlsx` | `audit/라벨_군집_인간평가_블라인드시트.xlsx` | label/cluster human-evaluation blind sheet |
| `audit/survey_easy_version.xlsx` | `audit/설문지_쉬운버전.xlsx` | questionnaire, easy version |
| `audit/survey_answer_key_do_not_open.xlsx` | `audit/설문지_정답키(열지마세요).xlsx` | questionnaire answer key (do not open) |
| `audit/survey_simplest_completed.xlsx` | `audit/설문지_초간단_작성.xlsx` | questionnaire, simplest version, completed (Annotator A) |
| `audit/survey_friend_version_rater2_completed.xlsx` | `audit/설문지_친구용_2차평가자_작성.xlsx` | questionnaire, version for external volunteer, 2nd rater, completed (Annotator B) |
| `audit/survey_friend_version_rater3_completed.xlsx` | `audit/설문지_친구용_3차평가자_작성.xlsx` | same, 3rd rater, completed (Annotator C) |
| `audit/survey_annotator_display_text.json` | `audit/설문지_한글번역.json` | questionnaire Korean translation (now an English rendering, see §4.6) |
| `audit/human_eval_three_annotators_results_260910.txt` | `audit/인간평가_3인_결과_260910.txt` | human evaluation, three-annotator results, 2026-09-10 |
| `audit/human_eval_results_260910.txt` | `audit/인간평가_결과_260910.txt` | human evaluation results (single annotator), 2026-09-10 |
| `audit/human_eval_stratified_sample_400.xlsx` | `audit/인간평가_층화표본400.xlsx` | human evaluation, stratified sample of 400 |
| `audit/llm_dual_classification_provisional_metrics.xlsx` | `audit/LLM이중분류_잠정지표.xlsx` | LLM dual classification, provisional metrics |
| `results/cluster_k_selection_silhouette_2to30.xlsx` | `results/군집_k선정_실루엣_2to30.xlsx` | cluster k selection, silhouette, k = 2–30 |
| `results/domain_validation_sample.xlsx` | `results/도메인_검증표본.xlsx` | domain validation sample |
| `results/domain_tagging.xlsx` | `results/도메인_태깅.xlsx` | domain tagging |
| `results/domain_tagging_validation.xlsx` | `results/도메인_태깅검증.xlsx` | domain tagging validation |
| `results/domain_GLM_taxonomy.xlsx` | `results/도메인_GLM_taxonomy.xlsx` | domain GLM taxonomy |
| `results/document_cluster_assignments.xlsx` | `results/문서_군집할당.xlsx` | document (repository) cluster assignments |
| `results/sensitivity_stars_archived.xlsx` | `results/민감도_stars_archived.xlsx` | sensitivity to stars/archived |
| `results/main_comparison_metrics_v2.xlsx` | `results/본비교_지표_v2.xlsx` | main method comparison, metrics |
| `results/main_comparison_k_sweep.xlsx` | `results/본비교_k스윕.xlsx` | main method comparison, k sweep |
| `results/stability_seed_bootstrap.xlsx` | `results/안정성_seed_bootstrap.xlsx` | stability, seeds and bootstrap |
| `results/topic_share_by_year.xlsx` | `results/연도별_토픽비중.xlsx` | topic (cluster) share by year |
| `results/topic_macro_k5.xlsx` | `results/토픽_macro_k5.xlsx` | topics (clusters), coarse k = 5 |
| `results/topic_meso_k12.xlsx` | `results/토픽_meso_k12.xlsx` | topics (clusters), fine-grained k = 12 |
| `results/PELT_monthly_sensitivity.xlsx` | `results/PELT_월별_민감도.xlsx` | PELT monthly sensitivity |

"Topic" in file names is the wording of earlier drafts; the manuscript calls these units *repository clusters*.

## 2. Raw data (`data/`)

### `data/github_ai_agent_raw_v2.xlsx`
Raw collected corpus, 9,947 unique repositories (one sheet, `Sheet1`). Produced by `scripts/github_collect.py` + `scripts/github_collect_2025fix.py`; read by `analysis_github_v2.py`, `analysis_domains.py`, `audit_kit.py`, `analysis_r1_revision.py`, `analysis_r2_precision_robustness.py`, `analysis_r8_strict_rater_B.py`, `r11_reanalysis.py`, `visuals_*.py`, `audit/make_adjudication_kit.py`. File unchanged from the original release.

| Column | Meaning |
|---|---|
| `full_name` | Repository `owner/name` |
| `description` | Repository description at collection time (empty if none) |
| `topics` | Topic tags, separated by `;` |
| `stars` | Stargazer count at collection time |
| `forks` | Fork count at collection time |
| `language` | Primary language reported by GitHub |
| `created_at` | Creation timestamp (ISO 8601, UTC) |
| `pushed_at` | Last push timestamp (ISO 8601, UTC) |
| `license` | SPDX license identifier (empty if none; `NOASSERTION` if unrecognized) |
| `archived` | Whether the repository is archived |
| `year` | Creation year (first four characters of `created_at`) |

Fifteen descriptions are written in Korean by the repository owners. They are original GitHub metadata and were used as such to compute the embeddings and clusters, so they are not modified. English translations:

| full_name | Korean original description | English translation |
|---|---|---|
| caretive-ai/project-multi-post-agent | 이 프로젝트는 AI 기반의 다국어 블로그 포스팅 자동화 에이전트 개발을 목표로 하는 교육용 프로젝트입니다. Caret AI 어시스턴트와 함께 "바이브코딩" 방식으로 진행되며, AI 에이전트 개발 및 LangGraph 활용에 대한 실습 경험을 제공합니다. | This is an educational project aimed at developing an AI-based agent that automates multilingual blog posting. It proceeds in a "vibe coding" manner with the Caret AI assistant and provides hands-on experience with AI agent development and LangGraph. |
| unohee/kis-agent | 한국투자증권 OpenAPI Python 래퍼 — CLI · Python SDK · LLM Agent · 실시간 WebSocket. 문서: unohee.github.io/kis-agent | Python wrapper for the Korea Investment & Securities OpenAPI — CLI · Python SDK · LLM Agent · real-time WebSocket. Docs: unohee.github.io/kis-agent |
| sysnet4admin/_Book_Claude-Code | < 한 걸음 앞선 개발자가 지금 꼭 알아야 할 클로드 코드 > | < Claude Code: what a developer one step ahead must know now > (book title) |
| popup-studio-ai/AI-driven-work | POPUP STUDIO의 AI Agent를 활용한 업무 프로세스 개선 프로젝트입니다. | A project to improve work processes using POPUP STUDIO's AI Agent. |
| DINKIssTyle/DINKIssTyle-AI-BBS | 로컬 LLM을 이용한 로컬 AI 커뮤니티 웹보드 서버입니다. | A local AI community web-board server using a local LLM. |
| HyunjunJeon/Deepagent-research-context-engineering | DeepAgent 기반 Research(연구) Multi Agent System 구축 - Context Engineering | Building a DeepAgent-based research multi-agent system - Context Engineering |
| jasonkang14/inflearn-langgraph-agent | 인프런의 "LangGraph를 활용한 AI Agent 개발" 강의 소스코드입니다 | Source code of Inflearn's course "AI Agent Development with LangGraph" |
| dabidstudio/python-ai-agents | 파이썬만으로 AI 에이전트 구현해보기 | Implementing AI agents with Python only |
| Pseudo-Lab/Proact0 | “Proact0”는 기존 AI Agent 개념의 발전을 제고하기 위해 설립된 비영리 오픈소스 연합 커뮤니티, OSPO(Open Source Program Office) 단체입니다. | "Proact0" is a non-profit open-source alliance community and OSPO (Open Source Program Office) organization founded to advance the existing AI agent concept. |
| ChangJu-Ahn/Microsoft-AI-Agent | Microsoft AI Agent 실습입니다. | Microsoft AI Agent hands-on practice. |
| gongwon-nayeon/fastcampus-aiagent | 패스트캠퍼스 AI Agent 강의 실습코드 | Practice code for the FastCampus AI Agent course |
| Choonholic/jpub_ai_agent | 《7가지 프로젝트로 배우는 LLM AI 에이전트 개발》 추가 지원 저장소 | Supplementary repository for the book "LLM AI Agent Development Learned through 7 Projects" |
| 2innnnn0/fastcampus-n8n-data-analysis-agent | [패스트캠퍼스 강의] n8n x 데이터 분석: 원클릭으로 끝내는 데이터 분석 자동화 (n8n 데이터분석 AI Agent) | [FastCampus course] n8n x data analysis: one-click data-analysis automation (n8n data-analysis AI Agent) |
| ai-agent-kr/Modern-AI-Agents | 도서 Building AI Agents with LLMs, RAG, and Knowledge Graphs, First Edition의 한글판의 깃허브 레포지토리입니다. | GitHub repository of the Korean edition of the book Building AI Agents with LLMs, RAG, and Knowledge Graphs, First Edition. |
| ai-agent-kr/agent-tutorial | 《AI 에이전트 개발 완벽 입문》 예제 코드 | Example code for the book "A Complete Introduction to AI Agent Development" |

### `data/github_collect.log`
Plain-text log of `scripts/github_collect.py` (English). One line per query × year slice: `<query> stars:>=5 created:<from>..<to> -> total <total_count>`, warnings when a slice exceeded 1,000 results (`WARN: >1000, truncated to top-star 1000`), cumulative unique counts per query, and the final count by year.

### `data/github_collect_2025fix.log`
Plain-text log of `scripts/github_collect_2025fix.py` (English). One line per monthly or weekly 2025 slice of the three truncated queries: `<query> stars:>=5 created:<from>..<to> -> <total_count> (incomplete=<incomplete_results>)`, followed by the merge summary (`old 6373 + newly-fetched 6410 -> merged unique 9947`) and the count by year.

## 3. Results (`results/`)

All files in this section are byte-identical to the original release apart from the file name (cell contents were already in English).

### `results/embeddings.npy`, `results/emb_keys.npy`
NumPy arrays written by `scripts/analysis_github_v2.py` (section 2) and read by `analysis_github_v2.py` (cache), `analysis_r1_revision.py`, `r11_reanalysis.py`. `embeddings.npy`: float32 matrix 9,601 × 1,024, BGE-M3 embeddings as returned by Ollama (the scripts L2-normalize them before K-means) of the document text name + description + tags. `emb_keys.npy`: object array (load with `allow_pickle=True`) of the 9,601 `full_name` values in row order.

### `results/document_cluster_assignments.xlsx`
The 9,601 analyzed repositories with cluster assignments. Produced by `analysis_github_v2.py` (section 10); read by `audit_kit.py`, `analysis_r1_revision.py`, `analysis_r2_precision_robustness.py`, `analysis_r8_strict_rater_B.py`, `r11_reanalysis.py`, `visuals_*.py`.
Columns: `full_name`, `stars`, `language`, `license`, `archived`, `year` (as in the raw data); `cluster` (coarse id 0–4); `cluster_meso` (fine-grained id 0–11).

### `results/cluster_k_selection_silhouette_2to30.xlsx`
K-means sweep on BGE-M3 embeddings (`analysis_github_v2.py`, section 4; read by `visuals_jss*.py`). Columns: `k` (2–30); `silhouette` (cosine silhouette on a fixed 5,000-repository subsample).

### `results/stability_seed_bootstrap.xlsx`
Stability of the k = 5 solution (`analysis_github_v2.py`). Rows: `20-seed ARI` (ARI between the reference partition and partitions from seeds 1–20), `bootstrap80 ARI` (ARI on 20 random 80% subsamples). Columns: `analysis`, `median`, `IQR_lo`, `IQR_hi` (25th/75th percentiles), `min`, `max`.

### `results/main_comparison_k_sweep.xlsx`
c_v coherence by method and k (`analysis_github_v2.py`, section 5; read by `visuals_jss*.py`, `analysis_r1_revision.py`). Columns: `method` (`BGE-M3+KMeans (proposed)`, `TF-IDF+KMeans`, `NMF (TF-IDF)`, `LDA (gensim)`); `k`; `c_v`.

### `results/main_comparison_metrics_v2.xlsx`
Method comparison at each method's c_v-optimal k, plus the fixed coarse/fine BGE-M3 solutions and BERTopic at its native k (`analysis_github_v2.py`). Columns: `method`; `best_k`; `c_v`; `c_npmi` (NPMI coherence); `diversity` (unique terms among all top-10 terms / (10k)).

### `results/topic_macro_k5.xlsx`, `results/topic_meso_k12.xlsx`
Cluster descriptions and LLM labels (`analysis_github_v2.py`, section 6; read by `audit/make_*` scripts). Columns: `cluster` (id); `n_docs` (repositories in cluster); `top_terms` (12 top TF-IDF terms, query-derived terms removed); `rep_repos` (5 repositories nearest the centroid, `;`-separated); `label_initial` (Gemma-3-12B label); `label_refined` (label after one Self-Refine round); `spec_initial`, `spec_refined` (Llama-3.1-8B specificity rating 1–5 of each label).

### `results/SelfRefine_macro.xlsx`, `results/SelfRefine_meso.xlsx`
Effect of Self-Refine (`analysis_github_v2.py`). Columns: `granularity` (macro/meso); `dup_init`, `dup_refined` (mean pairwise cosine similarity between label embeddings, before/after); `spec_init`, `spec_refined` (mean specificity rating, before/after).

### `results/GLM_taxonomy_macro.xlsx`, `results/GLM_taxonomy_meso.xlsx`
Full-period binomial GLM per cluster (`analysis_github_v2.py`, section 7; read by `analysis_r2_precision_robustness.py`, `analysis_r8_strict_rater_B.py`, `visuals_*.py`). Columns: `cluster`; `label` (refined label); `n`; `pre2023_share` (share of the cluster created before 2023); `OR_per_year`, `CI_lo`, `CI_hi`, `p`; `emergent`; `q_BH` (BH over non-emergent clusters; empty for emergent clusters); `taxonomy`.

### `results/topic_share_by_year.xlsx`
Share of each coarse cluster among repositories created in each year (`analysis_github_v2.py`; read by `visuals_jss*.py`). First column `year` (2016–2025); columns `0`–`4` = cluster ids; rows sum to 1.

### `results/PELT_monthly_sensitivity.xlsx`
PELT change points (`analysis_github_v2.py`, section 8; read by `visuals_jss*.py`). Columns: `series` (`monthly_total(log1p)` = monthly creation counts, log(1+x); `quarterly_share_T0`–`T4` = quarterly share of a coarse cluster); `model` (cost function `l2` or `rbf`); `pen` (penalty); `min_size` (minimum segment length); `changepoints` (list of change-point months `YYYY-MM` or quarters `YYYY-Qn`). The monthly series has 30 configurations (model × pen ∈ {0.5, 1, 2, 3, 5} × min_size ∈ {2, 3, 6}); see the note on the penalty grid in `REPRODUCIBILITY.md`.

### `results/sensitivity_stars_archived.xlsx`
GLM/taxonomy of the coarse clusters re-estimated on subsets (`analysis_github_v2.py`, section 9). Columns: `stars>=` (minimum stars: 5, 10, 50); `incl_archived` (archived repositories included); `cluster`; `label`; `n`; `OR`; `CI` (text `[lo,hi]`); `q` (BH q); `tax` (taxonomy).

### `results/domain_tagging.xlsx`
Keyword-based domain tags for all 9,947 repositories created 2016–2025 (`analysis_domains.py`; read by `analysis_r1_revision.py`, `analysis_r2_precision_robustness.py`, `analysis_r8_strict_rater_B.py`, `r11_reanalysis.py`, `visuals_*.py`, which restrict it to the 9,601 analyzed repositories). Columns: `full_name`; `year`; one boolean column per domain (11 domains); `General` (no domain matched).

### `results/domain_GLM_taxonomy.xlsx`
Full-period binomial GLM per domain (`analysis_domains.py`; read by `visuals_jss*.py`). Columns: `domain`; `n`; `pre2023_share`; `OR_per_year`; `CI_lo`; `CI_hi`; `p`; `emergent`; `q_BH` (BH over non-emergent domains); `taxonomy` (Emergent, Growing, Declining, Stable).

### `results/domain_validation_sample.xlsx`
Stratified validation sample of 300 repositories (`analysis_domains.py`). Columns: `full_name`; `description`; `year`; `llm_qwen`, `llm_llama` (single domain assigned by Qwen2.5-7B / Llama-3.1-8B, one of the 11 domains or `General`); one boolean keyword-tag column per domain; `General`.

### `results/domain_tagging_validation.xlsx`
Summary of the domain validation (`analysis_domains.py`). Columns: `n` (300); `model_agreement` (share where both models chose the same domain); `lexicon_consistent_vs_consensus` (share of model-consensus items where the keyword tags contain the consensus domain); `lexicon_vs_qwen`, `lexicon_vs_llama` (same, against each model).

### `results/R1_revision/` (produced by `scripts/analysis_r1_revision.py` unless noted)

| File / sheet | Columns and meaning |
|---|---|
| `A_k_selection_composite.xlsx` | `k`; `silhouette`; `calinski_harabasz`; `davies_bouldin`; `seed_ARI_median`, `seed_ARI_min` (ARI vs the reference partition over 10 seeds); `boot_ARI_median`, `boot_ARI_min` (ARI over 10 random 80% subsamples); `size_balance`; `smallest_share` (share of the smallest cluster); `c_v` |
| `B_glm_functional_form_sensitivity.xlsx` | One row per series; `level` (macro, meso, domain); `cluster` (series name); `loglin_OR`, `loglin_lo`, `loglin_hi`, `loglin_p` (log-linear full period); `spline_avg_OR_2023_25`, `spline_avg_OR_full` (average annual OR from a natural cubic spline, df = 3); `spline_LR_p_vs_linear` (likelihood-ratio test vs linear); `spline_monotone_2023_25`; `seg_pre2023_OR`, `seg_post2023_OR`, `seg_post_lo`, `seg_post_hi` (segmented model with a knot at 2023); `win2325_OR`, `win2325_lo`, `win2325_hi`, `win2325_p` (2023–2025 window); `direction_consistent`; `q_loglin_OR`, `q_loglin_lo`, `q_loglin_hi` (quarterly-resolution log-linear model); `q_spline_avg_OR`, `q_spline_share_first`, `q_spline_share_last` (quarterly spline); `direction_consistent_incl_quarterly` |
| `C_cohort_activity_survivorship.xlsx` | By creation `year`: `n`; `archived_pct`; `active_12m_pct`, `active_24m_pct` (pushed within 12/24 months before 2026-08-08); `median_stars`; `median_forks`; `median_days_since_push` |
| `C_cluster_activity.xlsx` | By coarse `cluster`: `n`; `archived_pct`; `active_12m_pct`; `median_stars`; `label` |
| `C_glm_active24m_sensitivity.xlsx` | `cluster` (series name); `n_active24m` (repositories active in the last 24 months); `OR_active24m`, `lo`, `hi` (GLM on active repositories only) |
| `D_audit_precision_by_stratum.xlsx`, sheets `overall`, `by_cluster`, `by_period` | `stratum` / `cluster` / `period`; `n`; `precision_both` (share both models assign an agent category = relevance-positive rate); `wilson_lo`, `wilson_hi`; `precision_either` (at least one model); `model_agreement`; `tutorial_or_awesome_either`; `nonagent_either`; `label` (by_cluster) |
| `D_audit_precision_by_stratum.xlsx`, sheet `category_dist` | First column = audit category; `qwen`, `llama` = share of the 404 audit repositories assigned to it by each model |
| `D_llm_kappa.json` | `kappa8`: Cohen's κ between the two models over 8 categories; `kappa_bin`: κ for agent vs non-agent |
| `E_representative_repos.xlsx` | `cluster` (T0–T4, M0–M11); `label`; `n`; `nearest_centroid` (repositories nearest the centroid, ` ; `-separated); `most_starred` |
| `F_precision_robustness.xlsx` (`analysis_r2_precision_robustness.py`) | `series`; `full_OR`/`_lo`/`_hi` (full period); `win_OR`/`_lo`/`_hi` (2023–2025); `pw_*` (precision-weighted GLM, weight = cluster relevance-positive rate); `cons_n`, `cons_*` (conservative corpus); `mc_same_sign_full`, `mc_same_sign_win` (share of 200 Monte-Carlo removals keeping the same trend direction) |
| `F3_precision_robustness_strict_raterB.xlsx` (`analysis_r8_strict_rater_B.py`) | Same columns, with weights and removal rates from the strictest human annotator (B) |

### `results/R11/` (produced by `scripts/r11_reanalysis.py`)

`R11_reanalysis.xlsx`:

| Sheet | Columns and meaning |
|---|---|
| `P1_RPR` | `stratum`; `n`; `sample_share`; `pop_share` (cluster share of the corpus); `RPR_both` (relevance-positive rate, both models agent), `lo`, `hi`; `RPR_either`. Last rows: unweighted sample rate and cluster-size weighted estimate |
| `P3_human_weighted` | `rater` (A, B, C, Majority, Unanimous, Any, LLM); `sample_rate`, `sample_wilson_lo/hi`; `weighted` (cluster-size weighted estimate), `weighted_se`, `weighted_normal_lo/hi`, `weighted_boot_lo/hi` (10,000 stratified bootstrap resamples); `p_T0`–`p_T4` (rate per cluster) |
| `P3_agreement` | `alpha_binary_ABC`, `alpha_binary_BC` (Krippendorff's α); `kappa_A-B`, `kappa_A-C`, `kappa_B-C` (Cohen's κ, binary); `non_unanimous` (items without a unanimous judgment) |
| `P4_misclassification` | `error_rates` (`LLM` = 1 − RPR per cluster; `StrictHuman` = 1 − Annotator B rate); `scenario` (`random`, `year2023`, `year2024`, `year2025`); `series`; `draws`; `base_win_OR`; `win_OR_median/min/max`, `win_lo_median`, `win_hi_median`; `win_same_sign`; `win_CI_excludes_1_same_dir`; `full_OR_median`; `full_same_sign` |
| `P4b_tipping_point` | `series`; `direction` (increase/decrease); `tipping_year`; `n_series_in_tipping_year`; `tipping_share_CI_includes_1`; `tipping_share_sign_reverses`; `tipping_CI_if_2023/2024/2025`; `audited_FP_rate_LLM`, `audited_FP_rate_LLM_upper95`, `audited_FP_rate_strict_human` |
| `P6_stability` | `method`; `k`; `seed_ARI_median`, `seed_ARI_min`; `subsample_ARI_median`, `subsample_ARI_min`; `smallest_share` |
| `P8_FDR16` | `series` (5 clusters + 11 domains); `n`; `pre2023_share`; `emergent`; `full_*`, `win_*`, `seg_*`, `q_*` (OR, lo, hi, p for full-period log-linear, 2023–2025 window, segmented post-2023 slope, quarterly models); `spline_LR_p`; `full_q16`, `win_q16`, `seg_q16`, `q_q16` (BH across all 16 series); `full_q_original_scheme` (earlier scheme, BH over non-emergent series only); `robust_after_FDR16` (`yes`, `direction only`, `no`) |

`R11_reanalysis_log.txt`: English plain-text log of the same analyses. `R11_repro_check.txt`: English output of `scripts/repro_compare.py` (MATCH/DIFF per file and conclusion).

`_human120.pkl`: pandas DataFrame (pickle protocol 5) of the 120 human-annotated repositories, written by `r11_reanalysis.py` and read by `audit/make_adjudication_kit.py` and `audit/score_adjudication.py`. Columns: `item_no` (Korean original `번호`, item number 1–120); `A`, `B`, `C` (binary agent judgment of each annotator); `full_name`; `cluster`; `year`; `llm_qwen`, `llm_llama` (audit categories); `LLM` (both models agent); `A_pos`, `B_pos`, `C_pos` (binary judgments); `Majority`, `Unanimous`, `Any`; `n_pos` (number of annotators judging agent); `disagree` (not unanimous). In the English version, the column name `번호` was renamed to `item_no` inside the pickle; values are unchanged.

## 4. Audit and annotation files (`audit/`)

Files in this section that contained Korean sheet names, headers, values, or instructions were rewritten with English text (cell values, formatting, data validation, and hyperlinks otherwise unchanged).

### 4.1 `audit/human_eval_stratified_sample_400.xlsx`
Relevance-audit sample (404 repositories, stratified by coarse cluster × creation period). Produced by `scripts/audit_kit.py`; read by `analysis_r1_revision.py`, `analysis_r2_precision_robustness.py`, `analysis_r8_strict_rater_B.py`, `r11_reanalysis.py`, `audit/make_easy_survey.py`, `audit/score_label_eval.py`, `audit/compute_alpha.py`.

Sheet `sample`: `full_name`; `description`; `topics`; `stars`; `year`; `cluster`; `llm_qwen`, `llm_llama` (audit category assigned by Qwen2.5-7B / Llama-3.1-8B); `url`; `rater1`, `rater2` (empty columns for optional human raters).

Sheet `guide` (category definitions):

| Column (English) | Korean original |
|---|---|
| `Category` | 분류 |
| `Definition` | 정의 |

| Category | Definition (English) | Korean original |
|---|---|---|
| Agent-framework | Library/framework/SDK for building AI agents | AI 에이전트 구축용 라이브러리/프레임워크/SDK |
| Agent-application | Actual application/product/tool that operates as an AI agent | AI 에이전트로 동작하는 실제 응용/제품/도구 |
| MCP-server | MCP server/client/integration | MCP 서버/클라이언트/연동 |
| Tutorial-example | Educational example, course, demo, or starter template | 교육용 예제·강좌·데모·스타터 템플릿 |
| Awesome-resource | awesome-list, link collection, curation | awesome-list·링크 모음·큐레이션 |
| Paper-code | Code or benchmark accompanying a paper | 논문 동반 코드/벤치마크 |
| Non-agent | Unrelated to AI agents | AI 에이전트와 무관 |
| Other | Cannot judge / other | 판단 불가/기타 |

### 4.2 `audit/llm_dual_classification_provisional_metrics.xlsx`
Summary of the dual-LLM audit (`audit_kit.py`). Columns: `n` (404); `model_agreement`; `provisional_precision_bothagent` (relevance-positive rate); `wilson_lo`, `wilson_hi`; `either_nonagent` (share labeled Non-agent by at least one model). Cell contents unchanged.

### 4.3 Human annotation of 120 repositories and 17 cluster labels

Item numbering: the 120 repositories (24 per coarse cluster, random order) and 17 labels (5 coarse T0–T4 + 12 fine-grained M0–M11) are numbered by `item_no` (Korean original `번호`) in all sheets.

**`audit/survey_answer_key_do_not_open.xlsx`** (produced by `audit/make_easy_survey.py`; read by all `score_*` scripts and `r11_reanalysis.py`). Sheet `repo_key`: `item_no`; `full_name`; `cluster`; `year`; `llm_qwen`; `llm_llama`. Sheet `label_key`: `item_no`; `cid` (T0–T4, M0–M11); `n_docs`; `label_refined`.

**`audit/survey_easy_version.xlsx`** (single-annotator version with dropdowns; produced by `make_easy_survey.py`; scored by `score_easy_survey.py`). This version was not used for the reported results.

| Sheet (English) | Korean original |
|---|---|
| `Read me` (instructions) | 읽어주세요 |
| `Repositories (120)` | 리포지토리 120건 |
| `Cluster labels (17)` | 군집 라벨 17건 |

| Column (English) | Korean original | Meaning |
|---|---|---|
| `item_no` | 번호 | Item number |
| `Repository name` | 리포지토리 이름 | `full_name` |
| `Description` | 설명 | GitHub description (English original) |
| `Tags` | 태그 | Topic tags |
| `Link (click)` | 링크(클릭) | Repository URL |
| `▶ Judgment (choose from dropdown)` | ▶ 판정 (드롭다운 선택) | Dropdown: `1 Yes - AI agent` (1 AI 에이전트 맞음), `2 Tutorial/resource list/paper code` (2 튜토리얼·자료모음·논문코드), `3 No or not sure` (3 아님 또는 모르겠음) |
| `Notes (optional)` | 메모(선택) | Free text |
| `Representative terms of this cluster` | 이 군집의 대표 단어 | Top terms (English) |
| `Representative repositories` | 대표 리포지토리 | Repositories nearest the centroid |
| `Name (label) given by AI` | AI가 붙인 이름(라벨) | `label_refined` |
| `▶ Does the name fit? (dropdown)` | ▶ 이름이 잘 맞나요? (드롭다운) | `3 Fits well` (3 잘 맞음), `2 Roughly fits` (2 대충 맞음), `1 Does not fit` (1 안 맞음) |
| `▶ Do the terms form one topic? (dropdown)` | ▶ 단어들이 한 주제로 보이나요? (드롭다운) | Same 3-point scale |

**`audit/survey_simplest_completed.xlsx`** (Annotator A, author), **`audit/survey_friend_version_rater2_completed.xlsx`** (Annotator B, external volunteer), **`audit/survey_friend_version_rater3_completed.xlsx`** (Annotator C, external volunteer). Completed O-mark questionnaires used for all reported human-annotation results. Generated by `audit/make_simplest_survey.py` (A) and `audit/make_friend_survey.py` (B, C); read by `audit/score_three_annotators.py`, `audit/score_simplest.py`, `scripts/r11_reanalysis.py`, `audit/make_adjudication_kit.py`. The annotators saw Korean text; in these English copies the Korean instructions, short descriptions, term lists, and labels are replaced by their English translations (from `audit/survey_annotator_display_text.json`). The annotators' marks are unchanged.

| Sheet (English) | Korean original |
|---|---|
| `Read before starting` (instructions; the last rows hold the respondent's name/date/experience) | 시작 전 읽기 |
| `① Projects (120)` | ① 프로젝트 120개 |
| `② Group names (17)` | ② 그룹 이름 17개 |

Sheet `① Projects (120)`:

| Column (English) | Korean original | Meaning |
|---|---|---|
| `item_no` | 번호 | Item number (the scripts re-number rows 1–120) |
| `What is this project? (short description)` | 이 프로젝트는 무엇인가요? (한글 설명) | Short description shown to the annotator (Korean translation of the GitHub description; English rendering in this copy) |
| `Link` | 링크 | Cell text `Open` (열기) with a hyperlink to the repository |
| `AI agent\nyes` | AI 에이전트\n맞음 | Mark "O" = class 1, AI agent (agent framework, application, or MCP server/tool) |
| `Resource list/\ntutorial` | 자료모음·\n튜토리얼 | Mark "O" = class 2, tutorial, curated list, template, or paper code |
| `No/\nnot sure` | 아님·\n모르겠음 | Mark "O" = class 3, unrelated or undecidable |

Sheet `② Group names (17)`:

| Column (English) | Korean original | Meaning |
|---|---|---|
| `item_no` | 번호 | Label item number |
| `Main terms of this group` | 이 그룹의 주요 단어들 (한글) | Top 10 terms (Korean glosses; English in this copy) |
| `Group name given by AI` | AI가 지은 그룹 이름 (한글) | LLM label (Korean translation; English in this copy) |
| `Name\nfits well` | 이름이\n잘 맞음 | Mark "O" = rating 3 |
| `Roughly\nfits` | 대충\n맞음 | Mark "O" = rating 2 |
| `Does not fit` | 안 맞음 | Mark "O" = rating 1 |

Accepted marks (scripts): `O`, `V`, `X`, `✓`, `○`, Greek `Ο`, and the Korean letter `ㅇ` (U+3147, written as `'\u3147'` in the code); exactly one mark per row is required. Respondent experience (last row of `Read before starting`, Korean `평소 AI/개발 경험 (없음 / 조금 / 많음)` = prior AI/software-development experience none / some / extensive): Annotator B `extensive` (많음), Annotator C `some` (조금).

**`audit/survey_annotator_display_text.json`** (read by `make_simplest_survey.py`, `make_friend_survey.py`). Object with three maps: `repo` (item number 1–120 → short description), `label` (label item 1–17 → label text), `terms` (English term → display gloss). In the original release the values were Korean translations shown to the annotators; in this version they are English renderings of those Korean texts (for `terms`, the English term with the clarification that the Korean gloss added, e.g. `"cli": "CLI (command line)"`).

**`audit/cluster_label_human_eval_blind_sheet.xlsx`** (blind label-rating kit; produced by `audit/make_label_eval_kit.py`; scored by `audit/score_label_eval.py`; not used for the reported results). Sheet `guide` (`Item` = 항목, `Description` = 설명): rows `coherence`, `label_fit`, `distinctness`, `word_intrusion`, `Scale` (척도), `Blinding` (블라인드) with English definitions. Sheet `cluster_rating`: `item_id` (C01–C17, masked), `top_terms`, `representative_repos`, `candidate_label`, `rater1..3_coherence`, `rater1..3_label_fit`, `rater1..3_distinctness` (1–5), `notes`. Sheet `word_intrusion`: `item_id`, `term1`–`term6` (one is an intruder), `rater1..3_pick`. Sheet `key`: `item_id`, `level` (macro/meso), `cluster` (T*/M*), `n_docs`, `intruder`.

**`audit/human_eval_three_annotators_results_260910.txt`**: output of `audit/score_three_annotators.py` (English): answers per annotator and class distribution (`exp` = self-reported experience), precision with Wilson CI, agreement and κ with the LLM consensus, pairwise agreement/κ (3-class and binary), Krippendorff's α, vote distribution, majority/unanimous/any precision, per-cluster rates, label-fit ratings.

**`audit/human_eval_results_260910.txt`**: output of `audit/score_simplest.py` for Annotator A only (first-round scoring). English translation of the printed lines; Korean originals: `판정 … 건 (미응답/중복표시 … 건) | 인간 정밀도` = judged items (unanswered/multiple marks) | human precision; `LLM 합의 정밀도` = LLM consensus precision; `인간↔LLM 일치` = human-LLM agreement; `자료모음/튜토리얼` = resource list/tutorial; `아님/모름` = no/not sure; `세그먼트별` = by segment (cluster); `라벨 적합도 평균 … 응답 … 건` = mean label fit … responses.

### 4.4 R11 adjudication kit

**`audit/R11_adjudication_sheets.xlsx`** (produced by `audit/make_adjudication_kit.py`; filled copies are scored by `audit/score_adjudication.py`; rules in `audit/R11_codebook.md`). Blank kit; not used to revise any reported judgment.

| Sheet (English) | Korean original |
|---|---|
| `Read me` | 읽어주세요 |
| `① Independent reannotation 120` | ① 독립 재평가 120 |
| `② Consensus adjudication 40` | ② 합의 판정 40 |

| Column (English) | Korean original | Meaning |
|---|---|---|
| `item_no` | 번호 | Item number (as in the questionnaires) |
| `repository` | repository | `full_name` |
| `Link` | 링크 | Repository URL |
| `Short description` | 한글 설명 | Short description shown to annotators (English rendering) |
| `description (original)` | description (원문) | Original GitHub description |
| `topics` | topics | Topic tags |
| `A original judgment`, `B original judgment`, `C original judgment` | A 원판정, B 원판정, C 원판정 | Original class of each annotator (sheet ② only) |
| `Votes for agent` | 찬성 수 | Number of annotators who chose class 1 (sheet ② only) |
| `Judgment (1/2/3)` | 판정(1/2/3) | Class to be entered (dropdown 1, 2, 3) |
| `Rule no.` | 규칙 번호 | Codebook rule R1–R10 |
| `Notes` | 메모 | Free text |

Class values: `1 Agent software` (1 에이전트 소프트웨어), `2 Learning/reference resource` (2 학습·참고 자료), `3 Unrelated/undecidable` (3 무관·판정불가).

## 5. Files referenced by scripts but not included

Generated on demand or part of the authors' working folder: `github_ai_agent_raw.xlsx` (initial collection, superseded by v2), `survey_easy_version_english_only.xlsx` (Korean original `설문지_쉬운버전_영문만.xlsx`), `survey_simplest.xlsx` (`설문지_초간단.xlsx`, blank form), `survey_friend_version_rater2.xlsx` (`설문지_친구용_2차평가자.xlsx`, blank form), `R11_adjudication_sheets_rater*.xlsx` (`R11_판정시트_평가자*.xlsx`), `R11_adjudication_sheets_consensus.xlsx` (`R11_판정시트_합의.xlsx`), `R11_adjudication_result.txt`, `fig6_domain_quarterly_trends.png` (`그림6_도메인_분기추이.png`), and the terminology-audit inputs/outputs under `30_analysis_results/term_review/` (`용어검토`): `prior_work_fulltext.json` (`선행연구_전문텍스트.json`), `term_DF_full.csv` (`용어DF_전수.csv`), `candidate_term_DF.csv` (`후보용어DF.csv`), `term_standardization_report_*.xlsx` (`용어표준화_결과보고_*.xlsx`).
