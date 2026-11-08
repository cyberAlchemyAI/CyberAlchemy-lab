"""Candidate-only review/application boundary with current full evidence replay."""
from copy import deepcopy
from pathlib import Path
import argparse
import fcntl
import json
import os
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'evidence'))
import aggregate as a
b=a.b;v=b.v;s=b.s;g=b.g;o=a.o
STATE='relational.shadow-application-state/v1-candidate'
REVIEW='relational.shadow-review/v1-candidate'
SHADOW=HERE/'shadow'


def policy():
    return {'schema':'relational.application-adapter-policy/v1-candidate',
        'state':'Explicit mutable candidate shadow directory only; immutable accepted and authority sources stay read-only.',
        'review':'Full R03 replay bound to exact request, complete dependencies, shadow baseline, epoch and source bytes.',
        'application':'Recapture all identities and run complete fresh evidence replay; no result cache or review-label authority.',
        'drift':'Refuse an outdated review; require a fresh review and, for a changed semantic baseline, a newly supported formal baseline.',
        'concurrency':'Advisory lock serializes cooperating local adapters; external writers and adversarial filesystem races are outside this candidate simulation.',
        'authority_effect':'none','human_authority_granted':False}


def read_input(path):
    path=Path(path).resolve()
    s.require(path.is_relative_to(s.ROOT) and path.is_file(),'input must be an existing workspace file')
    binding=s.binding(path);_,raw=v.safe_binding(binding,limit=4*1024*1024)
    try:value=b.i.c.d.decode(raw)
    except RecursionError as error:raise ValueError('JSON parser depth limit exceeded') from error
    s.require(isinstance(value,dict),'input must be a JSON object')
    return value,binding


def owned_state(path,existing=True):
    path=Path(path).resolve();root=SHADOW.resolve()
    s.require(path.is_relative_to(root) and path.suffix=='.json' and path!=root,'state must be a JSON file inside the candidate shadow directory')
    if existing:s.require(path.is_file(),'candidate shadow state does not exist; initialize it explicitly')
    return path


def current_adapter():
    paths={HERE/name for name in ['adapter.py','candidate-adapter','adapter-policy.json']}
    for tid in ['R03','C06']:
        task=s.task(tid);s.require(task['status']=='accepted','adapter prerequisite not accepted: '+tid)
        ref=task['validation']['acceptance_ref'];v.safe_binding(ref,limit=64*1024*1024)
        p=s.ROOT/ref['path'];paths.add(p)
        receipt=s.read(p)
        for item in receipt['artifacts']+receipt['dependency_bindings']:
            bound={'path':item['path'],'sha256':item['sha256']};v.safe_binding(bound,limit=64*1024*1024)
            paths.add(s.ROOT/item['path'])
    s.require(s.read(HERE/'adapter-policy.json')==policy(),'adapter policy changed')
    return [s.binding(p) for p in sorted(paths)]


def capture(path):
    path=owned_state(path);state,binding=read_input(path)
    s.require(set(state)=={'schema','epoch','baseline_identity','snapshot','source_inputs'} and state['schema']==STATE,'invalid shadow state fields/schema')
    s.require(type(state['epoch']) is int and state['epoch']>=0,'shadow epoch must be a nonnegative integer')
    s.require(isinstance(state['snapshot'],dict) and set(state['snapshot'])=={'registry','rules','graph'},'invalid shadow snapshot')
    s.require(state['baseline_identity']==g.c.identity(state['snapshot']),'shadow baseline identity differs from actual snapshot')
    s.require(isinstance(state['source_inputs'],list) and len(state['source_inputs'])<=64,'invalid shadow source inventory')
    for source in state['source_inputs']:
        p,_=v.safe_binding(source,limit=4*1024*1024)
        s.require(p.is_relative_to(SHADOW.resolve()),'simulated source must be in the shadow directory')
    return state,{'state':binding,'source_inputs':deepcopy(state['source_inputs']),
                  'epoch':state['epoch'],'baseline_identity':state['baseline_identity']}


def capture_matches(proposal,state):
    s.require(state['snapshot']==proposal['before'] and state['baseline_identity']==proposal['baseline_identity'],
              'application baseline changed or is outside the selected captured formal profile; fresh checking requires a supported baseline')


