from pathlib import Path
import json,hashlib,shutil,ast
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';HERE=RUN/'T21/website-integration-preparation-0001';HERE.mkdir();PROTO=HERE/'prototype';WEB=PROTO/'website';WEB.mkdir(parents=True)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 raw=v.encode() if isinstance(v,str) else (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 with p.open('xb') as f:f.write(raw)
# Explicit website-only read/copy; no repository/runtime tree or prior output copied.
website_rows=[]
for file in sorted((ROOT/'website').glob('*')):
 if file.is_file() and (file.suffix in {'.py','.json'}):shutil.copy2(file,WEB/file.name);website_rows.append(binding(file))
for file in sorted((ROOT/'website/source').rglob('*')):
 if not file.is_file() or '__pycache__' in file.parts or file.suffix=='.pyc':continue
 rel=file.relative_to(ROOT/'website');target=WEB/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);website_rows.append(binding(file))
targets=['website/build.py','website/site.json','website/source/governance-lab-series/render_article.py','website/source/governance-lab-series/documentation_checks.py','website/source/governance-lab-series/build_site_search.py','website/source/governance-lab-series/search_relevance.py','website/source/governance-lab-series/assets/site-search.js','website/source/governance-lab-series/templates/start-here.html.in','website/editorial-copy.json','tooling/docs/import_site_docs.py','docs/lab/MAINTENANCE.md','website/README.md','website/source/governance-lab-series/SITE-MAINTENANCE.md']
original=[]
for name in targets:
 file=ROOT/name;target=HERE/'preimages'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);original.append({'original':binding(file),'preimage':binding(target)})
write(HERE/'baseline-selection.json',{'schema_version':'lab-T21-website-stage-baseline/v1-candidate','authority_effect':'none','original_target_preimages':original,'explicit_website_scope':website_rows,'scope':'website root Python/JSON configuration and complete public source only; generated dist/artifacts/build/review/versions excluded','shared_mutation':False})
# Actual importer source stays at its true owned path. It reads HTML, never Lab modules.
(PROTO/'tooling/docs').mkdir(parents=True);shutil.copy2(ROOT/'tooling/docs/import_site_docs.py',PROTO/'tooling/docs/import_site_docs.py')
(PROTO/'docs/lab').mkdir(parents=True);shutil.copy2(ROOT/'docs/lab/MAINTENANCE.md',PROTO/'docs/lab/MAINTENANCE.md')
# Closed reviewed diagnostic source selection; future doc2 is explicitly pending.
NARR=RUN/'T21/runtime-narrative-preparation-0001';LAB=WEB/'source/governance-lab-series';RUNTIME=LAB/'runtime';RUNTIME.mkdir()
assert sha((NARR/'narrative.json').read_bytes())=='31d0aabdaa5d731b5ee3e6dbfec84ea1f34d8cfa16e3a30b0ad3d9a5c2121c3a'
assert sha((NARR/'source-map.json').read_bytes())=='b0567421784c9ec30cfb9cbe8e48a3bd98431dde04df11cc5f99bfdcaaf4e4c9'
assert sha((NARR/'independent-review-0001.json').read_bytes())=='9c80cafd2bf3e23486fccf24cd258ad23072cd9ad20c3ab4e0dae1e9a86ab716'
for name in ['narrative.json','source-map.json','independent-review-0001.json']:shutil.copy2(NARR/name,RUNTIME/name)
source_map=json.loads((NARR/'source-map.json').read_text());narrative=json.loads((NARR/'narrative.json').read_text());edition='diagnostic-doc1'
for key,row in source_map['source_bindings'].items():
 raw=(ROOT/row['snapshot_path']).read_bytes();assert sha(raw)==row['sha256'] and len(raw)==row['size_bytes']
 target=LAB/'research/sources/runtime'/edition/row['original_path'];write(target,raw.decode())
