# -*- coding: utf-8 -*-
"""Compare outputs regenerated in a fresh copy of the replication repository with the released files (review item 9).
usage: python repro_compare.py <fresh_copy_root> <released_repo_root> <R11_folder_xlsx> <run_log>
Numeric cells are compared with absolute tolerance 1e-9; text cells must be identical. Output: R11_repro_check.txt next to this script."""
import os, sys, re, numpy as np, pandas as pd
fresh, released, r11x, runlog = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__)); out = open(os.path.join(HERE, 'R11_repro_check.txt'), 'w', encoding='utf-8')
def log(s): print(s); out.write(s + '\n')
def cmp_xlsx(a, b, label):
    A = pd.read_excel(a, sheet_name=None); B = pd.read_excel(b, sheet_name=None); bad = []
    for sh in B:
        if sh not in A: bad.append(f'missing sheet {sh}'); continue
        x, y = A[sh], B[sh]
        if x.shape != y.shape or list(x.columns) != list(y.columns): bad.append(f'{sh}: shape/columns differ {x.shape} vs {y.shape}'); continue
        for c in y.columns:
            xs, ys = x[c], y[c]
            if pd.api.types.is_numeric_dtype(ys) and pd.api.types.is_numeric_dtype(xs):
                d = np.nanmax(np.abs(xs.astype(float).values - ys.astype(float).values)) if len(ys) else 0
                if (xs.isna() != ys.isna()).any() or (d > 1e-9): bad.append(f'{sh}.{c}: max abs diff {d:.3g}')
            elif not (xs.astype(str).values == ys.astype(str).values).all(): bad.append(f'{sh}.{c}: text differs')
    log(f'{"MATCH" if not bad else "DIFF "}  {label}' + ('' if not bad else '  -> ' + '; '.join(bad[:6])))
    return not bad
log('R11 reproduction check (2026-10-15): fresh copy of the replication repository (no .git), + results/embeddings.npy, emb_keys.npy')
log('scripts run in order: audit/score_three_annotators.py, scripts/analysis_r1_revision.py, scripts/analysis_r2_precision_robustness.py, scripts/analysis_r8_strict_rater_B.py, scripts/r11_reanalysis.py')
txt = open(runlog, encoding='utf-8', errors='replace').read()
log('exit codes: ' + ' '.join(re.findall(r'exit (\d+)', txt)))
ok = True
for f in ['B_glm_functional_form_sensitivity.xlsx', 'C_cohort_activity_survivorship.xlsx', 'C_cluster_activity.xlsx', 'C_glm_active24m_sensitivity.xlsx',
          'D_audit_precision_by_stratum.xlsx', 'E_representative_repos.xlsx', 'F_precision_robustness.xlsx', 'F3_precision_robustness_strict_raterB.xlsx']:
    ok &= cmp_xlsx(os.path.join(fresh, 'results', 'R1_revision', f), os.path.join(released, 'results', 'R1_revision', f), f'results/R1_revision/{f}')
ok &= cmp_xlsx(os.path.join(fresh, 'results', 'R11', 'R11_reanalysis.xlsx'), r11x, 'results/R11/R11_reanalysis.xlsx (vs authors\' run)')
# human annotation statistics printed by score_three_annotators.py vs the released result text
seg = txt.split('=== audit/score_three_annotators.py')[1].split('===')[0]
ref = open(os.path.join(released, 'audit', 'human_eval_three_annotators_results_260910.txt'), encoding='utf-8').read()
keys = ['precision 0.917', 'precision 0.700', 'precision 0.808', 'binary 0.285', 'majority(>=2 of 3) precision 0.792']
found = {k: (k in seg) for k in keys}
log(f'{"MATCH" if all(found.values()) else "DIFF "}  audit/score_three_annotators.py printed statistics: ' + ', '.join(f'{k}={v}' for k, v in found.items()))
ok &= all(found.values())
log('RESULT: ' + ('all regenerated outputs match the released files' if ok else 'differences found (see DIFF lines)'))
out.close()
