"""Bind actual-failure learning candidates without implying application/admission."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v84'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent_path=API/'receipts/R03-0122.json'
    parent=load(parent_path)
    learning_path=RUN/'Machine-policy-custody-lesson-0001/index.json'
    learning=load(learning_path)
    assert learning['result']=='PASS' and learning['body_count']==4 and learning['declared_typed_relation_count']==3
    assert not learning['current_source_imported'] and not learning['application_created'] and not learning['outcome_assessed']
    assert not learning['short_memory_exported'] and not learning['private_keys_exported'] and not learning['canonical_admission']
    rows={row['path']:row for row in parent['files']}
    for row in learning['files']:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for path in [parent_path,learning_path,Path(__file__).resolve()]:rows[bind(path)['path']]=bind(path)
    actual_path=RUN/'API84-Machine-seven-read-observation-0002.json'
    actual=load(actual_path) if actual_path.exists() else None
    if actual is not None:
        rows[bind(actual_path)['path']]=bind(actual_path)
        for row in actual['files']:rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'actual_failure_learning_candidate_binding':bind(learning_path),
           'actual_failure_learning_candidate_body_count':4,'actual_failure_learning_candidate_relation_count':3,
           'learning_candidate_in_current_source':False,'learning_candidate_application_created':False,
           'actual_Machine_repair_case_binding':bind(actual_path) if actual is not None else None,
           'actual_Machine_repair_case_posture':actual['result'] if actual is not None else 'running',
           'remaining_obligations':[
               *parent['remaining_obligations'][:2],
               'Import exact scoped learning candidates into a freshly signed owned source with declared applicability, map their closed relations, and consume from a new actual Agent Context. The original Context9 deliberately refuses current lessons without this closure.',
               'Select and perform an actual controlled later lesson application and record outcome/counterevidence. The prior code repair/qualification is independent counterevidence, not inferred lesson application or causal benefit.',
               *parent['remaining_obligations'][3:]],
           'change':parent['change']+' Materialized4actual-diagnostic learning candidate bodies and3declared Typed Relations using current admitted signatures and schemas. Actual Agent/Session audit identities and accountability come from retained controlled opening metadata, not RAM. Lesson states a scoped falsifiable Machine/parent policy custody repair prediction, exclusions and explicit retention/expiry. No current-source import, application/outcome or canonical admission is inferred.',
           'claim_ceiling':'Exact original failure, candidate scope repair and schema/closed-relation learning materialization only. Actual repaired Machine, signed learning continuity, application/outcome, fullAPI and final admission remain.',
           'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    output=API/'receipts/R03-0123.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),
                      'learning_candidate_bodies':4,'learning_candidate_relations':3,
                      'actual_repaired_case_posture':value['actual_Machine_repair_case_posture']}),flush=True)


if __name__=='__main__':main()
