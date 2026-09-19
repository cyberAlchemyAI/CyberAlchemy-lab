import json,sys,tarfile,subprocess,os
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0065-essays-agent-business-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0066';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/essays/capabilities/agent-runtime/authority-ontology/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    content=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def graph_check(nodes,relations,profile):
    ids=[n['id'] for n in nodes];edges=[e['id'] for e in relations]
    if len(ids)!=len(set(ids)) or len(edges)!=len(set(edges)):raise ValueError('Duplicate identity')
    if profile['authority_effect']!='none' or any(d['authority_effect']!='none' for d in nodes+relations):raise ValueError('Authority escalation')
    for e in relations:
        if e['source'] not in ids or e['target'] not in ids:raise ValueError('Dangling relation')
        if not isinstance(e['type'],str) or not e['type']:raise ValueError('Missing relation kind')
def build():
    for folder in [PREV,CAPS]:
        for entry in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
    for entry in tool.read(HERE/'package-inputs.json'):
        if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
    r=tool.read;p=PACKAGE/PREFIX;nodes=r(p/'NODES.json')['nodes'];relations=r(p/'RELATIONS.json')['relations'];profile=r(p/'PROFILE.json');graph_check(nodes,relations,profile)
    result=subprocess.run([sys.executable,str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation drift')
    cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME')
    if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability drift')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-authority#ontology','name':'Essays Agent Runtime Authority Model','version':'source-qualified-0066','concept_refs':['package/'+PREFIX+'NODES.json#/nodes/'+str(i) for i in range(len(nodes))],'relation_ids':['package/'+PREFIX+'RELATIONS.json#/relations/'+str(i) for i in range(len(relations))],'boundaries':['Candidate authority-governance model; source identities and ownership remain explicit.','No measured outcome, runtime conformance, definition promotion or operational effect.','All five selected evidence files match their declared fingerprints; pending security-owner gates remain explicit.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-authority#context','purpose':'Model owner-controlled grants, leases, proposals, browser-effect boundaries, credentials and uncertain-effect reconciliation.','identity_boundary':'One owner-controlled writing workspace across clients; proposals and browser evidence grant no editorial or external-action authority.','profile_ref':'package/'+PREFIX+'PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(PREV/'context.json')['node_id']]}
    headers=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'counts':{'concepts':len(nodes),'relationships':len(relations),'sources':len(r(p/'SOURCES.json')['sources']),'views':len(r(p/'VIEWS.json')['views']),'residue':len(r(p/'RESIDUE.json')['residue'])},'contracts':headers,'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'source_bindings':bind(HERE/'source-bindings.json'),'business_context':bind(PREV/'bundle.json'),'source_validation':bind(HERE/'source-validation.json'),'authority_effect':'none','limitations':['Authority model only; no runtime authorization or enforcement is performed.','Source does not define executable role/relationship signatures; import checks structure and preserves declared meanings.','Two source residue entries and pending security-owner gates remain visible; no approval is granted.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
