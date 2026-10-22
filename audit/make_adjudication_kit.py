# -*- coding: utf-8 -*-
"""Build the R11 adjudication kit (review item 2).
  Sheet ① independent re-annotation of all 120 repositories under the codebook (original judgments hidden)
  Sheet ② consensus adjudication of the 40 non-unanimous repositories (original judgments shown)
Input: ../01_재분석/_human120.pkl (written by r11_reanalysis.py), the original Korean descriptions, raw metadata.
Output: R11_판정시트.xlsx
"""
import os, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(os.path.dirname(HERE), 'results')):     # replication repository: audit/<this file>
    REPO = os.path.dirname(HERE); AUD = HERE; DATA = os.path.join(REPO, 'data'); PKL = os.path.join(REPO, 'results', 'R11', '_human120.pkl')
else:                                                                 # authors' working folder: 92_…/02_…/<this file>
    ROOT = os.path.dirname(os.path.dirname(HERE)); AUD = os.path.join(ROOT, '40_감사_인간평가키트'); DATA = os.path.join(ROOT, '10_데이터수집')
    PKL = os.path.join(HERE, '..', '01_재분석', '_human120.pkl')
H = pd.read_pickle(PKL)
ko = pd.read_excel(os.path.join(AUD, '설문지_초간단_작성.xlsx'), sheet_name='① 프로젝트 120개').iloc[:, :2]; ko.columns = ['번호', 'desc_ko']
raw = pd.read_excel(os.path.join(DATA, 'github_ai_agent_raw_v2.xlsx'))[['full_name', 'description', 'topics']]
H = H.merge(ko, on='번호').merge(raw, on='full_name', how='left')
CLS = {'1': '1 에이전트 소프트웨어', '2': '2 학습·참고 자료', '3': '3 무관·판정불가'}
YEL = PatternFill('solid', fgColor='FFF2CC'); HDR = PatternFill('solid', fgColor='D9E1F2'); WRAP = Alignment(wrap_text=True, vertical='top')
wb = Workbook(); ws0 = wb.active; ws0.title = '읽어주세요'
for i, line in enumerate([
    'R11 판정 키트 — 먼저 00_판정기준_codebook.md 를 읽으세요.',
    '시트 ① (독립 재평가): 120건 전부. 원래 판정은 보이지 않습니다. 다른 사람과 상의하지 마세요. 노란 칸에 1/2/3 과 규칙 번호(R1~R10).',
    '시트 ② (합의 판정): 원래 3인 판정이 갈린 40건. 원래 판정을 보고, 코드북 규칙을 근거로 최종 범주를 정합니다.',
    '시트 ①은 평가자마다 파일을 복사해 따로 작성(파일명 끝에 _평가자1, _평가자2). 시트 ②는 판정자 1인 또는 2인 합의로 한 파일.',
    '판정 근거는 저장소 이름·설명·태그가 1순위, 부족하면 링크의 README 첫 화면까지만.'], 1):
    ws0.cell(i, 1, line).alignment = WRAP
ws0.column_dimensions['A'].width = 120
def sheet(title, rows, show_orig):
    ws = wb.create_sheet(title)
    cols = ['번호', 'repository', '링크', '한글 설명', 'description (원문)', 'topics'] + (['A 원판정', 'B 원판정', 'C 원판정', '찬성 수'] if show_orig else []) + ['판정(1/2/3)', '규칙 번호', '메모']
    for j, c in enumerate(cols, 1):
        x = ws.cell(1, j, c); x.fill = HDR; x.font = Font(bold=True); x.alignment = WRAP
    dv = DataValidation(type='list', formula1='"1,2,3"', allow_blank=True); ws.add_data_validation(dv)
    for i, r in enumerate(rows.itertuples(), 2):
        vals = [r.번호, r.full_name, f'https://github.com/{r.full_name}', r.desc_ko, r.description, r.topics]
        if show_orig: vals += [CLS[r.A_raw], CLS[r.B_raw], CLS[r.C_raw], int(r.n_pos)]
        vals += [None, None, None]
        for j, v in enumerate(vals, 1):
            c = ws.cell(i, j, v); c.alignment = WRAP
        jcls = len(vals) - 2
        for j in (jcls, jcls + 1, jcls + 2): ws.cell(i, j).fill = YEL
        dv.add(ws.cell(i, jcls))
    for j, w in enumerate([6, 30, 32, 50, 50, 28] + ([16, 16, 16, 7] if show_orig else []) + [11, 10, 30], 1):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.freeze_panes = 'B2'
# original 3-class answers (the pickle keeps only binary columns), read with the scoring rule of score_three_annotators.py
MARK = lambda v: str(v).strip() not in ('', 'nan', 'None') and str(v).strip().upper().rstrip('.0') in ('O', '', 'V', 'X', '✓', 'ㅇ', '○', 'Ο')
FILES = {'A': '설문지_초간단_작성.xlsx', 'B': '설문지_친구용_2차평가자_작성.xlsx', 'C': '설문지_친구용_3차평가자_작성.xlsx'}
for k, f in FILES.items():
    d = pd.read_excel(os.path.join(AUD, f), sheet_name='① 프로젝트 120개'); d.columns = ['번호', 'desc', 'link', 'a1', 'a2', 'a3']; d['번호'] = range(1, len(d) + 1)
    d[k + '_raw'] = d.apply(lambda r: str([MARK(r.a1), MARK(r.a2), MARK(r.a3)].index(True) + 1), axis=1)
    H = H.merge(d[['번호', k + '_raw']], on='번호')
assert all(((H[k + '_raw'] == '1') == H[k + '_pos']).all() for k in 'ABC'),'binary columns disagree with raw answers'
sheet('① 독립 재평가 120', H.sample(frac=1, random_state=2026)[['번호', 'full_name', 'desc_ko', 'description', 'topics']], False)
sheet('② 합의 판정 40', H[H['disagree']].sort_values('번호'), True)
out = os.path.join(HERE, 'R11_판정시트.xlsx'); wb.save(out)
print('saved', out, '| sheet1 =', len(H), '| sheet2 =', int(H['disagree'].sum()))
