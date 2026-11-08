"""External actual native capture, separate from public workflow application.

The original ScopeIndex observation wraps the real capture receipt explicitly;
it never attributes the wrapper's scope proof to the core capture return value.
"""
import argparse
import base64
import copy
from contextlib import ExitStack
from datetime import timedelta
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import tempfile

VARIANT='implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/external-postimages-0002/external_ontology_capture.py'
VARIANT_SHA='3c6bee19c635eb3bf052ac4c72da587d7dc1309f7f21899c9c572046f89eef7f'
SNAPSHOT_SHA='dbaf2c8dddeb4153bf63488b140889d5c845f558ba25d19f604a4bd56387ff71'
REVIEW_SHA='35a1aea7ea51fbad340e9f6c55bc3a77b1b6361e2d2ac4269af951f5d718a1e2'
def need(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write(path,value):
    raw=value if type(value)is bytes else enc(value);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return {'ref':str(path),'sha256':sha(raw)}
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def frame(CF,P,M,D,view,cut,principal,run_ref):
    with M.model_read_batch(view):
        def role(identity):
            rows=[s for s in view.subjects.values()if s['identity']==identity and s['effective_state']in('admitted-current','local-admitted-current')]
            need(len(rows)==1,'one exact current Source frame identity required');return M.artifact_ref(view,rows[0]),M.record_bytes(view,rows[0])[0]
        source={key:role(identity)for key,identity in [('intent',D.records.INTENT),('work',D.records.WORK),('goal',D.records.GOAL),('coordination',D.records.COORDINATION),('project',view.custody_signed_sources.sources.scope_ref)]}
        edges=[]
        for s in view.subjects.values():
            if s['carrier_ref']!='cal.artifact-type.typed-relation/v3'or s['effective_state']not in('admitted-current','local-admitted-current'):continue
            raw=M.record_bytes(view,s)[0];body=P.frame_parse(raw)['payload']
            if body['relation_kind_ref']=='relation.member-of'and body['source']['version_ref']==source['goal'][0]['version_ref']and body['target']['version_ref']==source['project'][0]['version_ref']:edges.append((M.artifact_ref(view,s),raw))
        need(len(edges)==1,'one exact current Goal/Project edge required');source['goal_project']=edges[0]
        profiles=[s for s in view.subjects.values()if s['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1'and s['effective_state']in('admitted-current','local-admitted-current')]
        need(len(profiles)==1,'one exact current workflow decision profile required');dp=M.artifact_ref(view,profiles[0])
    capsule,raws=CF.FRAME.construct(root=P.ROOT,inputs=source,source_cut=cut,principal=principal,run_ref=run_ref)
    definition=json.loads((P.ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows/ontology-migration-local-runtime-evidence.json').read_bytes());definition['decision_profile']=dp
    db=P.binding('owned-fixture:definition',CF.P.enc(definition));actor={'principal_ref':principal,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    run={'schema_version':'lab-workflow-run/v1-candidate','run_ref':run_ref,'definition_binding':db,'actor':actor,'source_cut':cut,
         'intent':source['intent'][0],'intent_resolution':capsule['private_artifacts']['intent-resolution'],'work':source['work'][0],'coordination_context':source['coordination'][0],
         'state':definition['initial_state'],'event_bindings':[],'gaps':[],'outcome_assessment':None,'authority_effect':'none'}
    return run,CF.P.enc(run)

def scope_observation(*,evidence,capture,outputs,run_binding,work,actor,run_ref,cut,config_sha,producer,source_binding,prior=None):
    receipt_raw=capture['receipt_original'];receipt=json.loads(receipt_raw);transition=capture['transition_ref']
    need(transition in('transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated'),
         'scope observation route must be an actual ontology hydration stage')
    need(receipt['schema_version']=='lab-original-ontology-typed-capture/v1-candidate' and receipt['run_binding']==run_binding
         and receipt['work_ref']==work['version_ref'] and receipt['source_cut']==cut and receipt['authority_effect']=='none'
         and receipt['work_satisfaction_asserted']is False
         and sha(receipt_raw)==capture['receipt_binding']['sha256']==capture['returned_receipt_binding']['sha256'],
         'actual original ontology capture receipt/Run/Work/Source differs')
    need(outputs and all(header in receipt['artifacts']for header in outputs),'scope observation header absent from actual original capture')
    kinds=[header['carrier_ref']for header in outputs]
    expected={'cal.artifact-type.ontology-node/v2':18,'cal.artifact-type.ontology-edge/v1':12}if transition.endswith(':mapped')else {'cal.artifact-type.ontology-cut/v1':1,'cal.artifact-type.ontology-view/v1':1}
    need(set(kinds)==set(expected) and all(kinds.count(kind)==number for kind,number in expected.items())
         and len({header['version_ref']for header in outputs})==len(outputs),'complete exact actual ontology stage output categories required')
    members=[];entries=[];originals={}
    if prior is not None:
        raw,index,old=prior
        need(index['journal_config_sha256']==config_sha and index['work']==work and index['actor']==actor and index['run_ref']==run_ref and index['source_cut']==cut,
             'prior native ScopeIndex changes actual journal/Work/Actor/Source')
        entries=copy.deepcopy(index['entries']);members=copy.deepcopy(index['members']);originals=copy.deepcopy(old)
    lineage={'run_binding':run_binding,'work_ref':work['version_ref'],'source_cut':cut,'principal_ref':actor['principal_ref']}
    contract={'schema_version':'lab-private-owned-native-workflow-scope/v1-candidate','producer_binding':producer,'producer_entrypoint':'OntologyTypedCapture.produce',
              'review_sha256':REVIEW_SHA,'source_binding':source_binding,'source_cut':cut,'principal_ref':actor['principal_ref'],'work_ref':work['version_ref'],
              'container_scope_ref':outputs[0]['scope_ref'],'authority_scope_ref':work['scope_ref'],'permitted_body_scope_refs':[outputs[0]['scope_ref']],'authority_effect':'none'}
    proofs=[]
    for h in outputs:
        need(h['scope_ref']==contract['container_scope_ref'],'one actual native capture container scope required')
        proof={key:value for key,value in contract.items()if key not in('schema_version','permitted_body_scope_refs')}
        proof.update(schema_version='lab-original-native-record-scope/v1-candidate',artifact=h,body_scope_ref=h['scope_ref']);proofs.append(proof)
    wrapper={'schema_version':'lab-actual-native-ontology-scope-observation/v1','actual_capture_receipt_binding':capture['receipt_binding'],
             'actual_returned_capture_receipt_binding':capture['returned_receipt_binding'],
             'actual_capture_receipt_original_base64':base64.b64encode(capture['receipt_original']).decode(),
             'actual_capture_producer_binding':producer,'capture_returned_scope_proof':False,'scope_observer_created_wrapper_only':True,
             'artifacts':outputs,'proofs':proofs,'lineage':lineage,'authority_effect':'none'}
    prefix=sha(enc({'transition':transition,'run':run_binding}))[:24]
    def add(label,value):
        name=prefix+'-'+label+'.json';raw=enc(value);ref='actual-native-scope:'+sha(raw)
        same=[m for m in members if m['ref']==ref]
        if same:
            need(len(same)==1 and originals[same[0]['path']]==raw and same[0]['sha256']==sha(raw),'conflicting actual native scope evidence')
            return {'ref':ref,'sha256':sha(raw)}
        need(name not in originals,'duplicate actual native scope evidence path')
        originals[name]=raw;members.append({'ref':ref,'path':name,'sha256':sha(raw)});return {'ref':ref,'sha256':sha(raw)}
    cb=add('contract',contract);lb=add('lineage',lineage);rb=add('capture-observation',wrapper)
    for number,(h,proof)in enumerate(zip(outputs,proofs)):
        pb=add('proof-'+str(number),proof);entries.append({'transition_ref':transition,'artifact':h,'contract_binding':cb,'proof_binding':pb,'lineage_binding':lb,
             'producer_receipt_binding':rb,'artifact_selector':'/artifacts/'+str(number),'proof_selector':'/proofs/'+str(number),'lineage_selector':'/lineage'})
    root=evidence/'scope-evidence';root.mkdir(mode=0o700)
    for name,raw in originals.items():write(root/name,raw)
    index={'schema_version':'lab-owned-native-scope-index/v1','journal_config_sha256':config_sha,'scope_ref':work['scope_ref'],'run_ref':run_ref,
           'actor':actor,'work':work,'source_cut':cut,'members':members,'entries':entries,'authority_effect':'none'}
    return write(root/'scope-index.json',index),index

def run(config_path,evidence):
    selected=sys.modules.get('cal_installed_runtime_selection_v1');need(selected is not None,'actual installed native launcher required');selected.require_runtime_ready();selected.guard()
    root=selected.root();api=root/selected.current().package['entrypoint']['api_directory'];helper=root/'implementation/lab-runtime/local-host/t31-retained-api-0001';sys.path[:0]=[str(helper),str(api.parent)]
    CF=importlib.import_module('current_fixture');CF.helper_origins();R=importlib.import_module('retained')
    config=json.loads(R.read(Path(config_path).absolute()));need(set(config)=={'projection_selection','transition_ref','principal_ref','run_ref','previous_workflow','previous_scope'},'closed actual native capture selection required')
    need(config['transition_ref']in('transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated'),'exact original ontology hydration stage required')
    original=R.consume(**config['projection_selection']);need(original['projection_producer']is not None,'actual retained applied projection required')
    variant=root/VARIANT;need(sha(variant.read_bytes())==VARIANT_SHA,'actual independently selected capture variant differs');snapshot_path=Path(__file__).with_name('snapshot.py').absolute()
    need(sha(snapshot_path.read_bytes())==SNAPSHOT_SHA and not snapshot_path.is_relative_to(root),'exact external original snapshot capability required')
    evidence=Path(evidence).absolute();need(not evidence.exists()and evidence.parent.is_dir()and not evidence.is_relative_to(root),'fresh external native capture evidence required');evidence.mkdir(mode=0o700)
    P,A,F,M,S,H,G,SF=(importlib.import_module(api.name+'.'+name)for name in('protocol','auth','fixtures','artifact_model','service','handlers','guard','session_source_freshness'))
    source=selected.binding('api.source')['sha256'];profile=selected.binding('api.profile')['sha256'];manifest=G.verify(source);schemas=P.Schemas(profile);rows={(r['path'],r['sha256'])for r in manifest['files']}
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME)as view,ExitStack()as stack:
        d=P.source.current_legacy_delivery();cut=H.cut(view);need(cut==original['original_source_cut'],'actual current Source differs from retained projection')
        run_value,genesis_raw=frame(CF,P,M,d,view,cut,config['principal_ref'],config['run_ref']);run_raw=genesis_raw
        previous=config['previous_workflow']
        if previous is not None:
            _,_,run_raw=CF.PRIOR.verify(previous['journal_root'],previous['journal_head']);prior_run=json.loads(run_raw)
            need(all(prior_run[key]==run_value[key]for key in ('run_ref','definition_binding','actor','source_cut','intent','intent_resolution','work','coordination_context')),'actual previous workflow frame differs');run_value=prior_run
        run_binding=P.binding('owned-fixture:run-preimage',run_raw);work=run_value['work'];actor=run_value['actor']
        temp=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-actual-native-ontology-capture-')));temp.chmod(0o700);host_root=temp/'host';host_root.mkdir(mode=0o700);output=temp/'stage-originals';output.mkdir(mode=0o700)
        actual_receipt=original['projection_producer'];head_raw=original['files']['vault/ontology/HEAD.json'];head=json.loads(head_raw);generation=R.relative(head['generation']);archive=Path(config['projection_selection']['archive'])
        package=d.MAPPED.HERE/'packages/0001';materials={}
        def add(name,raw):
            ref='native-capture:'+name;need(ref not in materials,'duplicate native capture input');materials[ref]=raw;return P.binding(ref,raw)
        snapshot_control={'schema_version':'lab-private-original-ontology-archive/v1','generation_root':str(archive/'vault/ontology'/generation),
            'head_binding':add('actual-head',head_raw),'manifest_binding':add('actual-manifest',original['files']['vault/ontology/'+str(generation)+'/manifest.json']),
            'native_read_binding':add('actual-native-read',(package/'native-output.json').read_bytes()),
            'projection_receipt_binding':add('actual-projection-receipt',actual_receipt['receipt_original']),
            'mapping_binding':P.binding(str((d.MAPPED.HERE/'policy.json').relative_to(root)),(d.MAPPED.HERE/'policy.json').read_bytes()),
            'mapping_original_binding':P.binding(str((package/'mapping.json').relative_to(root)),(package/'mapping.json').read_bytes()),
            'work_ref':work['version_ref'],'source_cut':cut,'store_ref':head['store_ref'],'authority_effect':'none'}
        sb=add('snapshot-control',P.compact(snapshot_control));logical={'path':'private-host/actual-ontology-snapshot-v1.py','sha256':SNAPSHOT_SHA}
        external={'schema_version':'lab-private-external-native-capability/v1','logical_binding':logical,'component_binding':{'path':str(snapshot_path),'sha256':SNAPSHOT_SHA},
                  'entrypoint':'OntologySnapshot.capture','source_cut':cut,'principal_ref':actor['principal_ref'],'work_ref':work['version_ref'],'authority_effect':'none'}
        eb=add('external-selection',P.compact(external));rich=importlib.import_module(api.name+'.ontology_projection');rich_binding={'path':str(Path(rich.__file__).relative_to(root)),'sha256':sha(Path(rich.__file__).read_bytes())}
        template=root/'authority/artifact-types/ontology-view/v1/fixtures/valid/record.json';template_binding={'path':str(template.relative_to(root)),'sha256':sha(template.read_bytes())}
        hydration={'schema_version':'lab-private-original-ontology-hydration/v1-candidate','capability_binding':logical,'capability_entrypoint':'OntologySnapshot.capture',
                   'rich_method_binding':rich_binding,'record_version':'native-capture-'+config['transition_ref'].rsplit(':',1)[1]+'.1','view_template_binding':template_binding,'authority_effect':'none'}
        hb=add('hydration-control',P.compact(hydration));need((template_binding['path'],template_binding['sha256'])in rows,'actual view template must be selected by API Source before native work')
        key,path,_=F.provision(host_root,'reference-corrected',materials=materials,principal=actor['principal_ref']);policy=P.frame_parse(path.read_bytes());period=d.load(d.reader.HERE/'packages/0001/period.json');end=min(A.now()+timedelta(minutes=20),A.instant(period['expires_at']))
        authorization=root/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        policy.update(schema_version='lab-local-metadata-candidate-policy/v1-candidate',source_name=P.source.CURRENT_LEGACY_NAME,session_control=None,scope_control=None,
            purpose='durable-metadata-and-exact-candidate-preparation',allowed_operations=list(P.METADATA_SUPPORTED),development_authorization_binding=P.binding(str(authorization.relative_to(root)),authorization.read_bytes()),expires_at=end.isoformat(),max_request_bytes=1048576,max_response_bytes=2097152)
        path.write_bytes(P.compact(policy));channel=A.ReaderChannel(path,sha(path.read_bytes()),schemas);stack.callback(channel.close);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas);stack.callback(host.close)
        source_object=view.custody_signed_sources;family=SF.fresh_selected_source(source_object);basis=copy.deepcopy(SF.captured_source_basis(source_object))
        def guard():
            selected.guard();G.verify(source);schemas.guard();channel.guard();need(A.now()<end and H.cut(view)==cut and SF.captured_source_basis(source_object)==basis,'actual source/capture permission changed');SF.fresh_selected_source(source_object,family)
        guard();snapshot=load('_t31_actual_external_snapshot_'+str(os.getpid()),snapshot_path).OntologySnapshot(host,control_binding=sb,work_ref=work['version_ref'],live_guard=guard)
        capture_module=load(api.name+'._qualified_external_ontology_capture',variant)
        external_selection=capture_module.ExternalCapabilitySelection(host,binding=eb,capability=snapshot.capture,source_cut=cut,work_ref=work['version_ref'],live_guard=guard)
        st=temp.stat();custody={'root':str(temp),'identity':[st.st_dev,st.st_ino,os.getuid(),0o700],'output_roots':['stage-originals']}
        routes={ref:{'output_custody':custody,'output_scope_ref':head['store_ref'],'output_slot_ref':'slot:'+ref}for ref in('transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated')}
        capture=capture_module.OntologyTypedCapture(host,snapshot.capture,module=rich,control_binding=hb,route_rows=routes,read_public=P.source.original,source_rows=rows,carriers=CF.C.S.original_carriers(),guard=guard,external_selection=external_selection)
        produced=capture.produce(run_binding=run_binding,work_ref=work['version_ref'],source_cut=cut);guard();receipt_raw=(output/(produced['receipt_binding']['sha256']+'.json')).read_bytes();need(sha(receipt_raw)==produced['receipt_binding']['sha256'],'actual native capture receipt original differs')
        # Preserve originals from a second genuine cold read rather than
        # reconstructing the first call's unavailable return from a digest.
        external_selection.guard(snapshot.capture,{'resolver_binding':logical,'resolver_entrypoint':'OntologySnapshot.capture'})
        observed=snapshot.capture();guard()
        need(observed['cold_replay_binding']==produced['receipt']['original_cold_replay_binding'],
             'additional actual cold replay differs from original capture correspondence')
        external_selection.guard(snapshot.capture,{'resolver_binding':logical,'resolver_entrypoint':'OntologySnapshot.capture'})
        cold_originals={name:write(evidence/'additional-cold-originals'/(name+'.json'),observed[name+'_original'])
                        for name in('head','manifest','native_read','cold_replay','mapping_policy','mapping')}
        originals=[]
        for header in produced['artifacts']:
            raw=(output/(header['byte_sha256']+'.json')).read_bytes();need(sha(raw)==header['byte_sha256'],'actual original typed capture body differs');binding=write(evidence/'originals'/(header['byte_sha256']+'.json'),raw);originals.append({'artifact':header,'original_binding':binding})
        actual_capture_binding=write(evidence/'actual-capture-receipt.json',receipt_raw)
        allowed=set(importlib.import_module(api.name+'.workflow_output_registry').selected_transition(config['transition_ref'])['output_carriers'])
        outputs=[row['artifact']for row in originals if row['artifact']['carrier_ref']in allowed];need({h['carrier_ref']for h in outputs}==allowed,'actual stage output categories incomplete')
        if previous is None:
            initial=CF.C.S.OutputJournal.initialize(temp/'genesis-workflow',genesis_raw,work['scope_ref'],actor['principal_ref']);config_sha=initial.journal.config_sha256
        else:config_sha=previous['journal_head']['journal_config_sha256']
        prior_scope=CF.SC.capture(config['previous_scope'])if config['previous_scope']is not None else None
        source_row=importlib.import_module(api.name+'.runtime_selection').binding('family.source')
        scope_binding,index=scope_observation(evidence=evidence,capture={'transition_ref':config['transition_ref'],'receipt_binding':actual_capture_binding,'returned_receipt_binding':produced['receipt_binding'],'receipt_original':receipt_raw},outputs=outputs,
            run_binding=run_binding,work=work,actor=actor,run_ref=run_value['run_ref'],cut=cut,config_sha=config_sha,producer={'path':str(variant),'sha256':VARIANT_SHA},
            source_binding={'ref':source_row['path'],'sha256':source_row['sha256']},prior=prior_scope)
        # The exact actual scoped store checks the persisted proof/lineage before
        # this observation can be selected by a later public transition.
        need(index['actor']==actor,'scope wrapper changed actual actor');guard()
        result={'schema_version':'lab-actual-native-ontology-capture-observation/v1','result':'PASS-actual-native-capture-and-scope-observation','transition_ref':config['transition_ref'],
            'api_source_sha256':source,'api_profile_sha256':profile,'source_cut':cut,'actor':actor,'run_ref':run_value['run_ref'],'work':work,'run_binding':run_binding,
            'actual_capture_producer_binding':{'path':str(variant),'sha256':VARIANT_SHA},'actual_capture_receipt_binding':actual_capture_binding,'original_records':originals,
            'actual_returned_capture_receipt_binding':produced['receipt_binding'],
            'additional_actual_cold_replay':True,'original_capture_cold_receipt_reconstructed':False,'additional_cold_originals':cold_originals,
            'selected_stage_outputs':outputs,'scope_index_binding':scope_binding,'journal_config_sha256':config_sha,'projection_selection':config['projection_selection'],
            'scope_observation_is_wrapper':True,'public_workflow_transition_dispatched':False,'SourceAdmission_requirement_satisfied':False,'authority_effect':'none'}
        write(evidence/'RESULT.json',result);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--evidence',required=True);args=parser.parse_args()
    result=run(args.config,args.evidence);print(json.dumps({'result':result['result'],'scope_index_binding':result['scope_index_binding']},sort_keys=True),flush=True)
