#!/usr/bin/env python3
"""Read-only release inventory, links, preservation and source drift evidence."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

REPO = Path(__file__).resolve().parents[3]
SITE = REPO / 'website/dist'
OUT = REPO / 'website/output/playwright/ux-validator/20261012-whole-site'

def digest(p): return sha256(p.read_bytes()).hexdigest()

class Document(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.refs=[];self.tags=Counter();self.meta={};self.headings=[]
        self.h=None;self.htext=[];self.title='';self.in_title=False;self.redirect=None
        self.feed(raw)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags[tag]+=1
        if 'id' in a:self.ids.append(a['id'])
        if tag in ['a','img','script','link','source','iframe','object']:
            for k in ['href','src','data']:
                if a.get(k):self.refs.append(dict(tag=tag,url=a[k],rel=a.get('rel')))
        if tag=='meta':
            self.meta[a.get('name') or a.get('property') or a.get('http-equiv','')]=a.get('content','')
            if a.get('http-equiv','').lower()=='refresh':self.redirect=a.get('content')
        if tag in ['h1','h2','h3','h4']:self.h=tag;self.htext=[]
        if tag=='title':self.in_title=True
    def handle_data(self,data):
        if self.h:self.htext.append(data)
        if self.in_title:self.title+=data
    def handle_endtag(self,tag):
        if self.h==tag:self.headings.append(dict(level=tag,text=' '.join(''.join(self.htext).split())));self.h=None
        if tag=='title':self.in_title=False

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    release=json.loads((SITE/'release-manifest.json').read_text())
    pages={p.relative_to(SITE).as_posix():Document(p.read_text()) for p in SITE.rglob('*.html')}
    inventory=[];links=[];external=set()
    for name,d in sorted(pages.items()):
        p=SITE/name
        inventory.append(dict(page=name,sha256=digest(p),bytes=p.stat().st_size,title=d.title,
            redirect=d.redirect,alias=name.endswith('governance-lab-series.html'),
            description=d.meta.get('description'),canonical=next((x['url'] for x in d.refs if x['tag']=='link' and x.get('rel')=='canonical'),None),
            headings=d.headings,tag_counts=dict(d.tags),duplicate_ids=[k for k,n in Counter(d.ids).items() if n>1]))
        for ref in d.refs:
            u=urlsplit(ref['url'])
            if u.scheme or u.netloc:
                if u.scheme in ['http','https']:external.add(ref['url'])
                continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p
            exists=target.is_file();within=target.is_relative_to(SITE)
            fragment=unquote(u.fragment)
            target_name=target.relative_to(SITE).as_posix() if within else str(target)
            found=not fragment or target_name not in pages or fragment in pages[target_name].ids
            dynamic=fragment in ['start','foundations','system-map','catalog-history','craft-overview'] or bool(re.match(r'essay-\d+-section-\d+$',fragment)) or fragment.startswith('craft-')
            links.append(dict(page=name,tag=ref['tag'],href=ref['url'],target=target_name,exists=exists,within_site=within,fragment_exists=found,dynamic_candidate=dynamic))
    mismatches=[r['path'] for r in release['files'] if not (SITE/r['path']).is_file() or digest(SITE/r['path'])!=r['sha256']]
    catalog=json.loads((REPO/'website/source/governance-lab-series/research/catalog.json').read_text())
    manifest=json.loads((REPO/'website/source/governance-lab-series/research/documentation-manifest.json').read_text())
    capture=REPO/'website/source/governance-lab-series/research/sources'
    capture_drift=[];capture_missing=[];compared=0
    for p in sorted(capture.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(capture);current=REPO/rel
        if current.is_file():
            compared+=1
            if digest(p)!=digest(current):capture_drift.append(str(rel))
        else:capture_missing.append(str(rel))
    source_bindings=[]
    for b in manifest['bindings']:
        p=(REPO/'website/source/governance-lab-series'/b['source']).resolve()
        source_bindings.append(dict(source=b['source'],identity=b['identity'],matches=p.is_file() and digest(p)==b['sha256']))
    # Reuse the existing parser solely to compare protected exact record bodies.
    sys.path.insert(0,str(REPO/'website/source/governance-lab-series'))
    from build_site_search import Document as RichDocument, clean
    lib=RichDocument((SITE/'governance-lab-series/lab-reference-library.html').read_text())
    def normative(n):
        if n.has_class('reference-aid'):return ''
        return ' '.join(normative(c) if hasattr(c,'tag') else c for c in n.children)
    fingerprints=[sha256(clean(normative(n)).encode()).hexdigest() for n in lib.root.all(lambda n:n.has_class('record-body'))]
    baseline=json.loads((REPO/'website/source/governance-lab-series/research/preservation-baseline.json').read_text())['reference bodies excluding explanatory reading aids']
    receipts=json.loads((SITE/'governance-lab-series/research/editorial-edition.json').read_text())
    editorial_pages=receipts.get('pages',{})
    groups=release['search_groups']
    report=dict(release_sha256=digest(SITE/'release-manifest.json'),archive=json.loads((REPO/'website/artifacts/build.json').read_text()),
        html_pages=inventory,link_checks=links,missing_resources=[x for x in links if not x['exists'] or not x['within_site']],
        unresolved_fragments=[x for x in links if not x['fragment_exists']],external_links=sorted(external),
        manifest_digest_mismatches=mismatches,captured_sources=dict(compared=compared,changed=capture_drift,missing=capture_missing),
        selected_binding_mismatches=[b for b in source_bindings if not b['matches']],
        exact_reference_preservation=dict(count=len(fingerprints),matches=fingerprints==baseline),search_groups=groups)
    (OUT/'measurements').mkdir(exist_ok=True)
    (OUT/'measurements/static.json').write_text(json.dumps(report,indent=2)+'\n')
    # A compact HTTP check of every deployed file on the current preview.
    def check(row):
        try:
            with urlopen('http://127.0.0.1:33733/'+row['path'],timeout=15) as response:
                raw=response.read()
                return dict(path=row['path'],status=response.status,bytes=len(raw),digest_matches=sha256(raw).hexdigest()==row['sha256'])
        except Exception as error:return dict(path=row['path'],error=str(error))
    with ThreadPoolExecutor(max_workers=8) as pool:http=list(pool.map(check,release['files']))
    (OUT/'measurements/http-resources.json').write_text(json.dumps(http,indent=2)+'\n')
    print(json.dumps(dict(html=len(pages),links=len(links),missing_resources=len(report['missing_resources']),
        unresolved_fragments=len(report['unresolved_fragments']),manifest_mismatches=mismatches,
        captured_source_changes=len(capture_drift),reference_preserved=report['exact_reference_preservation'],
        http_files=len(http),http_failures=[x for x in http if x.get('status')!=200 or not x.get('digest_matches')]),indent=2))

if __name__=='__main__':main()
