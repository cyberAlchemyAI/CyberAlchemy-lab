"""Retain an actually observed rule-refusal candidate as workflow output.

No control effectiveness, operational failure, recovery, or source admission is
inferred from the isolated unknown-rule observation or its read-only retry.
"""
import importlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
import retained as R
ROOT=Path(__file__).resolve().parents[4]
CONTROL_ID='validator:local-lab:declared-failure-rule-closure-v9'
RULE_REF='product/lab/release-candidates/v1/interface/failure-assessment-rules-v9/source-manifest.json'
RULE_SHA='f05cd62d53dbde6a68534ba921c6e4573df51fe2e9eae9c62e1c22a20420f710'

def produce(*,records,observations,controls):
    R.need(type(controls)is dict and set(controls)=={'result_binding'},'closed actual rule-control observation required')
    binding=controls['result_binding'];R.need(type(binding)is dict and set(binding)=={'ref','sha256'},'closed actual rule observation result binding required')
    raw=R.read(Path(binding['ref']));R.need(R.sha(raw)==binding['sha256'],'actual rule observation result original differs');result=json.loads(raw)
    R.need(result['schema_version']=='lab-actual-failure-rule-control-observation/v1'
           and result['result']=='PASS-actual-known-rule-refusal-and-candidate-detect-binding'
           and result['actual_native_common_dispatcher']is True and result['metadata_effect_recorded']is True
           and result['actual_rule_result']=='not-evaluable' and result['known_result_retry_read_only']is True
           and result['control_effectiveness_established']is False and result['canonical_admissions']==0 and result['authority_effect']=='none',
           'actual bounded known-refusal/control observation did not pass')
    R.need(result['semantic_control_identity']==CONTROL_ID and result['actual_rule_source_binding']=={'ref':RULE_REF,'sha256':RULE_SHA}
           and R.sha((ROOT/RULE_REF).read_bytes())==RULE_SHA,'stable semantic control identity or independent rule source differs')
    selected=sys.modules.get('cal_installed_runtime_selection_v1');R.need(selected is not None and selected.root()==ROOT,'actual selected native rule observer context required');selected.guard()
    R.need(result['api_source_sha256']==selected.binding('api.source')['sha256'] and result['api_profile_sha256']==selected.binding('api.profile')['sha256'],
           'actual rule observer API/profile selection differs')
    api=ROOT/selected.current().package['entrypoint']['api_directory'];P=importlib.import_module(api.name+'.protocol');schemas=P.Schemas(result['api_profile_sha256'])
    def original(b):
        R.need(type(b)is dict and set(b)=={'ref','sha256'},'closed rule observation member binding required');raw=R.read(Path(b['ref']));R.need(R.sha(raw)==b['sha256'],'actual rule observation member differs');return raw
    reply_raw=original(result['actual_reply_binding']);report_raw=original(result['actual_rule_report_binding']);candidate_raw=original(result['candidate_original_binding'])
    reply,report,body=(json.loads(raw)for raw in (reply_raw,report_raw,candidate_raw))
    archive=Path(result['retained_originals']['path']);observation_raw=R.read(archive/'OBSERVATION.json')
    R.need(R.sha(observation_raw)==result['retained_originals']['observation_sha256'],'actual known-refusal Vault observation differs')
    observation=json.loads(observation_raw);witness=observation['observation']
    R.need(observation['schema_version']=='lab-retained-actual-caller-vault/v1' and observation['Reader_credentials_retained']is False
           and observation['current_permission_or_Session_reconstructed']is False and observation['authority_effect']=='none'
           and witness['operation']=='failure.assess' and witness['mode']=='controlled-unknown-rule'
           and witness['known_domain_refusal_is_recorded_metadata_effect']is True and witness['actual_reply']==reply
           and witness['api_source_sha256']==result['api_source_sha256'] and witness['api_profile_sha256']==result['api_profile_sha256']
           and R.sha(P.compact(witness['original_request']))==result['original_request_sha256']
           and witness['original_request']['expected_source_cut']==result['source_cut'],
           'actual known-refusal original request/reply/selection correspondence differs')
    members={}
    for row in observation['files']:
        R.need(type(row)is dict and set(row)=={'path','sha256','size_bytes'},'closed known-refusal archive member required')
        relative=R.relative(row['path']);R.need(str(relative)not in members,'duplicate actual known-refusal archive member')
        member=R.read(archive/relative);R.need(R.sha(member)==row['sha256'] and len(member)==row['size_bytes'] and b'PRIVATE KEY-----'not in member,
                                            'actual known-refusal archive original differs')
        members[str(relative)]=member
    R.need(not any(p.is_symlink()for p in archive.rglob('*')) and {p.relative_to(archive).as_posix()for p in archive.rglob('*')if p.is_file()}==set(members)|{'OBSERVATION.json'}
           and members.get('vault/objects/'+R.sha(report_raw)+'.json')==report_raw,'complete actual known-refusal Vault/report originals required')
    R.need(schemas.valid('api-reply',reply) and reply['operation']=='failure.assess' and reply['kind']=='error'
           and reply['request_binding']['sha256']==result['original_request_sha256']
           and reply['contract_profile_binding']['sha256']==result['api_profile_sha256'] and reply['message']['code']=='closure-missing'
           and schemas.protocol_valid(schemas.operations['failure.assess']['error_schema']['resource_uri'],reply['message']),
           'actual operation error-domain reply differs')
    R.need(report['schema_version']=='lab-failure-assessment-rule-checks/v1-candidate' and report['result']=='not-evaluable'
           and report['confirmed_cause_inferred']is False and report['recovery_or_control_effectiveness_inferred']is False,
           'actual rule observation inference ceiling differs')
    mode=result['original_failure_mode'];matches=[(h,b)for h,b in records.values()if h==mode]
    R.need(len(matches)==1 and mode['carrier_ref']=='cal.artifact-type.failure-mode/v1','actual observed control selects another failure Mode')
    related=[o for o in observations if o['actual_reply']['operation']=='failure.assess' and o['actual_reply']['kind']=='result'
             and any(h==mode and b==matches[0][1] and R.sha(b)==mode['byte_sha256'] for h,b in o['outputs'])
             and o['original_source_cut']==result['source_cut']]
    R.need(related,'actual control and assessed Mode producer/source correspondence differs')
    header=result['candidate_output'];R.need(set(header)==R.FIELDS and header['byte_sha256']==R.sha(candidate_raw)
           and body['node_id']==header['identity_ref'] and header['version_ref']==body['node_id']+'@candidate.1'
           and body['scope_ref']==header['scope_ref']==mode['scope_ref'] and body['lifecycle_state']=='candidate' and body['authority_effect']=='none',
           'actual candidate control original/header differs')
    payload=body['payload'];R.need(payload['failure_mode_ref']==mode['version_ref'] and payload['control_subject_ref']==CONTROL_ID
           and payload['primary_control_role']=='detect' and payload['installation_posture']=='candidate-local-runtime-observation'
           and payload['effectiveness_evidence_refs']==[]
           and payload['execution_evidence_refs']==[result['actual_reply_binding']['ref'],result['actual_rule_report_binding']['ref']],
           'actual candidate control semantics or evidence differs')
    Draft202012Validator(json.loads((ROOT/'authority/artifact-types/failure-control-binding/v1/schema.json').read_bytes())).validate(body);schemas.guard();selected.guard()
    return {'records':[(header,candidate_raw)],'consumed_input_refs':[mode['version_ref']],
            'consumed_observation_refs':[o['observation_binding']['ref']for o in related],
            'receipt':{'schema_version':'lab-retained-real-rule-control-production/v1','actual_result_binding':binding,
                       'actual_reply_binding':result['actual_reply_binding'],'actual_rule_report_binding':result['actual_rule_report_binding'],
                       'actual_known_refusal_observation_binding':{'ref':str(archive/'OBSERVATION.json'),'sha256':R.sha(observation_raw)},
                       'actual_known_refusal_original_hashes':{name:R.sha(raw)for name,raw in members.items()},
                       'actual_rule_source_binding':result['actual_rule_source_binding'],'semantic_control_identity':CONTROL_ID,
                       'original_failure_mode':mode,'candidate_output':header,'candidate_original_binding':result['candidate_original_binding'],
                       'control_effectiveness_established':False,'Source_admission':False,'authority_effect':'none'}}
