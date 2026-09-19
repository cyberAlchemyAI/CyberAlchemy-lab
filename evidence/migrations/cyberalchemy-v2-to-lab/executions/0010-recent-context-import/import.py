"""Import Recent Repository Context with acceptance requirements from its source."""
import collections
import json
from pathlib import Path
import re
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
PREVIOUS=HERE.parent/'0009-contextual-framings-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def acceptance(cap,definitions,model,plan):
    if cap['model_ref']!='recent-context.alch':raise ValueError('Unexpected model reference')
    indexed={d['id']:d for d in definitions['definitions']}
    if len(indexed)!=len(definitions['definitions']):raise ValueError('Duplicate Definition identity')
    mapped=[]
    for ident in plan['definition_ids']:
        d=indexed.get(ident)
        if not d or not tool.text(d.get('normative')) or d.get('authority_effect')!='none':raise ValueError('Missing or invalid source requirement: '+ident)
        mapped.append({'source':'definitions.json','selector':ident,'statement':d['normative']})
    for name in plan['rule_names']:
        matches=re.findall(r'^rule '+re.escape(name)+r':\n  ([^\n]+)$',model,re.M)
        if len(matches)!=1:raise ValueError('Missing or ambiguous authored rule: '+name)
        mapped.append({'source':'recent-context.alch','selector':'rule '+name,'statement':name+': '+matches[0]})
    if cap['maximum_limits']!={'commits':100,'files':1000}:raise ValueError('Capability limits changed')
    if cap['query_effect']!='read-only' or cap['authority_effect']!='none':raise ValueError('Unexpected query effect')
    if 'commitLimit <= 100' not in mapped[-2]['statement'] or 'pathLimit <= 1000' not in mapped[-2]['statement']:raise ValueError('Model limit mismatch')
    if mapped[-1]['statement']!='observation-only: mutationRequested == false':raise ValueError('Model observation rule changed')
    return mapped

def prepare():
    receipt=tool.read(PREVIOUS/'verification.json')
    for ref in receipt['bindings']:
        if ref['path'].endswith('/imports.json') and tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Previous import drift')
    # The original bulk receipt binds the reused importer implementation.
    original=tool.read(HERE.parent/'0008-capability-inventory-import/verification.json')
    for ref in original['bindings']:
        if ref['path'].endswith('capability_inventory_import.py') and tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Importer drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for ref in plan['sources']:
        p=SOURCE/ref['path']
        if tool.sha(p)!=ref['sha256']:raise ValueError('Source drift: '+ref['path'])
        docs[ref['path']]=p.read_text() if p.suffix=='.alch' else tool.read(p)
        for ptr,row in tool.walk(docs[ref['path']]):
            if tool.text(row.get('id')):index[row['id']].append({'source':{**ref,'selector':ptr},'record':row})
    prefix='agent-routing/capabilities/recent-context/'
    cap=docs[prefix+'capability.json']
    if cap['capability_id']!=plan['capability_id']:raise ValueError('Wrong capability')
    mappings=acceptance(cap,docs[prefix+'definitions.json'],docs[prefix+'recent-context.alch'],plan)
    enriched={**cap,'acceptance_conditions':[m['statement'] for m in mappings]}
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    source_ref=next(r for r in plan['sources'] if r['path']==prefix+'capability.json')
    result=tool.normalize({'record':enriched,'source':{**source_ref,'selector':''}},index,engine,registry['scope'])
    entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability')
    for ref in plan['sources']:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed during import')
    return {**result,'id':cap['capability_id'],'status':'imported-candidate','source':{**source_ref,'selector':''},'source_record':cap,'acceptance_mapping':mappings,'source_bindings':plan['sources'],'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False}

if __name__=='__main__':
    result=prepare();prior=tool.read(PREVIOUS/'imports.json')
    if any(x['id']==result['id'] for x in prior):raise ValueError('Already imported')
    combined=prior+[result]
    import engine
    nodes={}
    for item in combined:
        for record in [item['product'],item['capability']]:
            if record['node_id'] in nodes and nodes[record['node_id']]!=record:raise ValueError('Graph identity collision')
            nodes[record['node_id']]=record
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREVIOUS/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==result['id'] and row['source']==result['source'] and row['status']=='blocked':
            row.update(status='imported-candidate',reason='Six source normative definitions and three authored model rules mapped to acceptance requirements.');changed+=1
    if changed!=1:raise ValueError('Expected one blocked transition')
    inventory['counts']=dict(collections.Counter(x['status'] for x in inventory['results']))
    store=ROOT/'.local/capability-inventory-import-0010'
    if store.exists():raise ValueError('Preserve existing store')
    store.mkdir()
    for name,data in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:
        text=json.dumps(data,indent=2,sort_keys=True)+'\n';(HERE/name).write_text(text)
        if name=='imports.json':(store/name).write_text(text)
    print(json.dumps({'result':'PASS','capability':result['id'],'requirements':9,'counts':inventory['counts']}))
