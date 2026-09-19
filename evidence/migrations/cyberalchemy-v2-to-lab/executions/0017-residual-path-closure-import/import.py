"""Import source-linked DomainSpec capability using its explicit construction provenance."""
import collections,copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0016-ontology-incident-exclusion'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='implementation/domainspec-v2/development/evolvable-validation-framework/residuality-specialization-candidate-v1/'
ID='DSV2-EVF-RESIDUAL-PATH-CLOSURE'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    content=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def prepare():
    receipt=tool.read(PREV/'verification.json')
    for b in receipt['bindings']+[receipt['previous_inventory'],receipt['imported_store']]:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();inventory=tool.read(PREV/'inventory.json')
    row=next(r for r in inventory['results'] if r['id']==ID and r['category']=='declaration')
    source=SOURCE/row['source']['path']
    if tool.sha(source)!=row['source']['sha256']:raise ValueError('Capability drift')
    cap=tool.read(source);profile_path=SOURCE/PREFIX/'profile.json';profile=tool.read(profile_path)
    stages=profile['d65_provenance']
    capstage=next(x for x in stages if x['stage']=='product-capability')
    if capstage['path']!='product-capability.json':raise ValueError('Wrong capability link')
    stage=next(x for x in stages if x['stage']=='product-and-business-prototype')
    thesis_path=SOURCE/stage['path'].removeprefix('cyberAlchemy-v2/')
    if tool.sha(thesis_path)!=stage['sha256']:raise ValueError('Thesis provenance digest mismatch')
    thesis=thesis_path.read_text()
    def paragraph(text):return ' '.join(text.split())
    heading=thesis.split('## Thesis\n\n',1)[1].split('\n\n',1)[0]
    boundary='The product is the machinery that preserves meaning across this chain. A DomainSpec document,\ngenerated file, validator, receipt, or ontology projection is one part of that machinery; no\nsingle artifact is the product by itself.'
    if boundary not in thesis or 'owner: DomainSpec v2 owner\n' not in thesis or 'document_id: domainspec-product-thesis/v1\n' not in thesis:raise ValueError('Thesis selectors changed')
    product={'product_id':'domainspec-product-thesis/v1','role':'product','name':'DomainSpec','purpose':paragraph(heading),'identity_boundary':paragraph(boundary),'owner_route':'DomainSpec v2 owner'}
    sources=[bind(source,SOURCE),bind(profile_path,SOURCE),bind(thesis_path,SOURCE)]
    index={product['product_id']:[{'record':product,'source':{**sources[2],'selector':'#Thesis'}}]}
    mapped={**cap,'product_ref':product['product_id'],'outcome':cap['normal_intent'],'acceptance_conditions':[cap['testable_candidate']]}
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in sources:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift during preparation')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':sources,'product_projection':product,'mapping':{'product_ref':'profile.json /d65_provenance product-and-business-prototype -> exact digest-bound PRODUCT-THESIS.md document_id','outcome':'/normal_intent','acceptance_conditions':['/testable_candidate'],'exclusions':'/non_goals','owner_ref':'/owner'},'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Candidate record import only; evaluator runtime and example evidence not rerun.','Source prototype-candidate-unapproved lifecycle retained.','Construction links establish product provenance, not product approval.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(HERE.parent/'0014-continuous-task-loop-import/imports.json');combined=prior+[result];nodes={}
    if any(x['id']==ID for x in prior):raise ValueError('Already imported')
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            if row['status']!='blocked':raise ValueError('Wrong prior state')
            row.update(status='imported-candidate',reason='Explicit digest-bound construction provenance supplies DomainSpec Product; normal intent and testable candidate map required fields.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0017/imports.json',combined)
    print(json.dumps(inventory['counts']))
