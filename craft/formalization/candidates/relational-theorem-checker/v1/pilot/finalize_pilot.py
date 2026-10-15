#!/usr/bin/env python3
"""Record R06 only after an actual direct human review has been captured."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'workflow/cli'))
import runtime as c
s=c.s


def main():
    s.require(s.task('R06')['status']=='not-started','R06 already accepted; do not overwrite')
    path=HERE/'human-review.json'
    s.require(path.is_file(),'Actual human meaning, usefulness and bounded-use feedback is still required; do not invent it')
    human=s.read(path)
    s.require(human.get('schema')=='relational.human-candidate-review/v1' and
        human.get('source')=='direct user response in this thread' and human.get('quote'), 'missing captured direct human response')
    s.require(human.get('normative_meanings')=='accepted' and human.get('diagnostic_usefulness')=='accepted' and
        human.get('bounded_use_recommendation')=='recommended','human review requires revisions or is incomplete')
    s.require(human.get('authority_effect')=='none','candidate review cannot authorize an authority transition')
    # Capture is an operator trust boundary: this script cannot authenticate a
    # human from JSON labels. Codex must observe the direct response first.
    for binding in human['reviewed_artifacts']:c.v.safe_binding(binding,limit=64*1024*1024)
    audit=s.read(HERE/'machine-validation-audit.json');report=s.read(HERE/'shadow-pilot-report.json')
    s.require(audit['result']=='pass' and report['machine_result']=='pass','machine pilot incomplete')
    c.v.safe_binding(audit['validation_script']);c.v.safe_binding(report['validation_script'])
    paths={HERE/name for name in ['shadow-pilot-report.json','reviewer-feedback.md','supported-use-matrix.json',
        'context-pack.json','run_pilot.py','prepare_review.py','audit_machine.py','finalize_pilot.py',
        'pre-final-plan-audit.json','review-packet.md','review-explanation.md.in',
        'machine-validation-audit.json','human-review.json','complete_gate.py']}
    paths.update(p for p in (HERE/'cases').iterdir() if p.is_file())
    for binding in human['reviewed_artifacts']:
        p=s.ROOT/binding['path']
        if p.is_relative_to(HERE):paths.add(p)
    dependencies=[s.ROOT/b['path'] for b in audit['generated_evidence_dependencies']]
    for row in report['accepted_predecessor_cases']:
        c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
        dependencies.extend(s.ROOT/row[key]['path'] for key in ['outcome','stderr'])
    s.accept('R06',{str(p.relative_to(HERE)):p for p in sorted(paths)},
        ['Four fresh public command cases and thirty-three current accepted predecessor executions cover instance additions, unsupported endpoint changes, fresh kinds, complete rule changes, soundness/protected-boundary negatives, stale inputs and workflow failures. Actual graph/obligation sizes, wall time and peak RSS are recorded; the rule case has 15 satisfied obligations and the search case has exactly 14 satisfied plus one unknown witness.',
         'A direct human response, captured with its exact quote and reviewed artifact bindings, accepts the documented meanings and diagnostic usefulness separately from machine validity. The captured recommendation is bounded candidate use; operator capture is not machine authentication or organizational admission.'],
        ['The use matrix names exact captured structural/F0/fresh-head profiles, frozen epoch and lossy unary projection, remaining inherited semantics, measured-run limits and retained trust. Unsupported endpoint/old-head changes and unchecked search remain explicitly excluded from readiness.',
         'The pilot ran in candidate/owned shadow scopes and recorded no authority, deployment or live runtime change. Human review recommends bounded use only and is not an admission decision.'],
        sorted(set(dependencies)),human_review=s.binding(path))
    print('R06 accepted with actual human meaning/usefulness review')


if __name__=='__main__':main()
