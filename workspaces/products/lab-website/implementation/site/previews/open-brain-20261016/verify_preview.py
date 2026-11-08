"""Read-only integrity and internal route checks for this isolated preview."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,hashlib,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SITE=HERE/'site'
DIST=ROOT/'website/dist'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if d.get('id'):self.ids.append(d['id'])
  if tag=='a' and d.get('href'):self.links.append(d['href'])
  if tag in ('img','script') and d.get('src'):self.images.append(d['src'])
  if tag=='link' and d.get('href'):self.images.append(d['href'])
def parsed(path):
 p=Page();p.feed(path.read_text());return p
pages={p:parsed(p) for p in SITE.rglob('*.html')}
links=[];assets=[]
for path,p in pages.items():
 for typ,refs in [('link',p.links),('asset',p.images)]:
  for ref in refs:
   url=urlsplit(ref)
   if url.scheme or url.netloc or not url.path and not url.fragment:continue
   target=(SITE/unquote(url.path.lstrip('/'))) if url.path.startswith('/') else (path.parent/unquote(url.path)).resolve() if url.path else path
   if target.is_dir():target=target/'index.html'
   reason=None
   if not target.exists():reason='missing file'
   elif typ=='link' and url.fragment and target.suffix=='.html' and unquote(url.fragment) not in pages.get(target,Page()).ids:reason='missing fragment'
   if reason:(links if typ=='link' else assets).append({'page':str(path.relative_to(SITE)),'ref':ref,'reason':reason})
# Compare original files with corresponding preview, including anchor preservation.
missing_routes=[];missing_anchors=[]
for old in DIST.rglob('*'):
 if not old.is_file():continue
 relative=old.relative_to(DIST);new=SITE/relative
 if not new.exists():missing_routes.append(str(relative));continue
 if old.suffix=='.html' and str(relative) in json.loads((HERE/'build.json').read_text())['new_or_recomposed_pages']:
  before=parsed(old);after=pages[new]
  missing=set(before.ids)-set(after.ids)
  if missing:missing_anchors.append({'page':str(relative),'anchors':sorted(missing)})
baseline=json.loads((HERE/'baseline.json').read_text())
changed=[name for name,h in baseline.items() if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h]
built=json.loads((HERE/'build.json').read_text())['new_or_recomposed_pages']
duplicates=[{'page':name,'ids':[i for i,c in Counter(pages[SITE/name].ids).items() if c>1]} for name in built]
duplicates=[x for x in duplicates if x['ids']]
# Exact reference/runtime pages: only the local navigation ribbon and noindex metadata were inserted.
retained=[*DIST.glob('governance-lab-series/reference/*.html'),*DIST.glob('governance-lab-series/runtime-*.html')]
retained_mismatch=[]
for old in retained:
 new=(SITE/old.relative_to(DIST)).read_text()
 new=re.sub(r'<div class="local-preview-ribbon"[^>]*>.*?</div>','',new,count=1,flags=re.S)
 # Additive preview styles can follow the noindex metadata in the head.
 new=re.sub(r'<link data-preview-polish[^>]*>','',new)
 new=new.replace('<meta name="robots" content="noindex,nofollow"></head>','</head>',1)
 new=new.replace(' data-local-preview="polished"','',1)
 new=re.sub(r'(?:\?|&(?:amp;)?)preview_asset=[0-9a-f]{12}','',new)
 new=re.sub(r'<script data-preview-polish[^>]*></script>','',new)
 new=re.sub(r'<!--preview-runtime-diagram:start-->.*?<!--preview-runtime-diagram:end-->','',new,flags=re.S)
 new=re.sub(r'<details data-preview-diagram-source><summary>Read diagram source</summary>(<pre>.*?</pre>)</details>',r'\1',new,flags=re.S)
 if new!=old.read_text():retained_mismatch.append(str(old.relative_to(DIST)))
report={'html_pages':len(pages),'maintained_files_hashed':len(baseline),'maintained_files_changed':changed,'missing_original_routes':missing_routes,'missing_original_anchors':missing_anchors,'duplicate_ids_in_new_pages':duplicates,'link_issues':links,'asset_issues':assets,'exact_reference_runtime_pages':len(retained),'retained_mismatches':retained_mismatch}
(HERE/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()},indent=2))
