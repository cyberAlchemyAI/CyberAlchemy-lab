"""Import a coverage plan without promoting authored tests to passing evidence.
Open questions: README.md.
"""
import json,os,re,subprocess,sys,tarfile
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0068-essays-system-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0069';PACKAGE=STORE/'package';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';PREFIX=BASE+'conformance/bridge-ontology';OBL='cyberAlchemy-v2/essays/capabilities/agent-runtime/obligations/agent-runtime.obligations.json'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
r=tool.read
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def model_check(doc,obligations):
 rows=doc['coverage'];ids=[x['obligation'] for x in rows];expected=[x['obligation_id'] for x in obligations]
 if len(ids)!=len(set(ids)) or len(expected)!=len(set(expected)) or set(ids)!=set(expected):raise ValueError('Obligation closure failure')
 if doc['authority_effect']!='none':raise ValueError('Authority escalation')
 links=[]
 for i,row in enumerate(rows):
  if row['result']!='partial':raise ValueError('Proof state changed')
  if not row['implementation']:raise ValueError('Missing implementation mapping')
  for kind in ['implementation','evidence']:
   if len(row[kind])!=len(set(row[kind])):raise ValueError('Duplicate reference')
   for ref in row[kind]:
    file,sep,anchor=ref.partition('#');path=(PACKAGE/BASE/'implementation'/file).resolve()
    if not path.is_relative_to((PACKAGE/BASE).resolve()):raise ValueError('Reference escapes runtime scope')
    if not path.is_file():raise ValueError('Missing reference')
    if sep and not re.search(r'#\[(?:tokio::)?test\]\s*(?:async\s+)?fn\s+'+re.escape(anchor)+r'\s*\(',path.read_text()):raise ValueError('Missing authored test')
    links.append({'coverage_index':i,'kind':kind,'source_ref':ref,'path':str(path.relative_to(PACKAGE)),'sha256':tool.sha(path),'anchor':anchor or None})
 return links
def build():
 for folder in [PREV,CAPS]:
  for b in r(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Frozen predecessor drift')
 PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as a:a.extractall(PACKAGE,filter='data')
 for b in r(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 doc=r(PACKAGE/PREFIX/'COVERAGE.json');ob=r(PACKAGE/OBL)['obligations'];links=model_check(doc,ob)
 for name in [OBL,BASE+'domainspec/PREDECESSORS.json',BASE+'domainspec/generated/compile-receipt.json']:
  if (PACKAGE/name).read_bytes()!=(ROOT/'.local/ontology-context-import-0068/package'/name).read_bytes():raise ValueError('System predecessor mismatch')
 result=subprocess.run([sys.executable,str(PACKAGE/PREFIX/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validation mismatch')
 report=json.loads(result.stdout)
 if report['overall']!='FLAG' or report['partial']!=20 or report['pass_like']!=0 or report['errors']:raise ValueError('Source proof state changed')
 cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME')
 if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability drift')
 registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-conformance-bridge#ontology','name':'Essays Runtime Conformance Coverage Plan','version':'source-qualified-0069','concept_refs':['package/'+PREFIX+'/COVERAGE.json#/coverage/'+str(i) for i in range(20)],'relation_ids':[],'boundaries':['Coverage rows are obligation mappings, not new capabilities or authored graph edges.','All twenty proof states remain partial; test source presence is not execution evidence.','Historical DomainSpec receipt remains exact; execution 0068 successor is separately recorded.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-conformance-bridge#context','purpose':'Locate implementation and authored test references for each Essays runtime obligation and preserve missing evidence.','identity_boundary':'Candidate coverage plan only; no runtime or independent conformance claim.','profile_ref':'package/'+PREFIX+'/PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(PREV/'context.json')['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
 dump(HERE/'reference-bindings.json',links)
 gaps={'empty_evidence_obligations':[x['obligation'] for x in doc['coverage'] if not x['evidence']],'authored_tests':sorted({x['source_ref'] for x in links if x['anchor']}),'runtime_tests_executed':False,'source_residue':r(PACKAGE/PREFIX/'RESIDUE.json'),'authority_effect':'none'};dump(HERE/'evidence-gaps.json',gaps)
 bundle={'context':context,'ontology':ontology,'contracts':contracts,'counts':{'coverage_rows':20,'partial':20,'proven':0,'distinct_authored_tests':len(gaps['authored_tests']),'empty_evidence_rows':len(gaps['empty_evidence_obligations']),'reference_occurrences':len(links),'residue':len(gaps['source_residue']['residue'])},'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'source_validation':bind(HERE/'source-validation.json'),'reference_bindings':bind(HERE/'reference-bindings.json'),'evidence_gaps':bind(HERE/'evidence-gaps.json'),'system_context':bind(PREV/'bundle.json'),'capability_binding':bind(CAPS/'imports.json'),'authority_effect':'none','limitations':['Client parity has no authored evidence link.','Runtime tests are source references only; this import runs structural checks, not the runtime campaign.','All six original residue statements remain historical source statements; they do not override user authorization for subsequent local work.','Implementation binding and independent conformance remain separate checks.']}
 for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
