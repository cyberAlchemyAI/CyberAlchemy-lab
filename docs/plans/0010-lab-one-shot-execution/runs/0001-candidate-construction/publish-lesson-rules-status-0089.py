"""Publish verified pure lesson progress and the sole final admission boundary."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path): return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2); stream.write('\n')


def main():
    progress = BASE / 'api-v50/receipts/R03-0089.json'
    proof = load(progress)
    current = RUN / 'currentness-receipts/0153.json'
    checked = load(current)
    assert checked['result'] == 'PASS' and checked['completed_tasks'] == 36 and checked['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in checked['active_receipt_checks'])
    assert load(RUN / 'R03-0089-currentness-terminal-0001.json')['actual_exit_code'] == 0
    assert proof['lesson_selection_pure_rules_qualified'] and not proof['lesson_selection_public_handler_integrated']
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0089.md'
    with status.open('x') as stream:
        stream.write('''# Lab operational foundation: current candidate progress

The recommendation is in progress: build and verify the full candidate under the
existing authorization, then present one exact package for the sole final R08
owner admission after full S02. No additional construction approval is needed.

## Current state

| Item | State |
| --- | --- |
| Plan | 36/46 closed; R03/R06 in progress |
| Public contracts | 34 original contracts;17 authored handlers;17 missing operations |
| Typed operator | Separate API49/API50 full10-case suites PASS;12 actual calls each |
| Current full regression | Same API50 serialized452-case driver; typed10 complete, failure18 running |
| Lesson rules | New frozen pure evaluator;56 complete synthetic cases PASS |
| W06 retention | All53 original unchanged tests rerun PASS |
| Lesson API | Actual authenticated host and signed empty/nonempty source integration pending |
| Currentness | 153 PASS;38 active receipts;77 preparation files;887 baseline sources unchanged |
| Admission | Sole R08 pending full S02; no owner outcome supplied |

## New lesson-selection implementation

`lesson-selection-rules-v1` validates all three internal routing/applicability/domain
schemas, original Lesson carriers and original Lesson Selection output offline.
It checks exact original bytes, complete inventory/routing equality, independently
supplied review dispositions, retention, source cut, Session/Assignment joins,
expiry, every literal exclusion, current instructions, counterevidence and conflicts.

Missing or unresolved conditions block selection. Expired or explicitly excluded
lessons are omitted. Different otherwise eligible influences in one family block
both; an expired influence cannot block an eligible lesson. Returned check bytes
retain original evidence and counterevidence. No Application or store write occurs.

General status, retention and review profiles are explicitly declared. Their values
grant no authority. The original W06 controlled implementation and all53 tests
remain unchanged. The complete frozen56-case evaluator suite and53-test W06 suite
passed with actual runner exit0 and exact source checks before and after execution.

These are synthetic pure checks. Constructing ContextFacts, LessonFact or ReviewFact
authenticates no person, Agent or Session. The future host must select actual live
resources, original signed current inventory and independent policy, then complete
source and permission exit guards before exposing or materializing a result.

## Next work and decision boundary

1. Compose the lesson read through a declared successor policy and actual host
   transport; preserve existing operation sets and Machine action budget zero.
2. Qualify the complete empty and nonempty signed-source paths, refusal, expiry,
   revocation, changed source/permission, cleanup and Session disposal.
3. Finish the same API50 regression and all17 missing public operations, assigned
   Machine typed participation and canonical/internal endpoint resolvers.
4. Complete genuine R05 participant evidence, R06/R07 and the full S02 package.
5. Present exact reviewed package and evidence for the single final R08 decision.

Interrupted API47/API48 evidence remains preserved; unknown exits and cleanup are
not inferred. Live stores, existing keys and unrelated work are outside current
construction authorization. Durable Agent continuity remains Project State through
Context and Ontology Views; transient working state belongs to its Session.

R03-0089 binds15,597 files. The goal remains active and incomplete.
''')
    handoff = load(RUN / 'custody-integration-handoff-0075.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(current), current_status_binding=bind(status))
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] + [42656,10196,70081,50601,99443]))
    handoff['new_scoped_evidence']['lesson_select'] = 'Frozen pure evaluator56 synthetic checks PASS and all53 original W06 tests PASS; actual exit0. Public host/signed-source/Session composition remains pending.'
    handoff['next_action'] = [
        'Observe same28245 driver21680 and each actual child/report/terminal; no restart on observation timeout.',
        'Compose actual lesson.select transport and independently selected successor policy with frozen lesson-selection-rules-v1, original Context Query and Lesson Selection.',
        'Qualify signed empty/nonempty inventory and actual live Session/Assignment with complete source/permission guards; synthetic dataclass facts confer no authority.',
        'Complete all17 remaining operations, assigned Machine typed support, authority resolvers and genuine R05/R06/R07/S02 before sole R08.',
        'Preserve original failed/interrupted evidence; no existing private key, short memory, claim or fixture restoration.'
    ]
    handoff['terminal_bindings'].extend([bind(RUN / 'lesson-selection-rules-terminal-0001.json'), bind(RUN / 'R03-0089-currentness-terminal-0001.json')])
    hp = RUN / 'custody-integration-handoff-0076.json'
    put(hp, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0089.json'
    put(index, {'schema_version': 'lab-current-progress-index/v1-candidate', 'publisher_binding': bind(Path(__file__).resolve()),
        'progress_binding': bind(progress), 'currentness_binding': bind(current), 'status_binding': bind(status),
        'handoff_binding': bind(hp), 'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none',
        'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index), 'status': bind(status),
                      'handoff': bind(hp), 'goal_complete': False}), flush=True)


if __name__ == '__main__': main()
