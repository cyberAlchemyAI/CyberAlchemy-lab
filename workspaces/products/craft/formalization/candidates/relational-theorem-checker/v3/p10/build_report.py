"""Workload-scoped measurements with explicit reuse and no unsupported speedup."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from v3.p10.timing import validate_tree
from v3.p07.runs import inspect_record
from jsonschema import Draft202012Validator

benchmark=C.decode((HERE/'benchmark-results.json').read_bytes());timing=C.decode((HERE/'timing-controls.json').read_bytes())
require(benchmark['result']==timing['result']=='pass','incomplete measured controls')
controls=benchmark['controls']+timing['controls'];samples=benchmark['samples'];rows=[]
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'})
def union(intervals):
    total=0.;cursor=0.
    for a,b in sorted(intervals):total+=max(0.,b-max(a,cursor));cursor=max(cursor,b)
    return total
for sample in samples:
    request=C.decode(check(sample['input']).read_bytes());public=C.decode(check(sample['output']).read_bytes());owned=public['qualification']
    test(sample['name']+'-exact-source-policy',request['resource_policy']==sample['resource_policy'] and C.identity(request['resource_policy'])==owned['policy_identity'])
    validate_tree(sample['stage_tree'])
    test(sample['name']+'-all-recorded-intervals-complete',all(r['end_seconds'] is not None and r['outcome']!='unfinished' for r in sample['stage_tree']))
    if owned.get('owned_run'):test(sample['name']+'-owned-record-current',inspect_record(owned['owned_run'])['status']=='recorded-current')
    test(sample['name']+'-cleanup-complete',not (owned.get('supervised_run') or {}).get('cleanup',{}).get('remaining_pids',[]))
    if sample['actual_kernel_completion']:
        test(sample['name']+'-no-catalog-shrink',sample['required_ids']==[o['id'] for o in C.required_inventory('rule-only')])
        payload=C.decode(check(owned['qualified_result']['payload']).read_bytes())
        test(sample['name']+'-fresh-same-kernel-audit',payload['evidence']['general']['audit']['fresh_kernel_replay'] and payload['evidence']['general']['audit']['accepted'])
    test(sample['name']+'-advisory-is-not-hard-cap',sample['memory']['backend']!='advisory' or sample['memory']['hard_aggregate_cap'] is False)
    stages=sample['stage_tree'];root=next((r for r in stages if r['name']=='worker:qualification'),None)
    category={}
    for label,predicate in [
        ('compile_tools',lambda r:r['name'].startswith('tool:compile:')),
        ('general_replay',lambda r:r['name']=='tool:fresh-general-replay'),
        ('source_cache_guards',lambda r:r['name']=='context:source-and-cache-current'),
        ('source_projection',lambda r:r['name']=='tool:source-projection'),
        ('reference_evaluator_process',lambda r:r['name']=='tool:reference-evaluator'),
        ('saved_inspection_process',lambda r:r['name']=='tool:exact-evidence-inspection')]:
        intervals=[(r['start_seconds'],r['end_seconds']) for r in stages if predicate(r)]
        category[label]=union(intervals)
    selected=[(r['start_seconds'],r['end_seconds']) for r in stages if r['name'].startswith('tool:compile:') or r['name'] in ['tool:fresh-general-replay','context:source-and-cache-current','tool:source-projection','tool:reference-evaluator','tool:exact-evidence-inspection']]
    category['other_worker_time']=max(0.,root['inclusive_seconds']-union(selected)) if root else None
    leaf_eval=None
    if sample['actual_kernel_completion']:leaf_eval=payload['counters']['seconds']
    rows.append({'name':sample['name'],'status':sample['status'],'client_seconds':sample['client_seconds'],
                 'worker_seconds':root['inclusive_seconds'] if root else None,'category_seconds':category,'finite_evaluator_seconds':leaf_eval,
                 'peak_rss_observed':sample['memory']['peak_aggregate_rss_observed'],'scope':'Categories use interval union. Compiler/version time inside source guards is not independently added. Parent/supervisor durations are enclosing measurements.'})

# Aggregate application/registration timings were actually executed in P09.
# They remain recorded evidence for its representative workload, not new
# instrumented runs or rich-workload estimates.
layout=C.decode((BASE/'p09/layout-suite.json').read_bytes());retained=[]
for case in layout['cases']:
    for application in case['applications']:
        proposal=check(application['transaction']['proposal_qualification']).parent
        reg=C.decode(check(application['after']['registration']).read_bytes())
        proposal_record=C.decode((proposal/'owned-run-record.json').read_bytes());reg_record=C.decode(check(reg['owned_run']).read_bytes())
        p=proposal_record['timings']['supervised_seconds'];r=reg_record['timings']['supervised_seconds'];total=application['seconds']
        test(case['layout']+'-g'+str(application['after']['generation'])+'-nested-application-time-not-summed',total>=p+r)
        retained.append({'layout':case['layout'],'generation':application['after']['generation'],'application_seconds_inclusive':total,
            'proposal_supervised_seconds':p,'successor_registration_supervised_seconds':r,
            'application_source':binding(BASE/'p09/layout-suite.json'),'proposal_record':binding(proposal/'owned-run-record.json'),
            'registration_record':reg['owned_run'],'scope':'Recorded P09 representative workload; child run times are enclosed by application wall time, not added to it. No isolated commit-only timer was recorded.'})

limits=[
    str(len(samples))+' current instrumented workload samples; successful qualification and refusal are reported separately. No general throughput or latency guarantee.',
    'Cold means local dependencies are freshly recompiled; warm means their independently anchored bytes are copied/verified. OS page-cache state and other host load were not controlled.',
    'Monotonic host clock and source-bound instrumentation remain assumptions. Group exclusive time includes Python/checking/IO overhead; it is not CPU-only time.',
    'Advisory aggregate RSS observation is not a hard memory cap. No per-stage peak RSS attribution is available.',
    'Parent/supervisor/client durations are inclusive. Unknown overhead is not reassigned to replay. No isolated commit-only duration was measured in the reused P09 records.',
    'The variable-count stress case includes the body occurrences needed to bind its extra variables. Other primary dimensions are fixed; semantic agreement is required for cold/warm, not between different rule meanings.',
    'Fresh proof replay remains through the same pinned Lean kernel. No evaluator optimization or independent-kernel assurance is selected.'
]
limits.append('A zero category means that stage was not reached/executed in that sample; it does not describe the cost of completing an omitted stage.')
report={'schema':'relational.performance-report/v3','samples':samples,'retained_measurements':[binding(BASE/'p09/layout-suite.json'),binding(BASE/'p09/rich-layout-observation.json')],
    'timing_policy':'Monotonic intervals; exclusive time subtracts the union of direct child intervals; inclusive nesting is not independently summed.',
    'selection':'no-optimization','limits':limits,'authority_effect':'none'}
Draft202012Validator(C.decode((HERE/'performance-report.schema.json').read_bytes())).validate(report)
(HERE/'stage-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
summary={'result':'pass','rows':rows,'read_timings':benchmark['read_timings'],'recorded_shadow_timings':retained,'controls':controls,'report':binding(HERE/'stage-measurements.json'),'authority_effect':'none'}
Draft202012Validator(C.decode((HERE/'performance-controls.schema.json').read_bytes())).validate(summary)
(HERE/'performance-controls.json').write_text(json.dumps(summary,indent=2)+'\n')
profile={'schema':'relational.benchmark-profile/v3','source':benchmark['source'],'samples':[{'name':s['name'],'input':s['input'],'workload':s['workload'],'build_mode':s['build_mode'],'layout':s['layout']} for s in samples],
    'resource_policy':samples[0]['resource_policy'],'profile':'rich-positive-recursive-v2','fixed_required_ids':[o['id'] for o in C.required_inventory('rule-only')],
    'primary_stress_dimension':'one to three reference variables in the fresh exact-contract/scope rule, with necessary positive Conforms body binders',
    'runtime_roots':benchmark['runtime_roots'],'uncontrolled':['OS page-cache state','other host load'],'authority_effect':'none'}
Draft202012Validator(C.decode((HERE/'benchmark-profile.schema.json').read_bytes())).validate(profile)
(HERE/'benchmark-profile.json').write_text(json.dumps(profile,indent=2)+'\n')
lines=['# Measured performance and selection','',
    'Keep the accepted evaluator and fresh proof recipe. The measured report distinguishes actual complete qualification from explicit resource refusal; no speedup or wider-profile guarantee is selected.','',
    '| Sample | Actual outcome | Client seconds | Compile tools | General replay | Source/cache guards | Evaluator process | Peak observed RSS MiB |',
    '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for row in rows:
    c=row['category_seconds'];rss=row['peak_rss_observed'];lines.append(f"| {row['name']} | {row['status']} | {row['client_seconds']:.3f} | {c['compile_tools']:.3f} | {c['general_replay']:.3f} | {c['source_cache_guards']:.3f} | {c['reference_evaluator_process']:.3f} | {rss/1048576:.1f} |" if rss is not None else f"| {row['name']} | {row['status']} | {row['client_seconds']:.3f} | unknown | unknown | unknown | unknown | unknown |")
lines += ['', 'Compilation includes the projection, concrete witness, general submission and any cold local dependencies. General replay and guarded source/import currentness are retained checks. Finite evaluator-only time is separately recorded where a full payload exists; the process interval includes launch and transport. These measurements do not justify changing the evaluator or removing currentness/replay checks.','',
    'The primary workload is the richer target/scope cyclic source with sixteen domain values. Cold and warm runs use the same graph, rules and twenty-obligation catalog. The stress proposal adds two reference-variable binders to one fresh rule, producing 4,144 candidate substitutions overall without changing the graph, domain, predicate declarations, rule count or operator policy. It is a different rule meaning; a completed preflight is not a promise that its proof fits the time budget.','',
    'Recorded P09 applications took an enclosing wall interval and performed a separate proposal check and successor registration. The report retains those actual timings for their fifteen-value representative workload. Their child times are not summed again with the application total. Saved inspection/explanation timings are new read-only operations and do not create new qualification events.','',
    'The selected optimization is **none**. If a later optimization is proposed, it must target a measured cost and preserve independent equivalence targets, full closure/support checks and fresh replay. Raising deadlines or shrinking the catalog would change the operational or proof claim; neither is done here.','',
    'Limits: '+ ' '.join(limits),'']
(HERE/'performance-decision.md').write_text('\n'.join(lines));print('Performance reports closed:',len(samples),'samples;',len(controls),'controls')
