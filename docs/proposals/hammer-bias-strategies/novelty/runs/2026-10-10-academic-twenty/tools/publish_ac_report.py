#!/usr/bin/env python3
"""Publish actual closed evidence only; no native calls or semantic regrading.

Requires both independent completion auditors to pass, their actual root FINAL
witnesses, all admitted role closures, source integrity and a real goal-tool
bookkeeping snapshot. Earlier reports and first assessments are retained.
"""
import json
from ac_runtime import ROOT, read, save, sha, require, now, words
from ac_coverage_runtime_v7 import CoverageRuntime
from build_ac_report import link, table


def main():
    r = CoverageRuntime()
    admission = r.p('coverage/grammar/ADMISSION.v9.json')
    if admission.exists() and read(admission)['admit'] is True:
        from ac_grammar_runtime_v9 import GrammarRuntime
        r = GrammarRuntime()
    require(all(r.state(j['job_id'])['terminal'] for j in r.plan()),
            'An admitted role remains open')
    audits = {}
    for key in ['A', 'B']:
        audit_path = r.p('reports/COMPLETION-AUDIT-' + key + '.v3.json')
        audit = read(audit_path)
        require(words(audit) <= 6000, 'Auditor exceeds assigned word bound: ' + key)
        witness = read(r.p('receipts/completion-audit-' + key.lower() + '.final.json'))
        require(witness['observation'] == 'actual_FINAL', 'Actual auditor FINAL absent')
        require(witness['audit_path'] == str(audit_path) and
                witness['audit_sha256'] == sha(audit_path),
                'Auditor first observed output changed: ' + key)
        require(any(v['purpose'] == 'completion_audit' and
                    v['outcome'] == 'actual_spawn_observed' and
                    v['handle'] == witness['agent'] for v in r.invocations()),
                'Auditor FINAL has no matching actual spawn observation: ' + key)
        require(audit['audit_id'] == 'AC-COMPLETE-' + key and audit['status'] == 'pass',
                'Independent completion audit does not pass: ' + key)
        expected = {f'AC{i:02d}' for i in range(1, 21)}
        checks = audit['strategy_checks']
        require(len(checks) == 20 and {c['strategy_id'] for c in checks} == expected,
                'Audit does not cover every card exactly once')
        require(all(c['essential_agent_execution_satisfied'] is True and
                    c['comparisons_satisfied'] is True for c in checks),
                'Essential execution/comparison remains unfulfilled: ' + key)
        require(not any(i['blocking'] for i in audit['issues']), 'Blocking audit issue remains')
        require(all(audit[field]['pass'] is True for field in
                    ['ledger_check', 'source_and_first_save_check', 'report_claim_check']),
                'Independent ledger/source/report check does not pass: ' + key)
        audits[key] = audit
    verification = r.verify()
    require(verification['status'] == 'pass', 'Final integrity failed')
    external_sources = read(r.p('preparation/SKILL-SOURCES.v1.json'))['sources']
    require(all(sha(path) == digest for path, digest in external_sources.items()),
            'Instruction or dispatch provenance source changed since admission')
    calls = len(r.invocations())
    require(calls <= 260 and r.budget()['remaining_scheduled_calls'] == 0,
            'Native ledger does not close within ceiling')
    bookkeeping = read(r.p('receipts/GOAL-BOOKKEEPING-SNAPSHOT.v1.json'))
    require(bookkeeping['observation'] == 'actual_get_goal_tool_result',
            'Aggregate goal usage must come from the actual tool')
    results = read(r.p('reports/RESULTS.v2.json'))
    final = {
        'schema_version': 'academic-twenty.final-closeout.v3', 'utc': now(),
        'preaudit_results_path': 'reports/RESULTS.v2.json',
        'preaudit_results_sha256': sha(r.p('reports/RESULTS.v2.json')),
        'actual_native_invocations': r.invocations(), 'actual_native_calls': calls,
        'admitted_scheduled_dispositions': len(r.plan()),
        'all_admitted_dispositions_terminal': True,
        'completion_audits': audits, 'final_integrity': verification,
        'external_instruction_and_dispatch_sources_match_admission': True,
        'goal_bookkeeping_snapshot': bookkeeping,
        'per_role_model_tokens_and_hardware_cost': 'unavailable',
        'original_and_later_scopes_preserved': True,
        'ceiling': 260,
        'limits': ['Synthetic agent procedures and stipulated replay only',
                   'No human retention/incubation or model-weight learning',
                   'No independent platform/access/hidden-compute attestation',
                   'No statistical population effect, global originality or measured beneficiary benefit']}
    audit_rows = []
    for i in range(1, 21):
        ac = f'AC{i:02d}'
        audit_rows.append([ac] + [next(c for c in audits[k]['strategy_checks']
                                      if c['strategy_id'] == ac)['application_disposition']
                                  for k in ['A', 'B']])
    closure = (
        '\n## Final independent completion and accounting\n\n'
        f'The final shared ledger contains **{calls} actual native spawn/followup '
        'attempts**, including preparation, coordination, invalid first outputs '
        'and both completion auditors. The first report above is a pre-audit '
        'snapshot; its raw assessments and count are preserved. All admitted '
        'dispositions are terminal. Both fresh completion auditors pass their '
        'essential agent execution and comparison checks for all 20 cards. '
        'This is a completion assessment, not a universal efficacy finding.\n\n' +
        table(['Card', 'Completion auditor A', 'Completion auditor B'], audit_rows) +
        '\nThe original and later independent disagreements remain in the '
        'pre-audit results and source reviews. A later grammar case, fresh '
        'control or clarified input-evidence packet never regrades the '
        'original failed or unknown observation.\n\n'
        'Aggregate goal token/time bookkeeping is recorded from an actual '
        'tool snapshot at publication preparation. It includes root planning '
        'and continuation and cannot allocate compute to individual methods. '
        'Per-role model tokens, GPU time and hardware cost remain unavailable.\n\n' +
        ', '.join(link(label, r.p(path)) for label, path in [
            ('Final machine closeout', 'reports/RESULTS.v3.json'),
            ('Completion audit A', 'reports/COMPLETION-AUDIT-A.v3.json'),
            ('Completion audit B', 'reports/COMPLETION-AUDIT-B.v3.json'),
            ('Goal bookkeeping', 'receipts/GOAL-BOOKKEEPING-SNAPSHOT.v1.json')]) + '.\n')
    full = r.p('reports/EXECUTION-RESULTS.v1.md').read_text() + closure
    main_path = ROOT.parent.parent.parent / 'RESEARCH-REPORT.md'
    require(main_path.exists(), 'Main research report missing')
    before = main_path.read_text()
    require('## 18. Academic twenty: execution and comparison' not in before,
            'Final main report was already published')
    top_old = '**Academic extension:** 26 academic references and 20 additional strategy cards, prepared on 10 October 2026; a separate native execution pilot is now in progress.'
    top_new = '**Academic extension:** 26 academic references and 20 strategy cards, followed by a closed native agent study with separately declared control coverage and two independent completion audits.'
    require(before.count(top_old) == 1, 'Unexpected main report status text')
    after = before.replace(top_old, top_new)
    abstract_old = 'A separate bounded native follow-up is now in progress; its final results require closure and independent completion audits.'
    abstract_new = f'A separate native follow-up has now closed with {calls} actual delegated calls, preserved first failures, later control coverage and two fresh completion audits; section 18 reports its evidence and limits.'
    require(after.count(abstract_old) == 1, 'Unexpected main abstract text')
    after = after.replace(abstract_old, abstract_new)
    toc = '17. [Academic extension: creativity, emergence and learning](#17-academic-extension-creativity-emergence-and-learning)'
    require(after.count(toc) == 1, 'Unexpected main table of contents')
    after = after.replace(toc, toc + '\n18. [Academic twenty: execution and comparison](#18-academic-twenty-execution-and-comparison)')
    start = after.index('The linked academic documents are immutable preparation snapshots:')
    end = after.index('The earlier completed studies and their original findings remain unchanged.', start)
    end += len('The earlier completed studies and their original findings remain unchanged.')
    after = after[:start] + (
        'The linked academic documents remain preparation snapshots: no scored '
        'experiment was performed during their preparation. The subsequent '
        'AC01–AC20 study and separately declared coverage have closed under '
        'the independent completion checks summarized in section 18. Their '
        'original failures, unknowns, two packet-clarity phases and later '
        'comparison scopes remain explicit. Human learning, agent weight '
        'updates, canonical skill installation and default workflow changes '
        'remain unmeasured or unperformed. The earlier completed studies '
        'and their original findings remain unchanged.') + after[end:]
    matrix = []
    comparison_rows = []
    for row in results['strategy_reviews_and_endpoints']:
        scopes = []
        for key in ['first_independent_reviews', 'later_control_coverage_reviews',
                    'grammar_application_coverage_reviews']:
            scopes.append(', '.join(v['assessment']['application'] for v in row[key]) or 'Unrun')
        matrix.append([row['strategy_id'], row['title']] + scopes)
        for scope, key in [('Later controls', 'later_control_coverage_reviews'),
                           ('Separate grammar', 'grammar_application_coverage_reviews')]:
            for review in row[key]:
                for contrast in review['assessment']['comparisons']:
                    comparison_rows.append([
                        row['strategy_id'], scope + ' ' + review['review_job'],
                        ' versus '.join(contrast['arm_pair']), contrast['available'],
                        contrast['result']])
    section = (
        '\n\n## 18. Academic twenty: execution and comparison\n\n'
        'The academically motivated strategies were executed as bounded native '
        'agent procedures, with fresh criticism, selected Distill summaries '
        'and reconstruction where specified. Earlier-method instructions '
        'were rerun on the current synthetic cases. The full '
        + link('execution report', r.p('reports/EXECUTION-RESULTS.v2.md')) +
        ' preserves each final operation, modeled replay, available contrast, '
        'upstream novelty assessment, resource limit and raw reviewer disagreement. '
        'The following matrix keeps original assessments separate from later '
        'control review and the changed explicit-grammar case.\n\n' +
        table(['Card', 'Operation', 'First reviewers', 'Later control reviewers',
               'Separate grammar reviewers'], matrix) +
        '\nThe comparison findings below are the independent reviewers\' '
        'saved judgments, kept separately rather than averaged. An unavailable '
        'contrast remains unknown. The linked execution report adds full '
        'upstream, usefulness and burden evidence for every row.\n\n' +
        table(['Card', 'Review scope', 'Comparison', 'Available', 'Saved finding'],
              comparison_rows) +
        '\n### 18.1 What the cases can establish\n\n'
        'These experiments distinguish application from contribution: a '
        'procedure can be exercised, reconstruct a feasible option and tie '
        'ordinary analysis. A final choice can differ while its mechanism '
        'already exists in a proposal or criticism. Fixed-pool selection '
        'does not establish generation. The closed cases disclose supported '
        'affordances and permit strong ordinary controls to attain modeled '
        'workload floors; a local tie cannot establish that creativity has '
        'no value in less explicit settings. Per-card findings and their '
        'available comparison evidence are retained in the linked report.\n\n'
        'The first missing-output ordinary calls and invalid cap-bound '
        'builders remain failed observations, with their gates and '
        'unavailable contrasts. Fresh controls supply later evidence. '
        'The original example-free builder saved no JSON after using an '
        'unavailable interpreter command; its later endpoint uses the '
        'unchanged valid original critique and preserves that first failure. '
        'After 61 original roles had finished, 132 still-unadmitted packets '
        'received an explicit one-candidate builder/transfer field matching '
        'the existing validator; compliance across these two phases is '
        'not a creativity or learning effect. Later reviewers also received '
        'actual assigned input envelopes and literal case/method packs.\n\n'
        '### 18.2 Learning and emergence\n\n'
        'The academic evidence supports conditional improvements in creative '
        'performance through training. This agent study instead investigates '
        'mechanisms and external procedures. Context availability is not '
        'human incubation; retrieved cards are not unassisted retention; '
        'one-field external revision is not weight training. Actual '
        'beneficiary preferences support a usefulness question, while '
        'synthetic action counts do not measure beneficiary relief. '
        'Different routed source packs establish an information intervention, '
        'not independent empirical discoveries.\n\n'
        'No universal necessary-and-sufficient recipe emerges. For this '
        'research process, useful novelty requires usable knowledge, an '
        'admissible variable, actual construction, comparison with existing '
        'work and purpose-relevant evaluation. Retention and unfamiliar-case '
        'transfer require further evidence when learning is claimed. '
        'The eight ' + link('next experiment proposals', r.p('reports/INTERPRETATION-NOTES.v1.md')) +
        ' investigate discovery costs, explicit grammar, matched ordering, '
        'state-bearing learning, transferable feedback, constructive attack, '
        'beneficiary outcomes and equal-information source diversity. '
        'They remain proposals.\n\n'
        '### 18.3 Closeout and persistence\n\n'
        f'The final study used **{calls} actual delegated native calls** '
        'within its 260-call ceiling. All admitted dispositions are terminal '
        'and both fresh completion auditors pass essential agent execution '
        'and comparison coverage. Historical raw evidence and all first '
        'assessments remain intact. The catalog, source register, external '
        'procedure artifacts and execution evidence persist in the project; '
        'they have not been installed as global skills or changed defaults.\n\n' +
        link('Final accounting and audit evidence', r.p('reports/RESULTS.v3.json')) +
        ' records actual invocation and source checks. Aggregate goal '
        'token/time usage is a timestamped bookkeeping snapshot; per-role '
        'tokens, hidden compute and hardware costs are unavailable. Native '
        'terminal events are root/coordinator observations, without '
        'independent platform authentication.\n')
    outputs = ['reports/RESULTS.v3.json', 'reports/EXECUTION-RESULTS.v2.md',
               'preparation/RESEARCH-REPORT.pre-final-publication.md',
               'receipts/MAIN-REPORT-FINAL-PUBLICATION.v1.json']
    require(not any(r.p(path).exists() for path in outputs),
            'A first publication output already exists; preserve it and use a separately declared repair')
    # Every audit, source, ledger and report text guard has passed before the
    # first derived publication output is created.
    save(r.p('reports/RESULTS.v3.json'), final)
    save(r.p('reports/EXECUTION-RESULTS.v2.md'), full.encode())
    save(r.p('preparation/RESEARCH-REPORT.pre-final-publication.md'), before.encode())
    main_path.write_text(after + section)
    save(r.p('receipts/MAIN-REPORT-FINAL-PUBLICATION.v1.json'), {
        'utc': now(), 'main_path': str(main_path), 'before_sha256': sha(r.p('preparation/RESEARCH-REPORT.pre-final-publication.md')),
        'published_sha256': sha(main_path), 'final_results_sha256': sha(r.p('reports/RESULTS.v3.json')),
        'actual_native_calls': calls, 'both_completion_audits': 'pass',
        'publication_exception_only': True})
    print(json.dumps({'published': str(main_path), 'actual_calls': calls}))


if __name__ == '__main__':
    main()
