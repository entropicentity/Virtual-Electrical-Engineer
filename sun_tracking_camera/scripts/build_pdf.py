
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

base = Path('/workspace/sun_tracking_camera')
out = base / 'outputs'
pdf_path = out / 'sun_tracking_camera_package.pdf'

summary = (out / 'circuit_summary.md').read_text()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8, leading=10))
styles.add(ParagraphStyle(name='TightHeading', parent=styles['Heading2'], spaceAfter=6, spaceBefore=10))

story = []
story.append(Paragraph('Sun-Tracking Camera Design Package', styles['Title']))
story.append(Spacer(1, 0.15*inch))
story.append(Paragraph('Prototype ESP32-CAM + four-LDR sun sensor + dual-servo pan/tilt concept powered from a 5 V adapter.', styles['BodyText']))
story.append(Spacer(1, 0.2*inch))

sections = []
current_title = None
current_lines = []
for line in summary.splitlines():
    if line.startswith('## '):
        if current_title is not None:
            sections.append((current_title, '\n'.join(current_lines).strip()))
        current_title = line[3:].strip()
        current_lines = []
    elif line.startswith('### '):
        current_lines.append(f'<b>{line[4:].strip()}</b>')
    elif line.startswith('- '):
        current_lines.append('&bull; ' + line[2:].strip())
    elif line:
        current_lines.append(line)
    else:
        current_lines.append('')
if current_title is not None:
    sections.append((current_title, '\n'.join(current_lines).strip()))

for title, body in sections:
    story.append(Paragraph(title, styles['TightHeading']))
    for para in body.split('\n\n'):
        para = para.strip()
        if para:
            story.append(Paragraph(para.replace('\n', '<br/>'), styles['BodyText']))
            story.append(Spacer(1, 0.08*inch))

story.append(PageBreak())
story.append(Paragraph('Schematic / Wiring Overview', styles['Heading1']))
story.append(Spacer(1, 0.1*inch))
img = Image(str(out/'sun_tracking_camera_schematic.png'))
img.drawHeight = 6.5*inch
img.drawWidth = 7.5*inch
story.append(img)
story.append(Spacer(1, 0.15*inch))
story.append(Paragraph('Note: ADC pin labels in the diagram are conceptual placeholders for accessible analog inputs on the chosen carrier/backplane. A bare ESP32-CAM may need an external ADC or a more capable breakout.', styles['Small']))

story.append(PageBreak())
story.append(Paragraph('Bill of Materials', styles['Heading1']))
story.append(Spacer(1, 0.1*inch))

df = pd.read_csv(out/'bom.csv')
cols = ['Item','RefDes','Qty','Description','Recommended MPN','Supplier','Purchase URL']
table_data = [cols]
for _, row in df[cols].iterrows():
    table_data.append([
        str(row['Item']), str(row['RefDes']), str(row['Qty']),
        Paragraph(str(row['Description']), styles['Small']),
        Paragraph(str(row['Recommended MPN']), styles['Small']),
        Paragraph(str(row['Supplier']), styles['Small']),
        Paragraph(f'<link href="{row["Purchase URL"]}">link</link>', styles['Small'])
    ])

table = Table(table_data, repeatRows=1, colWidths=[0.4*inch,0.8*inch,0.4*inch,2.0*inch,1.3*inch,1.0*inch,1.1*inch])
table.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#1f4e79')),
    ('TEXTCOLOR',(0,0),(-1,0), colors.white),
    ('GRID',(0,0),(-1,-1),0.4, colors.grey),
    ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('FONTSIZE',(0,0),(-1,-1),8),
    ('LEADING',(0,0),(-1,-1),10),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke, colors.lightgrey])
]))
story.append(table)
story.append(Spacer(1, 0.15*inch))
story.append(Paragraph('Disclaimer: This package is suitable for prototyping and concept communication. Mechanical loading, thermal behavior, outdoor survivability, EMC, and long-term power integrity are not validated here.', styles['Small']))

doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
doc.build(story)
print(pdf_path)
