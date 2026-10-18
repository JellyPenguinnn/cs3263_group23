#!/usr/bin/env python3
"""Render the canonical Markdown report with ReportLab and Matplotlib MathText.

Run from any directory: python scripts/render_report.py [--source PATH] [--output PATH]
This deliberately supports the Markdown subset used by this report and fails on
unknown code fences/diagram structure. It does not change report content or claim
final submission readiness. PDF QA uses pdfplumber/pypdf and rendered page review.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from html import escape
import math
from pathlib import Path
import re

from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import MathTextParser
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, Image, KeepTogether,
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
    text = re.sub(r'&lt;br\s*/?&gt;', '<br/>', text)
    for index, (label, target) in enumerate(links):
        text = text.replace(f'@@LINK{index}@@',
                            f'<link href="{escape(target, quote=True)}" color="#1C5D7E">{escape(label)}</link>')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    # Courier at the same 11-point size; long IDs are allowed to wrap.
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)


BODY = ParagraphStyle('Body', fontName='Times-Roman', fontSize=11, leading=12.5,
                      textColor=INK, spaceAfter=6, splitLongWords=True, allowWidows=0, allowOrphans=0)
CELL = ParagraphStyle('Cell', parent=BODY, spaceAfter=0)
HEAD = ParagraphStyle('Heading', parent=BODY, fontName='Times-Bold', fontSize=13,
                      leading=15, spaceBefore=10, spaceAfter=7, keepWithNext=True)
TITLE = ParagraphStyle('Title', parent=HEAD, fontSize=23, leading=27,
                       alignment=TA_CENTER, spaceAfter=22)
CENTER = ParagraphStyle('Center', parent=BODY, alignment=TA_CENTER, spaceAfter=12)
CODE = ParagraphStyle('Equation', parent=BODY, fontName='Courier', leading=13,
                      leftIndent=8, rightIndent=8)
CAPTION = ParagraphStyle('TableCaption', parent=BODY, keepWithNext=True)


def math_layout(expression: str):
    # A 16-point base keeps MathText's 70% subscripts above the 11-point minimum.
    return MathTextParser('path').parse(
        f'${expression}$', dpi=72, prop=FontProperties(size=16, math_fontfamily='stix'))


class Equation(Flowable):
    """Draw parsed TeX as selectable vector glyphs, without a TeX installation."""
    def __init__(self, expression: str):
        super().__init__()
        self.layout = math_layout(expression)
        self.width, self.height = WIDTH, float(self.layout.height)+10
        if self.layout.width > WIDTH or min(g[1] for g in self.layout.glyphs) < 11:
            raise ValueError('Equation exceeds the report width or minimum font size')

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(INK)
        c.translate((WIDTH-self.layout.width)/2, self.layout.depth+5)
        for font, size, codepoint, x, y in self.layout.glyphs:
            name = 'Math-'+Path(font.fname).stem
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, font.fname))
            c.setFont(name, size)
            c.drawString(x, y, chr(codepoint))
        for x, y, width, height in self.layout.rects:
            c.rect(x, y, width, height, fill=1, stroke=0)
        c.restoreState()


class MermaidFigure(Flowable):
    """Place the checked Mermaid-produced vector PDF without redrawing its layout."""
    def __init__(self, source: list[str], placements: list):
        from pypdf import PdfReader
        super().__init__()
        directory = ROOT / 'docs/figures/report-compact-20261018'
        self.path = directory / 'architecture.pdf'
        receipt = json.loads((directory / 'architecture-receipt.json').read_text())
        raw = ('\n'.join(source).strip()+'\n').encode()
        if hashlib.sha256(raw).hexdigest() != receipt['mermaid_source_sha256']:
            raise ValueError('Mermaid source changed: regenerate the diagram and receipt')
        if hashlib.sha256(self.path.read_bytes()).hexdigest() != receipt['pdf_sha256']:
            raise ValueError('Mermaid PDF does not match its rendering receipt')
        page = PdfReader(self.path).pages[0]
        self.width = 340
        self.height = float(page.mediabox.height)*self.width/float(page.mediabox.width)
        self.placements = placements
        self.hAlign = 'CENTER'

    def draw(self):
        x, y = self.canv.absolutePosition(0, 0)
        self.placements.append((self.canv.getPageNumber()-1, x, y, self.width, self.path))


def overlay_mermaid(output: Path, placements: list):
    """Merge vector artwork after pagination; retain selectable text and arrows."""
    from pypdf import PdfReader, PdfWriter, Transformation
    if not placements:
        return
    document = PdfReader(io.BytesIO(output.read_bytes()))
    writer = PdfWriter()
    writer.clone_document_from_reader(document)
    for page_number, x, y, width, asset in placements:
        page = PdfReader(asset).pages[0]
        scale = width/float(page.mediabox.width)
        writer.pages[page_number].merge_transformed_page(
            page, Transformation().scale(scale).translate(x, y))
    with output.open('wb') as stream:
        writer.write(stream)


class Architecture(Flowable):
    """Draw the source diagram's exact nodes/edges using a fixed readable layout."""
    def __init__(self, source: list[str]):
        super().__init__()
        self.width, self.height = WIDTH, 440
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
            'G': (225, 413, 190), 'R': (225, 359, 190), 'V': (225, 305, 210),
            'A': (108, 251, 192), 'B': (343, 251, 192), 'S': (343, 197, 190),
            'O': (91, 89, 150), 'I': (274, 143, 190),
            'E': (274, 89, 190), 'D': (274, 35, 270),
        }

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(INK)
        c.setFillColor(INK)
        c.setLineWidth(1.25)
        half_height, tip_gap = 18, 3
        for a, b in self.edges:
            x, y, w = self.positions[a]
            tx, ty, tw = self.positions[b]
            if (a, b) == ('G', 'O'):
                points = [(x-w/2,y), (5,y), (5,ty), (tx-tw/2-tip_gap,ty)]
            elif (a, b) == ('G', 'I'):
                points = [(x+w/2,y), (WIDTH-5,y), (WIDTH-5,ty), (tx+tw/2+tip_gap,ty)]
            elif (a, b) == ('O', 'E'):
                points = [(x+w/2,y), (tx-tw/2-tip_gap,ty)]
            elif (a, b) == ('A', 'I'):
                # Separate input ports keep the direct and solver arrows distinct.
                points = [(x,y-half_height), (x,ty), (tx-tw/2-tip_gap,ty)]
            elif (a, b) == ('S', 'I'):
                points = [(x,y-half_height), (x,ty+half_height+tip_gap)]
            else:
                points = [(x,y-half_height), (tx,ty+half_height+tip_gap)]
            path = c.beginPath()
            path.moveTo(*points[0])
            for point in points[1:]:
                path.lineTo(*point)
            c.drawPath(path)
            px, py = points[-2]
            ex, ey = points[-1]
            angle = math.atan2(ey-py, ex-px)
            # Filled heads and a small box clearance remain visible at print size.
            ux, uy = math.cos(angle), math.sin(angle)
            bx, by = ex-6.5*ux, ey-6.5*uy
            head = c.beginPath()
            head.moveTo(ex, ey)
            head.lineTo(bx-3.2*uy, by+3.2*ux)
            head.lineTo(bx+3.2*uy, by-3.2*ux)
            head.close()
            c.drawPath(head, stroke=0, fill=1)
        style = ParagraphStyle('Node', parent=CELL, alignment=TA_CENTER, leading=12)
        for key, label in self.nodes.items():
            x, y, width = self.positions[key]
            c.setStrokeColor(MUTED)
            c.setLineWidth(.8)
            c.setFillColor(BLUE)
            c.roundRect(x-width/2,y-half_height,width,2*half_height,5,stroke=1,fill=1)
            label = '<br/>'.join(inline(part) for part in re.split(r'<br\s*/?>', label))
            p = Paragraph(label, style)
            _, height = p.wrap(width-10,30)
            if height > 30:
                raise ValueError(f'Diagram label does not fit: {key}')
            p.drawOn(c,x-width/2+5,y-height/2)
        c.restoreState()


