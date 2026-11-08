"""External qualification runner for selected-root real public transitions."""
import argparse
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys

def need(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write(path,value):
    raw=value if type(value)is bytes else enc(value)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return {'ref':str(path),'sha256':sha(raw)}

def validate_config(config,preflight_only):
    base={'schema_version','kind','selections','typed_productions','stages','final_state'}
    need(type(config)is dict and base<=set(config)<=base|{'scope_profile','continuation','original_bundles','native_emissions','identity_selection'}
         and config['schema_version']=='lab-actual-retained-workflow-run/v1' and type(config['stages'])is list and config['stages'],
         'closed independent current workflow runner selection required')
    for row in config['stages']:need(type(row)is dict and set(row)=={'transition_ref','input_refs','output_refs'},'closed exact stage selection required')
    need(not preflight_only or len(config['stages'])==1,'no-effect preflight requires exactly one selected stage')
    continuation=config.get('continuation')
    need(continuation is None or type(continuation)is dict and set(continuation)=={'principal_ref','run_ref','journal_root','journal_head'},'closed exact previous workflow continuation required')
    identity=config.get('identity_selection')
    need((identity is None and not config.get('native_emissions')) or
         (type(identity)is dict and set(identity)=={'principal_ref','run_ref'}
          and type(config.get('native_emissions')) is list
          and len(config['native_emissions'])==1 and continuation is None),
         'native first-Session selection requires one exact new Reader Actor/Run')
    return config

def run(config_path,evidence,preflight_only=False):
    selected=sys.modules.get('cal_installed_runtime_selection_v1');need(selected is not None,'actual selected installed native launcher required')
    selected.require_runtime_ready();selected.guard();root=selected.root();api=root/selected.current().package['entrypoint']['api_directory']
    helper=root/'implementation/lab-runtime/local-host/t31-retained-api-0001';sys.path[:0]=[str(helper),str(api.parent)]
    CF=importlib.import_module('current_fixture');need(Path(CF.__file__)==helper/'current_fixture.py','actual selected-root fixture required');CF.helper_origins()
    R=importlib.import_module('retained');raw=R.read(Path(config_path).absolute());config=json.loads(raw)
    validate_config(config,preflight_only)
    evidence=Path(evidence).absolute();need(not evidence.exists() and evidence.parent.is_dir() and not evidence.is_relative_to(root)
        and not any(p.is_symlink()for p in evidence.parents),'fresh external private workflow evidence required');evidence.mkdir(mode=0o700)
    transitions={s['transition_ref']:s['output_refs']for s in config['stages']};need(len(transitions)==len(config['stages']),'unique exact transitions required')
    proof=CF.ArchiveProof(config['selections'],transitions=transitions,
                          typed_productions=config['typed_productions'],
                          original_bundles=config.get('original_bundles',()),
                          native_emissions=config.get('native_emissions',()))
    if config.get('native_emissions'):
        need(proof.native_source_binding==selected.binding('api.source')
             and proof.native_profile_binding==selected.binding('api.profile')
             and proof.native_package_pin==selected.current().package_pin,
             'native first-Session installed package/source/profile selection differs')
    mod=lambda name:importlib.import_module(api.name+'.'+name)
    P,G,I,H,OW,A=(mod(n)for n in ('protocol','guard','integration_dispatch','handlers','owned_workflow_transition','auth'))
    source=selected.binding('api.source')['sha256'];profile=selected.binding('api.profile')['sha256'];G.verify(source);schemas=P.Schemas(profile)
    path=root/'implementation/lab-runtime/local-host/t17-current-common-caller-0001/retain.py';spec=importlib.util.spec_from_file_location('_t31_actual_vault_retention',path);retain=importlib.util.module_from_spec(spec);spec.loader.exec_module(retain)
    principal='principal:current-workflow-qualification:'+secrets.token_hex(12);run_ref='workflow-run:current-retained-'+config['kind']+':'+secrets.token_hex(12)
    if config.get('identity_selection') is not None:
        need(proof.native_identity==config['identity_selection'],
             'native first-Session Actor/Run differs from exact emission')
        principal=proof.native_identity['principal_ref'];run_ref=proof.native_identity['run_ref']
    previous_journal=None;previous_head=None;cases=[];unit='t31:actual-api:'+config['kind'];scope_profile=config.get('scope_profile')
    if config.get('continuation')is not None:
        previous=config['continuation'];principal=previous['principal_ref'];run_ref=previous['run_ref'];previous_journal=previous['journal_root'];previous_head=previous['journal_head']
    if scope_profile is not None:
        _,index,_=CF.SC.capture(scope_profile);actor=index['actor']
        need(all(actor[k]is None for k in ('agent_instance_ref','assignment_ref','session_ref'))and actor['role_assignment_refs']==[],
             'native ScopeIndex cannot reconstruct formal Session or Assignment capabilities')
        if previous_journal is None:principal=actor['principal_ref'];run_ref=index['run_ref']
        else:need(principal==actor['principal_ref']and run_ref==index['run_ref'],'scoped continuation selects another Actor/Run')
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME)as view:
        cut=H.cut(view)
        if proof.product_source_cut is not None:
            need(proof.product_source_cut==cut,
                 'product fixture originals select another current Source cut')
        if proof.native_source_cut is not None:
            need(proof.native_source_cut==cut,
                 'native first-Session originals select another current Source cut')
        for number,row in enumerate(config['stages'],1):
            stage=evidence/str(number).zfill(2);stage.mkdir(mode=0o700)
            print('stage-current-source-preflight:'+row['transition_ref'],flush=True)
            with CF.example(view,schemas,api_namespace=api.name,kind=config['kind'],transition=row['transition_ref'],proof=proof,principal=principal,run_ref=run_ref,
                            input_refs=row['input_refs'],previous_journal=previous_journal,previous_head=previous_head,scope_profile=scope_profile,preserve_failed_root=True)as(host,request,witness):
                store=witness['store'];call=request();deadline=A.instant(call['deadline']);capability=OW.selected(host)
                need(capability is not None,'actual native public workflow capability absent');capability.guard(deadline)
                if preflight_only:
                    # This is the unchanged public handler's complete semantic
                    # preflight. It retrieves/schema-checks exact Source roles,
                    # Decision/Effect edges and all stage inputs, but never
                    # invokes its durable apply method or dispatches a call.
                    evaluator=OW.OwnedWorkflowTransition(capability,deadline)
                    evaluator.preflight(call['message'],cut,call['idempotency_key'])
                    capability.guard(deadline)
                    result={'result':'PASS-current-native-Source-semantic-preflight','config_binding':{'ref':str(Path(config_path).absolute()),'sha256':sha(raw)},
                            'api_source_sha256':source,'api_profile_sha256':profile,'source_cut':cut,'authenticated_actor':OW.actor(host.channel),
                            'transition_ref':row['transition_ref'],'semantic_stages_checked':1,
                            'exact_Source_frame_roles':witness['index']['roles'],'public_operations_dispatched':0,'actual_transition_commits':0,'authority_effect':'none'}
                    write(evidence/'RESULT.json',result);return result
                before=store.replay()[0];call_raw=P.compact(call);surface=I.IntegrationService(host)
                need(surface.base is host and surface.schemas is schemas,'actual common Service dispatcher required');reply=surface.call(call_raw)
                write(stage/'request.json',call_raw);write(stage/'reply.json',P.compact(reply))
                need(schemas.valid('api-reply',reply)and reply['kind']=='result'and reply['request_binding']['sha256']==sha(call_raw),
                     'actual public transition did not return bound successful reply')
                uri=schemas.operations['workflow.transition']['result_schema']['resource_uri'];need(schemas.protocol_valid(uri,reply['message']),'actual public transition domain result schema differs')
                capability.guard(deadline);head,next_raw=store.replay();consumed=store.consume(head['sequence'])
                need(head['sequence']==before['sequence']+1 and [h for h,b in consumed]==proof.profile()['outputs'][row['transition_ref']],
                     'actual durable transaction/original outputs differ from selected producer')
                for h,body in consumed:need(proof.records[h['version_ref']]==(h,body),'committed actual original bytes differ')
                snapshot=lambda:{p.relative_to(host.vault.root).as_posix():sha(p.read_bytes())for p in host.vault.root.rglob('*')if p.is_file()}
                snapshot_before=snapshot();retry=copy.deepcopy(call);retry['call_id']+=':exact-retry';again=surface.call(P.compact(retry))
                need(again['kind']=='result'and again['message']==reply['message']and snapshot()==snapshot_before,'actual known transition retry changed durable Vault state')
                capability.guard(deadline)
                case={'operation':'workflow.transition','transition_ref':row['transition_ref'],'result':'PASS','expected_kind':'result',
                      'request_sha256':sha(call_raw),'original_request_base64':base64.b64encode(call_raw).decode(),'actual_reply':reply,
                      'actual_native_common_dispatcher':True,'actual_durable_output_count':len(consumed),'exact_retry_read_only':True}
                archived=retain.archive(stage/'originals',host.vault.root,{'source_sha256':source,'profile_sha256':profile,'unit':unit,'case':case,'original_request':call})
                capability.guard(deadline);need(store.replay()==(head,next_raw),'actual journal changed during archive')
                case['retained_originals']={'path':str(stage/'originals'),'observation_sha256':archived['observation_sha256']};cases.append(case)
                previous_journal=stage/'originals/vault/workflows/design'
                prior_index,_=CF.PRIOR.capture(previous_journal)
                previous_head={'journal_config_sha256':store.journal.config_sha256,'head':head,'run_sha256':sha(next_raw),'inventory_sha256':sha(CF.PRIOR.enc(prior_index))}
                write(stage/'committed-head.json',previous_head)
            print('actual-public-transition-PASS:'+row['transition_ref'],flush=True)
        final=json.loads(next_raw);need(final['state']==config['final_state'],'actual final workflow state differs')
        view.custody_signed_sources.guard();proof.guard();selected.guard();G.verify(source)
    result={'schema_version':'lab-actual-retained-workflow-qualification/v1','result':'PASS','unit':unit,'source_sha256':source,'profile_sha256':profile,
            'config_binding':{'ref':str(Path(config_path).absolute()),'sha256':sha(raw)},'source_cut':cut,'run_ref':run_ref,'principal_ref':principal,'cases':cases,
            'actual_public_transition_commits':len(cases),'final_state':final['state'],'canonical_admissions':0,'actual_owner_outcome':None,'authority_effect':'none'}
    if config['kind']=='ontology-migration-local-runtime-evidence':
        result.update(coverage_posture='adapted-local-technical-coverage-only',original_SourceAdmission_template_requirement_satisfied=False)
    write(evidence/'RESULT.json',result);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--evidence',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    result=run(args.config,args.evidence,args.preflight_only);print(json.dumps({'result':result['result'],'evidence':args.evidence},sort_keys=True),flush=True)
