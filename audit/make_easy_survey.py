# -*- coding: utf-8 -*-
"""아주 쉬운 1인용 설문지 생성 (2026-09-10)
  설문지_쉬운버전.xlsx  — 평가자가 여는 파일. 모델 라벨 없음(블라인드).
     시트1 '리포지토리 120건' : 번호·이름·설명·태그·링크 + [판정] 드롭다운 3택
     시트2 '군집 라벨 17건'   : 단어·대표리포·후보라벨 + [잘 맞나요] 드롭다운 3택
  설문지_정답키(열지마세요).xlsx — LLM 라벨·군집 ID. 채점 때만 사용.
채점: python score_easy_survey.py
"""
import os, random, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
random.seed(2026)
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), 'results') if os.path.isdir(os.path.join(os.path.dirname(HERE), 'results')) else os.path.join(os.path.dirname(HERE), '30_분석결과')
PER_CLUSTER = 24

# ── 1. 리포지토리 120건: 404 감사표본에서 세그먼트별 24건 층화 ──
aud = pd.read_excel(os.path.join(HERE, '인간평가_층화표본400.xlsx'), sheet_name='sample')
picks = []
for c in sorted(aud['cluster'].unique()):
    g = aud[aud['cluster'] == c]
    picks.append(g.sample(min(PER_CLUSTER, len(g)), random_state=100 + int(c)))
s = pd.concat(picks).sample(frac=1, random_state=7).reset_index(drop=True)
s.insert(0, '번호', range(1, len(s) + 1))

# ── 2. 군집 라벨 17건 ──
mac = pd.read_excel(os.path.join(RES, '토픽_macro_k5.xlsx')); mac['cid'] = 'T' + mac['cluster'].astype(str)
mes = pd.read_excel(os.path.join(RES, '토픽_meso_k12.xlsx')); mes['cid'] = 'M' + mes['cluster'].astype(str)
lab = pd.concat([mac, mes], ignore_index=True).sample(frac=1, random_state=3).reset_index(drop=True)
lab.insert(0, '번호', range(1, len(lab) + 1))

# ── 3. 설문지 xlsx ──
wb = Workbook(); ws = wb.active; ws.title = '리포지토리 120건'
head_fill = PatternFill('solid', fgColor='DDEBF7'); ans_fill = PatternFill('solid', fgColor='FFF2CC')
ws.append(['번호', '리포지토리 이름', '설명', '태그', '링크(클릭)', '▶ 판정 (드롭다운 선택)', '메모(선택)'])
for _, r in s.iterrows():
    ws.append([int(r['번호']), r['full_name'], str(r['description']), str(r['topics']).replace(';', ', '), r['url'], '', ''])
    ws.cell(ws.max_row, 5).hyperlink = r['url']; ws.cell(ws.max_row, 5).font = Font(color='0563C1', underline='single')
dv = DataValidation(type='list', formula1='"1 AI 에이전트 맞음,2 튜토리얼·자료모음·논문코드,3 아님 또는 모르겠음"', allow_blank=True, showDropDown=False)
dv.error = '드롭다운에서 고르세요'; ws.add_data_validation(dv); dv.add(f'F2:F{ws.max_row}')
for col, w in zip('ABCDEFG', [6, 34, 70, 40, 14, 34, 24]): ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
for c in ws[1]: c.fill = head_fill; c.font = Font(bold=True)
for i in range(2, ws.max_row + 1): ws.cell(i, 6).fill = ans_fill
ws.freeze_panes = 'A2'

ws2 = wb.create_sheet('군집 라벨 17건')
ws2.append(['번호', '이 군집의 대표 단어', '대표 리포지토리', 'AI가 붙인 이름(라벨)', '▶ 이름이 잘 맞나요? (드롭다운)', '▶ 단어들이 한 주제로 보이나요? (드롭다운)', '메모(선택)'])
for _, r in lab.iterrows():
    ws2.append([int(r['번호']), r['top_terms'], str(r['rep_repos']).replace(';', '\n'), r['label_refined'], '', '', ''])
dv2 = DataValidation(type='list', formula1='"3 잘 맞음,2 대충 맞음,1 안 맞음"', allow_blank=True); ws2.add_data_validation(dv2); dv2.add(f'E2:E{ws2.max_row}'); dv2.add(f'F2:F{ws2.max_row}')
for col, w in zip('ABCDEFG', [6, 50, 44, 40, 26, 30, 24]): ws2.column_dimensions[col].width = w
for row in ws2.iter_rows(min_row=1, max_row=ws2.max_row):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
for c in ws2[1]: c.fill = head_fill; c.font = Font(bold=True)
for i in range(2, ws2.max_row + 1): ws2.cell(i, 5).fill = ans_fill; ws2.cell(i, 6).fill = ans_fill
ws2.freeze_panes = 'A2'

ws0 = wb.create_sheet('읽어주세요', 0)
for line in ['이 파일은 혼자서 1시간 안에 끝내는 설문입니다.', '',
             '[시트 1] 리포지토리 120건 — 이름·설명·태그를 보고 노란 칸에서 하나만 고르세요.',
             '   1 AI 에이전트 맞음   = 에이전트를 만드는 도구/프레임워크, 에이전트로 동작하는 앱, MCP 서버',
             '   2 튜토리얼·자료모음·논문코드 = 강의용 예제, awesome 리스트, 논문 재현 코드',
             '   3 아님 또는 모르겠음 = AI 에이전트와 무관하거나 판단 불가',
             '   ※ 설명만으로 애매하면 링크를 눌러 10초만 보세요. 고민은 20초 이상 하지 마세요.',
             '', '[시트 2] 군집 라벨 17건 — 단어 묶음과 대표 리포를 보고, AI가 붙인 이름이 맞는지(3/2/1), 단어들이 한 주제인지(3/2/1) 고르세요.',
             '', '끝나면 파일을 저장하고 알려주세요. 채점은 자동입니다.']:
    ws0.append([line])
ws0.column_dimensions['A'].width = 110
out = os.path.join(HERE, '설문지_쉬운버전.xlsx'); wb.save(out)

# ── 4. 정답키(분리 파일) ──
with pd.ExcelWriter(os.path.join(HERE, '설문지_정답키(열지마세요).xlsx')) as w:
    s[['번호', 'full_name', 'cluster', 'year', 'llm_qwen', 'llm_llama']].to_excel(w, sheet_name='repo_key', index=False)
    lab[['번호', 'cid', 'n_docs', 'label_refined']].to_excel(w, sheet_name='label_key', index=False)
print('설문 120+17건 생성:', out)
