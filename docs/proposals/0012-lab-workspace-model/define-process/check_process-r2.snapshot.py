#!/usr/bin/env python3
"""Verify recorded real Define CLI runs; never provision/sign/apply or rewrite Packs."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROPOSAL = HERE.parent
ROOT = PROPOSAL.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


def read(path):
    return json.loads(path.read_text())


def require(value, code):
    if not value:
        raise ValueError(code)


def inventory(path):
    return {f.relative_to(path).as_posix(): sha(f.read_bytes()) for f in path.rglob('*') if f.is_file()}


def presentation():
    package = HERE / 'package-0002'
    pack = read(package / 'pack.json')
    materialized = read(HERE / 'materialized-0002/definitions/000/definition.json')
    answer = read(HERE / 'input/terminology-answer.json')
    lines = ['<!-- GENERATED from frozen Define Pack revision 2 and exact captured source bytes. -->', '',
        '# Define result: Lab workspace model', '',
        '**Actual CLI result: prepared-with-gaps.** Revision 2 preserves revision 1 and the explicit user terminology answer.', '',
        'The original proposal was authored directly before this Define pass. This run is corrective preparation, not retrospective proof that the original workflow occurred.', '',
        '- Consumer: `' + pack['scope']['consumer'] + '`',
        '- Intended use: `' + pack['scope']['intended_use'] + '`',
        '- Goal: ' + pack['scope']['goal'],
        '- Originating intent: ' + pack['scope']['originating_intent'], '',
        '## Explicit answer', '', answer['answer'], '',
        'This closes the terminology question for candidate authoring. It does not accept the entire Workspace meaning or establish native owner authority.', '',
        '## Actual stages', '',
        '| Stage | Observed result |', '| --- | --- |',
        '| Default Define/native-context integrity and read | Completed, no store/key setup |',
        '| Define v3 Lab snapshot capture | Completed, exact registry/body snapshot matching |',
        '| Prepare | Prepared with gaps |',
        '| Inspect | Frozen package integrity verified |',
        '| Materialize | Complete candidate Definition/v2 emitted with field lineage; owner outcome null |',
        '| Reconstruct | Exact frozen members restored |',
        '| Observe requested owner-review use | Blocked: local snapshot and current authority not established |', '',
        'The materialization operation emitted candidate bytes. Frozen preparation readiness and actual materialization results are separate records; no Pack is rewritten to convert a blocked use into permission.', '',
        '## Dispositions', '', '| Concept | Disposition | Decision route |', '| --- | --- | --- |']
    bodies = {}
    for item in pack['handling']:
        route = 'role:definition-owner'
        if item['disposition'] == 'reuse':
            ref = item['payload']['meaning_ref']
            body = read(package / 'inputs' / ref['input_id'])
            bodies[item['concept_id']] = body
            route = body['semantic_owner_ref']
        elif item['disposition'] == 'open':
            route = item['payload']['owner_route'] or 'unresolved'
        lines.append('| ' + item['concept_id'] + ' | ' + item['disposition'] + ' | `' + route + '` |')
    lines += ['', '## New Workspace proposal', '',
        'Candidate only, unchanged from the retained pre-Define draft. The CLI independently checked its carrier, symbol declarations and mechanical field attribution; semantic fidelity remains separately reviewable.', '',
        '**Normative proposal**', '', materialized['voices']['scientific_formal']['normative_statement'], '',
        '**Formal expression**', '', '```text', materialized['voices']['scientific_formal']['formal_expression'], '```', '',
        '**Notation**', '']
    lines += ['- `' + n['symbol'] + '`: ' + n['meaning'] for n in materialized['voices']['scientific_formal']['notation']]
    lines += ['', '**Plain-language interpretation**', '', materialized['voices']['plain_language']['explanation'], '',
        '**Domain interpretation**', '', materialized['voices']['domain_context']['explanation'], '']
    lines += ['- ' + text for text in materialized['voices']['domain_context']['examples']]
    lines += ['', '**Applicability**', '', materialized['scope']['applicability'], '', '**Boundaries**', '']
    lines += ['- ' + text for text in materialized['boundaries']]
    lines += ['', '## Local terminology convention', '',
        'The explicit answer is recorded as a local Pack working meaning. It is not selected for another shared Definition:', '',
        next(h['payload']['working_meaning']['statement'] for h in pack['handling'] if h['concept_id'] == 'lab-instance-terminology'), '',
        'Its scope is this candidate model. The source is the explicit user answer, not an inferred review decision.', '',
        '## Open questions and stopping conditions', '']
    for item in pack['handling']:
        if item['disposition'] != 'open': continue
        data = item['payload']
        lines += ['### ' + item['concept_id'], '', data['question'], '',
            '- Reason: ' + data['reason'], '- Affected use: `' + data['affected_use'] + '`',
            '- Owner route: `' + str(data['owner_route']) + '`', '- Next action: ' + data['continuation'], '']
    lines += ['Owner-review use additionally remains blocked by `local-snapshot` and `current-authority`. No operator setup, signing, native review/apply or canonical registry admission was performed.', '',
        '## Allowed use and claim ceiling', '',
        'Inspect the prepared meaning and exact sources; challenge or revise candidate content; verify frozen bytes; materialize the explicitly selected candidate. Native review/adoption/publication follows its own qualified route.', '',
        pack['claim_ceiling'], '',
        '## Exact reused meanings', '',
        'The Lab adapter records historical registry/body matches. Standalone Define keeps each meaning at local-reference standing; these snapshots are not authenticated current host permission. The excerpts below are complete selected normative statements, with original file and selected-entry hashes.', '']
    for item in pack['handling']:
        if item['disposition'] != 'reuse': continue
        body = bodies[item['concept_id']]
        ref = item['payload']['meaning_ref']
        raw = (package / 'inputs' / ref['input_id']).read_bytes()
        formal = body['voices']['scientific_formal']
        lines += ['### ' + body['term'], '', '- Disposition: reuse',
            '- Exact source: `' + ref['identity'] + '@' + ref['revision'] + '`',
            '- Source path / selector: `' + ref['input_id'] + '` / `""`',
            '- Original-file SHA-256: `' + sha(raw) + '`',
            '- Selected-entry SHA-256: `' + ref['sha256'] + '`',
            '- Owner route: `' + body['semantic_owner_ref'] + '`', '',
            formal['normative_statement'], '', '**Boundary conditions**', '']
        lines += ['- ' + b for b in formal['boundary_conditions']]
        lines += ['', '**Applicability to this Pack:** ' + item['payload']['applicability'], '']
    return '\n'.join(lines).rstrip() + '\n'


def check(write_report=False, render=False):
    p1 = HERE / 'package-0001'
    p2 = HERE / 'package-0002'
    first, second = read(p1 / 'pack.json'), read(p2 / 'pack.json')
    require(first['revision'] == 1 and second['revision'] == 2 and first['pack_id'] == second['pack_id'], 'revision-lineage')
    require(second['lineage']['predecessor_package_binding']['sha256'] == sha((p1 / 'pack.json').read_bytes()), 'predecessor-pin')
    for n in ('0001', '0002'):
        package = HERE / ('package-' + n)
        restored = HERE / ('reconstructed-' + n)
        require(inventory(package) == inventory(restored), 'reconstruction:' + n)
        materialized = HERE / ('materialized-' + n) / 'definitions/000'
        require((materialized / 'definition.json').read_bytes() ==
            (PROPOSAL / 'definition/lab-workspace/definition.json').read_bytes(), 'materialized-body:' + n)
        require((materialized / 'DEFINITION.md').read_bytes() ==
            (PROPOSAL / 'definition/lab-workspace/DEFINITION.md').read_bytes(), 'materialized-projection:' + n)
        require(read(HERE / ('materialized-' + n) / 'report.json')['actual_owner_outcome'] is None, 'owner-outcome-inflation')
    expected = {'reuse': 15, 'propose': 2, 'open': 2}
    require(dict(Counter(h['disposition'] for h in second['handling'])) == expected, 'dispositions')
    require({h['concept_id'] for h in second['handling'] if h['disposition'] == 'open'} ==
        {'formal-symbol-fit', 'semantic-owner-acceptance'}, 'open-question-loss')
    answer = read(HERE / 'input/terminology-answer.json')
    require(answer['answer_state'] == 'answered' and answer['answer'] ==
        'Use “Lab Workspace” for the durable scope and “runtime instance” for execution', 'answer-provenance')
    request = read(p2 / 'request.json')
    for row in request['source_bindings'] + request['evidence_bindings']:
        raw = (ROOT / row['path']).read_bytes()
        require(sha(raw) == row['sha256'] and len(raw) == row['bytes'], 'current-request-source:' + row['path'])
    adapter = read(HERE / 'capture-0002b/adapter-observation.json')
    require(len(adapter['reference_observations']) == 15 and
        all(o['registry_match'] == 'historical-match' for o in adapter['reference_observations']), 'reuse-snapshot-matching')
    observation = read(HERE / 'use-observation-0002/observation.json')
    require(observation['outcome'] == 'blocked' and observation['actual_owner_outcome'] is None and
        observation['operational_authorization'] == 'not-established', 'readiness-overclaim')
    require(second['readiness']['prepare-owner-review']['obligations'] == ['local-snapshot', 'current-authority'], 'review-obligation-loss')
    require(second['authority_effect'] == 'none' and second['assessments'] == [] and second['applications'] == [], 'domain-execution-overclaim')
    command_count = 0
    for file in sorted((HERE / 'commands').glob('*.run.json')):
        run = read(file)
        require(not set(run['argv'][1:]) & {'setup', 'authorize', 'apply', 'renew'}, 'unexpected-native-effect')
        command_count += 1
        if file.name in ('observe-use.run.json', 'r2b-observe-use.run.json'):
            require(run['exit_code'] == 3, 'blocked-use-not-recorded')
        elif file.name == 'r2-prepare.run.json':
            require(run['exit_code'] == 2, 'failed-input-not-preserved')
        else:
            require(run['exit_code'] == 0, 'unexpected-command-failure:' + file.name)
    materialization = read(HERE / 'materialized-0002/report.json')
    leaves = len(read(HERE / 'materialized-0002/definitions/000/field-lineage.json')['fields'])
    summary = {'status': 'prepared-with-gaps', 'authority_effect': 'none', 'scripted_cli_run_verified': True,
        'native_review_ready': False, 'native_review_performed': False, 'actual_owner_outcome': None,
        'current_pack_revision': 2, 'dispositions': expected, 'recorded_cli_commands': command_count,
        'historically_matched_reused_definitions': 15, 'materialized_definitions': materialization['definitions'],
        'materialized_field_lineage_leaves': leaves, 'exact_reconstruction': ['revision-1', 'revision-2'],
        'explicit_user_answer': answer['answer'], 'open_questions': ['formal-symbol-fit', 'semantic-owner-acceptance'],
        'owner_review_obligations': observation['outcome'] + ': local-snapshot; current-authority',
        'original_draft_changed': False, 'independent_semantic_review': 'pending'}
    result = presentation()
    if render:
        (HERE / 'RESULT.md').write_text(result)
    else:
        require((HERE / 'RESULT.md').read_text() == result, 'presentation-drift')
    if write_report:
        (HERE / 'process-check.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    return summary


if __name__ == '__main__':
    print(json.dumps(check(write_report='--write-report' in sys.argv, render='--render' in sys.argv), indent=2))