class Report(BaseDocTemplate):
    def __init__(self, output: Path):
        super().__init__(str(output), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=MARGIN, bottomMargin=MARGIN,
                         title='CS3263 Group 23 - Scheduling study', author='CS3263 Group 23')
        self.phase = 'Title'
        self.phase_pages = []
        frame = Frame(MARGIN,100,WIDTH,PAGE_H-202,leftPadding=0,rightPadding=0,
                      topPadding=0,bottomPadding=0,id='single-column')
        self.addPageTemplates(PageTemplate(id='Report',frames=frame,onPage=self.footer))

    def footer(self, canvas, doc):
        canvas.setFillColor(MUTED)
        canvas.setFont('Times-Roman',11)
        if doc.page > 1:
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
        ratios = (.20, .43, .37) if rows[0][0] == 'Model' else (.54, .23, .23)
        widths = [WIDTH*r for r in ratios]
    elif columns == 7:
        widths = [WIDTH*.16]+[WIDTH*.14]*6
    elif columns == 5:
        widths = [WIDTH*.28]+[WIDTH*.18]*4
    elif columns == 4 and rows[0][1] == 'Method':
        ratios = (.23,.23,.26,.28) if rows[0][0] == 'Model / task' else (.18,.26,.26,.30)
        widths = [WIDTH*ratio for ratio in ratios]
    else:
        widths = [WIDTH/columns]*columns
    method_table = columns == 4 and rows[0][1] == 'Method'
    metric_alignment = TA_CENTER if rows[0][0] == 'Model / task' else TA_RIGHT
    metric = ParagraphStyle('Metric', parent=CELL, alignment=metric_alignment)
    cells = [[Paragraph(('<b>'+inline(x)+'</b>') if i==0 else inline(x),
                        metric if method_table and j>=2 else CELL)
              for j,x in enumerate(row)] for i,row in enumerate(rows)]
    result = Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),.7,MUTED),('LINEBELOW',(0,-1),(-1,-1),.5,MUTED),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    if method_table:
        start, group = 1, 0
        while start < len(rows):
            end = start
            while end+1 < len(rows) and rows[end+1][0] == rows[start][0]:
                end += 1
            if end > start:
                result.setStyle(TableStyle([('SPAN',(0,start),(0,end)),
                                           ('VALIGN',(0,start),(0,end),'MIDDLE')]))
            if group % 2 == 0:
                result.setStyle(TableStyle([('BACKGROUND',(0,start),(-1,end),
                                            colors.HexColor('#F5F7FA'))]))
            result.setStyle(TableStyle([('LINEBELOW',(0,end),(-1,end),.4,MUTED)]))
            start, group = end+1, group+1
    return result


