"""Fresh, fail-closed native control and all-28 Workflow qualification.

Run this external orchestrator through the installed selected-python launcher.
Each child owns a new private fixture and idempotency key. A failed or
interrupted step is terminal for this run; inspect its retained originals and
start a new selected run rather than replaying a pending claim.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HELPERS=ROOT/'implementation/lab-runtime/local-host/t31-retained-api-0001'
INVENTORY=ROOT/'implementation/lab-runtime/local-host/t31-native-challenge-0001/ORIGINAL-28-TRANSITION-INVENTORY-0002.json'


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()


def read(binding):
    need(type(binding)is dict and set(binding)=={'path','sha256'},'closed exact file binding required')
    path=Path(binding['path'])
    need(path.is_absolute() and path.is_file() and not path.is_symlink() and not any(p.is_symlink()for p in path.parents),
         'absolute regular non-symlinked selected file required')
    raw=path.read_bytes();need(sha(raw)==binding['sha256'],'selected file bytes changed')
    return json.loads(raw)


def write(path,value):
    raw=value if type(value)is bytes else encoded(value)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as file:file.write(raw);file.flush();os.fsync(file.fileno())
    return {'path':str(path),'sha256':sha(raw)}


def selected(plan):
    runtime=sys.modules.get('cal_installed_runtime_selection_v1')
    need(runtime is not None,'installed selected-python launcher required')
    runtime.require_runtime_ready();runtime.guard()
    root=runtime.root()
    need(str(root)==plan['installed_repository'],'plan selects another installed repository')
    source=runtime.binding('api.source')['sha256'];profile=runtime.binding('api.profile')['sha256']
    need(source==plan['source_sha256'] and profile==plan['profile_sha256'],
         'plan selects another API Source/profile')
    launcher=root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
    need(launcher.is_file() and not launcher.is_symlink(),'selected installed launcher unavailable')
    return runtime,launcher


def check_prior_chain(binding,plan,wanted,depth=0):
    """Reconcile every prior ledger row to retained native child evidence."""
    if binding is None:return []
    need(depth<28,'prior phase chain exceeds original transition count')
    prior=read(binding)
    need(prior['schema_version']=='lab-t31-final-native-supervision-result/v1'
         and prior['mode']=='phase' and prior['result']=='PASS-phase'
         and prior['source_sha256']==plan['source_sha256']
         and prior['profile_sha256']==plan['profile_sha256']
         and prior['inventory_binding']==plan['inventory_binding']
         and prior['control_result_binding']==plan['control_result_binding'],
         'exact successful prior phase required')
    earlier=check_prior_chain(prior['prior_result_binding'],plan,wanted,depth+1)
    folder=Path(binding['path']).parent
    added=[]
    for row in prior['stage_evidence']:
        need(type(row)is dict and set(row)=={'terminal_binding','child_result_binding','expected_transitions'},
             'closed prior phase step evidence required')
        terminal_path=Path(row['terminal_binding']['path'])
        child_path=Path(row['child_result_binding']['path'])
        need(terminal_path.parent==folder and child_path.parent.parent==folder,
             'prior phase evidence paths differ')
        terminal=read(row['terminal_binding']);child=read(row['child_result_binding'])
        refs=[case.get('transition_ref') for case in child.get('cases',[])]
        need(terminal['result']=='PASS' and terminal['result_binding']==row['child_result_binding']
             and child['result']=='PASS' and child['source_sha256']==plan['source_sha256']
             and child['profile_sha256']==plan['profile_sha256']
             and child['actual_public_transition_commits']==len(refs)
             and refs==row['expected_transitions']
             and all(case.get('result')=='PASS' and case.get('actual_native_common_dispatcher')is True
                     and case.get('exact_retry_read_only')is True for case in child['cases']),
             'prior phase native child evidence differs')
        added.extend(refs)
    completed=earlier+added
    need(added and completed==wanted[:len(completed)]
         and prior['completed_transition_refs']==completed
         and prior['actual_transition_count']==len(completed),
         'prior phase cumulative evidence ledger differs')
    return completed


def validate(plan):
    base={'schema_version','mode','installed_repository','source_sha256','profile_sha256','authority_effect'}
    need(type(plan)is dict and plan.get('schema_version')=='lab-t31-final-native-supervision/v1'
         and plan.get('authority_effect')=='none' and plan.get('mode')in ('control','phase','transitions'),
         'closed final native plan required')
    if plan['mode']=='control':
        need(set(plan)==base,'closed control plan required')
    else:
        extra={'inventory_binding','control_result_binding','steps'}
        if plan['mode']=='phase':extra.add('prior_result_binding')
        need(set(plan)==base|extra,'closed native transition plan required')
        inventory=read(plan['inventory_binding'])
        need(Path(plan['inventory_binding']['path'])==INVENTORY and
             inventory['transition_count']==28 and len(inventory['rows'])==28,
             'exact original 28-transition inventory required')
        wanted=[row['transition_ref'] for row in inventory['rows']]
        need(type(plan['steps'])is list and bool(plan['steps']),'nonempty selected transition steps required')
        actual=[];names=[]
        for step in plan['steps']:
            need(type(step)is dict and set(step)=={'name','config_binding','expected_transitions'},
                 'closed transition step required')
            name=step['name'];need(type(name)is str and name and name.replace('-','').replace('_','').isalnum()
                 and len(name)<=64,'safe unique step name required')
            names.append(name)
            config=read(step['config_binding'])
            need(config['schema_version']=='lab-actual-retained-workflow-run/v1',
                 'selected native workflow configuration required')
            refs=[row['transition_ref'] for row in config['stages']]
            need(refs==step['expected_transitions'] and bool(refs),
                 'step does not select exact config transitions')
            actual.extend(refs)
        need(len(set(names))==len(names),'unique step names required')
        if plan['mode']=='transitions':
            need(actual==wanted,'steps must cover every original transition once in original order')
        else:
            prior=check_prior_chain(plan['prior_result_binding'],plan,wanted)
            need(type(prior)is list and prior==wanted[:len(prior)],
                 'prior completed transition ledger differs')
            need(actual and actual==wanted[len(prior):len(prior)+len(actual)],
                 'phase must add the exact next original transition slice')
        control=read(plan['control_result_binding'])
        need(control['result']=='PASS-actual-known-rule-refusal-and-candidate-detect-binding'
             and control['api_source_sha256']==plan['source_sha256']
             and control['api_profile_sha256']==plan['profile_sha256'],
             'fresh same-release control result required')
    selected(plan)
    return plan


def run_child(launcher,script,args,evidence,log_name,limit):
    cmd=[str(launcher),'-B',str(script),*args]
    stdout=evidence/(log_name+'-stdout.log');stderr=evidence/(log_name+'-stderr.log')
    with stdout.open('xb') as out,stderr.open('xb') as err:
        child=None
        try:
            child=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                                   start_new_session=True)
            exit_code=child.wait(timeout=limit)
            timed_out=False
        except subprocess.TimeoutExpired:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            child.wait()
            exit_code=None;timed_out=True
        except BaseException:
            if child is not None and child.poll() is None:
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                child.wait()
            raise
        out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
    return {'exit_code':exit_code,'timed_out':timed_out,
            'stdout_sha256':sha(stdout.read_bytes()),'stderr_sha256':sha(stderr.read_bytes())}


def run(plan_path,evidence,limit):
    plan=validate(read({'path':str(plan_path),'sha256':sha(plan_path.read_bytes())}))
    runtime,launcher=selected(plan)
    evidence=Path(evidence).absolute()
    need(not evidence.exists() and evidence.parent.is_dir() and not evidence.is_relative_to(runtime.root())
         and not any(p.is_symlink()for p in evidence.parents),'fresh external evidence directory required')
    evidence.mkdir(mode=0o700)
    write(evidence/'PLAN.json',plan)
    if plan['mode']=='control':
        steps=[{'name':'control-0001','script':HELPERS/'control_probe.py','args':[]}]
    else:
        steps=[{'name':s['name'],'script':HELPERS/'run_current.py',
                'args':['--config',s['config_binding']['path']],
                'expected_transitions':s['expected_transitions']} for s in plan['steps']]
    terminal=[];stage_evidence=[]
    for index,step in enumerate(steps,1):
        selected(plan)
        folder=evidence/f"{index:02d}-{step['name']}"
        need(not folder.exists(),'step evidence cannot be replayed')
        write(evidence/f"{index:02d}-START.json",{'step':step['name'],
              'observed_at':datetime.now(timezone.utc).isoformat(),'source_sha256':plan['source_sha256']})
        args=step['args']+['--evidence',str(folder)]
        observation=run_child(launcher,step['script'],args,evidence,
                              f"{index:02d}-{step['name']}",limit)
        result_path=folder/'RESULT.json'
        if observation['exit_code']==0 and result_path.is_file():
            result=json.loads(result_path.read_bytes())
            if plan['mode']=='control':
                ok=(result.get('result')=='PASS-actual-known-rule-refusal-and-candidate-detect-binding'
                    and result.get('api_source_sha256')==plan['source_sha256']
                    and result.get('api_profile_sha256')==plan['profile_sha256'])
            else:
                refs=[case.get('transition_ref') for case in result.get('cases',[])]
                ok=(result.get('result')=='PASS' and result.get('source_sha256')==plan['source_sha256']
                    and result.get('profile_sha256')==plan['profile_sha256']
                    and result.get('actual_public_transition_commits')==len(step['expected_transitions'])
                    and refs==step['expected_transitions']
                    and all(case.get('result')=='PASS' and case.get('actual_native_common_dispatcher')is True
                            and case.get('exact_retry_read_only')is True for case in result['cases']))
            observation['result_binding']={'path':str(result_path),'sha256':sha(result_path.read_bytes())}
        else:ok=False
        observation.update(step=step['name'],result='PASS' if ok else 'FAIL',
                           observed_at=datetime.now(timezone.utc).isoformat())
        terminal_binding=write(evidence/f"{index:02d}-TERMINAL.json",observation)
        terminal.append(observation)
        if ok and plan['mode']=='phase':
            stage_evidence.append({'terminal_binding':terminal_binding,
                'child_result_binding':observation['result_binding'],
                'expected_transitions':step['expected_transitions']})
        if not ok:break
    if all(row['result']=='PASS' for row in terminal) and len(terminal)==len(steps):
        selected(plan)
        completed=[]
        if plan['mode']=='phase':
            if plan['prior_result_binding'] is not None:
                completed=read(plan['prior_result_binding'])['completed_transition_refs']
            completed=completed+[
                ref for step in plan['steps'] for ref in step['expected_transitions']]
            inventory=read(plan['inventory_binding'])
            wanted=[row['transition_ref'] for row in inventory['rows']]
            need(completed==wanted[:len(completed)],'actual cumulative transition order differs')
        result={'schema_version':'lab-t31-final-native-supervision-result/v1',
                'result':('PASS-all28' if len(completed)==28 else 'PASS-phase')
                         if plan['mode']=='phase' else 'PASS',
                'mode':plan['mode'],'source_sha256':plan['source_sha256'],
                'profile_sha256':plan['profile_sha256'],'completed_steps':len(terminal),
                'actual_transition_count':28 if plan['mode']=='transitions' else len(completed),
                'authority_effect':'none'}
        if plan['mode']=='phase':
            result['inventory_binding']=plan['inventory_binding']
            result['completed_transition_refs']=completed
            result['control_result_binding']=plan['control_result_binding']
            result['prior_result_binding']=plan['prior_result_binding']
            result['stage_evidence']=stage_evidence
        write(evidence/'RESULT.json',result)
    else:
        result={'schema_version':'lab-t31-final-native-supervision-result/v1','result':'FAIL',
                'mode':plan['mode'],'completed_steps':len(terminal),'authority_effect':'none'}
        write(evidence/'FAILURE.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--child-timeout-seconds',type=int,default=10800)
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args();need(300<=args.child_timeout_seconds<=21600,'bounded child timeout required')
    if args.validate_only:
        row=validate(read({'path':str(args.plan.absolute()),'sha256':sha(args.plan.read_bytes())}))
        print(json.dumps({'result':'PASS-plan-only','mode':row['mode']},sort_keys=True))
    else:
        print(json.dumps(run(args.plan.absolute(),args.evidence,args.child_timeout_seconds),sort_keys=True),flush=True)
