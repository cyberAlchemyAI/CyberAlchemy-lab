from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit,unquote
import hashlib,json,sys,re,zipfile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;OLD=OUT/'baseline-dist';SITE=ROOT/'website/dist'
sys.path.insert(0,str(ROOT/'website/source/governance-lab-series'))
from build_site_search import Document,clean
oldpages=sorted(OLD.rglob('*.html'));missing=[];content=[];links=[];fragments=[]
for old in oldpages:
 name=old.relative_to(OLD);new=SITE/name
 if not new.exists():missing.append(str(name));continue
 a=Document(old.read_text());b=Document(new.read_text())
 # Preserve every original paragraph, heading, list item, definition and code.
 def prose(doc):return Counter(clean(n.text()) for n in doc.root.all(lambda n:n.tag in {'p','li','dt','dd','h1','h2','h3','h4','h5','h6','pre','figcaption'}) if clean(n.text()))
 missing_text=prose(a)-prose(b)
 if missing_text:content.append({'page':str(name),'missing':list(missing_text.items())[:10]})
 anchor=lambda d:Counter(n.attrs['href'] for n in d.root.all(lambda n:n.tag=='a' and n.attrs.get('href')))
 lost=anchor(a)-anchor(b)
 if lost:links.append({'page':str(name),'missing':list(lost.items())[:10]})
 lost_ids=set(a.ids)-set(b.ids)
 if lost_ids:fragments.append({'page':str(name),'missing':sorted(lost_ids)})
assert not missing,missing
assert not content,content[:8]
assert not links,links[:8]
assert not fragments,fragments[:8]
records=json.loads((OLD/'governance-lab-series/research/reference-pages.json').read_text())['records']
for row in records:
 name=Path('governance-lab-series')/row['href'];pattern=r'<div class="record-body">.*?</article>'
 assert re.search(pattern,(OLD/name).read_text(),re.S)[0]==re.search(pattern,(SITE/name).read_text(),re.S)[0],name
runtime=json.loads((OLD/'governance-lab-series/research/runtime-pages.json').read_text())['pages']
for row in runtime:
 name=Path('governance-lab-series')/row['site_file'];pattern=r'<article\b.*?</article>'
 assert re.search(pattern,(OLD/name).read_text(),re.S)[0]==re.search(pattern,(SITE/name).read_text(),re.S)[0],name
captured=[]
for old in (OLD/'governance-lab-series/research/sources').rglob('*'):
 if old.is_file():assert old.read_bytes()==(SITE/old.relative_to(OLD)).read_bytes(),old;captured.append(str(old.relative_to(OLD)))
manifest=json.loads((SITE/'release-manifest.json').read_text())
for row in manifest['files']:assert hashlib.sha256((SITE/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
with zipfile.ZipFile(ROOT/'website/artifacts/cyberalchemy-lab-website.zip') as z:
 assert z.testzip() is None
 for name in z.namelist():assert z.read(name)==(SITE/name).read_bytes(),name
summary={'baseline_routes_preserved':len(oldpages),'current_html_routes':len(list(SITE.rglob('*.html'))),'missing_original_prose':content,'missing_original_anchor_links':links,'missing_original_fragment_ids':fragments,'formal_reading_bodies_exact':len(records),'runtime_article_bodies_exact':len(runtime),'captured_source_files_exact':len(captured),'manifest_files_verified':len(manifest['files']),'archive_matches_dist':True}
(OUT/'preservation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
