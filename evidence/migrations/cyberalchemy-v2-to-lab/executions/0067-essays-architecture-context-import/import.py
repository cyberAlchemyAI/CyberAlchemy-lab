import json,sys,tarfile,subprocess,os
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0066-essays-authority-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0067';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/essays/development/agent-runtime/architecture-properties/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    content=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def model_check(types,properties,constraints,views,observations):
    collections=[(types,'type_id'),(properties,'property_id'),(constraints,'constraint_id'),(views,'view_id')]
    for rows,key in collections:
        ids=[row[key] for row in rows]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate identity')
        if any(row['authority_effect']!='none' for row in rows):raise ValueError('Authority escalation')
    type_ids={t['type_id'] for t in types};props={p['property_id']:p for p in properties};cons={c['constraint_id'] for c in constraints}
    for c in constraints:
        if c['subject_type'] not in type_ids or c['property_ref'] not in props:raise ValueError('Unresolved constraint reference')
        if c['on_unknown']!='unsupported':raise ValueError('Unknown evidence promoted')
        if c['operator']!='equals':raise ValueError('Unknown operator')
        value_type=props[c['property_ref']]['value_type']
        if value_type not in ['boolean','budget'] or c['expected_value']!=('true' if value_type=='boolean' else 'selected-profile'):raise ValueError('Source literal contract changed')
    covered=set()
    for view in views:
        ids=view['constraint_ids']
        if len(ids)!=len(set(ids)) or not set(ids)<=cons:raise ValueError('Invalid view reference')
        covered.update(ids)
    if covered!=cons:raise ValueError('View coverage incomplete')
    if observations['projections']!=[] or observations['authority_effect']!='none':raise ValueError('Observation or authority claim added')
def build():
    for folder in [PREV,CAPS]:
        for entry in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
    for entry in tool.read(HERE/'package-inputs.json'):
        if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
    r=tool.read;p=PACKAGE/PREFIX;types=r(p/'ELEMENT-TYPES.json')['element_types'];properties=r(p/'PROPERTIES.json')['properties'];constraints=r(p/'CONSTRAINTS.json')['constraints'];views=r(p/'VIEWS.json')['views'];observations=r(p/'OBSERVATION-PROJECTIONS.json');model_check(types,properties,constraints,views,observations)
    result=subprocess.run([sys.executable,str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation drift')
    cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME')
    if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability drift')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    refs=[]
    for file,key,rows in [('ELEMENT-TYPES.json','element_types',types),('PROPERTIES.json','properties',properties),('CONSTRAINTS.json','constraints',constraints)]:refs += ['package/'+PREFIX+file+'#/'+key+'/'+str(i) for i in range(len(rows))]
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-architecture#ontology','name':'Essays Agent Runtime Architecture Properties','version':'source-qualified-0067','concept_refs':refs,'relation_ids':[],'boundaries':['Source component types, properties and constraints remain distinct; no standalone relation graph is authored.','Expected values retain source string literals; no executable constraint-engine claim.','Empty observation projections establish no measured performance or implementation conformance.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-architecture#context','purpose':'Describe required runtime properties, constraints and evidence boundaries for Essays agent work.','identity_boundary':'Candidate architecture properties only; missing observations remain unsupported rather than inferred as passing.','profile_ref':'package/'+PREFIX+'PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(PREV/'context.json')['node_id']]}
    headers=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'counts':{'element_types':len(types),'properties':len(properties),'constraints':len(constraints),'views':len(views),'observations':0,'sources':5,'residue':len(r(p/'RESIDUE.json')['residue'])},'contracts':headers,'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'authority_context':bind(PREV/'bundle.json'),'source_bindings':bind(HERE/'source-bindings.json'),'source_validation':bind(HERE/'source-validation.json'),'authority_effect':'none','limitations':['Architecture requirement model only; no property satisfaction or runtime behavior established.','Budget constraints refer to selected profiles; no benchmark measurements imported.','Source boolean expectations remain the literal string true, without coercion or an executable evaluator.','Two source residue entries remain; no implementation, admission or external effect is granted.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
