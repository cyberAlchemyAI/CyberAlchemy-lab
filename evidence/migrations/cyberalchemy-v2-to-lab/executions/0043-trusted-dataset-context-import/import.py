"""Preserve dataset source registries without inventing typed graph relationships."""
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';STORE=ROOT/'.local/ontology-context-import-0043';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0042-hosted-exchange-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-MATERIALIZE-TRUSTED-DATASET'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_source(profile,ontology,definitions,cap):
    if profile['product_capability_id']!=ID or profile['ontology_id']!=ontology['ontology_id'] or cap['id']!=ID:raise ValueError('Wrong context binding')
    names=[]
    for key in ['entities','events','operations']:
        if not tool.strings(ontology[key]):raise ValueError('Empty concept registry')
        names+=ontology[key]
    if len(names)!=len(set(names)):raise ValueError('Duplicate source concept')
    rules=ontology['rules']
    if len({r['id'] for r in rules})!=len(rules) or any(not tool.text(r.get('statement')) for r in rules):raise ValueError('Invalid source rules')
    defs=definitions['definitions']
    if len({d['term'] for d in defs})!=len(defs) or any(not tool.text(d.get('meaning')) for d in defs):raise ValueError('Invalid definitions')
    if cap['product']['name']!='Trusted Dataset Materialization' or cap['capability']['product_ref']!=cap['product']['node_id']:raise ValueError('Standalone Product assignment lost')
    return {'named_concepts':len(names),'entities':len(ontology['entities']),'events':len(ontology['events']),'operations':len(ontology['operations']),'rules':len(rules),'definitions':len(defs),'typed_relationships':0,'relationship_posture':'not-authored-in-source-ontology'}
def build():
    for folder in [PREV,CAPS]:
        for b in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};snapshots=[]
    for b in plan['sources']:
        source=SOURCE/b['path']
        if tool.sha(source)!=b['sha256']:raise ValueError('Source drift')
        p=HERE/'source'/b['snapshot'];p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and p.read_bytes()!=source.read_bytes():raise ValueError('Snapshot drift')
        p.write_bytes(source.read_bytes());docs[b['snapshot']]=tool.read(p);snapshots.append(bind(p))
    cap=next(c for c in tool.read(CAPS/'imports.json') if c['id']==ID)
    if cap['source_record']!=docs['product-capability.json']:raise ValueError('Capability source changed')
    counts=validate_source(docs['profile.json'],docs['ontology.json'],docs['definitions.json'],cap)
    refs=['source/ontology.json#/'+key+'/'+str(i) for key in ['entities','events','operations'] for i in range(len(docs['ontology.json'][key]))]
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**base,'node_id':'lab:ontology-contexts/trusted-dataset#ontology','kind':'ontology','name':'Trusted Dataset Materialization source context','version':'source-snapshot-0043','concept_refs':refs,'relation_ids':[],'boundaries':['Source concepts are name lists with five rules; typed relationships are not authored.','Pipeline and physical bindings are preserved evidence, not executed behavior.']}
    context={**base,'node_id':'lab:ontology-contexts/trusted-dataset#context','kind':'context','purpose':cap['capability']['outcome'],'identity_boundary':'Standalone Trusted Dataset Materialization Product context; work orchestration is a dependency, not Product ownership.','profile_ref':'source/profile.json','relevance':[cap['product']['node_id'],cap['capability']['node_id'],ontology['node_id']]}
    contracts=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(tool.read(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'source_ontology':docs['ontology.json'],'definitions':docs['definitions.json'],'counts':counts,'snapshots':snapshots,'source_bindings':plan['sources'],'contracts':contracts,'capability_binding':{'inventory':bind(CAPS/'imports.json'),'id':ID,'node_id':cap['capability']['node_id'],'product_node_id':cap['product']['node_id']},'authority_effect':'none','limitations':['No typed relationship or branch semantics inferred from concept names or rule prose.','SourceCheckpoint, PublicationReceipt and physical history definitions remain in the separate definition registry; not silently added as source ontology entities.','Profile references to code/generated outputs remain source metadata; snapshot is not a standalone executable package.','No ETL, publication, connector, SQL or recovery execution.']}
    for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
    dump(STORE/'bundle.json',bundle)
    for p in (HERE/'source').iterdir():
        t=STORE/'source'/p.name;t.parent.mkdir(parents=True,exist_ok=True)
        if t.exists() and t.read_bytes()!=p.read_bytes():raise ValueError('Store snapshot drift')
        t.write_bytes(p.read_bytes())
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
