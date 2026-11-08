"""Review current final-source controls and accept the separate E00 profile."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;sys.path.insert(0,str(BASE.parent))
from v3.execution import support as s

report=s.read(HERE/'controls.json')
s.require(report['result']=='pass' and report['new_complete_expression_witnesses']==6,'final expression controls incomplete')
roots=[];fresh=[]
for case in report['cases']:
    s.check(case['input']);answer=s.read(s.check(case['answer']))
    if answer.get('supervised_run',{}).get('job'):roots.append(Path(answer['supervised_run']['job']))
    if answer['status']=='fresh-extension-candidate':
        value=answer['value'];s.check(answer['completion'])
        for ref in value['imports']+value['worker_sources']:s.check(ref)
        for module in value['kernel']:s.check(module['source']);s.check(module['olean'])
        s.require(all('sorryAx' not in m['output'] for m in value['kernel']),'admitted expression proof')
        fresh.append(value)
s.require(len(fresh)==6,'six final full witnesses required')
text='''# E00 implementation review

The separately versioned condition-expression profile implements atomic leaves, binary conjunction/disjunction and bounded negation with reviewed Strong Kleene semantics. The universal Lean evaluator/independent-evidence-rail equality and exact activation theorem compiled before runtime. Every truth-table row is checked against an explicit independent table; missing leaves stay unknown.

All leaf evaluations are validated before evaluating any branch. Duplicate or contradictory evidence, wrong leaf revision, profile, context, subject, target, scope or epoch is invalid. Unknown operators are explicitly unsupported. Node/depth/leaf cutoffs are resource refusals. Epochs in this new canonical transport must decode as integers; Boolean epochs are invalid. The unchanged legacy APIs retain their own normalization rules.

The public entry point is `execution.extension_runtime.Client('E00', policy).qualify(raw_bytes)`. Raw decode, schema/work validation, normalization, mapped source inspection, fresh universal/concrete compilation and same-kernel replay occur in the retained owned supervisor. Required memory control is conditional on actual host capability; default memory observation remains advisory. Cleanup precedes process-local event issuance. Saved, altered or new-client results cannot rehydrate that event.

Six actual final-source full witnesses cover positive, negative and unknown expressions, mapped activation, unknown inactivity and opposing origin-bearing norms. Mapped potentials come from an exact inspected original source/typed/kernel witness; their frame and root condition revision are checked again in the new concrete witness. These mapped proofs are recorded-current inspection, not fresh mapped events. Expression meaning has a separate versioned profile and content identity; no declaration silently replaces the atomic core meaning. Every active origin is retained, including require/forbid opposition. This profile supplies neither fulfillment nor admission and does not authorize core publication.

The first mapped run exposed elaboration recursion in numeric encoding of long origin strings. The encoder now uses escaped Lean string literals for ordinary strings and numeric scalar construction for control characters; invalid Unicode scalars are refused. The failed attempt and earlier development smoke evidence are retained as historical attempts, not counted as final-source qualifications. Operator/resource policies were not raised to make the example pass.

Limitations: supplied leaf truth and profile-local expression declaration truth remain assumptions. The JSON-to-Lean bridge is tested, not universally verified; E05 addresses its reduction. Same pinned Lean kernel with inspected foundational axioms is not an independent checker. A completed expression witness does not supply a real-world action, a human assessment or a live publication capability. The separate original atomic profile remains selectable through the unchanged mapped API.

All three E00 criteria are satisfied by author table review before runtime, the universal and actual full expression/activation witnesses with adversarial controls, and explicit unsupported operator behavior. All other selected extensions remain outstanding.
'''
(HERE/'expression-review.md').write_text(text)
s.write(HERE/'early-attempts-status.json',{'result':'retained-historical-not-final-source-qualification',
    'early_smoke':s.binding(HERE/'first-smoke-result.json'),'failed_log':s.binding(HERE/'validation-attempt-1.log'),
    'reason':'Early smoke preceded root-condition contract; first mapped attempt failed elaboration and issued no extension event. Final controls use the corrected complete source inventory.',
    'authority_effect':'none'})
extra=[p for p in HERE.glob('*') if p.is_file() and p.name not in ['task-acceptance.json','control-progress.json']]
extra += [p for p in (HERE/'formal-build').rglob('*') if p.is_file()]
extra += [p for p in (HERE/'evidence'/report['run_id']).rglob('*') if p.is_file()]
for root in roots:extra += [p for p in root.rglob('*') if p.is_file()]
extra += [BASE/'execution/extension_runtime.py',BASE/'execution/extension_worker.py',BASE/'execution/E00-implementation-plan.md']
extra=list({str(p.resolve()):p for p in extra}.values())
s.accept('E00',[
    'Independent Strong Kleene tables and evidence-rail denotation were author reviewed before the evaluator; evaluation_denotes and exact keyed activation compiled universally first. The proposed separate profile includes bounded negation and preserves unknown.',
    'Six actual final-source full supervised expression witnesses precede any reported norm activation. Exact original mapped source/proof inspection and new frame/root-condition/activation equations retain all origins; every runtime result is source-bound and no saved evidence creates fresh mapped or publication authority.',
    'Unknown operators refuse explicitly; all supplied evidence is checked before evaluation so nonessential branches cannot hide contradictions or key drift. Resource cutoffs/cancellation/backend refusal and saved-event challenges pass. Legacy atomic profile is unchanged and separately selectable.'
],report['controls'],extra=extra)
print('E00 accepted:',len(report['controls']),'controls; six full final-source witnesses.',flush=True)
