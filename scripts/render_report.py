#!/usr/bin/env python3
"""Render the canonical Markdown draft. Optional dependency: reportlab==4.4.9.

Run from any directory: python scripts/render_report.py [--source PATH] [--output PATH]
This deliberately supports the Markdown subset used by this report and fails on
unknown code fences/diagram structure. It does not change report content or claim
final submission readiness. PDF QA uses pdfplumber/pypdf and rendered page review.
"""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PAGE_W, PAGE_H = A4
MARGIN = 72
WIDTH = PAGE_W - 2 * MARGIN
INK = colors.HexColor('#172536')
MUTED = colors.HexColor('#405469')
BLUE = colors.HexColor('#E9F0F6')
NORMALIZE = str.maketrans({'–': '-', '—': '-', '’': "'", '“': '"', '”': '"', '→': '->'})


def inline(text: str) -> str:
    """Keep all visible words; render link labels without printing raw URLs."""
    text = text.translate(NORMALIZE)
    links = []
    def link(match):
        label, target = match.groups()
        if target.startswith(('https://', 'http://')):
            links.append((label, target))
            return f'@@LINK{len(links)-1}@@'
        return label
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = escape(text)
    for index, (label, target) in enumerate(links):
        text = text.replace(f'@@LINK{index}@@',
                            f'<link href="{escape(target, quote=True)}" color="#1C5D7E">{escape(label)}</link>')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    # Courier at the same 11-point size; long IDs are allowed to wrap.
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)


BODY = ParagraphStyle('Body', fontName='Times-Roman', fontSize=11, leading=12.5,
                      textColor=INK, spaceAfter=6, splitLongWords=True)
CELL = ParagraphStyle('Cell', parent=BODY, spaceAfter=0)
HEAD = ParagraphStyle('Heading', parent=BODY, fontName='Times-Bold', fontSize=13,
                      leading=15, spaceBefore=10, spaceAfter=7, keepWithNext=True)
TITLE = ParagraphStyle('Title', parent=HEAD, fontSize=23, leading=27,
                       alignment=TA_CENTER, spaceAfter=22)
CENTER = ParagraphStyle('Center', parent=BODY, alignment=TA_CENTER, spaceAfter=12)
CODE = ParagraphStyle('Equation', parent=BODY, fontName='Courier', leading=13,
                      leftIndent=8, rightIndent=8)


class Architecture(Flowable):
    """Draw the source diagram's exact nodes/edges using a fixed readable layout."""
    def __init__(self, source: list[str]):
        super().__init__()
        self.width, self.height = WIDTH, 394
        self.nodes, self.edges = {}, []
        pattern = r'([A-Z])(?:\[([^\]]+)\])?\s*-->\s*([A-Z])(?:\[([^\]]+)\])?'
        for line in source:
            if line.strip() == 'flowchart LR':
                continue
            match = re.fullmatch(pattern, line.strip())
            if not match:
                raise ValueError(f'Unsupported Mermaid line: {line}')
            left, label_l, right, label_r = match.groups()
            if label_l:
                self.nodes[left] = label_l
            if label_r:
                self.nodes[right] = label_r
            self.edges.append((left, right))
        if set(self.nodes) != set('GRVABSOIED'):
            raise ValueError('Diagram nodes changed: review layout before rendering')
        self.positions = {
            'G': (225, 365, 190), 'R': (225, 317, 190), 'V': (225, 269, 210),
            'A': (108, 221, 192), 'B': (343, 221, 192), 'S': (343, 173, 190),
            'O': (87, 77, 150), 'I': (274, 125, 190),
            'E': (274, 77, 190), 'D': (274, 29, 270),
        }

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(MUTED)
        c.setLineWidth(.7)
        for a, b in self.edges:
            x, y, w = self.positions[a]
            tx, ty, tw = self.positions[b]
            if (a, b) == ('G', 'O'):
                points = [(x-w/2,y), (5,y), (5,ty), (tx-tw/2,ty)]
            elif (a, b) == ('G', 'I'):
                points = [(x+w/2,y), (WIDTH-5,y), (WIDTH-5,ty), (tx+tw/2,ty)]
            elif (a, b) == ('O', 'E'):
                points = [(x+w/2,y), (tx-tw/2,ty)]
            elif (a, b) == ('A', 'I'):
                points = [(x,y-20), (x,149), (tx,149), (tx,ty+20)]
            else:
                points = [(x,y-20), (tx,ty+20)]
            path = c.beginPath()
            path.moveTo(*points[0])
            for point in points[1:]:
                path.lineTo(*point)
            c.drawPath(path)
            px, py = points[-2]
            ex, ey = points[-1]
            import math
            angle = math.atan2(ey-py, ex-px)
            for offset in (-.45, .45):
                c.line(ex,ey,ex-5*math.cos(angle+offset),ey-5*math.sin(angle+offset))
        style = ParagraphStyle('Node', parent=CELL, alignment=TA_CENTER, leading=12)
        for key, label in self.nodes.items():
            x, y, width = self.positions[key]
            c.setFillColor(BLUE)
            c.roundRect(x-width/2,y-20,width,40,5,stroke=1,fill=1)
            p = Paragraph(inline(label), style)
            _, height = p.wrap(width-10,36)
            if height > 36:
                raise ValueError(f'Diagram label does not fit: {key}')
            p.drawOn(c,x-width/2+5,y-height/2)
        c.restoreState()