def envelope(phase,execution='completed',currentness='current',status='not-applied',**extra):
    return {'schema':'relational.application-adapter-outcome/v1-candidate','phase':phase,
        'execution':execution,'currentness':currentness,'status':status,'authority_effect':'none',
        'human_authority_granted':False,'review_result_reused':False,'fresh_replay_performed':False,
        'requires_fresh_review':False,'diagnostics':[],**extra}


def initialize(path):
    path=owned_state(path,existing=False);s.require(not path.exists(),'initialization refuses to overwrite existing shadow state')
    v.replay.verify(s.read(s.BASE/'replay/dependency-manifest.json'))
    snapshot=g.c.baseline()
    value={'schema':STATE,'epoch':0,'baseline_identity':g.c.identity(snapshot),'snapshot':snapshot,'source_inputs':[]}
    path.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create: this command cannot replace an existing candidate or authority record.
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    return envelope('init',status='shadow-initialized',state=s.binding(path)),0


def load_requests(proposal_path,bundle_path):
    proposal,pbinding=read_input(proposal_path);bundle=None;bbinding=None
    if bundle_path:bundle,bbinding=read_input(bundle_path)
    b.source_boundary(proposal);b.execution_profile(proposal)
    return proposal,bundle,{'proposal':pbinding,'bundle':bbinding}


def check_requests(requests):
    for binding in requests.values():
        if binding is not None:v.safe_binding(binding,limit=4*1024*1024)


def review(proposal_path,bundle_path,state_path,output):
    proposal,bundle,requests=load_requests(proposal_path,bundle_path)
    state,captured=capture(state_path);capture_matches(proposal,state)
    dependencies=b.dependencies(proposal);adapter=current_adapter()
    outcome=a.verify(proposal,bundle)
    check_requests(requests)
    s.require(capture(state_path)[1]==captured,'application source/state changed during review')
    s.require(b.dependencies(proposal)==dependencies and current_adapter()==adapter,'semantic or adapter dependencies changed during review')
    outcome_path=output/'verified-review-outcome.json';s.write(outcome_path,outcome)
    dep_path=output/'captured-dependencies.json';s.write(dep_path,dependencies)
    receipt={'schema':REVIEW,'requests':requests,'captured_application':captured,
        'proposal_identity':g.c.identity(proposal),'policy_identity':g.c.identity(policy()),
        'dependencies':s.binding(dep_path),'adapter_bindings':adapter,'outcome':s.binding(outcome_path),
        'authority_effect':'none','human_authority_granted':False}
    receipt_path=output/'review.json';s.write(receipt_path,receipt)
    return envelope('review',execution=outcome['execution'],currentness=outcome['currentness'],
        status='candidate-ready-for-review' if o.exit_code(outcome)==0 else 'candidate-review-blocked',
        fresh_replay_performed=True,review_record=s.binding(receipt_path),outcome=outcome,
        captured_application=captured),o.exit_code(outcome)


def read_review(path):
    value,binding=read_input(path)
    s.require(set(value)=={'schema','requests','captured_application','proposal_identity','policy_identity',
        'dependencies','adapter_bindings','outcome','authority_effect','human_authority_granted'} and value['schema']==REVIEW,'invalid review record fields/schema')
    s.require(value['authority_effect']=='none' and value['human_authority_granted'] is False,'review cannot grant authority')
    s.require(value['policy_identity']==g.c.identity(policy()),'review policy changed')
    s.require(isinstance(value['requests'],dict) and set(value['requests'])=={'proposal','bundle'},'invalid review request inventory')
    return value,binding


