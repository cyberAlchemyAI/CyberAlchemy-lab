"""Contract controls and exact predecessor/semantic-inventory alignment."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'execution'))
import support as s
import contracts as c
import build_contracts

build_contracts.build()
controls=[]
def positive(name,fn):
    fn();controls.append({'name':name,'result':'pass','expected':'accepted'})
def negative(name,fn):
    try:fn()
    except Exception as e:
        controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(e).splitlines()[0]})
        return
    raise AssertionError('unexpected acceptance '+name)

for schema in sorted((HERE/'contracts').glob('*.schema.json')):
    positive('schema-well-formed-'+schema.name,lambda schema=schema:c.load_schema(schema.name.removesuffix('.schema.json')))
proposal=s.read(s.V2/'s13/exact-contract-scope-kind-proposal.json')
limits=s.read(s.V2/'s17/preflight-bounds.json')['limits']
policy={'schema':'relational.resource-policy/v3','work_limits':{k:v for k,v in limits.items() if k!='lean_stage_seconds'},'stage_seconds':60,'run_seconds':600,'memory_bytes':4294967296,'memory_mode':'advisory','output_bytes':4194304,'max_parallel_workers':1}
request={'schema':'relational.qualification-request/v3','operation':'qualify','source_profile':'rich-positive-recursive-v2','proposal':proposal,'resource_policy':policy,'layout':'staged','build_mode':'warm'}
positive('strict-request-accepts-bound-v2-proposal',lambda:c.validate('request',request))
bad=copy.deepcopy(request);bad['proposal']['before']['schema']='relational.baseline/v3'
negative('reject-v2-baseline-relabeled-v3',lambda:c.validate('request',bad))
bad=copy.deepcopy(request);bad['caller_obligations']=[]
negative('reject-caller-obligation-selection',lambda:c.validate('request',bad))
bad=copy.deepcopy(request);bad['proposal']['after']['producers'][0]['class']='user-observation'
negative('reject-new-unselected-producer-class',lambda:c.validate('request',bad))
bad=copy.deepcopy(policy);bad['work_limits']['domain']=999
negative('reject-work-ceiling-increase',lambda:c.validate('resource-policy',bad))
negative('reject-duplicate-json-key',lambda:c.decode(b'{"a":1,"a":2}'))
negative('reject-NaN',lambda:c.decode(b'{"a":NaN}'))
negative('reject-numeric-overflow',lambda:c.decode(b'{"a":1e999}'))
negative('reject-deep-json',lambda:c.decode(b'['*65+b'0'+b']'*65))
negative('reject-oversized-input',lambda:c.decode(b' '*4194305))
positive('quoted-braces-do-not-increase-depth',lambda:c.decode(json.dumps({'text':'{'*100}).encode()))
for unsafe in ['../escape','a/../escape','/absolute','C:\\private\\file']:
    negative('reject-unsafe-binding-'+unsafe,lambda unsafe=unsafe:c.validate('binding',{'kind':'repo','path':unsafe,'sha256':'a'*64}))

shape_binding={'kind':'repo','path':'shape-only-fixture','sha256':'a'*64}
manifest={'schema':'relational.proof-manifest/v3','identity':{k:'a'*64 for k in ['request','proposal','baseline','profile','catalog','toolchain','source_profile']},'change_class':'rule-only','witness':{'layout':'staged','modules':[{'role':r,'module':'Fixture_'+r,'source':shape_binding,'olean':shape_binding} for r in ['data','typed','closure','expansion']]},'obligations':[o['id'] for o in c.required_inventory('rule-only')],'general':shape_binding,'projection':shape_binding,'dependencies':shape_binding,'bound_result':shape_binding,'generator':shape_binding,'authority_effect':'none'}
positive('exact-staged-inventory-shape',lambda:c.validate_manifest_inventory(manifest,'rule-only'))
for n in [0,3,5]:
    bad=copy.deepcopy(manifest);bad['witness']['modules']=(bad['witness']['modules']+[bad['witness']['modules'][0]])[:n]
    negative('reject-module-count-'+str(n),lambda bad=bad:c.validate_manifest_inventory(bad,'rule-only'))
bad=copy.deepcopy(manifest);bad['witness']['modules'].reverse()
negative('reject-module-role-order',lambda:c.validate_manifest_inventory(bad,'rule-only'))
bad=copy.deepcopy(manifest);bad['obligations'].pop()
negative('reject-shrunken-obligation-inventory',lambda:c.validate_manifest_inventory(bad,'rule-only'))
negative('reject-register-inventory-as-rule-only',lambda:c.validate_manifest_inventory(manifest,'register'))
resources={'enforcement':'advisory','outcome':'completed','events':[],'policy_identity':c.identity(policy)}
qualified={'schema':'relational.qualification-result/v3','status':'qualified-candidate','request_identity':c.identity(request),'run_id':'shape-fixture','manifest':manifest,'claims':[],'resource_report':resources,'payload':shape_binding,'complete_closure':True,'application_authorized':False,'authority_effect':'none'}
positive('qualified-result-shape',lambda:c.validate('result',qualified))
bad=copy.deepcopy(qualified);bad['application_authorized']=True
negative('saved-result-cannot-authorize-application',lambda:c.validate('result',bad))
bad=copy.deepcopy(qualified);bad['resource_report']['outcome']='oom'
negative('oom-cannot-be-qualified',lambda:c.validate('result',bad))
for status in ['invalid','unsupported','unknown-resource','cancelled','unsupported-policy']:
    failure={'schema':'relational.qualification-result/v3','status':status,'request_identity':c.identity(request),'run_id':'shape-fixture','reason':'refused for control','stage':'fixture','claims':[],'resource_report':resources,'complete_closure':False,'application_authorized':False,'authority_effect':'none'}
    positive('failure-variant-'+status,lambda failure=failure:c.validate('result',failure))
    bad=copy.deepcopy(failure);bad['complete_closure']=True
    negative('failure-cannot-claim-closure-'+status,lambda bad=bad:c.validate('result',bad))

catalog=c.catalog();legacy=s.read(s.V2/'s15/obligation-catalog.json')
s.require(catalog['change_classes']==legacy['change_classes'] and catalog['obligations']==legacy['obligations'],'catalog weakened or changed')
lean=(HERE.parent/'p00/EvidenceSemantics.lean').read_text()
camel=['snapshotShape','sourceCurrent','profileCatalogCurrent','referenceImmutability','producerPolicy','projectionExact','kindProjectionExact','unaryViewExact','sealedDerivationExact','sourceSupportExact','typedTheory','protectedLineage','derivationSoundness','closureAdequacy','completeClosure','sourceInterpretation','conditionConsistency']
registration=lean.split('def registrationObligations',1)[1].split('def requiredObligations',1)[0]
import re
s.require(re.findall(r'\.([a-zA-Z]+)',registration)==camel,'P00 normative catalog ordering mismatch')
positive('P00-catalog-exact-order-agrees',lambda:None)
coverage=s.read(HERE/'coverage.json')
s.require(len(coverage['predecessor_tasks'])==19 and len(coverage['concepts'])==17 and len(coverage['relations'])==41,'coverage mismatch')
s.require(coverage['retained_declarations']==176,'declaration scope drift')
for b in s.read(HERE/'contract-source-bindings.json')['bindings']:s.check(b)
s.write(HERE/'request-fixture.json',request)
s.write(HERE/'contract-controls.json',{'result':'pass','controls':controls,'scope':'Schema/transport/inventory controls only; shape bindings are not proof qualification.','formal_inventory_alignment':True})
s.accept('P01',[
    'All 19 predecessor tasks, 17 concepts, 41 relations and the scoped 176-declaration inventory have explicit preserved/extension dispositions; all seven extensions are selected.',
    'Seven closed schemas and tagged outcome variants align with the independently compiled P00 inventory; the exact 17/20/18 obligation selections are retained and shrunken/reordered inventories reject.',
    'Explicit named v2 adaptation, immutable source-schema bindings, strict JSON and CLI/inspection boundaries are documented and exercised by positive and negative controls.'
],controls,extra=[HERE/'contracts.py',HERE/'build_contracts.py',HERE/'run_p01.py',HERE/'contract-source-bindings.json',HERE/'contract-controls.json',HERE/'request-fixture.json'])
print('P01 accepted: '+str(len(controls))+' contract controls')
