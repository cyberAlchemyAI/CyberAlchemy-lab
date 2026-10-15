from pathlib import Path
import sys,re,copy,subprocess
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contracts as c
s=c.s;HERE=c.HERE
sys.path.insert(0,str(s.V1/'inference/derivations'))
import derivation_checker as renderer
s.context('S15',[(s.BASE/'s00/RequirementSemantics.lean','producer classes/source faithful distinction'),(s.BASE/'s01/requirements.json','retained limits and new requirements'),(s.V1/'inference/profile/frontend.py','TheoryValid/roots/normalization'),(s.V1/'evolution/proposals/classifier.py','computed change classification'),(s.V1/'references/resolver.py','exact registry source fields'),(s.PROPOSAL,'S15 baseline contract')],[{'decision':'Structural contract is not independent registration; qualification and replay required before application','basis':'S15/S09 DAG separation'},{'decision':'Same reference retains exact kind/content; new revision for semantic replacement','basis':'explicit reference policy'}])
b=c.fixture();normal=c.validate_baseline(b)['normal'];s.write(HERE/'baseline-example.json',b)
source='import BaselineContract\nnamespace Successor.Baseline.Controls\nopen Inference\ndef theory : Theory := '+renderer.theory_lean(normal)+'\ntheorem nonempty_old_rules : theory.rules ≠ [] := by decide\ntheorem nonempty_baseline_valid : TheoryValid theory := by decide\ntheorem empty_initial_valid : InitialValid theory [] := by decide\n#print axioms nonempty_baseline_valid\nend Successor.Baseline.Controls\n'
(HERE/'BaselineControls.lean').write_text(source)
results=[]
def control(name,fn,positive=False):
 try:fn();s.require(positive,'attack accepted '+name);results.append({'name':name,'result':'pass','outcome':'accepted-structural-contract'})
 except Exception as e:
  if positive:raise
  s.require(not str(e).startswith('attack accepted'),'control failed '+name);results.append({'name':name,'result':'pass','outcome':'rejected','reason':str(e).splitlines()[0]})
def mutate(fn):
 q=copy.deepcopy(b);fn(q);return c.validate_baseline(q)
control('nonempty-old-rule-baseline',lambda:c.validate_baseline(b),True)
control('byte-whitespace-distinct-canonical-identical',lambda:s.require(c.decode(__import__('json').dumps(b))==b,'decode mismatch'),True)
control('same-reference-kind',lambda:c.reference_stability(b['graph'],{'nodes':[{**b['graph']['nodes'][0],'kind':'contract'}]}))
control('same-reference-content',lambda:c.reference_stability(b['graph'],{'nodes':[{**b['graph']['nodes'][0],'content_identity':'0'*64}]}))
control('new-reference-revision',lambda:c.reference_stability(b['graph'],{'nodes':[{**b['graph']['nodes'][0],'ref':{**b['graph']['nodes'][0]['ref'],'version':'v-next'},'kind':'contract'}]}),True)
control('stale-catalog',lambda:mutate(lambda q:q.update(catalog_identity='0'*64)))
control('v1-profile-substitution',lambda:mutate(lambda q:q.update(profile_identity='0'*64)))
control('toolchain-substitution',lambda:mutate(lambda q:q['toolchain'].update(sha256='0'*64)))
control('epoch-drift',lambda:mutate(lambda q:q['context'].update(epoch=1)))
control('duplicate-json-key',lambda:c.decode('{"x":1,"x":2}'))
control('extra-contract-field',lambda:mutate(lambda q:q.update(proof_pass=True)))
control('sealed-conformance-seed',lambda:mutate(lambda q:q['inference']['facts'].append({'predicate':'Conforms','terms':[q['inference']['domain'][0]]})))
control('constant-sealed-rule-head',lambda:mutate(lambda q:q['inference']['rules'].append({'id':'forge','version':'v2','head':{'predicate':'Conforms','terms':[{'constant':q['inference']['domain'][0]}]},'body':[]})))
control('semantic-alias-producer',lambda:mutate(lambda q:q['producers'][-1].update(meaning='member-conformance')))
control('new-scope-outside-domain',lambda:mutate(lambda q:q['inference']['rules'][0]['body'].append({'predicate':'ConformsTo','terms':[{'variable':'x'},{'variable':'y'},{'constant':{'kind':'scope','value':'absent-scope'}}]})))
control('caller-shrunken-profile',lambda:c.validate_profile({**c.profile(),'supported_changes':['register']}))
control('unsupported-mixed-change',lambda:c.obligations('mixed'))
control('generated-exact-rule-only-inventory',lambda:s.require(len(c.obligations('rule-only'))==20 and len({o['id'] for o in c.obligations('rule-only')})==20,'inventory mismatch'),True)
logs=s.compile_modules(HERE/'build',s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','StressTypes','ObligationSemantics'})+[('RequirementSemantics',s.BASE/'s00/RequirementSemantics.lean'),('BaselineContract',HERE/'BaselineContract.lean'),('BaselineControls',HERE/'BaselineControls.lean')])
s.write(HERE/'baseline-controls.json',{'result':'pass','controls':results,'modules':logs,'catalog_inventory':{k:[o['id'] for o in c.obligations(k)] for k in c.catalog()['change_classes']},'claim_ceiling':'Structural contract and binding checks; independent baseline registration deferred S09','authority_effect':'none'})
s.accept('S15',['Actual nonempty old-rule TheoryValid example compiled; contract has no empty-old-rule restriction.','Fixed selected catalog generates exact inventories by computed supported change; profile binds schemas/catalog/policy/formal sources.','Same-reference kind/content, profile/catalog/toolchain drift and sealed producer substitutions rejected.'],controls=results,extra_dependencies=[HERE/'contracts.py',HERE/'BaselineControls.lean',HERE/'selected-profile.json',HERE/'baseline-example.json'])
print('S15 accepted: '+str(len(results))+' controls; nonempty old-rule baseline compiled.')