def apply(review_path,proposal_path,bundle_path,state_path,output):
    receipt,review_binding=read_review(review_path)
    proposal,bundle,requests=load_requests(proposal_path,bundle_path)
    s.require(requests==receipt['requests'] and g.c.identity(proposal)==receipt['proposal_identity'],'review request identity changed; substitution cannot inherit checking')
    state_path=owned_state(state_path)
    # Only cooperating instances of this candidate adapter share this lock.
    with state_path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        state,captured=capture(state_path)
        s.require(captured==receipt['captured_application'],'application source/state changed since review; fresh checking required')
        capture_matches(proposal,state)
        for bound in receipt['adapter_bindings']:v.safe_binding(bound,limit=64*1024*1024)
        _,raw=v.safe_binding(receipt['dependencies'],limit=4*1024*1024);previous=b.i.c.d.decode(raw)
        dependencies=b.dependencies(proposal)
        s.require(previous==dependencies,'review semantic dependencies changed; fresh checking required')
        _,raw=v.safe_binding(receipt['outcome'],limit=4*1024*1024);old=b.i.c.d.decode(raw)
        required=[x['id'] for x in g.generate(proposal)['obligations']]
        o.validate(old,required);s.require(o.exit_code(old)==0,'previous candidate review is not ready; request a fresh review')
        adapter=current_adapter()
        s.require(adapter==receipt['adapter_bindings'],'adapter changed since review; fresh checking required')
        # The actual application result is always freshly recomputed. The old ready label is never used as evidence.
        outcome=a.verify(proposal,bundle)
        check_requests(requests);v.safe_binding(review_binding,limit=4*1024*1024)
        s.require(capture(state_path)[1]==captured,'application source/state changed during fresh checking')
        s.require(b.dependencies(proposal)==dependencies and current_adapter()==adapter,'semantic or adapter dependencies changed during fresh checking')
        outcome_path=output/'application-replay-outcome.json';s.write(outcome_path,outcome)
        if o.exit_code(outcome)!=0:
            return envelope('apply',execution=outcome['execution'],currentness=outcome['currentness'],
                status='fresh-replay-blocked',fresh_replay_performed=True,outcome=outcome),o.exit_code(outcome)
        updated=deepcopy(state);updated['epoch']+=1;updated['snapshot']=deepcopy(proposal['after'])
        updated['baseline_identity']=g.c.identity(updated['snapshot'])
        # Same-directory replacement, while holding the candidate's cooperative writer lock.
        with tempfile.NamedTemporaryFile(mode='w',dir=state_path.parent,prefix='.shadow-',delete=False) as stream:
            json.dump(updated,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno());staged=Path(stream.name)
        try:
            s.require(capture(state_path)[1]==captured,'application source/state changed before shadow commit')
            os.replace(staged,state_path)
        finally:
            staged.unlink(missing_ok=True)
        return envelope('apply',status='applied-to-shadow',fresh_replay_performed=True,
            outcome=outcome,review_record=review_binding,previous_application=captured,
            new_state=s.binding(state_path),new_epoch=updated['epoch'],
            candidate_baseline_identity=updated['baseline_identity']),0


class Parser(argparse.ArgumentParser):
    def error(self,message):raise ValueError(message)


def main():
    phase=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] in ['init','review','apply'] else 'review'
    runs=HERE/'runs';runs.mkdir(exist_ok=True);output=Path(tempfile.mkdtemp(prefix='boundary-',dir=runs))
    try:
        parser=Parser(description=__doc__);commands=parser.add_subparsers(dest='phase',required=True)
        init=commands.add_parser('init');init.add_argument('--state',type=Path,required=True)
        rev=commands.add_parser('review');rev.add_argument('proposal',type=Path)
        app=commands.add_parser('apply');app.add_argument('review',type=Path);app.add_argument('--proposal',type=Path,required=True)
        for p in [rev,app]:p.add_argument('--state',type=Path,required=True);p.add_argument('--bundle',type=Path)
        args=parser.parse_args();phase=args.phase
        if phase=='init':result,code=initialize(args.state)
        elif phase=='review':result,code=review(args.proposal,args.bundle,args.state,output)
        else:result,code=apply(args.review,args.proposal,args.bundle,args.state,output)
    except (ValueError,KeyError,TypeError,UnicodeError,g.c.jsonschema.ValidationError) as error:
        message=str(error);stale=any(x in message for x in ['stale','changed','substitution'])
        result=envelope(phase,execution='not-run',currentness='stale' if stale else 'unresolved',
            status='fresh-check-required' if stale else 'input-invalid',requires_fresh_review=stale,
            diagnostics=[a.diagnostic('application-stale' if stale else 'input-invalid',message,
                location='candidate application boundary',next_action='Recapture current candidate state and sources, request a fresh full review, and use a supported formal baseline.')])
        code=7 if stale else 2
    except OSError:
        result=envelope(phase,execution='unavailable',currentness='unresolved',status='provider-unavailable',
            diagnostics=[a.diagnostic('provider-unavailable','Candidate filesystem or required provider is unavailable.')]);code=5
    s.write(output/'adapter-outcome.json',result)
    print(json.dumps(result,indent=2,ensure_ascii=False));return code


if __name__=='__main__':raise SystemExit(main())
