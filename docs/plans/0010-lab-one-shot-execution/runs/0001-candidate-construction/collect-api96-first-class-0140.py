"""Preserve the sequential class before stopping redundant remaining execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import time

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
PLAN=RUN/'API96-class-worker-plan-0140.json'
EVENTS=RUN/'API96-all-0134.events.jsonl'
OUTPUT=RUN/'API96-sequential-first-class-0140.json'
PID=411579
PREFIX='_cal_API96_original323_actual.'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not OUTPUT.exists()
    assert binding(PLAN)['sha256']=='bb222638d482c7ddff50f571e25cd249f11eb25064f83e4ee60da55ba59a375f'
    plan=json.loads(PLAN.read_bytes());selected=set(plan['sequential_first_class'])
    deadline=time.monotonic()+7200
    while time.monotonic()<deadline:
        lines=EVENTS.read_text().splitlines();rows=[]
        for line in lines:
            try:rows.append(json.loads(line))
            except json.JSONDecodeError:break  # A still-open final append is not evidence.
        cases=[r for r in rows if r.get('result') and r.get('test','').startswith(PREFIX+'run_session_checks.')]
        identifiers={r['test'][len(PREFIX):].replace('.py:','.') for r in cases}
        expected={m.replace('.py:','.') for m in selected}
        following=next((r for r in rows if r.get('phase')=='running' and r.get('test','').startswith(PREFIX)
                        and not r['test'].startswith(PREFIX+'run_session_checks.')),None)
        if expected<=identifiers and following:
            cmd=Path('/proc')/str(PID)/'cmdline'
            if cmd.exists():
                args=cmd.read_bytes().split(b'\0')
                assert b'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/qualify-api96-0134.py' in args
                os.kill(PID,signal.SIGINT)
                for _ in range(300):
                    if not cmd.exists():break
                    time.sleep(0.1)
                assert not cmd.exists(),'sequential process did not exit; do not escalate'
            api=ROOT/'product/lab/release-candidates/v1/interface/api-v96'
            spec=importlib.util.spec_from_file_location('_first_class_exit_guard',api/'guard.py')
            guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(plan['source_sha256'])
            value={'schema_version':'lab-actual-sequential-class-observation/v1-candidate',
                   'result':'PASS' if len(cases)==34 and all(r['result']=='PASS' for r in cases) else 'FAIL',
                   'selected_methods':plan['sequential_first_class'],'actual_methods':len(cases),'cases':cases,
                   'following_class_started_after_original_class_cleanup':following,
                   'independent_source_guard_after_process_exit':True,'sequential_full_suite_complete':False,
                   'sequential_redundant_remainder_stopped_by_SIGINT':True,
                   'reason':'Eight disjoint class workers cover the remaining methods within the original source validity period.',
                   'files':[binding(PLAN),binding(EVENTS),binding(Path(__file__).resolve())],
                   'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
                   'claim_ceiling':'Exact first 34 original methods only; aggregate qualification requires every remaining worker and final guards.'}
            with OUTPUT.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
            print(json.dumps({'result':value['result'],'report_binding':binding(OUTPUT)}),flush=True)
            return
        if not (Path('/proc')/str(PID)/'cmdline').exists():raise RuntimeError('sequential run exited before the selected class boundary')
        time.sleep(1)
    raise RuntimeError('original class boundary not observed within collector limit')
if __name__=='__main__':main()