class Report(BaseDocTemplate):
    def __init__(self, output: Path):
        super().__init__(str(output), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=MARGIN, bottomMargin=MARGIN,
                         title='CS3263 Group 23 - Development draft', author='CS3263 Group 23')
        self.phase = 'Title'
        self.phase_pages = []
        frame = Frame(MARGIN,100,WIDTH,PAGE_H-202,leftPadding=0,rightPadding=0,
                      topPadding=0,bottomPadding=0,id='single-column')
        self.addPageTemplates(PageTemplate(id='Report',frames=frame,onPage=self.footer))

    def footer(self, canvas, doc):
        canvas.setFillColor(MUTED)
        canvas.setFont('Times-Roman',11)
        canvas.drawString(MARGIN,PAGE_H-82,'CS3263 Group 23 | DEVELOPMENT DRAFT')
        canvas.drawRightString(PAGE_W-MARGIN,78,str(doc.page))

    def afterFlowable(self, flowable):
        if getattr(flowable,'report_phase',None):
            self.phase = flowable.report_phase
        if not self.phase_pages or self.phase_pages[-1][0] != self.page:
            self.phase_pages.append((self.page,self.phase))
        elif getattr(flowable,'report_phase',None):
            self.phase_pages[-1] = (self.page,self.phase)


def table(lines: list[str]):
    rows = [[cell.strip() for cell in line.strip().strip('|').split('|')] for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r':?-+:?',x) for x in row)]
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise ValueError('Unequal table columns')
    if columns == 2:
        widths = [WIDTH*.28, WIDTH*.72]
    elif columns == 3:
        widths = [WIDTH*.54,WIDTH*.23,WIDTH*.23]
    elif columns == 7:
        widths = [WIDTH*.16]+[WIDTH*.14]*6
    else:
        widths = [WIDTH/columns]*columns
    cells = [[Paragraph(('<b>'+inline(x)+'</b>') if i==0 else inline(x),CELL)
              for x in row] for i,row in enumerate(rows)]
    result = Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),.7,MUTED),('LINEBELOW',(0,-1),(-1,-1),.5,MUTED),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    return result


def render(source: Path, output: Path):
    lines = source.read_text().splitlines()
    story = []
    i = 0
    phase = 'Title'
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('# '):
            story.extend([Spacer(1,100),Paragraph(inline(line[2:]),TITLE)])
            i += 1
            continue
        if line.startswith('## '):
            label = line[3:]
            if phase == 'Title' or label.startswith('References'):
                phase = 'References' if label.startswith('References') else 'Body'
                story.append(PageBreak())
                heading = Paragraph(inline(label),HEAD)
                heading.report_phase = phase
            else:
                heading = Paragraph(inline(label),HEAD)
            story.append(heading)
            i += 1
            continue
        if line.startswith('```'):
            kind = line[3:]
            end = i+1
            while end < len(lines) and not lines[end].startswith('```'):
                end += 1
            if end == len(lines):
                raise ValueError('Unclosed fence')
            if kind == 'mermaid':
                story.append(Architecture(lines[i+1:end]))
                story.append(Spacer(1,8))
            elif kind == 'text':
                for item in lines[i+1:end]:
                    story.append(Paragraph(escape(item.translate(NORMALIZE)),CODE))
            else:
                raise ValueError(f'Unsupported fence: {kind}')
            i = end+1
            continue
        if line.startswith('|'):
            end = i
            while end < len(lines) and lines[end].startswith('|'):
                end += 1
            story.extend([table(lines[i:end]),Spacer(1,8)])
            i = end
            continue
        if re.match(r'^\d+\. ', line):
            story.append(Paragraph(inline(line),BODY))
            i += 1
            continue
        end = i+1
        while end < len(lines) and lines[end].strip() and not lines[end].startswith(('#','```','|')) and not re.match(r'^\d+\. ', lines[end]):
            end += 1
        text = ' '.join(lines[i:end])
        story.append(Paragraph(inline(text),CENTER if phase=='Title' else BODY))
        i = end
    output.parent.mkdir(parents=True,exist_ok=True)
    document = Report(output)
    document.build(story)
    for page, phase in document.phase_pages:
        print(f'page {page}: {phase}')
    print(f'output: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'report/study-draft.md')
    parser.add_argument('--output',type=Path,default=ROOT/'output/pdf/study-draft.pdf')
    args = parser.parse_args()
    render(args.source,args.output)
