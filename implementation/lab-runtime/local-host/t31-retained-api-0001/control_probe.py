"""Actual recorded rule refusal supporting a candidate detection binding.

The known domain refusal is an observed metadata effect, not a preclaim error or
control-effectiveness claim. No original producer, permission or clock changes.
"""
import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
CONTROL_ID='validator:local-lab:declared-failure-rule-closure-v9'
RULE_SOURCE_REF='product/lab/release-candidates/v1/interface/failure-assessment-rules-v9/source-manifest.json'
RULE_SOURCE_SHA='f05cd62d53dbde6a68534ba921c6e4573df51fe2e9eae9c62e1c22a20420f710'
CONTROL_TEMPLATE_REF='authority/artifact-types/failure-control-binding/v1/fixtures/valid/record.json'
CONTROL_TEMPLATE_SHA='fe54d7755751dd1b36c2e1331ebbcac29c36ef500aeaeda3544374d1838311fd'
CONTROL_SCHEMA_REF='authority/artifact-types/failure-control-binding/v1/schema.json'
CONTROL_SCHEMA_SHA='6f639e94525244173934cc9376259572e4a4320c81709016f447fad66e98f5b8'

def control_template(root):
    values=[]
    for ref,digest in [(CONTROL_TEMPLATE_REF,CONTROL_TEMPLATE_SHA),(CONTROL_SCHEMA_REF,CONTROL_SCHEMA_SHA)]:
        path=Path(root)/ref
        need(not path.is_symlink() and not any(p.is_symlink()for p in path.parents),'exact public control template/schema origin required')
        raw=path.read_bytes();need(sha(raw)==digest,'exact public control template/schema bytes differ');values.append(json.loads(raw))
    Draft202012Validator(values[1]).validate(values[0]);return tuple(values)

def validate_rule_source(binding):
    need(type(binding)is dict and set(binding)=={'ref','sha256'}
         and binding=={'ref':RULE_SOURCE_REF,'sha256':RULE_SOURCE_SHA},
         'independently selected exact rule-source binding differs')
    return binding

def validate_known_refusal(schemas,request_raw,reply,profile_binding):
    need(schemas.valid('api-reply',reply) and reply['request_binding']['sha256']==sha(request_raw)
         and reply['contract_profile_binding']==profile_binding and reply['kind']=='error'
         and reply['message']['code']=='closure-missing',
         'actual unknown-rule outcome did not record expected known refusal')
    uri=schemas.operations['failure.assess']['error_schema']['resource_uri']
    need(schemas.protocol_valid(uri,reply['message']),
         'actual failure.assess error violates selected operation-domain schema')
    return reply

def write(path,raw):
    if not isinstance(raw,bytes):raw=enc(raw)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return {'ref':str(path),'sha256':sha(raw)}
