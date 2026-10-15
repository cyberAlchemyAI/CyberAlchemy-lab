"""Retain actual identity/dispatch refusal proof and complete plan obligations."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v85'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent_path=API/'receipts/R03-0125.json';parent=load(parent_path)
    actual_path=RUN/'API85-Machine-scope-refusals-0001.json';actual=load(actual_path)
    assert actual['result']=='PASS' and actual['actual_cases']==1 and actual['failures']==actual['errors']==0
    assert len(actual['checks'])==4 and all(row['result']=='PASS' for row in actual['checks'])
    assert not actual['source_permission_and_clock_callbacks_replaced'] and not actual['time_bounds_extended']
    assert not actual['private_memory_or_credentials_exported'] and actual['canonical_effects']==0
    rows={row['path']:row for row in parent['files']}
    for row in actual['files']:rows[row['path']]=row
    for path in [parent_path,actual_path,Path(__file__).resolve()]:rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'actual_Machine_scope_refusals_binding':bind(actual_path),'actual_Machine_scope_refusal_cases':1,
           'actual_Machine_scope_refusal_checks':4,
           'remaining_obligations':[
               parent['remaining_obligations'][0],
               'Extend changed-callback/foreign actual-owner/signed-source negative coverage where original criteria require it; passing current4private identity/dispatch checks does not close fullAPI scope.',
               *parent['remaining_obligations'][2:]],
           'change':parent['change']+' Actual private scope refusal episode passed1case/4checks: exact actual parent policy host only, original dispatch refused before journal claim inside pure scope, missing live resource refused without reconstruction, and wrong bridge channel rejected. Original callbacks/clock/lifetime remained; no credentials/RAM exported or canonical effects. Full20selection21646continues.',
           'current_Machine_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual7Machine-read path and4private identity/dispatch refusal checks only. Full lifecycle, remaining11handlers, signed learning/application/outcomes and final owner admission remain.'}
    output=API/'receipts/R03-0126.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),'actual_refusal_checks':4,
                      'same_full20_job':21646,'whole_API_qualified':False}),flush=True)


if __name__=='__main__':main()
