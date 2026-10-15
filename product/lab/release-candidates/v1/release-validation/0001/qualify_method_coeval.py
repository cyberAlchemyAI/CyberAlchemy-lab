"""Actual original Method instance against the explicit technical candidate revision."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
import materialize_targets_v2 as M
B=M.B

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--api-directory',required=True)
    parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--meta-proposal-sha256',required=True);parser.add_argument('--instance-sha256',required=True)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output).resolve();B.need(output.parent==B.HERE and not output.exists(),'exclusive owned proof required')
    api=Path(args.api_directory).resolve();meta=B.HERE/'native-method-namespace-revision-0001/native-proposal.json'
    instance=B.ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method/example.json'
    value=B.exact(meta,args.meta_proposal_sha256);raw=B.read(instance);B.need(B.sha(raw)==args.instance_sha256,'independent original Method body differs')
    fd=os.open(B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock',os.O_RDWR|os.O_NOFOLLOW)
    started=datetime.now(timezone.utc).isoformat();result=None;failure=None;entry=False;exit_guard=False;guard=None
    try:
        fcntl.flock(fd,fcntl.LOCK_SH)
        guard,bridge,schemas=M.family(api,args.source_sha256,args.profile_sha256);entry=True
        with bridge.replay_source('source8-session-participation') as view:
            before=view.handle.common.digest(view.data['projection']);record=json.loads(raw)
            B.need(len(value['targets'])==1 and value['targets'][0]['category']=='artifact-type','exact reviewed metatype proposal required')
            contract=value['targets'][0]['contract'];B.need(contract['semantic_kind']=='method' and contract['identity_field']=='method_id','original Method identity contract differs')
            proposal={**value,'proposal_id':'method-v1-namespace-coeval-original-instance-review-0254','targets':[
                value['targets'][0],{'category':'artifact-instance','operation':'admit',
                    'version_ref':record['method_id']+'@'+record['version'],
                    'carrier_ref':value['targets'][0]['version_ref'],'record':record,
                    'predecessor_ref':None,'decision_ref':'decision:original-Method-coeval-instance-review-0254',
                    'contract':None,'content':view.handle.custody.content_entry(raw)}]}
            with tempfile.TemporaryDirectory(prefix='cal-S02-method-coeval-native-review-0254-') as temporary:
                store=Path(temporary)/'store';store.mkdir(mode=0o700)
                for name,body in view.originals.items():
                    p=store/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                    with p.open('xb') as stream:stream.write(body)
                    p.chmod(0o600)
                result=view.handle.store_module.Store(store,B.ROOT).review(proposal)
                B.need(result['target_count']==2 and [r['category'] for r in result['decision_cores']]==['artifact-type','artifact-instance'], 'actual independent two-core result differs')
                B.need(all((store/name).read_bytes()==body for name,body in view.originals.items()),'pure Review changed original source bytes')
                B.need({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()}==set(view.originals),'pure Review created source or Session material')
            B.need(view.handle.common.digest(view.data['projection'])==before,'original projection grafted')
            view.handle.guard()
        schemas.guard();guard.verify(args.source_sha256);B.exact(api/'contract-profile.json',args.profile_sha256)
        B.exact(meta,args.meta_proposal_sha256);B.need(B.bind(instance)['sha256']==args.instance_sha256,'original instance exit bytes differ');exit_guard=True
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    good=result is not None and failure is None and entry and exit_guard
    report={'schema_version':'lab-original-Method-coeval-technical-revision-review/v1-candidate',
        'result':'REVIEWED-CANDIDATE-ONLY' if good else 'REFUSED','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
        'caller_binding':B.bind(Path(__file__)),'API_source_binding':B.bind(api/'source-manifest.json'),
        'API_profile_binding':B.bind(api/'contract-profile.json'),'original_metatype_proposal_binding':B.bind(meta),
        'original_Method_body_binding':B.bind(instance),'actual_native_review':result,'failure':failure,
        'full_source_entry_guard':entry,'full_source_exit_guard':exit_guard,'fixture_example_only':True,
        'original_Method_body_unchanged':True,'owned_scratch_removed':True,'source8_projection_grafted':False,
        'source_admissions':0,'actual_owner_outcome':None,'runtime_activations':0,'authority_effect':'none',
        'final_member_package_qualified':False,'release_ready':False,'task_complete':False,'goal_complete':False}
    B.emit(output,report);print(json.dumps({'result':report['result'],'report_binding':B.bind(output),'failure':failure}),flush=True)
    return 0 if good else 2

if __name__=='__main__':raise SystemExit(main())
