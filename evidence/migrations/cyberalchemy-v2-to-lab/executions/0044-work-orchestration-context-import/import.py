"""Import an isolated source-qualified Work Orchestration context and ontology candidate."""
import json,sys,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREFIX='work-orchestration/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
PREV=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0044'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_source(profile,nodes,relations,capability):
    if profile['product_capability_ref']!=capability['id'] or profile['ontology_type']!='business-domain':raise ValueError('Wrong capability/profile')
    ns=nodes['nodes'];rs=relations['relations'];vocab=relations['relation_vocabulary']
    if len({n['id'] for n in ns})!=len(ns):raise ValueError('Duplicate concept identity')
    if len({r['id'] for r in rs})!=len(rs):raise ValueError('Duplicate relation identity')
    ids={n['id']:n for n in ns};types={v['type']:v for v in vocab}
    if len(types)!=len(vocab):raise ValueError('Duplicate relation signature')
    for n in ns:
        if n['authority_effect']!='none' or not tool.text(n.get('owner_route')):raise ValueError('Invalid concept authority/owner')
    for r in rs:
        if r['source'] not in ids or r['target'] not in ids:raise ValueError('Dangling relation endpoint')
        if r['type'] not in types:raise ValueError('Undeclared relation kind')
        t=types[r['type']]
        if ids[r['source']]['role'] not in t['source_roles'] or ids[r['target']]['role'] not in t['target_roles']:raise ValueError('Relation role mismatch')
        if r['authority_effect']!='none':raise ValueError('Relation grants authority')
    return {'concepts':len(ns),'relations':len(rs),'relation_kinds':len(types),'source_blocked_concepts':[n['id'] for n in ns if n.get('candidate_status')=='blocked']}
def build():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Capability import drift')
    for b in tool.read(HERE.parent/'0043-trusted-dataset-context-import/verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous context drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};snapshots=[]
    for b in plan['sources']:
        p=(SOURCE if b['root']=='current' else ROOT.parent/'cya-orquestrator')/b['path']
        if tool.sha(p)!=b['sha256']:raise ValueError('Source drift')
        name=Path(b['path']).name;target=HERE/b['snapshot']
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes():raise ValueError('Preserve snapshot')
        target.write_bytes(p.read_bytes());snapshots.append(bind(target))
        if b['root']=='current' and target.suffix=='.json' and target.parent==HERE/'source':docs[name]=tool.read(target)
    spec=importlib.util.spec_from_file_location('wo_source_validator',HERE/'source/scripts/validate.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    validator.PACKAGE_ROOT=HERE/'source';validator.REPOSITORY_ROOT=HERE/'evidence-root'
    validator.SHARED_CAPABILITY_SCHEMA=validator.REPOSITORY_ROOT/'cyberAlchemy-v2/capability/schemas/capability.schema.json'
    source_validation=validator.validate()
    if source_validation['status']!='PASS':raise ValueError(source_validation['errors'])
    dump(HERE/'source-validation.json',source_validation)
    profile=docs['profile.json'];capability=next(i for i in tool.read(PREV/'imports.json') if i['id']==profile['product_capability_ref'])
    if capability['source_record']!=docs['product-capability.json']:raise ValueError('Capability source mismatch')
    counts=validate_source(profile,docs['nodes.json'],docs['relations.json'],capability)
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'owner_ref':profile['meaning_owner']}
    ontology={**base,'node_id':'lab:ontology-contexts/work-orchestration#ontology','kind':'ontology','name':'Bounded Composite Work','version':'source-snapshot-0044','concept_refs':['source/nodes.json#/nodes/'+str(i) for i in range(counts['concepts'])],'relation_ids':[r['id'] for r in docs['relations.json']['relations']],'boundaries':['Source business ontology only; system implementation and runtime activation are separate.','Preserve source candidate and blocked postures; source relationships do not grant authority.']}
    context={**base,'node_id':'lab:ontology-contexts/work-orchestration#context','kind':'context','purpose':capability['capability']['outcome'],'identity_boundary':'Bounded Work Orchestration business meaning, source-qualified concepts and relations; not a scheduler selection or a global ontology merger.','profile_ref':'source/profile.json','relevance':[capability['capability']['node_id'],ontology['node_id']]}
    contracts=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json'
        Draft202012Validator(tool.read(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'source_graph':{'nodes':docs['nodes.json']['nodes'],'relations':docs['relations.json']['relations'],'relation_vocabulary':docs['relations.json']['relation_vocabulary']},'capability_binding':{'inventory':bind(PREV/'imports.json'),'id':capability['id'],'node_id':capability['capability']['node_id']},'counts':counts,'snapshots':snapshots,'source_bindings':plan['sources'],'contracts':contracts,'authority_effect':'none','scope':'isolated source-qualified context import','source_validation':source_validation,'evidence_recovery':'Original pinned evidence recovered from ../cya-orquestrator; package copied from ../cyberAlchemy-v2 without modification','limitations':['Concepts and relation semantics retain source shapes; not globally normalized or admitted.','Context profile is the pinned source profile, not a newly admitted Lab execution profile.','Historical evidence references remain source metadata; downstream runtime and recovery tests not executed.','No automatic ontology merging or runtime activation.']}
    for b in plan['sources']:
        if tool.sha((SOURCE if b['root']=='current' else ROOT.parent/'cya-orquestrator')/b['path'])!=b['sha256']:raise ValueError('Source changed')
    dump(HERE/'context.json',context);dump(HERE/'ontology.json',ontology);dump(HERE/'bundle.json',bundle);dump(STORE/'bundle.json',bundle)
    # Include exact companion source snapshots so local refs resolve after recovery.
    for b in plan['sources']:
        p=HERE/b['snapshot'];target=STORE/b['snapshot'];target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes():raise ValueError('Store snapshot drift')
        target.write_bytes(p.read_bytes())
    return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
