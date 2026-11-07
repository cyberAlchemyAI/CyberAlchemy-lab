#!/usr/bin/env python3
"""Author the PDF and Word rules from maintained structured text and event config.

Requires python-docx and reportlab (available in the bundled workspace runtime).
The ordinary static-site build validates the published bytes without these deps.
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import hashlib,json,re,zipfile
from html import escape
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'source/governance-lab-series/downloads'
source=ROOT/'hackathon-rules.json';config=json.loads((ROOT/'hackathon.json').read_text());data=json.loads(source.read_text(encoding='utf-8'))
RULE_KEYS=['year','timezone','registration_opens_at','registration_closes_at','build_opens_at','submissions_close_at','voting_opens_at','voting_closes_at','provisional_results_at','report_deadline_at','selection_ends_at','minimum_age','data_retention_days','prize_delivery','organizer_name','contact_email','rules_version','rules_updated','categories']
projection={k:config[k] for k in RULE_KEYS};projection_bytes=json.dumps(projection,sort_keys=True,ensure_ascii=True).encode()
labels={'RULES_VERSION':config['rules_version'],'RULES_UPDATED':datetime.fromisoformat(config['rules_updated']).strftime('%B %d, %Y').replace(' 0',' '),'EVENT_YEAR':str(config['year']),'MINIMUM_AGE':str(config['minimum_age'])}
for label,key in [('REGISTRATION_OPEN','registration_opens_at'),('REGISTRATION_CLOSE','registration_closes_at'),('BUILD_OPEN','build_opens_at'),('SUBMISSION_CLOSE','submissions_close_at'),('VOTING_OPEN','voting_opens_at'),('VOTING_CLOSE','voting_closes_at'),('RESULTS','provisional_results_at'),('REPORT','report_deadline_at'),('FINAL','selection_ends_at')]:
 d=datetime.fromisoformat(config[key]);labels[label]=d.strftime('%B')+f' {d.day}, {d.year} at '+d.strftime('%H:%M:%S' if d.second else '%H:%M')
blocks=[]
for b in data['blocks']:
 text=b['text']
 for key,value in labels.items():text=text.replace('{{'+key+'}}',value)
 assert '{{' not in text,text
 blocks.append({**b,'text':text})
assert data['version']==config['rules_version']
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
font=next(p for p in [Path('C:/Windows/Fonts/consola.ttf'),Path('/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf')] if p.is_file());pdfmetrics.registerFont(TTFont('RulesMono',str(font)))
doc=Document();section=doc.sections[0];section.top_margin=section.bottom_margin=Inches(.7);section.left_margin=section.right_margin=Inches(.75)
for name in ['Normal','Title','Heading 1']:
 doc.styles[name].font.name='Consolas';doc.styles[name].font.color.rgb=RGBColor.from_string('241F20')
doc.styles['Normal'].font.size=Pt(10.5);doc.styles['Normal'].paragraph_format.space_after=Pt(7)
doc.styles['Title'].font.size=Pt(24);doc.styles['Heading 1'].font.size=Pt(15);doc.styles['Heading 1'].font.color.rgb=RGBColor.from_string('B31535')
for b in blocks:doc.add_paragraph(b['text'],style='Title' if b['style']=='Title' else 'Heading 1' if b['style'].startswith('Heading') else 'Normal')
doc.core_properties.title='CyberAlchemy Lab x Craft Hackathon — full rules v'+config['rules_version'];stamp=datetime.fromisoformat(config['calendar_revision_at']).replace(tzinfo=None);doc.core_properties.created=doc.core_properties.modified=stamp
buffer=BytesIO();doc.save(buffer)
# Normalize archive metadata, preserving reproducibility for a fixed source/config.
with zipfile.ZipFile(buffer) as original,zipfile.ZipFile(OUT/'hackathon-rules.docx','w',zipfile.ZIP_DEFLATED) as target:
 for name in original.namelist():
  info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;target.writestr(info,original.read(name))
styles={'Title':ParagraphStyle('Title',fontName='RulesMono',fontSize=23,leading=29,textColor=HexColor('#b31535'),spaceAfter=20),'Heading':ParagraphStyle('Heading',fontName='RulesMono',fontSize=14,leading=19,textColor=HexColor('#b31535'),spaceBefore=15,spaceAfter=8,keepWithNext=True),'Normal':ParagraphStyle('Normal',fontName='RulesMono',fontSize=10.5,leading=15,textColor=HexColor('#241f20'),spaceAfter=8)}
story=[Paragraph(escape(b['text']),styles['Title' if b['style']=='Title' else 'Heading' if b['style'].startswith('Heading') else 'Normal']) for b in blocks]
def footer(canvas,document):
 canvas.saveState();canvas.setFont('RulesMono',8);canvas.setFillColor(HexColor('#6c5a59'));canvas.drawString(48,24,'CyberAlchemy Lab | Rules v'+config['rules_version']);canvas.drawRightString(A4[0]-48,24,str(document.page));canvas.restoreState()
SimpleDocTemplate(str(OUT/'hackathon-rules.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=44,title=doc.core_properties.title,author='CyberAlchemy Lab').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=lambda *a,**kw:Canvas(*a,**(kw | {"invariant":1})))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'version':config['rules_version'],'updated':config['rules_updated'],'source_sha256':sha(source),'config_keys':RULE_KEYS,'config_sha256':hashlib.sha256(projection_bytes).hexdigest(),'paragraphs':len(blocks),'files':{n:sha(OUT/n) for n in ['hackathon-rules.pdf','hackathon-rules.docx']}}
(OUT/'hackathon-rules-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest))
