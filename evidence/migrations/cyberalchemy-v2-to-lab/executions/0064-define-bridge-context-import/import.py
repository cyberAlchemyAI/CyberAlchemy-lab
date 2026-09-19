import json,sys,tarfile,subprocess,os
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];CAPS=HERE.parent/'0035-definition-card-import';BUSINESS=HERE.parent/'0062-shared-meaning-context-import';SYSTEM=HERE.parent/'0063-define-session-context-import';STORE=ROOT/'.local/ontology-context-import-0064';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/define/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    content=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def graph_check(nodes,relations,profile,external):
    ids=[n['id'] for n in nodes];edges=[e['id'] for e in relations]
    if len(ids)!=len(set(ids)) or len(edges)!=len(set(edges)):raise ValueError('Duplicate identity')
    if set(ids)&set(external):raise ValueError('Child identity redefined')
    if profile['authority_effect']!='none' or any(d['authority_effect']!='none' for d in nodes+relations):raise ValueError('Authority escalation')
    universe=set(ids)|set(external)
    for e in relations:
        if e['source'] not in universe or e['target'] not in universe:raise ValueError('Unresolved endpoint')
        if e['type'] not in profile['allowed_relation_types']:raise ValueError('Unknown relation kind')
def build():
    for folder in [BUSINESS,SYSTEM,CAPS]:
        for entry in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
    for entry in tool.read(HERE/'package-inputs.json'):
        if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
    r=tool.read;p=PACKAGE/PREFIX;nodes=r(p/'nodes.json')['nodes'];relations=r(p/'relations.json')['relations'];profile=r(p/'profile.json')
    external={}
    for name,folder,path,key in [('business',BUSINESS,'business-ontology/NODES.json','id'),('system',SYSTEM,'system-ontology/NODES.json','node_id')]:
        for i,node in enumerate(r(p/path)['nodes']):
            qualified=name+'::'+node[key]
            if any(qualified in [e['source'],e['target']] for e in relations):external[qualified]={'context_bundle':bind(folder/'bundle.json'),'source_ref':'package/'+PREFIX+path+'#/nodes/'+str(i)}
    graph_check(nodes,relations,profile,external)
    result=subprocess.run([sys.executable,str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation drift')
    cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-DEFINE-SHARED-MEANING')
    if cap['source_record']!=r(p/'capabilities/define-shared-meaning.product-capability.json'):raise ValueError('Capability drift')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/define-bridge#ontology','name':'Define Business/System Bridge','version':'source-qualified-0064','concept_refs':['package/'+PREFIX+'nodes.json#/nodes/'+str(i) for i in range(len(nodes))],'relation_ids':['package/'+PREFIX+'relations.json#/relations/'+str(i) for i in range(len(relations))],'boundaries':['Parent owns two bridge nodes; business and system endpoints resolve through exact imported child contexts.','Declared alignment is not measured product value or implementation conformance.','Child system compiler flag and unadmitted larger ontology header remain unchanged.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/define-bridge#context','purpose':'Trace Define business meaning to proposed session operations while preserving evidence gaps and child ownership.','identity_boundary':'Parent bridge relations across the exact business and system contexts; no redefinition or promotion of child nodes.','profile_ref':'package/'+PREFIX+'profile.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(BUSINESS/'context.json')['node_id'],r(SYSTEM/'context.json')['node_id']]}
    headers=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'counts':json.loads(result.stdout)['summary'],'contracts':headers,'external_nodes':external,'child_contexts':[bind(folder/'bundle.json') for folder in [BUSINESS,SYSTEM]],'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'source_recovery':bind(HERE/'source-recovery.json'),'source_validation':bind(HERE/'source-validation.json'),'parent_material_selection':bind(HERE/'parent-material-selection.json'),'authority_effect':'none','limitations':['Business/system bridge traceability only; no runtime implementation or product outcome claim.','Twenty handled definition records remain candidate example evidence; construction handoffs remain empty and blocked.','Eleven parent residue entries remain open evidence; child compiler and schema limits persist.','Only parent thesis fingerprint and size are explicit successors; exact imported child snapshots remain unchanged.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
