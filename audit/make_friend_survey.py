# -*- coding: utf-8 -*-
"""초간단 설문지: 한글만, 큰 글씨, O 하나만 치면 끝. → 설문지_초간단.xlsx (채점: score_simplest.py)"""
import os, json, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
HERE = os.path.dirname(os.path.abspath(__file__))
tr = json.load(open(os.path.join(HERE, '설문지_한글번역.json'), encoding='utf-8'))
base = pd.read_excel(os.path.join(HERE, '설문지_쉬운버전_영문만.xlsx'), sheet_name='리포지토리 120건')
labs = pd.read_excel(os.path.join(HERE, '설문지_쉬운버전_영문만.xlsx'), sheet_name='군집 라벨 17건')
thin = Side(style='thin', color='BBBBBB'); box = Border(left=thin, right=thin, top=thin, bottom=thin)
H = PatternFill('solid', fgColor='305496'); Y = PatternFill('solid', fgColor='FFF2CC'); G = PatternFill('solid', fgColor='E2EFDA')
big = Font(size=13); bold = Font(size=13, bold=True, color='FFFFFF')

wb = Workbook(); ws = wb.active; ws.title = '① 프로젝트 120개'
ws.append(['번호', '이 프로젝트는 무엇인가요? (한글 설명)', '링크', 'AI 에이전트\n맞음', '자료모음·\n튜토리얼', '아님·\n모르겠음'])
for _, r in base.iterrows():
    ws.append([int(r['번호']), tr['repo'].get(str(r['번호']), ''), '열기', '', '', ''])
    c = ws.cell(ws.max_row, 3); c.hyperlink = r['링크(클릭)']; c.font = Font(size=12, color='0563C1', underline='single')
for col, w in zip('ABCDEF', [6, 72, 7, 13, 13, 13]): ws.column_dimensions[col].width = w
ws.row_dimensions[1].height = 42
for r in range(1, ws.max_row + 1):
    ws.row_dimensions[r].height = ws.row_dimensions[r].height or 48
    for c in range(1, 7):
        cell = ws.cell(r, c); cell.border = box; cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center' if c != 2 else 'left')
        if r == 1: cell.fill = H; cell.font = bold
        else:
            if c != 3: cell.font = big
            if c >= 4: cell.fill = Y
            if c == 2: cell.fill = G
ws.freeze_panes = 'A2'

ws2 = wb.create_sheet('② 그룹 이름 17개')
ws2.append(['번호', '이 그룹의 주요 단어들 (한글)', 'AI가 지은 그룹 이름 (한글)', '이름이\n잘 맞음', '대충\n맞음', '안 맞음'])
for _, r in labs.iterrows():
    terms = [t.strip() for t in str(r['이 군집의 대표 단어']).split(',')][:10]
    ws2.append([int(r['번호']), ', '.join(tr['terms'].get(t, t) for t in terms), tr['label'].get(str(r['번호']), ''), '', '', ''])
for col, w in zip('ABCDEF', [6, 58, 34, 12, 12, 12]): ws2.column_dimensions[col].width = w
ws2.row_dimensions[1].height = 42
for r in range(1, ws2.max_row + 1):
    if r > 1: ws2.row_dimensions[r].height = 52
    for c in range(1, 7):
        cell = ws2.cell(r, c); cell.border = box; cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center' if c not in (2, 3) else 'left')
        if r == 1: cell.fill = H; cell.font = bold
        else:
            cell.font = big
            if c >= 4: cell.fill = Y
            if c in (2, 3): cell.fill = G
ws2.freeze_panes = 'A2'

ws0 = wb.create_sheet('시작 전 읽기', 0)
lines = ['AI 에이전트 프로젝트 분류 설문 — 참여해 주셔서 감사합니다!', '',
         '■ 이게 뭔가요?',
         '   GitHub에 올라온 프로젝트 120개가 정말 "AI 에이전트" 관련인지, 사람 눈으로 확인하는 설문입니다.',
         '   정답은 없습니다. 첫인상으로 편하게 골라 주세요. 전문 지식이 없어도 괜찮습니다.', '',
         '■ 어떻게 하나요? (30~40분)',
         '   ① 시트 "① 프로젝트 120개"로 가서, 한글 설명을 읽고 노란 칸 셋 중 하나에만 O 를 칩니다.',
         '        · AI 에이전트 맞음    = AI가 스스로 일을 처리해 주는 프로그램, 또는 그런 프로그램을 만드는 도구·부품(MCP 서버 포함)',
         '        · 자료모음·튜토리얼  = 링크 모음집, 강의·예제, 논문 실험 코드처럼 "쓰는 프로그램"이 아닌 것',
         '        · 아님·모르겠음      = AI 에이전트와 상관없어 보이거나, 읽어도 판단이 안 되는 것',
         '   ② 시트 "② 그룹 이름 17개"로 가서, 단어 묶음을 보고 AI가 지은 이름이 어울리는지 셋 중 하나에 O.', '',
         '■ 팁',
         '   · 설명이 애매하면 "열기"를 눌러 GitHub 페이지를 10초만 보세요. 20초 넘게 고민하지 마세요.',
         '   · 한 줄에 O는 하나만. 잘못 쳤으면 지우고 다시 치면 됩니다.',
         '   · 다 하면 Ctrl+S 로 저장한 뒤 이 파일을 그대로 보내 주세요.', '',
         '■ 응답자 정보 (아래 노란 칸에 적어 주세요)',
         '   이름(또는 별명):', '   날짜:', '   평소 AI/개발 경험 (없음 / 조금 / 많음):']
for l in lines: ws0.append([l])
ws0.column_dimensions['A'].width = 110
for r in range(1, ws0.max_row + 1):
    ws0.cell(r, 1).font = Font(size=14 if r == 1 else 12, bold=(r == 1 or lines[r-1].startswith('■')))
for r in range(ws0.max_row - 2, ws0.max_row + 1):
    ws0.cell(r, 2).fill = Y; ws0.column_dimensions['B'].width = 30
out = os.path.join(HERE, '설문지_친구용_2차평가자.xlsx'); wb.save(out); print('saved', out)
