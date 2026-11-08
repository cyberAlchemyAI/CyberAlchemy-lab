"""Select actual successful T17 originals and create review/failure controls."""
import argparse
import importlib
import json
import os
from pathlib import Path
import sys

def need(value,reason):
    if not value:raise ValueError(reason)
def run(terminal_path,output,kind,control_result=None,preflight_only=False):
    selected=sys.modules.get('cal_installed_runtime_selection_v1');need(selected is not None,'selected installed launcher required');selected.require_runtime_ready();selected.guard();root=selected.root()
    folder=root/'implementation/lab-runtime/local-host/t31-retained-api-0001';sys.path.insert(0,str(folder));R=importlib.import_module('retained');P=importlib.import_module('producer')
    terminal_path=Path(terminal_path).absolute();raw=R.read(terminal_path);terminal=json.loads(raw);need(terminal['result']=='PASS','actual passing T17 terminal required')
    operation={'review-admission':'proposal.review','failure-assessment':'failure.assess'}[kind]
    cases=[case for case in terminal['cases']if case['operation']==operation and case['expected_kind']=='result'and case['result']=='PASS'];need(len(cases)==1,'one exact successful producer case required');case=cases[0];archive=case['retained_originals']
    selection={'archive':archive['path'],'observation_sha256':archive['observation_sha256'],'terminal_result':str(terminal_path),'terminal_sha256':R.sha(raw),
      'source_sha256':terminal['source_sha256'],'profile_sha256':terminal['profile_sha256'],'operation':operation};observed=R.consume(**selection)
    need(terminal['source_sha256']==selected.binding('api.source')['sha256']and terminal['profile_sha256']==selected.binding('api.profile')['sha256'],
         'final T17 producer source/profile selection differs')
    def plugin(name,controls):
        path=folder/name;return {'module_binding':{'path':str(path.relative_to(root)),'sha256':R.sha(path.read_bytes())},'entrypoint':'produce','controls':controls}
    typed=[];transitions={};stage_inputs={}
    def ref(carrier,records):
        matches=[h['version_ref']for h,body in records.values()if h['carrier_ref']=='cal.artifact-type.'+carrier];need(len(matches)==1,'one exact typed role required: '+carrier);return matches[0]
    records={h['version_ref']:(h,body)for h,body in observed['outputs']}
    if kind=='review-admission':
        typed=[plugin('review_scope.py',{'review_observation_ref':observed['observation_binding']['ref']})]
        transition='transition:review-admission:review-ready';transitions[transition]=[ref('decision-bundle/v1',records),ref('decision-checkpoint/v1',records)]
        proof=P.ArchiveProof([selection],transitions=transitions,typed_productions=typed);records=proof.records
        stage_inputs[transition]={'cal.artifact-type.'+carrier:ref(carrier,records)for carrier in('decision-bundle/v1','decision-checkpoint/v1','decision-scope/v2')}
        final='review-ready'
    else:
        transitions={'transition:failure-assessment:classified':[ref('classification-assignment/v1',records)],'transition:failure-assessment:assessed':[ref('failure-assessment/v1',records)]}
        if control_result is not None:
            path=Path(control_result).absolute();binding={'ref':str(path),'sha256':R.sha(R.read(path))};typed=[plugin('rule_control.py',{'result_binding':binding})]
            result=json.loads(R.read(path));transitions['transition:failure-assessment:response-assessed']=[result['candidate_output']['version_ref']]
        proof=P.ArchiveProof([selection],transitions=transitions,typed_productions=typed);records=proof.records
        for transition in transitions:
            carriers=['failure-occurrence/v1','evidence-set/v1']
            if not transition.endswith(':classified'):carriers.append('classification-assignment/v1')
            if transition.endswith(':response-assessed'):carriers.append('failure-assessment/v1')
            stage_inputs[transition]={'cal.artifact-type.'+carrier:ref(carrier,records)for carrier in carriers}
        final='response-assessed'if control_result is not None else'assessed'
    stages=[{'transition_ref':transition,'input_refs':stage_inputs[transition],'output_refs':outputs}for transition,outputs in transitions.items()]
    if preflight_only:stages=stages[:1];final={'review-admission':'review-ready','failure-assessment':'classified'}[kind]
    config={'schema_version':'lab-actual-retained-workflow-run/v1','kind':kind,'selections':[selection],'typed_productions':typed,'stages':stages,'final_state':final}
    output=Path(output).absolute();need(not output.exists()and output.parent.is_dir()and not output.is_relative_to(root),'fresh external private workflow config required');raw=P.enc(config)
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return {'config':str(output),'sha256':R.sha(raw),'selected_stages':[stage['transition_ref']for stage in stages],'public_API_dispatched':False,'authority_effect':'none'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--terminal',required=True);parser.add_argument('--output',required=True);parser.add_argument('--kind',choices=['review-admission','failure-assessment'],required=True);parser.add_argument('--control-result');parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    print(json.dumps(run(args.terminal,args.output,args.kind,args.control_result,args.preflight_only),sort_keys=True),flush=True)
