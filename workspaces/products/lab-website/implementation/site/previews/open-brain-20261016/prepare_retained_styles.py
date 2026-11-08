"""Recover scoped figure styles from unchanged, approved preview source assets."""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'site/governance-lab-series/assets'
PREFIX='.ob-preview .retained-reading '
def selectors(text):
 parts=[];start=0;depth=0
 for i,ch in enumerate(text):
  if ch in '([':depth+=1
  elif ch in ')]':depth-=1
  elif ch==',' and not depth:parts.append(text[start:i]);start=i+1
 return parts+[text[start:]]
def scoped(text,keep=lambda selector:True):
 text=re.sub(r'/\*.*?\*/','',text,flags=re.S);out=[];pos=0
 while pos<len(text):
  start=text.find('{',pos)
  if start<0:break
  heading=text[pos:start].strip();depth=1;end=start+1
  while depth and end<len(text):
   depth+=(text[end]=='{')-(text[end]=='}');end+=1
  body=text[start+1:end-1]
  if heading.startswith('@'):
   inner=scoped(body,keep)
   if inner.strip():out.append(heading+'{\n'+inner+'}\n')
  else:
   selected=[s.strip().replace('.research-site ','') for s in selectors(heading) if keep(s)]
   if selected:out.append(','.join(PREFIX+s for s in selected)+'{'+body.strip()+'}\n')
  pos=end
 return ''.join(out)
company=scoped((SOURCE/'company-brain-map.css').read_text())
map_adaptations=scoped((SOURCE/'diagram-reading.css').read_text(),lambda s:'.company-brain-map' in s)
parts=['.research-loop','.loop-steps','.loop-return','.brain-overview','.brain-context','.brain-state','.incident-strip']
research=scoped((SOURCE/'research-site.css').read_text(),lambda s:any(p in s for p in parts))
(HERE/'assets/retained-figures.css').write_text('/* Scoped restoration of approved company-brain, research and diagram-reading figure styles. */\n'+company+map_adaptations+research)
