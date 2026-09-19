"""Preserve the core KEP source graph with explicit external Product closure."""
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';STORE=ROOT/'.local/ontology-context-import-0037';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0036-alchlang-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-GRANT-ENCRYPTED-KNOWLEDGE-COOWNERSHIP'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_graph(source,external):
    if source['capability_ref']!=ID or source['ontology_type']!='business-domain' or source['authority_effect']!='none':raise ValueError('Wrong source boundary')
    nodes=source['nodes'];relations=source['relations'];ids={n['id'] for n in nodes}
    if len(ids)!=len(nodes):raise ValueError('Duplicate source concept')
    if len({r['id'] for r in relations})!=len(relations):raise ValueError('Duplicate source relation')
    missing={r[k] for r in relations for k in ['source','target']}-ids
    if missing!=set(external) or set(external)!={'CA2-PRODUCT-CYBERALCHEMY'}:raise ValueError('Unresolved or unexpected external endpoint')
    for n in nodes:
        if not tool.text(n.get('role')) or not tool.text(n.get('meaning')):raise ValueError('Missing concept meaning')
    for r in relations:
        if not tool.text(r.get('type')) or not tool.text(r.get('meaning')):raise ValueError('Missing relation meaning')
    for key,ident in [('rules','rule_id'),('proof_requirements','proof_id')]:
        rows=source[key]
        if len({r[ident] for r in rows})!=len(rows) or any(not tool.text(r.get('statement')) for r in rows):raise ValueError('Invalid rule/proof set')
    return {'concepts':len(nodes),'relations':len(relations),'external_concepts':len(external),'rules':len(source['rules']),'proof_requirements':len(source['proof_requirements']),'role_signature_validation':'not-declared-by-source'}
def build():
    for folder in [CAPS,PREV]:
        for b in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};snapshots=[]
    for b in plan['sources']:
        path=SOURCE/b['path']
        if tool.sha(path)!=b['sha256']:raise ValueError('Source drift')
        target=HERE/'source'/b['snapshot'];target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=path.read_bytes():raise ValueError('Snapshot drift')
        target.write_bytes(path.read_bytes());snapshots.append(bind(target))
        docs[b['snapshot']]=tool.read(target) if target.suffix=='.json' else target.read_text()
    source=docs['business-ontology.json'];thesis=docs['product-thesis.record.json']
    if source['definition_source']['sha256']!=tool.sha(HERE/'source/DEFINITIONS.md'):raise ValueError('Definition binding stale')
    cap=next(i for i in tool.read(CAPS/'imports.json') if i['id']==ID)
    if cap['source_record']!=docs['product-capability.json']:raise ValueError('Capability source drift')
    parent_nodes=docs['parent-product-nodes.json']['nodes'];matches=[(i,n) for i,n in enumerate(parent_nodes) if n.get('id')=='CA2-PRODUCT-CYBERALCHEMY']
    if len(matches)!=1:raise ValueError('Ambiguous parent Product')
    index,node=matches[0];external={node['id']:{'snapshot_ref':'source/parent-product-nodes.json#/nodes/'+str(index),'record':node}}
    counts=validate_graph(source,external)
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'owner_ref':thesis['owner_route']}
    ontology={**base,'node_id':'lab:ontology-contexts/kep#ontology','kind':'ontology','name':'Knowledge Exchange Protocol business context','version':'source-snapshot-0037','concept_refs':['source/business-ontology.json#/nodes/'+str(i) for i in range(counts['concepts'])]+[external[node['id']]['snapshot_ref']],'relation_ids':[r['id'] for r in source['relations']],'boundaries':['Source Product meaning only; Lab admission and operational authority remain separate.','Parent Product is an explicit external source binding, not a merged identity.']}
    context={**base,'node_id':'lab:ontology-contexts/kep#context','kind':'context','purpose':cap['capability']['outcome'],'identity_boundary':'Core KEP business semantics for exact versions, identities, co-ownership, envelopes and acknowledgements; not a Solana or storage realization.','profile_ref':'source/business-ontology.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    contracts=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(tool.read(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'source_graph':source,'external_endpoints':external,'source_bindings':plan['sources'],'snapshots':snapshots,'contracts':contracts,'counts':counts,'capability_binding':{'inventory':bind(CAPS/'imports.json'),'id':ID,'node_id':cap['capability']['node_id']},'authority_effect':'none','limitations':['Source admitted posture is preserved as provenance, not promoted to Lab admission.','Source declares no relation role signatures; validation covers explicit meanings and endpoint closure only.','Source proof requirements remain evidence requirements, not newly executed tests.','Context profile_ref points to source ontology metadata; not an admitted execution profile.']}
    for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
    dump(STORE/'bundle.json',bundle)
    for p in (HERE/'source').iterdir():
        target=STORE/'source'/p.name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes():raise ValueError('Store snapshot drift')
        target.write_bytes(p.read_bytes())
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
