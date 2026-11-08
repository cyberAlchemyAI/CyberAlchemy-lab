"""Thin maintained runtime renderer selected by explicit reviewed input hashes."""
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
    if review.get('bindings',{}).get('narrative.json')!=selection['narrative_binding']['sha256'] or review.get('bindings',{}).get('source-map.json')!=selection['source_map_binding']['sha256']:raise ValueError('Peer review must bind both selected owner files')
    pages=narrative['pages']
    if selection['page_count']!=14 or len(pages)!=14 or selection['section_count']!=67 or sum(len(p['sections']) for p in pages)!=selection['section_count']:raise ValueError('Fourteen complete runtime pages required')
    for field in ['key','site_file','article_id','markdown_route']:
        if len({p[field] for p in pages})!=14:raise ValueError('Distinct runtime page routes required')
    for p in pages:
        if not re.fullmatch('runtime-[a-z0-9-]+\.html',p['site_file']) or not re.fullmatch('runtime-[a-z0-9-]+',p['article_id']):raise ValueError('Closed actual page/article identity required')
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
        result=result.replace('</head>','<link rel="stylesheet" href="runtime/runtime.css">\n</head>',1)
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