def cover_page(lines: list[str]):
    """Lay out the report title fields; keep private member details in the source."""
    blocks = re.split(r'\n\s*\n', '\n'.join(lines).strip())
    if (len(blocks) != 8 or not blocks[0].startswith('# ')
            or blocks[3] != 'PROJECT REPORT'):
        raise ValueError('Expected title, school, course, report label, subtitle, group, member heading and members')
    title, school, course, label, subtitle, group, member_heading, members = blocks
    styles = {
        'school': ParagraphStyle('CoverSchool', parent=CENTER, fontName='Helvetica-Bold', fontSize=15, leading=18, spaceAfter=12),
        'course': ParagraphStyle('CoverCourse', parent=CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14, spaceAfter=0),
        'label': ParagraphStyle('CoverLabel', parent=CENTER, fontName='Helvetica-Bold', fontSize=13, leading=16, spaceAfter=14),
        'title': ParagraphStyle('CoverTitle', parent=CENTER, fontName='Helvetica-Bold', fontSize=20, leading=24, spaceAfter=18),
        'subtitle': ParagraphStyle('CoverSubtitle', parent=CENTER, fontName='Helvetica-Oblique', fontSize=11, leading=15, spaceAfter=0),
        'group': ParagraphStyle('CoverGroup', parent=CENTER, fontName='Helvetica-Bold', fontSize=14, leading=18, spaceAfter=10),
        'members': ParagraphStyle('CoverMembers', parent=CENTER, fontName='Helvetica', fontSize=11, leading=17, spaceAfter=0),
    }
    logo = Image(str(ROOT/'docs/figures/nus-logo.png'))
    logo.drawHeight *= 340/logo.drawWidth
    logo.drawWidth = 340
    logo.hAlign = 'CENTER'
    return [logo, Spacer(1, 8), Paragraph(inline(school), styles['school']),
            Paragraph(inline(course), styles['course']), Spacer(1, 45),
            Paragraph(inline(label), styles['label']),
            Paragraph(inline(title[2:]), styles['title']),
            Paragraph(inline(subtitle), styles['subtitle']), Spacer(1, 45),
            Paragraph(inline(group), styles['group']),
            Paragraph(inline(member_heading), styles['members']), Spacer(1, 6),
            Paragraph(inline(members), styles['members'])]


def render(source: Path, output: Path):
    lines = source.read_text().splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith('## '))
    story = cover_page(lines[:i])
    phase = 'Title'
    mermaid_placements = []
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
                story.append(MermaidFigure(lines[i+1:end], mermaid_placements)
                             if lines[i+1].strip() == 'flowchart TD'
                             else Architecture(lines[i+1:end]))
                story.append(Spacer(1,8))
            elif kind == 'text':
                for item in lines[i+1:end]:
                    story.append(Paragraph(escape(item.translate(NORMALIZE)),CODE))
            elif kind == 'math':
                story.append(Equation(' '.join(lines[i+1:end])))
            else:
                raise ValueError(f'Unsupported fence: {kind}')
            i = end+1
            continue
        image_match = re.fullmatch(r'!\[([^\]]+)\]\(([^)]+)\)', line)
        if image_match:
            caption, target = image_match.groups()
            image_path = (source.parent/target).resolve()
            if not image_path.is_file():
                raise ValueError(f'Missing report figure: {target}')
            figure = Image(str(image_path))
            figure.drawHeight *= WIDTH/figure.drawWidth
            figure.drawWidth = WIDTH
            story.append(KeepTogether([figure, Paragraph(inline(caption), BODY), Spacer(1, 5)]))
            i += 1
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
        while end < len(lines) and lines[end].strip() and not lines[end].startswith(('#','```','|','![')) and not re.match(r'^\d+\. ', lines[end]):
            end += 1
        text = ' '.join(lines[i:end])
        style = CENTER if phase=='Title' else CAPTION if text.startswith(('**Table ', '**Worked example:')) else BODY
        story.append(Paragraph(inline(text),style))
        i = end
    output.parent.mkdir(parents=True,exist_ok=True)
    document = Report(output)
    document.build(story)
    overlay_mermaid(output, mermaid_placements)
    for page, phase in document.phase_pages:
        print(f'page {page}: {phase}')
    print(f'output: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'docs/submission-report.md')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/submission-report.pdf')
    args = parser.parse_args()
    render(args.source,args.output)
