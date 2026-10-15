from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import json,hashlib,sys,gzip,base64,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;SITE=ROOT/'website/dist';checked=[];broken=[];duplicates=[]
class Refs(HTMLParser):
 def __init__(self,page):super().__init__();self.page=page;self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  for key in ['href','src','data']:
   if key not in a:continue
   u=urlsplit(a[key])
   if u.scheme or u.netloc or not u.path:continue
   dest=(self.page.parent/unquote(u.path)).resolve();checked.append(a[key])
   if not dest.is_file() or not dest.is_relative_to(SITE):broken.append({'page':str(self.page.relative_to(SITE)),'url':a[key]})
for p in SITE.rglob('*.html'):
 parser=Refs(p);parser.feed(p.read_text());duplicate={i for i in parser.ids if parser.ids.count(i)>1}
 if duplicate:duplicates.append({'page':str(p.relative_to(SITE)),'duplicates':sorted(duplicate)})
assert not broken,broken[:10];assert not duplicates,duplicates[:10]
lab=SITE/'governance-lab-series';receipt=json.loads((lab/'research/site-search-index.json').read_text())
for n,var,delivery in [('site-search-index','LabSiteSearchIndex',receipt['delivery']),('site-search-quick','LabSiteSearchQuick',receipt['quick_delivery'])]:
 s=(lab/'assets'/(n+'.js')).read_text();packed=json.loads(re.search(r'atob\(("[^"]+")\)',s)[1]);data=gzip.decompress(base64.b64decode(packed));literal=json.JSONDecoder().raw_decode((lab/'assets'/delivery['fallback']).read_text().split('window.'+var+'=',1)[1])[0];assert json.loads(data)==literal
 assert hashlib.sha256(data).hexdigest()==delivery['payload_sha256'];assert hashlib.sha256((lab/'assets'/delivery['fallback']).read_bytes()).hexdigest()==delivery['fallback_sha256']
for name,digest in receipt['source_html_sha256'].items():assert hashlib.sha256((lab/name).read_bytes()).hexdigest()==digest,name
result={'html_pages':len(list(SITE.rglob('*.html'))),'local_references':len(checked),'broken':broken,'duplicate_ids':duplicates,'search_entries':receipt['entries'],'compressed_plain_payloads_identical':True,'search_source_fingerprints_match':True,'deployment_performed':False}
(OUT/'integrity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
