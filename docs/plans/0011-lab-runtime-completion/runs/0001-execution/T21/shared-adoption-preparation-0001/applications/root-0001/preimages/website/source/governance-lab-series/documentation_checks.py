"""Source impact, local structure and preservation checks for the documentation."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote, urlsplit
import hashlib
import json
import sys
import os
from build_site_search import Document, clean
from practical_docs import PAGES

ROOT=Path(__file__).resolve().parent
BASELINE=ROOT/'research/preservation-baseline.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def duplicates(document):
    ids=[n.attrs['id'] for n in document.root.all(lambda n:'id' in n.attrs)]
    return sorted(key for key,count in Counter(ids).items() if count>1)
def affected(bindings,source,new_digest):
    return sorted({page for b in bindings if b['source']==source and b['sha256']!=new_digest for page in b['affected_pages']})

def build_manifest():
    catalog=json.loads((ROOT/'research/catalog.json').read_text());examples=json.loads((ROOT/'research/documentation-examples.json').read_text())
    bindings=[]
    groups=[('definitions','source','sha256'),('artifact_types','source','artifact_sha256'),('artifact_types','schema_source','schema_sha256'),('relations','source','instance_sha256')]
    for group,path_key,digest_key in groups:
        for row in catalog[group]:
            source=row[path_key];identity=row.get('ref') or row.get('artifact_type_ref') or row.get('relation_kind_ref')
            pages=['lab-reference-library.html','governance-lab-reference.html','governance-lab-series.html','incident-walkthrough.html','concept-comparisons.html','start-here.html']
            coverage=[e['key'] for e in examples['examples'] if source in [e['schema_source'],e['contract_source']]]
            if coverage:pages+=list(key+'.html' for key in PAGES)
            bindings.append(dict(identity=identity,selected_version=row.get('version') or identity.split('/')[-1],source=source,sha256=row[digest_key],affected_pages=sorted(set(pages)),
                explanatory_claims=['Selected meaning or format and its independent standing.','Derived views and documentation supply no automatic authority.'],example_coverage=coverage))
    for name in ['research/incident-extraction-case.json','../craft-documentation-proposal/craft-model.md']:
        bindings.append(dict(identity=name,selected_version='exact captured content',source=name,sha256=sha(ROOT/name),affected_pages=list(key+'.html' for key in PAGES)+['incident-walkthrough.html','governance-lab-reference.html','lab-reference-library.html'],
            explanatory_claims=['Fixed case scope and unresolved cause/impact/recovery.' if 'incident' in name else 'Calculation is pure; Operation owns state change.'],example_coverage=['incident' if 'incident' in name else 'capacity']))
    manifest=dict(version=1,authority_effect='none',bindings=bindings,impact_policy='Conservative page-level review dependencies; changed sources trigger review, never automatic authority or admission.',
      critical_distinctions=['definition authority / action permission','provenance / proof','acceptance / activation','durable project state / session memory','declared relation / drawn arrow','pure Calculation / state-changing Operation'],
      html_files=[*['index.html','company-brain.html','research.html','source-and-status.html','hackathon.html','start-here.html','incident-walkthrough.html','concept-comparisons.html','governance-lab-reference.html','governance-lab-series.html','lab-reference-library.html'],*(key+'.html' for key in PAGES),
                  'governance-authority.html','governance-provenance.html','governance-lifecycle.html','../craft-documentation-proposal/craft-model.html'])
    (ROOT/'research/documentation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def check(manifest):
    failures=[];checks=[]
    def require(condition,label,details=None):
        checks.append(dict(check=label,pass_=bool(condition),details=details))
        if not condition:failures.append(label)
    documents={name:Document((ROOT/name).read_text()) for name in manifest['html_files']}
    documents_by_path={os.path.abspath(ROOT/name):doc for name,doc in documents.items()}
    exist_cache={};hash_cache={}
    for name,doc in documents.items():
        require(not duplicates(doc),'Unique identifiers: '+name,duplicates(doc))
        for node in doc.root.all(lambda n:n.tag in ['a','link','script','img']):
            href=node.attrs.get('href') or node.attrs.get('src');
            if not href:continue
            u=urlsplit(href)
            if u.scheme or u.netloc:continue
            target=(ROOT/name).parent/unquote(u.path) if u.path else ROOT/name
            absolute=os.path.abspath(target)
            if absolute not in exist_cache:exist_cache[absolute]=target.exists()
            require(exist_cache[absolute],'Local destination: '+name+' → '+href)
            if target.suffix=='.html' and u.fragment and exist_cache[absolute]:
                selected=documents_by_path.get(absolute)
                if selected is None:selected=Document(target.read_text())
                # Some guide/library routes are created by the documented enhancement.
                dynamic=u.fragment in ['start','foundations','system-map','catalog-history','craft-overview'] or u.fragment.startswith('essay-') and '-section-' in u.fragment
                require(dynamic or selected.by_id(unquote(u.fragment)) is not None,'Fragment: '+name+' → '+href)
    changed=[]
    for b in manifest['bindings']:
        source=b['source']
        if source not in hash_cache:hash_cache[source]=sha(ROOT/source)
        current=hash_cache[source]
        if current!=b['sha256']:changed.append(dict(source=b['source'],affected=affected(manifest['bindings'],b['source'],current)))
    require(not changed,'Selected source fingerprints',changed)
    baseline=json.loads(BASELINE.read_text());new=documents['lab-reference-library.html']
    editorial_path=ROOT/'research/editorial-edition.json'
    if editorial_path.exists():
        # The captured formal baseline remains fixed. The adopted editorial
        # edition records the intentionally revised explanatory essay bodies.
        editorial=json.loads(editorial_path.read_text())
        baseline['expanded essay paragraphs']=editorial['expanded_essay_fingerprints']
    preserved=[]
    def normative_text(n):
        if n.has_class('reference-aid'):return ''
        return ' '.join(normative_text(c) if hasattr(c,'tag') else c for c in n.children)
    for label,predicate in [('reference bodies excluding explanatory reading aids',lambda n:n.has_class('record-body')),('expanded essay paragraphs',lambda n:n.tag=='article' and n.attrs.get('id','').startswith('essay-'))]:
        a=baseline[label]
        record_manifest=ROOT/'research/reference-pages.json'
        if label.startswith('reference bodies') and record_manifest.exists():
            record_rows=json.loads(record_manifest.read_text())['records']
            require(len(record_rows)==454,'All canonical reference identities',len(record_rows))
            nodes=[documents[row['href']].root.first(predicate) for row in record_rows]
            require(all(nodes),'Every canonical page contains its exact body')
        else:nodes=new.root.all(predicate)
        b=[hashlib.sha256(clean(normative_text(n)).encode()).hexdigest() for n in nodes if n is not None]
        require(a==b,'Preserved '+label,dict(before=len(a),after=len(b)));preserved.append(dict(content=label,count=len(b)))
    guide=documents['governance-lab-reference.html'];heading_map=json.loads((ROOT/'research/guide-heading-identities.json').read_text())['headings']
    for title,row in heading_map.items():
        node=guide.by_id(row['id']);require(node is not None and clean(node.text())==title,'Stable guide heading: '+row['id'])
    index_receipt=json.loads((ROOT/'research/site-search-index.json').read_text())
    require(sha(ROOT/'assets/site-search-index.js')==index_receipt['index_sha256'],'Search index fingerprint')
    for name,expected in index_receipt['source_html_sha256'].items():require(sha(ROOT/name)==expected,'Search source current: '+name)
    for name in PAGES:require(name+'.html' in index_receipt['source_html_sha256'],'Search covers: '+name)
    # Calibration includes a source change, an unchanged source, and an unrelated
    # path; helpers must not invent impact for a file with no declared consumers.
    first=manifest['bindings'][0];fixture_bindings=[first]
    calibration=[dict(fixture='valid unique IDs',pass_=duplicates(Document('<p id="a"></p><p id="b"></p>'))==[]),
       dict(fixture='invalid duplicate IDs',pass_=duplicates(Document('<p id="a"></p><p id="a"></p>'))==['a']),
       dict(fixture='false positive: repeated visible words',pass_=duplicates(Document('<p>Work</p><p>Work</p>'))==[]),
       dict(fixture='unchanged source',pass_=affected(fixture_bindings,first['source'],first['sha256'])==[]),
       dict(fixture='changed source identifies consumers',pass_=affected(fixture_bindings,first['source'],'0'*64)==first['affected_pages']),
       dict(fixture='unrelated source has no inferred consumers',pass_=affected(fixture_bindings,'unrelated.json','0'*64)==[])]
    require(all(r['pass_'] for r in calibration),'Hard-rule calibration',calibration)
    report=dict(result='pass' if not failures else 'needs-fix',checks=checks,failures=failures,calibration=calibration,preserved=preserved,
      scope='Structural and preservation checks only; editorial consistency and participant understanding need their own evidence.')
    (ROOT/'research/documentation-maintenance-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'checks':len(checks),'failures':failures[:20]}))
    return not failures

if __name__=='__main__':
    manifest_path=ROOT/'research/documentation-manifest.json'
    manifest=build_manifest() if '--freeze' in sys.argv or not manifest_path.exists() else json.loads(manifest_path.read_text())
    if '--impact' in sys.argv:
        source=sys.argv[sys.argv.index('--impact')+1];print(json.dumps({'source':source,'affected_pages':affected(manifest['bindings'],source,sha(ROOT/source))}))
    else:sys.exit(0 if check(manifest) else 1)