selection={'schema_version':'lab-runtime-documentation-selection/v1-candidate','authority_effect':'none','edition_id':edition,'standing':'reviewed-diagnostic-staging-ND01-final-evidence-pending','narrative_binding':{'path':'narrative.json','sha256':sha((RUNTIME/'narrative.json').read_bytes())},'source_map_binding':{'path':'source-map.json','sha256':sha((RUNTIME/'source-map.json').read_bytes())},'review_binding':{'path':'independent-review-0001.json','sha256':sha((RUNTIME/'independent-review-0001.json').read_bytes())},'expected_review_result':'PASS-scoped-static-preparation-with-ND01-evidence-selection-gap','evidence_prefix':'research/sources/runtime/'+edition+'/','page_count':14,'section_count':67,'final_publication_qualified':False}
write(RUNTIME/'selection.json',selection)
config=json.loads((WEB/'site.json').read_text());config['runtime_documentation_selection']={'path':'source/governance-lab-series/runtime/selection.json','sha256':sha((RUNTIME/'selection.json').read_bytes())};(WEB/'site.json').write_text(json.dumps(config,sort_keys=True,indent=2)+'\n')
# Retain the narrative parser/body implementation at its own real maintained origin.
generator=(NARR/'generate.py').read_text();tree=ast.parse(generator);node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Renderer')
keep={'__init__','destination','inline','blocks','diagram','body'};node.body=[n for n in node.body if isinstance(n,ast.FunctionDef) and n.name in keep]
body='"""Narrative-owned text/table/code/diagram projection; no runtime imports."""\nimport html,hashlib,re\nfrom pathlib import Path\nTOKEN = re.compile(r"\\[\\[(source|page|concept):([a-z0-9-]+)\\|([^\\]]+)\\]\\]")\ndef sha(raw):return hashlib.sha256(raw).hexdigest()\ndef slug(text):return re.sub(r"[^a-z0-9]+","-",text.lower()).strip("-")\n'+ast.unparse(node)+'\n'
start=body.index('    def destination(');end=body.index('    def inline(',start)
body=body[:start]+'''    def destination(self,kind,key,mode,page,parent):
        if mode!='fragment':raise ValueError('Site body projection requires fragment mode')
        if kind=='source':return self.output+self.source_rows[key]['original_path']
        if kind=='page':return self.pages[key]['site_file']
        filename,anchor=self.concepts[key][0].split('#',1)
        return Path(filename).name+'#'+anchor

'''+body[end:]
write(RUNTIME/'body.py',body)
write(LAB/'runtime_docs.py',r'''"""Thin maintained runtime renderer selected by explicit reviewed input hashes."""
from html import escape
import hashlib,json,math,os,re
from pathlib import Path
from build_site_search import Document
from runtime.body import Renderer

def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(base,row):
    if type(row) is not dict or set(row)!= {'path','sha256'}:raise ValueError('closed runtime documentation binding required')
    rel=Path(row['path'])
    if rel.is_absolute() or rel.as_posix()!=row['path'] or '..' in rel.parts or '\\' in row['path']:raise ValueError('canonical runtime input required')
    path=base/rel
    if not path.is_file() or path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('regular selected runtime input required')
    raw=path.read_bytes()
    if sha(raw)!=row['sha256']:raise ValueError('reviewed runtime documentation input changed')
    return raw

def selected(root):
    pin=os.environ.get('LAB_SITE_RUNTIME_SELECTION_SHA256')
    if not pin or re.fullmatch('[a-f0-9]{64}',pin) is None:raise ValueError('Explicit site.json runtime selection digest required')
    base=root/'runtime';selection=json.loads(exact(base,{'path':'selection.json','sha256':pin}))
    fields={'schema_version','authority_effect','edition_id','standing','narrative_binding','source_map_binding','review_binding','expected_review_result','evidence_prefix','page_count','section_count','final_publication_qualified'}
    if set(selection)!=fields or selection['schema_version']!='lab-runtime-documentation-selection/v1-candidate' or selection['authority_effect']!='none':raise ValueError('Closed runtime documentation selector required')
    if re.fullmatch('[a-z0-9-]+',selection['edition_id']) is None or selection['evidence_prefix']!='research/sources/runtime/'+selection['edition_id']+'/':raise ValueError('Exact isolated evidence namespace required')
    narrative=json.loads(exact(base,selection['narrative_binding']));sources=json.loads(exact(base,selection['source_map_binding']));review=json.loads(exact(base,selection['review_binding']))
    if review['result']!=selection['expected_review_result'] or not review['result'].startswith('PASS'):raise ValueError('Exact reviewed narrative edition required')
    pages=narrative['pages']
    if len(pages)!=selection['page_count']!=14 or len(pages)!=14 or sum(len(p['sections']) for p in pages)!=selection['section_count']:raise ValueError('Fourteen complete runtime pages required')
    for field in ['key','site_file','article_id','markdown_route']:
        if len({p[field] for p in pages})!=14:raise ValueError('Distinct runtime page routes required')
    for p in pages:
        if not re.fullmatch('runtime-[a-z0-9-]+.html',p['site_file']) or not re.fullmatch('runtime-[a-z0-9-]+',p['article_id']):raise ValueError('Closed actual page/article identity required')
    for row in sources['source_bindings'].values():
        path=selection['evidence_prefix']+row['original_path'];raw=exact(root,{'path':path,'sha256':row['sha256']})
        if len(raw)!=row['size_bytes']:raise ValueError('Complete selected public evidence bytes required')
    return selection,narrative,sources

def render(root):
    selection,narrative,sources=selected(root);shell=(root/'templates/start-here.html.in').read_text();outputs={};records=[]
    renderer=Renderer(narrative,sources,selection['evidence_prefix'])
    for page in narrative['pages']:
        body=renderer.body(page,'fragment',root);document=Document(body)
        toc=''.join('<a href="#'+node.attrs['id']+'">'+escape(node.first(lambda n:n.tag=='h2').text())+'</a>' for node in document.root.all(lambda n:n.tag=='section' and n.attrs.get('id')))
        result=re.sub(r'<title>.*?</title>','<title>'+escape(page['title'])+' · CyberAlchemy Lab</title>',shell,count=1,flags=re.S)
        result=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+escape(page['description'],quote=True)+'">',result,count=1)
        result=result.replace('href="#start-here"','href="#'+page['article_id']+'"').replace('data-site-start aria-current="page"','data-site-start')
        result,count=re.subn(r'<article id="start-here".*?</article>',lambda m:'<article id="'+page['article_id']+'" class="start-content" tabindex="-1">'+body+'</article>',result,count=1,flags=re.S)
        if count!=1:raise ValueError('Shared article shell changed')
        result,count=re.subn(r'(<details class="docs-toc" id="start-toc"><summary>On this page</summary><nav aria-label="Headings on this page">).*?(</nav></details>)',lambda m:m[1]+toc+m[2],result,count=1,flags=re.S)
        if count!=1:raise ValueError('Shared TOC shell changed')
        minutes=max(1,math.ceil(len(re.findall(r'\b[\w’-]+\b',document.root.text()))/220));result=result.replace('{{READING_TIME}}',str(minutes))
        if '{{' in result:raise ValueError('Unresolved runtime shell field')
        outputs[page['site_file']]=result;records.append({'site_file':page['site_file'],'article_id':page['article_id'],'title':page['title'],'markdown_route':page['markdown_route'],'reading_minutes':minutes,'sections':[{'id':page['article_id']+'-'+re.sub('[^a-z0-9]+','-',s['title'].lower()).strip('-'),'title':s['title'],'body_sha256':sha(s['body'].encode())} for s in page['sections']]})
    metadata={'schema_version':'lab-runtime-site-pages/v1-candidate','authority_effect':'none','selection_sha256':os.environ['LAB_SITE_RUNTIME_SELECTION_SHA256'],'edition_id':selection['edition_id'],'standing':selection['standing'],'pages':records,'final_publication_qualified':selection['final_publication_qualified']}
    (root/'research/runtime-pages.json').write_text(json.dumps(metadata,sort_keys=True,indent=2)+'\n')
    return outputs

def register_manifest(root,manifest):
    selection,narrative,sources=selected(root)
    pages=[p['site_file'] for p in narrative['pages']]
    manifest['html_files']=list(dict.fromkeys(manifest['html_files']+pages));manifest['runtime_pages_manifest']='research/runtime-pages.json'
    for key,row in sources['source_bindings'].items():
        source=selection['evidence_prefix']+row['original_path']
        if not any(b['source']==source for b in manifest['bindings']):manifest['bindings'].append({'identity':'runtime-public-source:'+key,'selected_version':selection['edition_id'],'source':source,'sha256':row['sha256'],'affected_pages':pages,'explanatory_claims':['Exact public documentation snapshot only; no source admission or runtime qualification.'],'example_coverage':[]})
    return manifest
''')
# Additive shared build hook and immutable configured selector (only prototype/postimages).
file=WEB/'build.py';s=file.read_text();s=s.replace('steps = [','config=json.loads((ROOT/"site.json").read_text())\n    runtime=config.get("runtime_documentation_selection")\n    if runtime is not None:\n        if set(runtime)!={"path","sha256"} or runtime["path"]!="source/governance-lab-series/runtime/selection.json":raise ValueError("Closed configured runtime documentation selection required")\n        if digest(ROOT/runtime["path"])!=runtime["sha256"]:raise ValueError("Explicit runtime selector changed")\n        env["LAB_SITE_RUNTIME_SELECTION_SHA256"]=runtime["sha256"]\n    steps = [',1);file.write_text(s)
file=LAB/'render_article.py';s=file.read_text().replace('from practical_docs import render as render_practical_docs','from practical_docs import render as render_practical_docs\nfrom runtime_docs import render as render_runtime_docs, register_manifest as register_runtime_manifest')
s=s.replace('variants.update(render_practical_docs(ROOT))','variants.update(render_practical_docs(ROOT))\nvariants.update(render_runtime_docs(ROOT))')
s+= "\nmanifest_path=ROOT/'research/documentation-manifest.json'\nmanifest=register_runtime_manifest(ROOT,json.loads(manifest_path.read_text()))\nmanifest_path.write_text(json.dumps(manifest,indent=2)+'\\n')\n";file.write_text(s)
file=LAB/'documentation_checks.py';s=file.read_text();s=s.replace("    (ROOT/'research/documentation-manifest.json').write_text", "    from runtime_docs import register_manifest\n    manifest=register_manifest(ROOT,manifest)\n    (ROOT/'research/documentation-manifest.json').write_text",1);file.write_text(s)
file=LAB/'build_site_search.py';s=file.read_text();marker="    guide=documents[names[0]]";extra="""    from runtime_docs import selected as runtime_selected
    runtime_selection,runtime_narrative,runtime_sources=runtime_selected(ROOT)
    for page in runtime_narrative['pages']:
        name=page['site_file'];raw=read(ROOT/name);document=Document(raw)
        documents[name]=document;hashes[name]=hashlib.sha256(raw.encode()).hexdigest();article=document.by_id(page['article_id'])
        add('Operate the Lab',page['title'],name,article,'Lab runtime',[page['key'].replace('-',' ')])
        for section in article.all(lambda n:n.tag=='section' and n.attrs.get('id')):
            heading=section.first(lambda n:n.tag=='h2')
            if heading:add('Operate the Lab',heading.text(),name+'#'+section.attrs['id'],section,page['title'])
""";s=s.replace(marker,extra+marker,1);file.write_text(s)
# Runtime topic expectations are independently declared before index construction.
queries=[('How do I inspect the Lab without a store?','runtime-first-inspection.html','The admitted public inspection task.'),('How do I prepare local Work?','runtime-local-work.html','Separate owned disposable local Work preparation.'),('How do I recover and retry safely?','runtime-recovery.html','Retry and recovery boundaries.'),('How do I use Paperclip as a Lab reader?','runtime-paperclip.html','Bounded Paperclip reader scope.'),('What is the runtime status and evidence?','runtime-status.html','Dated evidence and current limitations.'),('Where is runtime state and short memory?','runtime-state-memory.html','State ownership and ephemeral memory.')]
file=LAB/'search_relevance.py';s=file.read_text().replace('QUERIES = [','QUERIES = [\n'+''.join(' '+repr(q)+',\n' for q in queries),1);s=s.replace('    return judgments',"    from runtime_docs import selected as runtime_selected\n    from pathlib import Path\n    _,runtime_narrative,_=runtime_selected(Path(__file__).resolve().parent)\n    for page in runtime_narrative['pages']:\n        judgments.append(dict(query=page['title'],acceptable=[page['site_file']],rationale='Exact reviewed runtime task title.',kind='exact-title'))\n    return judgments");file.write_text(s)
# Static fallback and the enhanced shared sidebar both get all14 routes.
nav='<div class="docs-navigation-group" data-navigation-group="Operate the Lab"><p class="tree-label">Operate the Lab</p>'+''.join('<a href="'+p['site_file']+'" data-site-runtime="'+p['key']+'">'+p['title']+'</a>' for p in narrative['pages'])+'</div>'
file=LAB/'templates/start-here.html.in';s=file.read_text().replace('<a href="record-examples.html"',nav+'\n<a href="record-examples.html"',1);file.write_text(s)
file=LAB/'assets/site-search.js';s=file.read_text();s=s.replace("      ['Software design',[", "      ['Operate the Lab',[\n"+''.join('        '+json.dumps([p['site_file'],p['title'],'runtime'])+',\n' for p in narrative['pages'])+"      ]],\n      ['Software design',[",1);s=s.replace("      if(marker==='craft')", "      if(marker==='runtime')a.dataset.siteRuntime=href.replace('.html','');\n      if(marker==='craft')",1);s=s.replace("'Practical guides','Reference examples'", "'Practical guides','Operate the Lab','Reference examples'",1);file.write_text(s)
# Route registration uses the HTML source as single body owner.
file=PROTO/'tooling/docs/import_site_docs.py';s=file.read_text();s=s.replace("    importer.routes[('governance-lab-reference.html', '')]", "    runtime_manifest=args.site/'research/runtime-pages.json'\n    if runtime_manifest.is_file():\n        runtime=json.loads(runtime_manifest.read_text())\n        if runtime['schema_version']!='lab-runtime-site-pages/v1-candidate' or len(runtime['pages'])!=14:raise ValueError('Fourteen exact runtime import routes required')\n        for page in runtime['pages']:\n            importer.add(page['site_file'],page['article_id'],'runtime/'+page['markdown_route'])\n    importer.routes[('governance-lab-reference.html', '')]",1)
# Public Python evidence is copied as inert asset, never imported/executed.
s=s.replace("        if '/research/sources/' in target.as_posix():", "        if '/research/sources/runtime/' in target.as_posix() and target.is_file():\n            return self.asset(target,output)\n        if '/research/sources/' in target.as_posix():",1);file.write_text(s)
# Register reviewed runtime wording as identity editorial entries; code/formal bodies remain protected.
# Use source parser in owned scope: only build_site_search has no import-time writes.
import sys;sys.path.insert(0,str(LAB));from runtime.body import Renderer;from build_site_search import Document
corpus=json.loads((WEB/'editorial-copy.json').read_text());renderer=Renderer(narrative,source_map,selection['evidence_prefix'])
for page in narrative['pages']:
 d=Document(renderer.body(page,'fragment',LAB))
 for p in d.root.all(lambda n:n.tag=='p'):
  text=' '.join(p.text().split())
  if text:corpus['entries'].append({'page':'governance-lab-series/'+page['site_file'],'original':text,'editorial':text,'review_basis':'Exact selected narrative1 scoped preparation; ND01 final evidence successor pending.'})
