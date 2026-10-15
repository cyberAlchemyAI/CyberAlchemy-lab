"""Owned documentation integrity checks; no Lab/native/runtime imports."""
from pathlib import Path
import ast,hashlib,html,json,os,re,sys
from urllib.parse import unquote,urlsplit
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
PROTO=HERE/'prototype';LAB=PROTO/'website/source/governance-lab-series';SITE=PROTO/'website/dist/governance-lab-series'
sys.path.insert(0,str(LAB))
from build_site_search import Document
from runtime.body import Renderer
from markdown_it import MarkdownIt
sha=lambda b:hashlib.sha256(b).hexdigest()
count=0
parsed_documents={}
def target_document(path):
 raw=path.read_bytes();key=(str(path),sha(raw))
 if key not in parsed_documents:parsed_documents[key]=Document(raw.decode())
 return parsed_documents[key]

def check(ok,msg):
 global count
 count+=1
 if not ok:raise AssertionError(msg)

baseline=json.loads((HERE/'baseline-selection.json').read_text())
for row in baseline['explicit_website_scope']:
 check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Shared website input changed: '+row['path'])
for pair in baseline['original_target_preimages']:
 for row in pair.values():check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Exact preimage changed: '+row['path'])
indices=json.loads((HERE/'maintained-index-selection.json').read_text())
for pair in indices['original_target_preimages']:
 for name in ['original','preimage']:
  row=pair[name];check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Independent maintained index preimage')
check(not (ROOT/indices['absent_source']['path']).exists(),'Actual absent tutorial index preserved')
narrative=json.loads((LAB/'runtime/narrative.json').read_text());sources=json.loads((LAB/'runtime/source-map.json').read_text());selection=json.loads((LAB/'runtime/selection.json').read_text());peer=json.loads((LAB/'runtime/independent-review-0001.json').read_text())
check(peer['bindings']['narrative.json']==sha((LAB/'runtime/narrative.json').read_bytes()),'Narrative peer pin')
check(peer['bindings']['source-map.json']==sha((LAB/'runtime/source-map.json').read_bytes()),'Source map peer pin')
check(len(narrative['pages'])==14 and sum(len(p['sections']) for p in narrative['pages'])==67,'Complete narrative')
renderer=Renderer(narrative,sources,selection['evidence_prefix']);pages=[];html_links=0;html_anchor_findings=[]
for page in narrative['pages']:
 expected=Document(renderer.body(page,'fragment',LAB));actual=Document((SITE/page['site_file']).read_text());article=actual.root.first(lambda n:n.attrs.get('id')==page['article_id']);check(article is not None,'Selected article present')
 check(len(actual.root.all(lambda n:n.attrs.get('id')==page['article_id']))==1,'Unique article identity')
 for section in page['sections']:
  sid=page['article_id']+'-'+re.sub('[^a-z0-9]+','-',section['title'].lower()).strip('-')
  a=actual.root.first(lambda n:n.attrs.get('id')==sid);e=expected.root.first(lambda n:n.attrs.get('id')==sid)
  check(a is not None and re.findall(r'[\w]+|[^\w\s]',a.text())==re.findall(r'[\w]+|[^\w\s]',e.text()),'Preserved section body: '+sid)
  check(actual.root.first(lambda n:n.tag=='a' and n.attrs.get('href')=='#'+sid) is not None,'TOC entry '+sid)
 check([n.text() for n in article.all(lambda n:n.tag=='code')]==[n.text() for n in expected.root.all(lambda n:n.tag=='code')],'Preserved commands/diagram code')
 ids=[n.attrs['id'] for n in actual.root.all(lambda n:'id'in n.attrs)];check(len(ids)==len(set(ids)),'No duplicated ids')
 for a in actual.root.all(lambda n:n.tag in {'a','link','script','img'}):
  value=a.attrs.get('href') or a.attrs.get('src')
  if not value:continue
  split=urlsplit(value)
  if split.scheme or split.netloc:continue
  target=(SITE/page['site_file']).parent/unquote(split.path) if split.path else SITE/page['site_file']
  target=target.resolve();check(target.is_relative_to(PROTO/'website/dist') and target.is_file(),'Portable runtime resource: '+value);html_links+=1
  if split.fragment and target.suffix=='.html':
   doc=target_document(target)
   found=any(n.attrs.get('id')==split.fragment for n in doc.root.all(lambda n:'id'in n.attrs))
   if not found:html_anchor_findings.append({'page':page['site_file'],'href':value,'context':'selected-article' if a in article.all(lambda n:n.tag=='a') else 'inherited-shell'})
   if a in article.all(lambda n:n.tag=='a'):check(found,'Portable selected article anchor: '+value)
 md=PROTO/'docs/lab/runtime'/page['markdown_route'];check(md.is_file(),'Actual Markdown route '+str(md))
 markdown=md.read_text()
 for code in expected.root.all(lambda n:n.tag=='code'):
  check(code.text() in markdown,'Actual Markdown code parity '+page['key'])
 pages.append({'key':page['key'],'site_file':page['site_file'],'site_sha256':sha((SITE/page['site_file']).read_bytes()),'markdown_route':md.relative_to(PROTO).as_posix(),'markdown_sha256':sha(md.read_bytes())})
