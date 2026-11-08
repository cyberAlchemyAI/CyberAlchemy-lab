#!/usr/bin/env python3
"""Prepare concrete human review material after the machine pilot completes."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'workflow/cli'))
import runtime as c
s=c.s


def audit_plan():
    plan=s.read(s.PLAN);rows=[]
    for task in plan['tasks']:
        row={'task':task['id'],'layer':task['layer'],'status':task['status'],
             'criteria':task['acceptance_criteria'],'deliverables':task['outputs'],'dependencies':task['depends_on']}
        if task['status']=='accepted':
            ref=task['validation']['acceptance_ref'];c.v.safe_binding(ref,limit=64*1024*1024)
            receipt=s.read(s.ROOT/ref['path'])
            s.require([x['criterion'] for x in receipt['criteria']]==task['acceptance_criteria'],'criterion drift: '+task['id'])
            s.require(all(x['result']=='pass' and (x.get('finding') or x.get('evidence')) for x in receipt['criteria']),'missing criterion evidence: '+task['id'])
            s.require(set(task['outputs'])<=set(x['name'] for x in receipt['artifacts']),'missing deliverable: '+task['id'])
            for item in receipt['artifacts']+receipt['dependency_bindings']:
                c.v.safe_binding({'path':item['path'],'sha256':item['sha256']},limit=64*1024*1024)
            legacy=[]
            bound={(item['path'],item['sha256']) for item in receipt['artifacts']+receipt['dependency_bindings']}
            for criterion in receipt['criteria']:
                if not criterion.get('finding'):
                    sources=[]
                    for reference in criterion['evidence']:
                        path=(s.BASE/reference).resolve()
                        s.require(path.is_relative_to(s.BASE) and path.is_file(),'missing legacy criterion source: '+reference)
                        binding=s.binding(path)
                        sources.append({'binding':binding,'previously_bound_in_receipt':(binding['path'],binding['sha256']) in bound})
                    legacy.append({'criterion':criterion['criterion'],'kind':'legacy explicit evidence list; no invented finding',
                        'current_reference_snapshot':sources})
            row.update(receipt=ref,artifact_count=len(receipt['artifacts']),dependency_binding_count=len(receipt['dependency_bindings']),
                evidence_findings=receipt['criteria'],legacy_criterion_sources=legacy,
                machine_evidence='current scoped accepted exports',human_review=receipt.get('human_review'))
        else:row.update(machine_evidence='pending final review; not counted complete',human_review=None)
        rows.append(row)
    return {'schema':'relational.pre-final-plan-audit/v1-candidate','requirements':rows,
        'counts':{'tasks':len(rows),'working_units':sum(len(t['working_units']) for t in plan['tasks']),
            'edges':sum(len(t['depends_on']) for t in plan['tasks']),'accepted':sum(t['status']=='accepted' for t in plan['tasks'])},
        'scope':'Current receipt, explicit criterion and artifact audit. Human R06/G4 completion is still pending; a plan or receipt alone is not a new theorem proof.',
        'authority_effect':'none'}


def main():
    report=s.read(HERE/'shadow-pilot-report.json')
    s.require(report['machine_result']=='pass' and report['human_review']=='pending','completed machine pilot or pending review missing')
    c.v.safe_binding(report['validation_script'])
    for row in report['fresh_cases']+report['accepted_predecessor_cases']:
        c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
    matrix={'schema':'relational.supported-use-matrix/v1-candidate','baseline':s.binding(s.BASE/'replay/dependency-manifest.json'),
        'human_use_recommendation':'pending','authority_effect':'none',
        'profiles':[
            {'id':c.F0,'supported':'Three relations, 28 exact ordered pairs; literal version/scope/receipt bindings and independent graph invariant.',
             'meaning_limit':'Accepted assessment and authority-evidence truth are supplied assumptions; no authentic execution or admission.',
             'evidence':'Actual kernel checked input and general checker soundness; R04 positive and negative command cases.'},
            {'id':c.STRUCTURE,'supported':'All 41 captured relation kinds, 550 ordered pairs and 109 node kinds as a structural profile.',
             'meaning_limit':'263 inherited source-semantic obligations remain unsupported; structure cannot establish those meanings.',
             'evidence':'R04 full-registry positive and negative fresh kernel checks.'},
            {'id':'unchanged / instance-only','supported':'Complete 9-obligation replay under the fixed captured registry and selected F0 semantics.',
             'meaning_limit':'Selected-data compatibility, general invariant preservation and model conservativity remain separate.',
             'evidence':'R03/R04 complete positive and actual semantic negative; R05 added assertion and fresh application replay.'},
            {'id':'fresh-kind-extension','supported':'Append-only fresh identifiers with the declared pure annotation interpretation, exact signatures and closed string qualifiers.',
             'meaning_limit':'An empty ordered-pair declaration has no instances; its valid carrier rejects every new-kind instance. No inference or external evidence meaning is added.',
             'evidence':'R03 nonempty/empty pair carriers and complete 9-obligation cases; R04 actual public fresh-kind replay.'},
            {'id':'rule-only-extension','supported':'Captured empty old-rule baseline; unchanged graph and registry; fresh ordinary unary ReviewSignal heads and old-predicate positive bodies.',
             'meaning_limit':'Conforms(subject) is an existential projection of validated F0 edges. Candidate epoch is frozen at 0; other contexts/targets and real authority are not inferred.',
             'evidence':'R06 fresh 15-obligation replay with actual submitted proof and exact checked countermodel; generic derivation, closure, lineage and rule-model conservativity guarantees.'},
            {'id':'check-proof','supported':'R02 independently selected exact required statement/definition and pure transitive proof closure under pinned Lean 4.33.1.',
             'meaning_limit':'Same pinned kernel through an independent replay path, not a second kernel implementation. Proof rejection is invalid evidence, not theorem refutation.',
             'evidence':'R02 30 controls, R04 actual exact/weak/stale proof commands and R06 submitted-proof replay.'},
            {'id':'bounded-search','supported':'Provider result transport with unknown verdict until an exact witness is independently checked.',
             'meaning_limit':'Completion, found flags or exhaustion do not establish theorem evidence, absence or review readiness.',
             'evidence':'R03 actual method control and R06 complete public workflow ending unresolved/code 4.'}],
        'unsupported':['Existing endpoint-pair widening or qualifier/meaning changes without a new preservation profile.',
            'Old-predicate heads, fresh recursive bodies, mixed graph/rule changes or a nonempty prior rule baseline in the captured integration adapter.',
            'Full semantics of the inherited registry outside selected profiles, authentic issuer/receipt validation, live authority transactions, deployment and autonomous theorem generation.'],
        'retained_trust':['Source meaning and unary abstraction','JSON projection, hashing, host runtime and OS',
            'Pinned Lean kernel/toolchain and verifier implementation','Supplied independent assessment/root truth',
            'Ordinary local filesystem ownership and cooperative application lock']}
    s.write(HERE/'supported-use-matrix.json',matrix)
    s.write(HERE/'pre-final-plan-audit.json',audit_plan())
    feedback=HERE/'reviewer-feedback.md'
    if not feedback.exists():
        feedback.write_text('# Reviewer feedback\n\nHuman semantic assessment: **pending**.\n\nHuman diagnostic-usefulness assessment: **pending**.\n\nHuman bounded-use recommendation: **pending**.\n\nNo human approval or disagreement has been recorded. Machine proof validity and candidate author self-review are separate evidence.\n')
    rule_positive=next(x for x in report['fresh_cases'] if x['name']=='complete-rule-change')
    search_negative=next(x for x in report['fresh_cases'] if x['name']=='search-without-checked-witness')
    diag=s.read(s.BASE/'workflow/cli/cases/extension-semantic-failure-outcome.json')
    sample=next(x for x in diag['diagnostics'] if x['code']=='wrong-target-version')
    # Keep explanatory prose in a readable template and bind observations to
    # the current machine report. Regeneration preserves human feedback.
    results=['| Fresh pilot case | Exit | Readiness | What it demonstrates |',
             '|---|---|---|---|']
    interpretations={
        'endpoint-extension-unsupported':'Existing endpoint widening is outside the supported profile.',
        'complete-rule-change':'All 15 required obligations were satisfied for the captured fresh-head rule.',
        'protected-head-unsupported':'The captured extension profile rejects a new old/protected predicate head.',
        'search-without-checked-witness':'Search without the required checked witness remains unresolved.'}
    for row in report['fresh_cases']:
        results.append('| '+row['name']+' | '+str(row['exit_code'])+' | '+row['readiness']+' | '+interpretations[row['name']]+' |')
    costs=['| Fresh replay | Elapsed time | Peak process RSS |', '|---|---|---|']
    for row in [rule_positive,search_negative]:
        metrics=row['process_measurements']
        seconds=metrics['elapsed_seconds'];rss=metrics['peak_rss_kib']
        costs.append(f"| {row['name']} | {seconds:,.2f} seconds (about {seconds/60:.1f} minutes) | {rss:,.0f} KiB (about {rss/1048576:.2f} GiB) |")
    substitutions={
        'BASE':str(s.BASE),'PLAN':str(s.PLAN),'PILOT':str(HERE),
        'DIAGNOSTIC_MESSAGE':sample['message'],'DIAGNOSTIC_LOCATION':sample['location'],
        'DIAGNOSTIC_OBLIGATION':sample['obligation_id'],'DIAGNOSTIC_ACTION':sample['next_action'],
        'PILOT_RESULTS':'\n'.join(results),'PILOT_COSTS':'\n'.join(costs),
        'PREDECESSOR_COUNT':str(len(report['accepted_predecessor_cases']))}
    text=(HERE/'review-explanation.md.in').read_text(encoding='utf-8')
    for key,value in substitutions.items():text=text.replace('{{'+key+'}}',value)
    s.require('{{' not in text,'unresolved explanatory template field')
    (HERE/'review-packet.md').write_text(text,encoding='utf-8')
    print('R06 review packet prepared; human semantics, diagnostic usefulness and use recommendation remain pending')


if __name__=='__main__':main()
