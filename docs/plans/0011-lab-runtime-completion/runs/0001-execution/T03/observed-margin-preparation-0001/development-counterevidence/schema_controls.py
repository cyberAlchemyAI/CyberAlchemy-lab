import json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.append(str(ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'))
from jsonschema import Draft202012Validator,FormatChecker
schema=json.loads((HERE/'observed-margin-policy.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
V=Draft202012Validator(schema,format_checker=FormatChecker());template=json.loads((HERE/'UNQUALIFIED-POLICY-TEMPLATE.json').read_bytes());assert not V.is_valid(template)
fixture={**template,'status':'empirically-qualified','execution_identity':{key:'1'*64 for key in template['execution_identity']},'evidence_bindings':[{'path':'synthetic/inert.json','sha256':'2'*64}],'sample_count':1,'phase_upper_bounds_us':{key:1 for key in template['phase_upper_bounds_us']},'uncertainty_reserve_us':1,'gate_overhead_upper_bound_us':1,'valid_until':'2030-01-01T00:00:00Z'}
assert V.is_valid(fixture)
assert not V.is_valid({**fixture,'sample_count':True})
assert not V.is_valid({**fixture,'undeclared_effect_override':True})
assert not V.is_valid({**fixture,'valid_until':'not-a-date'})
report={'schema_version':'lab-T03-margin-schema-pure-controls/v1-candidate','result':'PASS-schema-only','authority_effect':'none','task_complete':False,'synthetic_policy_not_real_qualification':True,'schema_valid':True,'unqualified_null_template_rejected':True,'synthetic_complete_shape_accepted':True,'bool_sample_count_rejected':True,'extra_effect_override_rejected':True,'bad_validity_date_rejected':True,'Lab_runtime_or_lease_constructed':False}
(HERE/'schema-controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'result':report['result'],'result_sha256':hashlib.sha256((HERE/'schema-controls-result.json').read_bytes()).hexdigest()}))