expected_public={}
for row in sources['source_bindings'].values():
 path=SITE/selection['evidence_prefix']/row['original_path'];check(path.is_file() and sha(path.read_bytes())==row['sha256'] and path.stat().st_size==row['size_bytes'],'Packaged exact public resource '+row['original_path']);expected_public[path.relative_to(SITE/selection['evidence_prefix']).as_posix()]=row['sha256']
actual_public={p.relative_to(SITE/selection['evidence_prefix']).as_posix():sha(p.read_bytes()) for p in (SITE/selection['evidence_prefix']).rglob('*') if p.is_file()}
check(actual_public==expected_public and len(actual_public)==74,'Public resource namespace is closed to reviewed 74 rows')
check(not (SITE/'research/sources/runtime/diagnostic-doc1').exists(),'No diagnostic old edition packaged')
md_parser=MarkdownIt();missing_md=[];local_md_links=0
for md in (PROTO/'docs/lab').rglob('*.md'):
 for token in md_parser.parse(md.read_text()):
  for child in token.children or []:
   if child.type not in {'link_open','image'}:continue
   value=child.attrGet('href' if child.type=='link_open' else 'src');split=urlsplit(value)
   if split.scheme or split.netloc or not split.path:continue
   target=(md.parent/unquote(split.path)).resolve();local_md_links+=1
   if not target.is_file():missing_md.append({'source':md.relative_to(PROTO).as_posix(),'target':value})
manifest=json.loads((PROTO/'docs/lab/IMPORT-MANIFEST.json').read_text());check(len(manifest['pages'])==507 and manifest['unresolved_links']==[],'Actual importer routes/link manifest')
for asset in manifest['assets']:check(sha((PROTO/'docs/lab'/asset['path']).read_bytes())==asset['sha256'],'Imported asset pin')
# Actual original-page and Craft body preservation through the full final pipeline.
original_site=HERE/'diagnostic-generation-0001/site';original_pages=0;original_articles=0;original_code_blocks=0;craft_pages=0
lexical=lambda text:re.findall(r'[\w]+|[^\w\s]',text)
for old in original_site.rglob('*.html'):
 relative=old.relative_to(original_site)
 if old.name.startswith('runtime-'):continue
 new=PROTO/'website/dist'/relative
 check(new.is_file(),'Original deployed page retained: '+relative.as_posix())
 a=Document(old.read_text());b=Document(new.read_text())
 aa=a.root.all(lambda n:n.tag=='article');bb=b.root.all(lambda n:n.tag=='article')
 check([lexical(n.text()) for n in aa]==[lexical(n.text()) for n in bb],'Original article meaning retained: '+relative.as_posix())
 ac=a.root.all(lambda n:n.tag=='pre');bc=b.root.all(lambda n:n.tag=='pre')
 check([n.text() for n in ac]==[n.text() for n in bc],'Original formal/code blocks retained: '+relative.as_posix())
 original_pages+=1;original_articles+=len(aa);original_code_blocks+=len(ac)
 if 'craft-documentation-proposal' in relative.parts:craft_pages+=1
check(html_anchor_findings==[],'No inherited navigation anchor findings')
# Original formal/source renderer methods preserved; only destination is adapted to explicit staging.
owner=ast.parse((ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/runtime-narrative-preparation-0001/generate.py').read_text()) if (ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/runtime-narrative-preparation-0001/generate.py').is_file() else None
result={'schema_version':'lab-T21-owned-pipeline-checks/v1','authority_effect':'none','result':'PASS-owned-runtime-website-and-import-scoped','assertions':count,'pages':pages,'html_links_checked':html_links,'html_anchor_findings':html_anchor_findings,'public_sources':len(actual_public),'markdown_local_links_checked':local_md_links,'markdown_missing_files':missing_md,'markdown_link_scope':'Explanatory routes checked separately from inert downloaded snapshots; direct-source snapshots retain original outbound fields and are not recursive bundles.','import_source_comparisons':manifest['source_comparison_counts'],'actual_repository_currentness_established':False,'original_page_preservation':{'pages':original_pages,'articles':original_articles,'pre_blocks':original_code_blocks,'craft_pages':craft_pages},'browser_review_separate':True,'full_T21_complete':False}
(HERE/'pipeline-checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['result','assertions','html_links_checked','public_sources','markdown_local_links_checked']}|{'markdown_missing_files':len(missing_md),'original_page_preservation':result['original_page_preservation']}))
