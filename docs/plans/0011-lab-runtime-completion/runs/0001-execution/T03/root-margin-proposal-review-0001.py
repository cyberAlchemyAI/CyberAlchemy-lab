"""Independent pure review; creates no Lab objects, permits or effects."""
import ast, copy, hashlib, importlib.util, json, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T03/observed-margin-preparation-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(path,pin):
    raw=path.read_bytes();assert sha(raw)==pin,str(path);return raw
manifest=json.loads(exact(P/'source-manifest-0002.json','6c3618f53adbf4a4b528eff5afff70f09008916643d9cdc411d6fddf7903dbc0'))
for row in manifest['files']:
    raw=exact(ROOT/row['path'],row['sha256']);assert len(raw)==row['size_bytes']
boundary=json.loads((P/'BOUNDARIES.json').read_bytes())
for row in boundary['exact_current_preimages_rechecked']:
    raw=exact(ROOT/row['path'],row['sha256']);assert len(raw)==row['size_bytes']
path=P/'margin.py';raw=exact(path,'c9a7fcdce86ebd974259a8b6e0a76c9c6b3d39327cce6151b8488e644d911c50')
spec=importlib.util.spec_from_file_location('_cal_root_margin_pure_review_0001',path)
m=importlib.util.module_from_spec(spec);exec(compile(raw,str(path),'exec'),m.__dict__)
template=json.loads((P/'UNQUALIFIED-POLICY-TEMPLATE.json').read_bytes())
policy={**template,'status':'empirically-qualified','execution_identity':{k:'1'*64 for k in m.IDENTITY_FIELDS},'evidence_bindings':[{'path':'synthetic/inert.json','sha256':'2'*64}],'sample_count':1,'phase_upper_bounds_us':{k:1 for k in m.REMAINING['application-preclaim']},'uncertainty_reserve_us':1,'gate_overhead_upper_bound_us':1,'valid_until':'2031-01-01T00:00:00Z'}
observed=datetime(2030,1,1,tzinfo=timezone.utc)
deadlines={k:(observed+timedelta(microseconds=12)).isoformat() for k in m.DEADLINE_FIELDS}
def decide(p=policy,identity=None,d=deadlines,load=True,checkpoint='application-preclaim'):
    return m.decide(p,p['execution_identity'] if identity is None else identity,d,observed.isoformat(),checkpoint,load_current=load)
checks=[]
def refused(label,expected,**kwargs):
    try:decide(**kwargs)
    except m.MarginRefusal as error:assert error.reason==expected,(label,error.reason);checks.append(label)
    else:raise AssertionError(label+' unexpectedly accepted')
positive=decide();assert positive['remaining_margin_us']==1 and positive['required_observed_tail_us']==11
checks.append('one-microsecond-positive-margin')
refused('exact-equality-refused','real-lease-cannot-fit-observed-tail',d={k:(observed+timedelta(microseconds=11)).isoformat() for k in deadlines})
for k in m.DEADLINE_FIELDS:
    refused('each-independent-deadline-'+k,'real-lease-cannot-fit-observed-tail',d={**deadlines,k:observed.isoformat()})
refused('actual-load-required','actual-load-unknown-or-outside-calibration',load=False)
refused('identity-mismatch','empirical-execution-identity-differs',identity={**policy['execution_identity'],'source_sha256':'3'*64})
refused('unknown-policy','empirical-policy-unqualified',p={**policy,'status':'unqualified'})
refused('missing-phase','empirical-phase-bound-unknown',p={**policy,'phase_upper_bounds_us':{}})
refused('bool-overhead','empirical-uncertainty-or-gate-overhead-unknown',p={**policy,'gate_overhead_upper_bound_us':True})
refused('unsafe-evidence-path','empirical-evidence-path-unsafe',p={**policy,'evidence_bindings':[{'path':'../elsewhere','sha256':'2'*64}]})
refused('impossible-calendar','invalid-real-deadline',p={**policy,'valid_until':'2031-02-30T00:00:00Z'})
refused('expired-calibration','empirical-policy-expired',p={**policy,'valid_until':observed.isoformat()})
assert decide(checkpoint='assessment-preclaim')['required_observed_tail_us']==7
checks.append('assessment-tail-excludes-completed-application-phases')
from jsonschema import Draft202012Validator,FormatChecker
schema=json.loads((P/'observed-margin-policy.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema,format_checker=FormatChecker())
timestamps=['2031-01-01T00:00:00Z','2031-01-01T00:00:00+00:00','2031-01-01T00:00:00.123456Z','2031-01-01T00:00:00.123456+00:00']
timestamp_results=[{'value':v,'schema_valid':validator.is_valid({**policy,'valid_until':v}),'calendar_valid':bool(m.instant(v))} for v in timestamps]
assert all(row['schema_valid'] and row['calendar_valid'] for row in timestamp_results)
vault=ast.parse((ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/workspace.py').read_bytes())
claim=next(n for n in ast.walk(vault) if isinstance(n,ast.FunctionDef) and n.name=='claim')
assert ast.dump(claim.args,include_attributes=False)==boundary['original_Vault_claim_signature_AST']
for row in manifest['files']:exact(ROOT/row['path'],row['sha256'])
for row in boundary['exact_current_preimages_rechecked']:exact(ROOT/row['path'],row['sha256'])
report={'schema_version':'lab-T03-root-margin-proposal-review/v1-candidate','result':'PASS-scoped-boundary-proposal-only; production-integration-and-calibration-open','authority_effect':'none','frozen_inputs_verified':len(manifest['files']),'original_target_preimages_verified':len(boundary['exact_current_preimages_rechecked']),'pure_synthetic_controls':checks,'valid_UTC_timestamp_controls':timestamp_results,'original_Vault_claim_signature_unchanged':True,'findings':[{'id':'R1','severity':'reviewer-inference-corrected','finding':'Actual unchanged frozen UTC regex accepts Z/+00:00 and fractional forms. Failed reviewer assertion and preimage preserved; no production regex defect reproduced.'},{'id':'R2','severity':'production-integration-obligation','finding':'Existing assessment Service has no SessionAttachment. The actual adapter needs an independently guarded private composition link to the original live parent resource; policy/Actor names are insufficient.'},{'id':'R3','severity':'production-integration-obligation','finding':'Calibration and full software/profile identity are unknown. A pure synthetic policy cannot justify empirical reserves or changed code/source transfer. Unknown enforced calibration must refuse before material/allocation/claim.'}],'original_call_and_operator_deadlines_conservatively_bound_full_tail':True,'original_target_code_modified':False,'actual_Lab_constructor_or_lease_executed':False,'empirical_margin_qualified':False,'task_complete':False}
out=RUN/'T03/root-margin-proposal-review-0001.json'
with out.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':report['result'],'controls':len(checks),'receipt_sha256':sha(out.read_bytes())}))