(WEB/'editorial-copy.json').write_text(json.dumps(corpus,ensure_ascii=False,indent=2)+'\n')
# Maintained Markdown indexes are edited directly; imported bodies remain generated.
file=PROTO/'docs/lab/MAINTENANCE.md';file.write_text(file.read_text()+'''\n## Runtime handbook\n\nMaintain runtime narrative/source-map and explicit reviewed selection in website/source/governance-lab-series/runtime; update the exact site.json selection hash after independent review. Never select an edition by largest filename. Build first, then import the final14 registered runtime article routes. Generated runtime Markdown is a projection, not another maintained narrative owner. Check source integrity, source/standing scope, observed failures and remaining journeys separately from site rendering.\n''')
# Reviewable selected postimages preserve exact original targets; new leaves explicit.
for row in original:
 name=row['original']['path'];src=PROTO/name
 if not src.is_file():continue
 if src.read_bytes()!=(ROOT/name).read_bytes():write(HERE/'postimages'/name,src.read_text())
for file in [LAB/'runtime_docs.py',*RUNTIME.glob('*')]:
 if file.is_file():write(HERE/'postimages'/file.relative_to(PROTO),file.read_text())
write(HERE/'diagnostic-input-selection.json',{'schema_version':'lab-T21-owned-website-prototype-inputs/v1-candidate','authority_effect':'none','edition':edition,'reviewed_owner_inputs':[binding(NARR/name) for name in ['narrative.json','source-map.json','independent-review-0001.json','generate.py']],'selector_binding':binding(RUNTIME/'selection.json'),'page_count':14,'section_count':67,'public_source_count':len(source_map['source_bindings']),'ND01_unresolved':True,'shared_website_docs_or_importer_mutated':False,'final_doc2_selection_binding':None,'final_doc2_peer_binding':None,'actual_runtime_or_private_input':False})
for file in HERE.glob('postimages/**/*.py'):ast.parse(file.read_bytes())
print(json.dumps({'prototype':str(PROTO),'website_files':len(website_rows),'postimages':len(list((HERE/'postimages').rglob('*'))),'selector_sha':config['runtime_documentation_selection']['sha256'],'diagnostic_only':True}))
