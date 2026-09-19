"""Build the explicit candidate contract registry and import its dependent Capability."""
import collections
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
PREVIOUS=HERE.parent/'0010-recent-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
from contracts import contracts,check
from test_contracts import fixture

def dump(path,value):
    text=json.dumps(value,indent=2,sort_keys=True)+'\n'
    if path.exists() and path.read_text()!=text:raise ValueError('Preserve existing artifact: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def bind(path,root=ROOT):return {'root':'lab' if root==ROOT else 'cav2','path':str(path.relative_to(root)),'sha256':tool.sha(path)}

def main():
    registry=tool.load_registry()
    for ref in tool.read(PREVIOUS/'verification.json')['bindings']:
        if tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Predecessor drift')
    original=tool.read(HERE.parent/'0008-capability-inventory-import/verification.json')
    for ref in original['bindings']:
        if ref['path'].endswith('capability_inventory_import.py') and tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Importer drift')
    audit=tool.read(HERE.parent/'0011-governed-access-reference-audit/results.json')
    for ref in audit['source_bindings']:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Audited source drift')
    source_refs=[];index=collections.defaultdict(list)
    for name in ['commercial-agent-access/product-capability.json','commercial-agent-access/nodes.json','commercial-agent-access/product-capability-support.json','commercial-agent-access/definitions.json','commercial-agent-access/residue.json','ontology/product/nodes.json']:
        p=SOURCE/name;source_refs.append(bind(p,SOURCE))
        for ptr,row in tool.walk(tool.read(p)):
            for key in ['id','node_id','registry_id']:
                if tool.text(row.get(key)):index[row[key]].append({'source':{**bind(p,SOURCE),'selector':ptr},'record':row})
    cap=tool.read(SOURCE/'commercial-agent-access/product-capability.json')
    required=set(sum([cap[k] for k in ['input_contract_refs','output_contract_refs','context_policy_refs']],[]))
    if required!=set(contracts()):raise ValueError('Candidate registry membership differs from requested contracts')
    entries=[]
    for ident,(kind,source_id,schema) in contracts().items():
        source_candidates=index[source_id]
        if len(source_candidates)!=1:raise ValueError('Ambiguous source concept: '+source_id)
        concept=source_candidates[0]
        path=HERE/'contracts'/ident
        dump(path/'schema.json',schema);sample=fixture(ident);check(ident,sample);dump(path/'example.json',sample)
        record={'id':ident,'kind':kind,'meaning':concept['record']['meaning'],'status':'candidate-unadmitted','authority_effect':'none','action_authorized':False,
                'elaborates_source_concept':concept['source'],'source_concept_id':source_id,
                'mapping_effect':'proposed carrier contract for this source concept; no identity equivalence or admission',
                'schema':bind(path/'schema.json'),'example':bind(path/'example.json'),
                'design_choices':['Closed candidate-only representation; no field grants execution authority.','Schema fields and version 1 are new local proposals, not inherited KEP protocol approval.','Timestamps, where present, are integer UTC Unix seconds.'],
                'limits':['Supplied caller, validation and decision claims are not authenticated.','No filesystem, network, custody, signature or runtime implementation is provided.']}
        dump(path/'contract.json',record)
        ref=bind(path/'contract.json');entries.append({'id':ident,'binding':ref,'source_concept_id':source_id})
        index[ident].append({'source':{**ref,'selector':''},'record':record})
    dump(HERE/'candidate-registry.json',{'status':'candidate-unadmitted','authority_effect':'none','scope':registry['scope'],'entries':entries,'source_bindings':source_refs})
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    capref=bind(SOURCE/'commercial-agent-access/product-capability.json',SOURCE)
    normalized=tool.normalize({'record':cap,'source':{**capref,'selector':''}},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    result={**normalized,'id':cap['capability_id'],'source':{**capref,'selector':''},'source_record':cap,'status':'imported-candidate','contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'candidate_contract_registry':bind(HERE/'candidate-registry.json'),'source_bindings':source_refs,'authority_effect':'none','operational_use_authorized':False,'operational_blockers':['Candidate contracts require owner adoption before operational use.','KEP service-exchange capability and ontology admission remain absent.','Authentication, filesystem enforcement and service realization are not implemented by this bundle.']}
    for ref in source_refs:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed during import')
    prior=tool.read(PREVIOUS/'imports.json')
    if any(x['id']==result['id'] for x in prior):raise ValueError('Already imported')
    combined=prior+[result];nodes={}
    for item in combined:
        for node in [item['product'],item['capability']]:
            if node['node_id'] in nodes and nodes[node['node_id']]!=node:raise ValueError('Identity collision')
            nodes[node['node_id']]=node
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREVIOUS/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==result['id'] and row['status']=='blocked' and row['source']['path']==capref['path']:
            row.update(status='imported-candidate',reason='16 explicit local candidate contracts constructed and validated; operational service exchange remains unadmitted.');changed+=1
    if changed!=1:raise ValueError('Expected one transition')
    inventory['counts']=dict(collections.Counter(x['status'] for x in inventory['results']))
    store=ROOT/'.local/capability-inventory-import-0012'
    if store.exists():raise ValueError('Preserve existing store')
    for name,data in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,data)
    dump(store/'imports.json',combined)
    print(json.dumps({'result':'PASS','candidate_contracts':len(entries),'counts':inventory['counts']}))
if __name__=='__main__':main()
