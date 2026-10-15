"""Complete the staged API95 freeze; preserve its recorded construction attempt."""
import hashlib
import importlib.util
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v94';API=BASE/'api-v95'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def main():
    assert not (API/'source-manifest.json').exists()
    spec=importlib.util.spec_from_file_location('_api95_finalize_parent',OLD/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    parent=g.verify('309aef6ef048a4aab9964a009244a4f789225895a982229f260e02e474723bbf')
    profile=load(API/'contract-profile.json')
    rows={r['path']:r for r in profile['files']}
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json'),bind(Path(__file__).resolve())]:full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    context=RUN/'context-R03-full-qualification-0134.json'
    value={**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'unchanged_inherited_method_count':322,'explicit_revised_methods':['test_preparation.py:test_small_receipt_budget_refused_before_effect'],
        'fixture_input_revision':{'before':"c['max_response_bytes']=1",'after':"c['message']['budget']['max_output_bytes']=1",'assertions_changed':False},
        'qualification_context_binding':bind(context),'freeze_finalizer_binding':bind(Path(__file__).resolve()),
        'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False}
    with (API/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json')}))
if __name__=='__main__':main()
