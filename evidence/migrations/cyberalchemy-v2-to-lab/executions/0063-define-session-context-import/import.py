import json,sys,tarfile,subprocess,os
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0062-shared-meaning-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0063';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/define/system-ontology/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    content=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def graph_check(nodes,relations,profile):
    ids=[n['node_id'] for n in nodes];edges=[e['relation_id'] for e in relations]
    if len(ids)!=len(set(ids)) or len(edges)!=len(set(edges)):raise ValueError('Duplicate identity')
    if profile['authority_effect']!='none' or any(d['authority_effect']!='none' for d in nodes+relations):raise ValueError('Authority escalation')
    if profile['implementation_status']!='not-implemented' or any(n['implementation_status']!='not-implemented' for n in nodes):raise ValueError('Implementation escalation')
    for e in relations:
        if e['from_node_id'] not in ids or e['to_node_id'] not in ids:raise ValueError('Dangling relation')
        if e['type'] not in profile['allowed_relation_types']:raise ValueError('Unknown relation kind')
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
    if result.returncode!=2 or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation drift')
    cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-DEFINE-SHARED-MEANING')
    if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/define/capabilities/define-shared-meaning.product-capability.json'):raise ValueError('Capability drift')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/define-session#ontology','name':'Define Session System Model','version':'source-qualified-0063','concept_refs':['package/'+PREFIX+'NODES.json#/nodes/'+str(i) for i in range(len(nodes))],'relation_ids':['package/'+PREFIX+'RELATIONS.json#/relations/'+str(i) for i in range(len(relations))],'boundaries':['Candidate session model; indexes preserve exact source-owned node and connection identities.','Compiler conformance is not evaluable; runtime remains not implemented.','Uses the explicitly unadmitted larger ontology header from execution 0048.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/define-session#context','purpose':'Model how Define sessions preserve questions, answers, evidence, revisions and Definition Pack exports.','identity_boundary':'One proposed Define session runtime; source-owned graph and candidate limits remain explicit.','profile_ref':'package/'+PREFIX+'PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    entry=next(e for e in registry['entries'] if e['target_id']=='type.context');schema=(ROOT/entry['binding']['path']).parent/'schema.json'
    Draft202012Validator(r(schema)).validate(context)
    candidate_schema=HERE/'ontology.schema.json';Draft202012Validator(r(candidate_schema)).validate(ontology)
    bundle={'context':context,'ontology':ontology,'counts':json.loads(r(HERE/'source-validation.json')['stdout'])['summary'],'context_schema':bind(schema),'ontology_schema':{'binding':bind(candidate_schema),'admission':'not-granted','source_execution':'0048-agent-reasoning-context-import'},'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'source_recovery':bind(HERE/'source-recovery.json'),'source_validation':bind(HERE/'source-validation.json'),'authority_effect':'none','limitations':['65-node session model only; compiler conformance remains not evaluable and implementation remains not implemented.','All 23 source selections are exact recovered versions, not a claim of latest global authority.','Five residue entries remain visible.','Ontology header uses an unadmitted candidate schema; admitted registry unchanged.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
