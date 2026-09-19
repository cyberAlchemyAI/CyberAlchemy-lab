"""Map reference credit release action rules into candidate acceptance conditions."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0020-typed-backend-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='language/capabilities/alchlang/plans/three-vertical-compilation-campaign/execution/verticals/customer-credit-release/'
ID='CA2-REF-CAP-CUSTOMER-CREDIT-RELEASE'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def requirements(cap,domain,ontology):
    if domain.get('capability_ref')!=cap['capability_id'] or ontology.get('capability_ref')!=cap['capability_id']:raise ValueError('Wrong capability binding')
    if domain.get('business_ontology_ref')!=ontology.get('ontology_id'):raise ValueError('Wrong ontology binding')
    if domain.get('owner_route')!=cap['owner_route'] or domain.get('authority_effect')!='none':raise ValueError('Owner or authority mismatch')
    actions=[a for a in domain['actions'] if a['id']=='release-credit']
    if len(actions)!=1:raise ValueError('Missing release action')
    action=actions[0];mapping={}
    for ident in action['rule_refs']:
        matches=[r for r in domain['rules'] if r['id']==ident]
        if len(matches)!=1 or ident in mapping:raise ValueError('Missing or duplicate rule')
        rule=matches[0]
        if not tool.text(rule.get('description')) or action['id'] not in rule.get('action_refs',[]):raise ValueError('Invalid rule binding')
        mapping[ident]=rule['description']
    if len(mapping)!=4:raise ValueError('Unexpected rule set')
    boundaries=[b for b in domain['authority_boundaries'] if b['id']==action['authority_boundary_ref']]
    if len(boundaries)!=1 or boundaries[0]['effect']!='in-memory adapter invocation':raise ValueError('Unexpected effect boundary')
    if action['failure_continuation']!='return-denied-or-blocked':raise ValueError('Wrong failure continuation')
    return list(mapping.values()),mapping

def prepare():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
        docs[b['path']]=tool.read(SOURCE/b['path'])
        for ptr,row in tool.walk(docs[b['path']]):
            for key in ['id','node_id','capability_id','product_id']:
                if tool.text(row.get(key)):index[row[key]].append({'source':{**b,'selector':ptr},'record':row})
    cap=docs[PREFIX+'product-capability.json'];assert cap['capability_id']==ID
    inventory=tool.read(PREV/'inventory.json');row=next(r for r in inventory['results'] if r['id']==ID and r['category']=='declaration')
    if tool.sha(SOURCE/row['source']['path'])!=row['source']['sha256']:raise ValueError('Inventory source drift')
    conditions,mapping=requirements(cap,docs[PREFIX+'alchlang.domain.json'],docs[PREFIX+'business-ontology.json'])
    mapped={**cap,'acceptance_conditions':conditions}
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'acceptance_mapping':mapping,'reference_mapping':{'acceptance_conditions':'alchlang.domain.json /actions/release-credit rule_refs -> exact rule descriptions','contracts':'Inline input_contract/output_contract preserved in source_record; no separate contract identity invented'},'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Reference description imported only; in-memory example execution and runtime conformance not rerun. Inline input/output contracts preserved as source metadata.','Real lending decisions and fund transfers remain explicitly excluded.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(PREV/'imports.json');assert not any(r['id']==ID for r in prior)
    combined=prior+[result];nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            assert row['status']=='blocked';row.update(status='imported-candidate',reason='Four action-linked source rules mapped to acceptance conditions; domain/ontology ownership and in-memory effect boundary validated.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0021/imports.json',combined)
    print(json.dumps(inventory['counts']))
