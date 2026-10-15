"""Compile public documentation text into a shared, file:// compatible index."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import ast

ROOT = Path(__file__).resolve().parent
CRAFT = ROOT.parent / 'craft-documentation-proposal'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def read(path):
    with path.open('rb') as source:
        return b''.join(iter(lambda: source.read(16384), b'')).decode('utf-8')

def write(path, value):
    data = value.encode('utf-8')
    temp = path.with_name('.' + path.name + '.tmp')
    with temp.open('wb') as target:
        for offset in range(0, len(data), 16384):
            target.write(data[offset:offset+16384])
    temp.replace(path)

class Node:
    def __init__(self, tag='', attrs=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = None
    def has_class(self, value):
        return value in self.attrs.get('class','').split()
    def all(self, predicate):
        out = [self] if predicate(self) else []
        for child in self.children:
            if isinstance(child, Node): out.extend(child.all(predicate))
        return out
    def first(self, predicate):
        return next(iter(self.all(predicate)), None)
    def text(self):
        if self.tag in {'script','style','button','nav'}: return ''
        return ' '.join(child.text() if isinstance(child, Node) else child for child in self.children)

class Document(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.root=Node(); self.stack=[self.root]
        self.feed(value)
        self.ids={}
        for node in self.root.all(lambda n:'id' in n.attrs):
            self.ids.setdefault(node.attrs['id'],node)
    def handle_starttag(self, tag, attrs):
        node=Node(tag,dict(attrs));node.parent=self.stack[-1]; self.stack[-1].children.append(node)
        if tag not in VOID: self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag==tag:
                self.stack=self.stack[:index]; break
    def handle_data(self,value): self.stack[-1].children.append(value)
    def by_id(self, key): return self.ids.get(key)

def clean(value): return re.sub(r'\s+',' ',value).strip()

def build():
    entries=[]; documents={}; hashes={}; dynamic_ids=set()
    names=['governance-lab-reference.html','lab-reference-library.html','../craft-documentation-proposal/craft-model.html']
    intro_name='start-here.html'
    intro_raw=read(ROOT/intro_name)
    documents[intro_name]=Document(intro_raw);hashes[intro_name]=hashlib.sha256(intro_raw.encode()).hexdigest()
    for name in names:
        raw=read(ROOT/name); documents[name]=Document(raw); hashes[name]=hashlib.sha256(raw.encode()).hexdigest()
    def add(group,title,href,node,section='',aliases=None):
        assert node is not None,(title,href)
        entries.append({'id':href,'group':group,'title':clean(title),'href':href,'section':section,'aliases':aliases or [],'text':clean(node.text())})
    for name, root_id, group in [('index.html','lab-home','The Lab'), ('research.html','research-lab','Research lab'), ('company-brain.html','company-brain','The Lab'), ('source-and-status.html','source-and-status','Sources'), ('hackathon.html','hackathon','Hackathon')]:
        if not (ROOT/name).is_file(): continue
        raw=read(ROOT/name);document=Document(raw)
        documents[name]=document;hashes[name]=hashlib.sha256(raw.encode()).hexdigest()
        article=document.by_id(root_id);title=article.first(lambda n:n.tag=='h1').text()
        aliases=['hackathon','competition','register','prizes','vote','Craft hackathon','solo project'] if group=='Hackathon' else ['company brain','open brain'] if group=='The Lab' else ['source code repository','installation','release status','CyberAlchemy Lab'] if group=='Sources' else ['research lab','culture','cybernetics']
        add(group,title,name,article,'CyberAlchemy Lab' if group=='The Lab' else 'CyberAlchemy',aliases)
        for section in article.all(lambda n:n.tag=='section' and n.attrs.get('id')):
            heading=section.first(lambda n:n.tag=='h2')
            if heading:add(group,heading.text(),name+'#'+section.attrs['id'],section,title)
    intro=documents[intro_name]
    add('Start here','Start here: CyberAlchemy Lab',intro_name,intro.by_id('start-here'),'Getting started',['introduction','new to the Lab','beginner'])
    for section in intro.by_id('start-here').all(lambda n:n.tag=='section' and n.attrs.get('id')):
        add('Start here',section.first(lambda n:n.tag=='h2').text(),intro_name+'#'+section.attrs['id'],section,'Getting started')
    for key in ['incident-walkthrough','concept-comparisons']:
        name=key+'.html';raw=read(ROOT/name)
        document=Document(raw);documents[name]=document;hashes[name]=hashlib.sha256(raw.encode()).hexdigest()
        article=document.by_id(key);title=article.first(lambda n:n.tag=='h1').text()
        add('Learning paths',title,name,article,'Getting started')
        for section in article.all(lambda n:n.tag=='section' and n.attrs.get('id')):
            add('Learning paths',section.first(lambda n:n.tag=='h2').text(),name+'#'+section.attrs['id'],section,title)
    from practical_docs import PAGES
    for key in PAGES:
        name=key+'.html'; raw=read(ROOT/name); document=Document(raw)
        documents[name]=document;hashes[name]=hashlib.sha256(raw.encode()).hexdigest()
        article=document.by_id(key);title=article.first(lambda n:n.tag=='h1').text()
        group='Reference examples' if key=='record-examples' else 'Practical guides'
        add(group,title,name,article,title)
        for section in article.all(lambda n:n.tag=='section' and n.attrs.get('id')):
            add(group,section.first(lambda n:n.tag=='h2').text(),name+'#'+section.attrs['id'],section,title)
    from runtime_docs import selected as runtime_selected
    runtime_selection,runtime_narrative,runtime_sources=runtime_selected(ROOT)
    for page in runtime_narrative['pages']:
        name=page['site_file'];raw=read(ROOT/name);document=Document(raw)
        documents[name]=document;hashes[name]=hashlib.sha256(raw.encode()).hexdigest();article=document.by_id(page['article_id'])
        add('Operate the Lab',page['title'],name,article,'Lab runtime',[page['key'].replace('-',' ')])
        for section in article.all(lambda n:n.tag=='section' and n.attrs.get('id')):
            heading=section.first(lambda n:n.tag=='h2')
            if heading:add('Operate the Lab',heading.text(),name+'#'+section.attrs['id'],section,page['title'])
    guide=documents[names[0]]
    labels={'governance':'Authority and meaning','evidence':'Provenance and evidence','change':'Lifecycle and admission','purpose':'Intent, product and project','records':'Definitions and connections','agent':'Agent work and memory','learning':'Operational learning','today':'Current operational scope'}
    for route,title in labels.items():
        scope=guide.by_id(route)
        aliases={'governance':['What governs meaning and action?','Three questions for governance','authority'], 'evidence':['Where did this come from?','provenance'], 'change':['What can change from here?','lifecycle']}.get(route,[])
        add('Guide',title,names[0]+'#'+route,scope,'Visual guide',aliases)
        def in_details(node):
            parent=node.parent
            while parent and parent is not scope:
                if parent.tag=='details':return True
                parent=parent.parent
            return False
        headings=scope.all(lambda n:(n.tag=='h2' or (n.tag=='h3' and (n.has_class('article-subheading') or (n.parent and n.parent.has_class('lens-visual-heading'))))) and not in_details(n))
        chunks={heading:Node() for heading in headings}; current=[None]
        def collect(node):
            if node.tag in {'script','style','button','nav'}:return
            if node in chunks:current[0]=node
            for child in node.children:
                if isinstance(child,Node):collect(child)
                elif current[0] is not None:chunks[current[0]].children.append(child)
        collect(scope)
        for index,heading in enumerate(headings,1):
            identifier=heading.attrs.get('id') or f'docs-{route}-heading-{index}'
            dynamic_ids.add(names[0]+'#'+identifier)
            add('Guide',heading.text(),names[0]+'#'+identifier,chunks[heading],title)
    for route,title,node in [
        ('start','Explore CyberAlchemy Lab',guide.root.first(lambda n:n.has_class('article-masthead'))),
        ('foundations','Definitions first',guide.root.first(lambda n:n.has_class('introduction'))),
        ('system-map','Interactive system map',guide.by_id('map-explorer')),
        ('reading-next','Reference and sources',guide.by_id('reading-next'))]:
        add('Guide',title,names[0]+'#'+route,node,'Visual guide')
    library=documents[names[1]]
    subtitle_literal=re.search(r'const subtitles = (\{.*?\n  \});',read(ROOT/'assets/lab-library-docs.js'),re.S).group(1)
    subtitles=ast.literal_eval(subtitle_literal)
    for essay in library.root.all(lambda n:n.tag=='article' and n.attrs.get('id','').startswith('essay-')):
        title=essay.first(lambda n:n.tag=='h2').text()
        add('Expanded essays',title,names[1]+'#'+essay.attrs['id'],essay.first(lambda n:n.has_class('prose')),'Expanded essays')
        paragraphs=[node for node in essay.first(lambda n:n.has_class('prose')).children if isinstance(node,Node) and node.tag=='p']
        for index,(number,heading) in enumerate(subtitles[essay.attrs['id']]):
            stop=subtitles[essay.attrs['id']][index+1][0]-1 if index+1<len(subtitles[essay.attrs['id']]) else len(paragraphs)
            chunk=Node();chunk.children=paragraphs[number-1:stop]
            href=names[1]+'#'+essay.attrs['id']+'-section-'+str(number);dynamic_ids.add(href)
            add('Expanded essays',heading,href,chunk,clean(title))
    catalog_groups=[('definitions','Definitions'),('types','Record formats'),('relations','Connection rules'),('endpoints','Endpoint kinds')]
    record_manifest_path=ROOT/'research/reference-pages.json'
    record_pages={row['id']:row for row in json.loads(read(record_manifest_path))['records']} if record_manifest_path.exists() else {}
    for key,title in catalog_groups:
        panel=library.by_id('catalog-'+key)
        add('Reference records',title,names[1]+'#catalog-'+key,panel.first(lambda n:n.has_class('atlas-intro')),'Reference catalog')
        for row in panel.all(lambda n:n.has_class('catalog-item')):
            title_node=row.first(lambda n:n.has_class('catalog-title'))
            record=record_pages.get(row.attrs['id'])
            if record:
                path=record['href'];raw=read(ROOT/path);document=Document(raw)
                documents[path]=document;hashes[path]=hashlib.sha256(raw.encode()).hexdigest()
                body=document.root.first(lambda n:n.has_class('record-body'))
                href=path+'#'+row.attrs['id']
            else:
                body=row.first(lambda n:n.has_class('record-body'));href=names[1]+'#'+row.attrs['id']
            refs=[clean(n.text()) for n in body.all(lambda n:n.has_class('record-id'))]
            add('Reference records',title_node.text(),href,body,title,refs+[row.attrs['id']])
    add('Reference records','How to use the library',names[1]+'#library-reading-guide',library.by_id('library-reading-guide'),'Reference library')
    add('Reference records','Versions and record facets',names[1]+'#catalog-history',library.root.first(lambda n:n.has_class('catalog-extras')),'Reference library')
    add('Sources','Sources and open questions',names[1]+'#research',library.by_id('research'),'Research library')
    craft=documents[names[-1]]
    add('Craft','Craft: compiling software from explicit models',names[-1]+'#craft-overview',craft.root.first(lambda n:n.has_class('hero')),'Craft overview')
    for section in craft.root.all(lambda n:n.has_class('article-section')):
        title=clean(section.first(lambda n:n.tag=='h2').text())
        add('Craft',title,names[-1]+'#'+section.attrs['id'],section,'Craft · software design')
        headings=section.all(lambda n:n.tag=='h3' and n.attrs.get('id'))
        for heading in headings:
            siblings=section.children;start=siblings.index(heading);chunk=Node()
            for child in siblings[start:]:
                if child is not heading and isinstance(child,Node) and child.tag=='h3':break
                chunk.children.append(child)
            add('Craft',heading.text(),names[-1]+'#'+heading.attrs['id'],chunk,title)
    robot_name='../robot-learning-series/robot-learning-series.html'
    if (ROOT/robot_name).is_file():
        raw=read(ROOT/robot_name); robot=Document(raw)
        documents[robot_name]=robot;hashes[robot_name]=hashlib.sha256(raw.encode()).hexdigest()
        add('Applications','Robot learning with CyberAlchemy Lab',robot_name,robot.root.first(lambda n:n.tag=='main'),'Robot learning',['robot learning','movement code','physics experiments'])
        for essay in robot.root.all(lambda n:n.tag=='article' and n.attrs.get('id','').startswith('essay-')):
            add('Applications',essay.first(lambda n:n.tag=='h2').text(),robot_name+'#'+essay.attrs['id'],essay,'Robot learning')
    vocabulary=json.loads(read(ROOT/'search_vocabulary.json'))['topics']
    for entry in entries:
        entry['aliases'] += vocabulary.get(entry['href'], [])
    assert set(vocabulary).issubset({entry['href'] for entry in entries}), 'Vocabulary points to a removed topic.'
    ids=[entry['id'] for entry in entries]
    from search_relevance import bind
    judgments=bind(entries)
    write(ROOT/'research/search-judgments.json',json.dumps({'method':'Independently selected exact destinations. Judgments do not create aliases. Report task-query target rank within the first three and exact-title target rank one.','judgments':judgments},indent=2)+'\n')
    assert len(ids)==len(set(ids)),'Duplicate search destinations'
    groups={group:sum(entry['group']==group for entry in entries) for group in sorted({entry['group'] for entry in entries})}
    for entry in entries:
        path,_,fragment=entry['href'].partition('#')
        if entry['href'] not in dynamic_ids and fragment not in {'start','foundations','system-map','catalog-history','craft-overview'}:
            assert documents[path].by_id(fragment) if fragment else True,entry['href']
    from search_features import compile_entries
    prepared, statistics = compile_entries(entries)
    payload={'version':1,'entries':prepared,'preparedStats':statistics,'groups':groups}
    from compressed_script import write_payload
    delivery=write_payload(ROOT/'assets/site-search-index.js','LabSiteSearchIndex',payload,set_base=True)
    # Small first-pass corpus shares identities, aliases and literal excerpts.
    # It is never a replacement for complete-record search or its judgments.
    quick_entries, quick_statistics = compile_entries([{**entry, 'text': entry['text'][:64]} for entry in entries])
    quick = {'version': 1, 'groups': groups, 'entries': quick_entries, 'preparedStats': quick_statistics}
    quick_delivery = write_payload(ROOT/'assets/site-search-quick.js', 'LabSiteSearchQuick', quick, set_base=True)
    code=read(ROOT/'assets/site-search-index.js')
    receipt={'authority_effect':'none','entries':len(entries),'groups':groups,'source_html_sha256':hashes,'index_sha256':hashlib.sha256(code.encode()).hexdigest(),'delivery':delivery,'quick_delivery':quick_delivery,'scope':'Research entrance, product introduction, documentation text and exact reference bodies; source research files are not separately indexed.'}
    write(ROOT/'research/site-search-index.json',json.dumps(receipt,indent=2)+'\n')
    visual_model=ROOT/'research/visual-article-model.json'
    if visual_model.exists():
        model=json.loads(read(visual_model));model['design']['navigation']['search_entries']=len(entries)
        write(visual_model,json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'search_entries':len(entries),'groups':groups,'index_bytes':len(code.encode())}))
    return receipt

if __name__=='__main__': build()
