"""Reconcile both actual original suite terminals without changing task closure."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    terminal=RUN/'API80-machine-lifecycle-full-terminal-0001.json'
    report=RUN/'API80-machine-lifecycle-full-0001.json'
    v=load(report)
    assert load(terminal)['actual_exit_code']==1
    assert v['actual_cases']==20 and v['failures']==0 and v['errors']==1
    parent=RUN/'custody-integration-handoff-0102.json'
    old=load(parent)
    before=RUN/'OPERATIONAL-FOUNDATION-STATUS-0120.md'
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0121.md'
    text=before.read_text().replace(
        'The same API80 original20case job remains observed until its actual terminal.\nThe API83 original seven-read method also runs with an explicitly declared',
        'API80 also completed all20original cases with actual exit1:19passes,\n1observation-helper error,0assertion failures and5retained Machine replies.\nIts error occurred while observing session.inspect after a successful actual\nMachine context.get reply. The observer tried to access the disposed peer service;\nthe underlying transport outcome remains unrecorded and full qualification stays\nopen. Both original suite terminals are preserved.\nThe API83 original seven-read method runs with an explicitly declared')
    assert text!=before.read_text()
    with status.open('x') as stream:stream.write(text)
    handoff=RUN/'custody-integration-handoff-0103.json'
    emit(handoff,{**old,'parent_handoff_binding':bind(parent),'current_status_binding':bind(status),
                  'API80_original_terminal_binding':bind(terminal),'API80_original_report_binding':bind(report),
                  'closed_jobs_do_not_repoll':sorted(set(old['closed_jobs_do_not_repoll']+[19391,84158])),
                  'same_live_jobs':[{'tool_session_id':60417,'API':83,'purpose':'original-seven-read-method-with-parent-owned-test-observation'}],
                  'next_action':[
                      'Observe the same API83 original seven-read diagnosis job60417, retain actual returned transport outcomes and timing after peer disposal; runtime clocks/permissions/source callbacks stay unchanged.',
                      *old['next_action'][1:]]})
    old_index=RUN/'R03-CURRENT-PROGRESS-0120.json'
    index=RUN/'R03-CURRENT-PROGRESS-0121.json'
    emit(index,{**load(old_index),'parent_index_binding':bind(old_index),'publisher_binding':bind(Path(__file__).resolve()),
                'status_binding':bind(status),'handoff_binding':bind(handoff),
                'API80_original_terminal_binding':bind(terminal),'API80_original_report_binding':bind(report),
                'API80_actual_cases':20,'API80_actual_passes':19,'API80_actual_errors':1,
                'same_live_jobs':[60417]})
    print(json.dumps({'result':'PUBLISHED-ACTUAL-ORIGINAL-TERMINALS','index':bind(index),
                      'status':bind(status),'handoff':bind(handoff),'live_job':60417}),flush=True)


if __name__=='__main__':main()
