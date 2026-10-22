# -*- coding: utf-8 -*-
"""Build the blind human-evaluation kit for cluster quality and LLM labels (R1, comments 8/9).
Outputs: 라벨_군집_인간평가_블라인드시트.xlsx with sheets
  - cluster_rating : per cluster (5 macro + 12 meso, order shuffled, ids masked) -> coherence / label_fit / distinctness (1-5) per rater
  - word_intrusion : 17 items, 5 top terms + 1 intruder term shuffled -> rater picks the intruder (accuracy = topic coherence proxy)
  - key            : mapping from masked id to real cluster (KEEP HIDDEN from raters)
  - guide          : rating instructions
Scoring: score_label_eval.py
"""
import os, random, pandas as pd
random.seed(7)
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), 'results') if os.path.isdir(os.path.join(os.path.dirname(HERE), 'results')) else os.path.join(os.path.dirname(HERE), '30_분석결과')
mac = pd.read_excel(os.path.join(RES, '토픽_macro_k5.xlsx')); mac['level'] = 'macro'; mac['cid'] = 'T' + mac['cluster'].astype(str)
mes = pd.read_excel(os.path.join(RES, '토픽_meso_k12.xlsx')); mes['level'] = 'meso'; mes['cid'] = 'M' + mes['cluster'].astype(str)
allc = pd.concat([mac, mes], ignore_index=True)
allc['terms'] = allc['top_terms'].apply(lambda s: [t.strip() for t in s.split(',')])
order = list(range(len(allc))); random.shuffle(order)
rows, intr, key = [], [], []
for j, i in enumerate(order):
    r = allc.loc[i]; mid = f'C{j+1:02d}'
    rows.append(dict(item_id=mid, top_terms=', '.join(r['terms'][:12]), representative_repos=r['rep_repos'], candidate_label=r['label_refined'],
                     rater1_coherence='', rater1_label_fit='', rater1_distinctness='', rater2_coherence='', rater2_label_fit='', rater2_distinctness='', rater3_coherence='', rater3_label_fit='', rater3_distinctness='', notes=''))
    # word intrusion: 5 own terms + 1 term from a different cluster at the same level that is NOT in own top-12
    own = r['terms'][:5]; pool = allc[(allc['level'] == r['level']) & (allc.index != i)]
    cands = [t for t in sum(pool['terms'].tolist(), []) if t not in r['terms']]; intruder = random.choice(cands)
    six = own + [intruder]; random.shuffle(six)
    intr.append(dict(item_id=mid, **{f'term{n+1}': six[n] for n in range(6)}, rater1_pick='', rater2_pick='', rater3_pick=''))
    key.append(dict(item_id=mid, level=r['level'], cluster=r['cid'], n_docs=r['n_docs'], intruder=intruder))
guide = pd.DataFrame({'항목': ['coherence', 'label_fit', 'distinctness', 'word_intrusion', '척도', '블라인드'],
                      '설명': ['상위 단어와 대표 리포지토리가 하나의 일관된 주제를 이루는가 (1=전혀 아님, 5=매우 그렇다)',
                              '제시된 후보 라벨이 그 군집의 내용을 정확히 서술하는가 (1~5)',
                              '이 군집이 시트의 다른 군집들과 구별되는 독자적 내용인가 (1~5)',
                              'term1~6 중 나머지 5개와 어울리지 않는 단어 1개를 고르시오 (term 번호 기입)',
                              '1~5 정수. 판단이 어려우면 3.', '평가자는 key 시트를 보지 말 것. 군집 순서는 무작위·번호 마스킹']})
out = os.path.join(HERE, '라벨_군집_인간평가_블라인드시트.xlsx')
with pd.ExcelWriter(out) as w:
    guide.to_excel(w, 'guide', index=False); pd.DataFrame(rows).to_excel(w, 'cluster_rating', index=False)
    pd.DataFrame(intr).to_excel(w, 'word_intrusion', index=False); pd.DataFrame(key).to_excel(w, 'key', index=False)
print('written', out, len(rows), 'items')
