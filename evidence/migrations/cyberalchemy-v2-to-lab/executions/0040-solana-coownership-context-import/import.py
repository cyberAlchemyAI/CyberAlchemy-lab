"""Preserve the core KEP source graph with explicit external Product closure."""
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';STORE=ROOT/'.local/ontology-context-import-0040';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0039-three-layer-recovery-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-REALIZE-NO-PRICE-SOLANA-COOWNERSHIP'
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
    if missing or external:raise ValueError('Unresolved or unexpected external endpoint')
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
    profile=docs['profile.json'];thesis=docs['product-thesis.record.json']
    source={**profile,'nodes':docs['nodes.json']['nodes'],'relations':docs['relations.json']['relations'],'rules':docs['rules.json']['rules'],'proof_requirements':docs['proof-requirements.json']['proof_requirements'],'residue':docs['residue.json']}
    definition_source=next(v for v in docs['sources.json']['sources'] if v['source_id']=='SRC-KEP-SOL-DEFINITIONS')
    if definition_source['sha256']!=tool.sha(HERE/'source/DEFINITIONS.md'):raise ValueError('Definition binding stale')
    cap=next(i for i in tool.read(CAPS/'imports.json') if i['id']==ID)
    if cap['source_record']!=docs['product-capability.json']:raise ValueError('Capability source drift')
    if profile['ontology_id']!=cap['source_record']['business_ontology_ref']:raise ValueError('Wrong ontology profile')
    known={n['id'] for n in source['nodes']}|{r['rule_id'] for r in source['rules']}|{p['proof_id'] for p in source['proof_requirements']}
    for binding in docs['definition-bindings.json']['bindings']:
        if not set(binding['ontology_refs'])<=known:raise ValueError('Dangling definition binding')
    external={}
    counts=validate_graph(source,external)
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'owner_ref':thesis['owner_route']}
    ontology={**base,'node_id':'lab:ontology-contexts/solana-coownership#ontology','kind':'ontology','name':'No-Price Solana Co-ownership business context','version':'source-snapshot-0040','concept_refs':['source/nodes.json#/nodes/'+str(i) for i in range(counts['concepts'])],'relation_ids':[r['id'] for r in source['relations']],'boundaries':['Source Product meaning only; Lab admission and operational authority remain separate.','All relationship endpoints resolve within this source graph; no external concepts merged.']}
    context={**base,'node_id':'lab:ontology-contexts/solana-coownership#context','kind':'context','purpose':cap['capability']['outcome'],'identity_boundary':'Source Solana co-ownership meaning: signing-key bindings, exact program state, atomic grants, envelope commitments and replay identity; no runtime execution or deployment.','profile_ref':'source/profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    contracts=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(tool.read(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'source_graph':source,'definition_bindings':docs['definition-bindings.json'],'external_endpoints':external,'source_bindings':plan['sources'],'snapshots':snapshots,'contracts':contracts,'counts':counts,'capability_binding':{'inventory':bind(CAPS/'imports.json'),'id':ID,'node_id':cap['capability']['node_id']},'authority_effect':'none','limitations':['Source construction and evidence postures remain preserved; not promoted to Lab admission.','Source declares no relation role signatures; validation covers explicit meanings and endpoint closure only.','Source proof requirements remain evidence requirements, not newly executed tests.','Context profile_ref points to source ontology metadata; not an admitted execution profile.']}
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