def load(path):
    name='_t31_probe_'+str(os.getpid());spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def run(evidence):
    selected=sys.modules.get('cal_installed_runtime_selection_v1');need(selected is not None,'selected installed native launcher required')
    selected.require_runtime_ready();selected.guard();root=selected.root();api=root/selected.current().package['entrypoint']['api_directory']
    evidence=Path(evidence).absolute();need(not evidence.exists() and evidence.parent.is_dir() and not evidence.is_relative_to(root)
        and not any(p.is_symlink() for p in evidence.parents),'fresh private external probe evidence root required');evidence.mkdir(mode=0o700)
    sys.path.insert(0,str(api.parent));m={name:importlib.import_module(api.name+'.'+name) for name in ('protocol','guard','auth','handlers','failure_fixture','integration_dispatch','workspace')}
    P,G,A,H,F,I,W=(m[k] for k in ('protocol','guard','auth','handlers','failure_fixture','integration_dispatch','workspace'))
    source=selected.binding('api.source')['sha256'];profile=selected.binding('api.profile')['sha256'];G.verify(source);schemas=P.Schemas(profile)
    template,control_schema=control_template(root)
    retention=load(root/'implementation/lab-runtime/local-host/t17-current-common-caller-0001/retain.py')
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        with F.example(view,schemas,mode='unknown-rule') as (host,request,witness):
            try:
                surface=I.IntegrationService(host);need(surface.base is host and surface.schemas is schemas,'actual shared common dispatcher required')
                raw=P.compact(request);reply=surface.call(raw);W.privacy(reply)
                validate_known_refusal(schemas,raw,reply,schemas.profile_binding)
                reports=[]
                for path in (host.vault.root/'objects').glob('*.json'):
                    original=W.read_private(path);need(path.stem==sha(original),'actual report original digest differs')
                    body=P.frame_parse(original)
                    if type(body)is dict and body.get('schema_version')=='lab-failure-assessment-rule-checks/v1-candidate':reports.append((body,original))
                need(len(reports)==1 and reports[0][0]['result']=='not-evaluable'
                     and reports[0][0]['confirmed_cause_inferred']is False
                     and reports[0][0]['recovery_or_control_effectiveness_inferred']is False,
                     'actual rule refusal/cause/control residue differs')
                snapshot=lambda:{p.relative_to(host.vault.root).as_posix():sha(p.read_bytes()) for p in host.vault.root.rglob('*') if p.is_file()}
                before=snapshot();retry=copy.deepcopy(request);retry['call_id']+=':actual-known-result-retry'
                again=surface.call(P.compact(retry));need(again['message']==reply['message'] and again['kind']=='error' and snapshot()==before,'known refusal retry dispatched or changed durable state')
                host.channel.guard();need(A.now()<A.instant(request['deadline']),'current rule observation expired')
                archived=retention.archive(evidence/'originals',host.vault.root,{'operation':'failure.assess','mode':'controlled-unknown-rule',
                    'original_request':request,'actual_reply':reply,'known_domain_refusal_is_recorded_metadata_effect':True,
                    'api_source_sha256':source,'api_profile_sha256':profile})
                write(evidence/'request.json',raw);reply_binding=write(evidence/'reply.json',P.compact(reply));report_binding=write(evidence/'rule-report.json',reports[0][1])
                targets=witness['proposal']['targets'];mode=next(t['artifact'] for t in targets if t['artifact']['carrier_ref']=='cal.artifact-type.failure-mode/v1')
                need(control_template(root)==(template,control_schema),'independently selected control template/schema changed');body=copy.deepcopy(template)
                control_source=F.composition.RULES/'source-manifest.json';control_binding=validate_rule_source({'ref':str(control_source.relative_to(root)),'sha256':sha(control_source.read_bytes())})
                identity='failure-control-binding:observed-local-rule-refusal:'+sha(reports[0][1])[:24]
                body.update(node_id=identity,scope_ref=view.data['config']['scope_ref'],owner_ref=host.channel.context['principal_ref'],
                    lifecycle_state='candidate',evidence_refs=[reply_binding['ref'],report_binding['ref'],'software-source:local-failure-rules-v9:'+control_binding['sha256']],successor_refs=[],
                    name='Candidate binding to observed local failure-rule detection',
                    claim_ceiling='Actual isolated unknown-rule refusal and read-only known-result retry only. No real failure, confirmed cause, deployed external control, recovery or effectiveness claim.')
                body['payload'].update(control_subject_ref=CONTROL_ID,failure_mode_ref=mode['version_ref'],
                    primary_control_role='detect',installation_posture='candidate-local-runtime-observation',execution_evidence_refs=[reply_binding['ref'],report_binding['ref']],
                    effectiveness_evidence_refs=[],owner_ref=host.channel.context['principal_ref'])
                body['relation_refs']=[{'relation_kind_ref':'relation.controls','direction':'source','counterpart_kind':'failure-mode','counterpart_ref':mode['version_ref']}]
                Draft202012Validator(control_schema).validate(body);original=enc(body)
                output=write(evidence/'failure-control-binding.json',original)
                header={'scope_ref':body['scope_ref'],'identity_ref':identity,'version_ref':identity+'@candidate.1','carrier_ref':'cal.artifact-type.failure-control-binding/v1','byte_sha256':sha(original)}
                result={'schema_version':'lab-actual-failure-rule-control-observation/v1','result':'PASS-actual-known-rule-refusal-and-candidate-detect-binding',
                    'api_source_sha256':source,'api_profile_sha256':profile,'source_cut':H.cut(view),'original_request_sha256':sha(raw),
                    'actual_reply_binding':reply_binding,'actual_rule_report_binding':report_binding,'actual_rule_source_binding':control_binding,
                    'semantic_control_identity':CONTROL_ID,'semantic_identity_is_private_candidate_not_Source_admission':True,'private_semantic_control_definition':{'identity_ref':CONTROL_ID,'source_binding':control_binding,'entrypoint':'AssessmentRules.evaluate','purpose':'Observe refusal of an undeclared compatibility rule in an isolated candidate postimage'},'actual_rule_result':'not-evaluable','known_result_retry_read_only':True,'candidate_output':header,'candidate_original_binding':output,
                    'original_failure_mode':{k:v for k,v in mode.items() if k!='candidate_contract_binding'},'retained_originals':archived,
                    'actual_native_common_dispatcher':True,'metadata_effect_recorded':True,'control_effectiveness_established':False,'canonical_admissions':0,'authority_effect':'none'}
                result.update(candidate_template_binding={'ref':CONTROL_TEMPLATE_REF,'sha256':CONTROL_TEMPLATE_SHA},
                              candidate_schema_binding={'ref':CONTROL_SCHEMA_REF,'sha256':CONTROL_SCHEMA_SHA})
                write(evidence/'RESULT.json',result)
            except BaseException as error:
                # Observe and retain actual possibly pending metadata before the
                # fixture closes. Never recreate a journal from a hash/reply.
                try:
                    F0=importlib.import_module(api.name+'.fixtures')
                    inspect_request=F0.call(host.channel.context,'operation.inspect',None,
                        lookup={'operation':request['operation'],'idempotency_key':request['idempotency_key']})
                    inspect_reply=I.IntegrationService(host).call(P.compact(inspect_request))
                    write(evidence/'failed-operation-inspect.json',{'original_request':inspect_request,'actual_reply':inspect_reply})
                except BaseException:
                    pass
                try:
                    retention.archive(evidence/'failure-originals',host.vault.root,{
                        'api_source_sha256':source,'api_profile_sha256':profile,'exception_class':type(error).__name__,
                        'original_request':request,'authority_effect':'none'})
                except BaseException:
                    pass
                raise
    G.verify(source);return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--evidence',required=True)
    print(json.dumps(run(parser.parse_args().evidence),sort_keys=True),flush=True)
