#!/usr/bin/env python3
"""Validate one definition-complete candidate carrier against its bound relation model."""
from __future__ import annotations
import hashlib,importlib.util,json
from pathlib import Path
import jsonschema
LAB=Path(__file__).resolve().parents[2]
ROOT_TYPE=LAB/'authority/artifact-types/artifact-type/v2/artifact.json'
DEFINITIONS=LAB/'authority/definitions/registry.json'
GENERATOR=LAB/'tooling/generators/endpoint_carrier.py'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def roles_for(kind,model):
 out=[]
 for e in model['entries']:
  targets=sorted({p['target_kind'] for p in e['allowed_endpoint_pairs'] if p['source_kind']==kind}); sources=sorted({p['source_kind'] for p in e['allowed_endpoint_pairs'] if p['target_kind']==kind})
  if targets:out.append({'relation_kind_ref':e['relation_kind_id'],'direction':'source','counterpart_kinds':targets})
  if sources:out.append({'relation_kind_ref':e['relation_kind_id'],'direction':'target','counterpart_kinds':sources})
 return sorted(out,key=lambda x:(x['relation_kind_ref'],x['direction']))
def validate_package(root):
 a=load(root/'artifact.json');s=load(root/'schema.json');w=load(root/a['validation_contract']['positive_witness']);reg=load(DEFINITIONS);binding=a['semantic_definition_bindings'][0];mb=a['relation_model_binding'];model=load(LAB/mb['path']);checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 ck('candidate-no-effect',a['status']=='candidate-unadmitted' and a['authority_effect']==w['authority_effect']=='none',{'status':a['status'],'effect':a['authority_effect']})
 ck('artifact-type-v2-root',a['artifact_type_root_binding']['path']==str(ROOT_TYPE.relative_to(LAB)) and a['artifact_type_root_binding']['sha256']==sha(ROOT_TYPE),a['artifact_type_root_binding'])
 ck('current-admitted-definition',reg['current_lookup'].get(binding['definition_ref'].split('@')[0])==binding['definition_ref'] and binding['admission_posture']=='admitted' and sha(LAB/binding['path'])==binding['sha256'],binding)
 ck('relation-model-current',sha(LAB/mb['path'])==mb['sha256'] and model['status']=='candidate-complete-awaiting-owner-review' and model['authority_effect']=='none',mb)
 expected=roles_for(a['classification']['semantic_kind'],model);ck('closed-relation-role-surface',a['relation_roles']==expected and a['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in expected}) and bool(expected),{'declared':a['relation_roles'],'expected':expected})
 ck('closed-schema-current',s.get('additionalProperties') is False and a['schema_digest']==sha(root/'schema.json'),a['schema_digest'])
 errors=[e.message for e in jsonschema.Draft202012Validator(s).iter_errors(w)];ck('positive-witness',not errors,errors)
 hostile=[]
 for rel in a['validation_contract']['negative_witnesses']:
  es=[e.message for e in jsonschema.Draft202012Validator(s).iter_errors(load(root/rel))];hostile.append({'path':rel,'rejected':bool(es),'errors':es})
 ck('five-hostile-rejections',len(hostile)==5 and all(x['rejected'] for x in hostile),hostile)
 allowed={(x['relation_kind_ref'],x['direction'],k) for x in expected for k in x['counterpart_kinds']};actual={(x['relation_kind_ref'],x['direction'],x['counterpart_kind']) for x in w['relation_refs']};ck('fixture-relations-declared',bool(actual) and actual<=allowed,{'actual':sorted(actual),'allowed':sorted(allowed)})
 ck('explicit-non-collapse',bool(a['hostile_non_collapse']) and a['classification']['semantic_kind'] not in a['hostile_non_collapse'] and len(a['orthogonality_rules'])==4,a['hostile_non_collapse'])
 spec=importlib.util.spec_from_file_location('carrier_generator',GENERATOR);mod=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(mod)
 ck('deterministic-projections',(root/'ARTIFACT.md').read_text()==mod.render_artifact(a) and (root/a['validation_contract']['positive_projection']).read_text()==mod.render_instance(a,w),{'artifact':sha(root/'ARTIFACT.md'),'fixture':sha(root/a['validation_contract']['positive_projection'])})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';r={'schema_version':'cyberalchemy-lab-definition-complete-carrier-validation/v1','subject':a['artifact_type_ref'],'result':result,'authority_effect':'none','checks':checks,'materials':{'artifact_sha256':sha(root/'artifact.json'),'schema_sha256':sha(root/'schema.json'),'positive_witness_sha256':sha(root/a['validation_contract']['positive_witness'])},'claim_ceiling':'PASS proves this exact candidate carrier, Definition binding, relation surface, closed schema, fixture, hostile cases, and projections. It admits nothing.'};dump(root/'receipts/validation.json',r);print(json.dumps({'subject':a['artifact_type_ref'],'result':result,'checks':len(checks)},sort_keys=True));return 0 if result=='PASS' else 1
