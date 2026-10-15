#!/usr/bin/env python3
"""Render observed native results, preserving original and later review scopes.

No model calls or automatic semantic grades. Call only after both plans close.
The first execution report precedes the independent completion audits.
"""
import collections, json, re
from ac_runtime import ROOT, Runtime, read, save, sha, require, now, words
from ac_complete_keys_runtime_v15 import CoverageRuntime
from summarize_ac import derive, family

def link(label,path):return '['+label+']('+str(path)+')'
def cell(v):
    if v is None:v='Unknown'
    elif type(v) is bool:v='Yes' if v else 'No'
    return str(v).replace('|',' / ').replace('\n',' ')
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(c) for c in row)+' |' for row in rows])+'\n'
def addition_display(c):
    if c['available'] is not True:
        return 'Unavailable / unknown; raw assessment '+cell(c['qualified_addition'])
    return c['qualified_addition']
def reviews(r,ac,scope):
    out=[]
    prefix={'original':'REVIEW-','ordinary':'COV-REVIEW-','grammar':'G-COV-REVIEW-'}[scope]
    for j in r.plan():
        if j['role']!='review' or not j['job_id'].startswith(prefix):continue
        p=r.p('raw/'+j['job_id']+'.json')
        if not p.exists():continue
        v=read(p)
        if not isinstance(v,dict):continue
        out += [{'review_job':j['job_id'],'valid':r.state(j['job_id'])['valid'],'assessment':a} for a in v.get('strategy_reviews',[]) if isinstance(a,dict) and a.get('strategy_id')==ac]
    return out
def endpoint(r,j):
    s=r.state(j['job_id']);p=r.p('raw/'+j['job_id']+'.json')
    if not s['valid']:return s['disposition']+'; unavailable'
    v=read(p)
    if j['role']=='selection':
        sel=v['selection'];return 'implementation '+json.dumps(sel.get('implementation',[]))+'; investigation '+json.dumps(sel.get('investigation',[]))
    cs=v.get('candidates',[])
    if not cs:return 'No candidate; inspect source-bound refusal'
    rp=read(r.p('replays/'+j['job_id']+'.json'))
    played={p['candidate_id']:p['replay'] for p in rp['candidate_replays']}
    return '; '.join(f"{c['id']}: {family(r.effective_case(j),c)}, {played[c['id']]['status']}, {played[c['id']].get('action_count','?')} actions" for c in cs)
def main():
    r=CoverageRuntime();grammar_admitted=r.p('coverage/grammar/ADMISSION.v11.json').exists() and read(r.p('coverage/grammar/ADMISSION.v11.json'))['admit'] is True
    if grammar_admitted:
        from ac_grammar_complete_runtime_v15 import GrammarRuntime
        r=GrammarRuntime()
        for path,digest in read(r.p('coverage/grammar/BUDGET-CLARIFICATION-FREEZE.v12.json'))['sources'].items():
            require(sha(path)==digest,'Grammar budget clarification source drift')
    post_admitted=r.p('coverage/post-invalid/ADMISSION.v13.json').exists() and read(r.p('coverage/post-invalid/ADMISSION.v13.json'))['admit'] is True
    if post_admitted:
        from ac_post_invalid_complete_runtime_v15 import Runtime as PostRuntime
        r=PostRuntime()
    source_admitted=r.p('coverage/source-completion/ADMISSION.v17.json').exists() and read(r.p('coverage/source-completion/ADMISSION.v17.json'))['admit'] is True
    if source_admitted:
        from ac_source_completion_runtime_v17 import Runtime as SourceRuntime
        r=SourceRuntime()
    provenance_admitted=r.p('coverage/provenance-fidelity/ADMISSION.v18.json').exists() and read(r.p('coverage/provenance-fidelity/ADMISSION.v18.json'))['admit'] is True
    if provenance_admitted:
        from ac_provenance_fidelity_runtime_v18 import Runtime as ProvenanceRuntime
        r=ProvenanceRuntime()
    require(all(r.state(j['job_id'])['terminal'] for j in r.plan()),'All admitted original and coverage dispositions must be terminal')
    witness_files=['receipts/coordinator.final.json','receipts/coverage-coordinator.final.json']
    if grammar_admitted:witness_files.append('receipts/grammar-coordinator.final.json')
    for f in witness_files:
        require(read(r.p(f))['observation']=='actual_FINAL','Coordinator actual FINAL witness absent: '+f)
    if post_admitted:
        post_closure=read(r.p('receipts/POST-INVALID-CLOSURE.v13.json'))
        require(post_closure['observation']=='actual_root_coordinated_closure' and post_closure['all_five_terminal'] is True,'Separate five-role actual root closure required')
    if source_admitted:
        source_closure=read(r.p('receipts/SOURCE-COMPLETION-CLOSURE.v17.json'))
        require(source_closure['observation']=='actual_root_coordinated_closure' and source_closure['all_scheduled_terminal'] is True and source_closure['scheduled_count']==10,'Actual separate ten-role source-comparison closure required')
    if provenance_admitted:
        provenance_closure=read(r.p('receipts/PROVENANCE-FIDELITY-CLOSURE.v18.json'))
        require(provenance_closure['observation']=='actual_root_coordinated_closure' and provenance_closure['all_scheduled_terminal'] is True and provenance_closure['scheduled_count']==8,'Actual eight-role provenance closure required')
        from verify_ac_provenance_v18 import check
        require(check(r)['status']=='pass','Actual literal transmission check required')
    integrity=r.verify();require(integrity['status']=='pass','Execution integrity verification failed')
    primary=read(r.p('reports/RESULTS.v1.json'));methods=read(r.p('inputs/methods.json'));rows=[]
    for ac in [f'AC{i:02d}' for i in range(1,21)]:
        own=[j for j in r.original_plan() if j['strategy_id']==ac]
        title=methods[ac]['instructions'].splitlines()[0].removeprefix('### '+ac+'. ')
        first=reviews(r,ac,'original');later=reviews(r,ac,'ordinary');grammar=reviews(r,ac,'grammar')
        grammar_jobs=[j for j in r.grammar_plan() if j['strategy_id']==ac and j['role']=='builder'] if grammar_admitted else []
        arrangement_jobs=[j for j in r.coverage_plan() if j['strategy_id']==ac and j.get('arrangement_coverage') and j['role']=='builder']
        control_jobs=[j for j in r.coverage_plan() if j['strategy_id']==ac and j.get('additional_control_coverage') and j['role'] in ['builder','transfer','selection']]
        rows.append({'strategy_id':ac,'title':title,'first_independent_reviews':first,'later_control_coverage_reviews':later,'grammar_application_coverage_reviews':grammar,'native_arrangement_coverage_endpoints':[{'job':j,'actual_state':r.state(j['job_id']),'summary':endpoint(r,j)} for j in arrangement_jobs],'native_additional_control_endpoints':[{'job':j,'actual_state':r.state(j['job_id']),'summary':endpoint(r,j)} for j in control_jobs],'native_grammar_endpoints':[{'job':j,'actual_state':r.state(j['job_id']),'summary':endpoint(r,j)} for j in grammar_jobs],'native_endpoints':[{'job':j,'actual_state':r.state(j['job_id']),'summary':endpoint(r,j)} for j in own if j['role'] in ['builder','transfer','selection']],'old_method_ids':list(dict.fromkeys(j['method_id'] for j in own if j['arm'] in ['OLD','FIXED']))})
    timing=[];output_sizes=[];adjacent_trials=[]
    for j in r.plan():
        jid=j['job_id'];s=r.state(jid)
        trial=r.p('replays/'+jid+'.adjacent-settings.json')
        if j.get('post_attack_adjacent_trial') and trial.exists():
            adjacent_trials.append({'job_id':jid,'actual_state':s,'path':str(trial),'sha256':sha(trial),'actual_model_record':read(trial)})
        if s['disposition']=='finished':
            admission=read(r.p('receipts/jobs/'+jid+'.admitted.json'))
            timing.append({'job_id':jid,'utc_admitted':admission['utc'],'utc_finished_recorded':s['utc'],'limit':'Admission/terminal bookkeeping envelope, not GPU runtime or exact cognition time'})
        p=r.p('raw/'+jid+'.json')
        if p.exists():
            try:v=read(p);n=words(v)
            except Exception:n=None
            output_sizes.append({'job_id':jid,'artifact':'main','valid':s['valid'],'bytes':p.stat().st_size,'normalized_words':n,'sha256':sha(p)})
        side=r.p('raw/'+jid+'.arrangements.json')
        if side.exists():output_sizes.append({'job_id':jid,'artifact':'arrangement_sidecar','valid':s['valid'],'bytes':side.stat().st_size,'normalized_words':words(read(side)),'sha256':sha(side)})
    consolidated={'schema_version':'academic-twenty.original-and-control-coverage.v2','utc':now(),'original197_status':primary['actual_native_status'],'later_control_status':r.coverage_status(),'later_control_scheduled_dispositions':len(r.coverage_plan()),'separate_grammar14_status':r.grammar_status() if grammar_admitted else 'conditional preparation unrun','actual_native_invocation_ledger':r.invocations(),'integrity':integrity,'strategy_reviews_and_endpoints':rows,'post_attack_adjacent_pure_model_trials':adjacent_trials,'timing_envelopes':timing,'output_size_measurements':output_sizes,'native_model_tokens':'unavailable','hidden_compute':'unavailable','independent_completion_audits':'reserved, not yet performed by this renderer','first_outputs_and_reviews_preserved':True,'statistical_population_effect':'not supported'}
    consolidated['initial_later75_count']=75
    consolidated['post_invalid5_status']=r.post_invalid_status() if post_admitted else 'prepared, unadmitted'
    consolidated['post_invalid_closure']=post_closure if post_admitted else None
    consolidated['source_completion10_status']=r.source_completion_status() if source_admitted else 'prepared, unadmitted'
    consolidated['source_completion_closure']=source_closure if source_admitted else None
    consolidated['provenance_fidelity8_status']=r.provenance_status() if provenance_admitted else 'unadmitted'
    consolidated['provenance_fidelity_closure']=provenance_closure if provenance_admitted else None
    save(r.p('reports/RESULTS.v2.json'),consolidated)
    ordinary=[j for j in r.plan() if j['strategy_id']=='ORD']
    parts=['# Academic twenty: observed execution and comparisons\n',
      'This report covers the actual native AC01–AC20 agent procedures and their earlier-method comparisons. It preserves the first 197-role study and the separate later ordinary and arrangement-control coverage. Independent completion audits follow this first rendering; no automatic application, novelty or efficacy grade is assigned by the renderer.\n',
      '## Execution and evidence\n',
      f"The shared ledger contains **{len(r.invocations())} actual native invocation attempts** at rendering, including preparation, independent preflight, coordination, successful or invalid roles and any failed calls. The original plan has {len(r.original_plan())} scheduled dispositions; the separate control coverage has {len(r.coverage_plan())}. Two completion auditors remain reserved within the separately frozen{r.budget()['ceiling']}-call later cumulative ceiling (original260 and previous later300 root protocols preserved). Native FINALs are coordinator/root observations, rather than independently authenticated platform exports.\n",
      'Both first ordinary proposals returned actual FINAL without saved files because root had omitted the output directory. The two invalid first attempts and four downstream gates remain unchanged. A separate later six-role ordinary study and ten independent reviews supply new comparison evidence. Those later comparisons do not overwrite original unavailable comparisons or turn missingness into zero.\n',
      'Actual first REVIEW4/5 gaps motivated separately admitted matched-absence controls, routine and P10 selection, equally practiced older-procedure retrieval, prospective overfitting screening before later heldout uses, source-routing coverage and an older P08 endpoint from valid unchanged upstream evidence. Original failed/gated source routes and reviewer disagreements stay visible. Later comparisons cannot identify equal hidden compute or new root-unseen holdouts. The extra source/role/holdout provenance manifests address missing packet evidence without overwriting first reviewer doubts.\n',
      'The original AC09 NONE builder also returned actual FINAL without a JSON save after its command used unavailable python. That invalid original endpoint remains unavailable. One separately admitted later NONE builder uses the identical actual original case, method, bounds and unchanged valid critique handoff; the original first/second/critique pool remains preserved control evidence. This supplies a later endpoint rather than an original repair.\n',
      'Actual first REVIEW3 clauses motivated twelve further fidelity roles: accurate before/revised preservation, independent ROOT:S03 investigators, ordinary improvement of the unchanged verified core, bounded same-parent/actual-account checks and a post-attack adjacent builder. The latter reconstructs one preregistered received construction and triggers three locked pure-model setting executions after actual native FINAL. Those executions are neither three native calls nor independently searched constructions. The source-bound checks cannot invent a failed defended premise or unsupported useful link. Original not-applied/unknown judgments and incomplete comparisons remain preserved.\n',
      'The original-grammar and AC07 OLD/BREADTH builders returned three candidates despite the stricter one-candidate role bound and were locked invalid. The original packet contained a generic three-candidate cap. After 61 original roles had closed, a frozen prospective clarification applied to 132 still-unadmitted jobs: future builder/transfer packets say candidate_cap1, matching the already-existing literal and validator bounds. Cases, methods, dependencies, word/search allowances and all admitted original packets/first outputs remain intact. The 197-role study therefore has two disclosed packet-clarity phases; do not interpret improved role compliance as creativity or learning, or claim the generic field stayed unchanged. Separate later control evidence preserves original failures and missingness.\n',
      'The first AC04 ordering contrast had three treatment and two older-arm initial constructions. Later coverage prospectively prescribes three initial constructions and six search slots for both fresh arrangement-first and function-first arms. The original unequal-count comparison remains visible. The later reviewers also inspect saved assigned-packet manifests and literal source-bank bytes; this distinguishes equal AM/AI delivery from actual use. Version4/5 pure preparation errors were detected before any coverage native call, and their unrun drafts remain preserved.\n',
      'Two actual later COV-REVIEW-1 first outputs were locked invalid because they added top-level fields outside the unchanged six-key review schema. Their raw assessments are displayed as unadmitted rows, not semantic grades. The common literal also requested empty fields that the review schema excludes; a frozen prospective v12 clarification makes the existing six-key requirement explicit only for eight still-unadmitted later reviews and the two conditional grammar reviews. All payload schemas, validators, cases, methods, resources, dependencies and first grades remain unchanged. This is a protocol clarity phase, not evidence of creativity or learning.\n',
      ('The initial later protocol retains its75 dispositions. A separate post-invalid protocol adds five actually executed roles: an older matched-absence endpoint from the unchanged valid critique and four fresh reviews. The failed older builder omitted job_id and reported a generic memory lookup before reading its packet; its claim that those results were unused is unverified. That invalid first output and its actual FINAL remain intact. The later endpoint receives no failed builder output; all five packets explicitly state the existing complete key set and task-first source boundary. The initial75 plus post-invalid5 subtotal is80; the separately declared source10 phase brings the aggregate later-control count to90. The original75 plan is unchanged. These are new observations, not repaired first attempts or evidence of absence of influence.\n' if post_admitted else ''),
      'A pure later-review start assertion failed before admission or native call because the whole prompt included preserved historical copies of the same instruction. Frozen v14 wrappers apply the already-declared clarification only to the current envelope, preserving historical PAYLOAD_JSON bytes exactly. This is a pure adapter correction, not a native draw, retry or method/learning effect. The separately frozen grammar budget memo supersedes only stale260 references in inherited unrun preparation with the actual later cumulative300 ceiling; the originalroot260 protocol remains historical.\n',
      'Four later source-route actors called before the complete-key clarification added prohibited top-level provenance/pool objects and remain invalid, with four uncalled descendant gates. A prospective v15 clarification names the existing13 nonreview keys and records source details inside existing traces/handoffs. Separately declared source-completion coverage, when admitted, supplies new shared and distinct source route/exchange/builder chains and two fresh reviews from unchanged valid pre-assistance pools; it is not a precursor rerun or earlier output repair. The ten-role v17 plan prospectively supersedes the six-role v16 preparation before either was admitted; those are not sixteen executions. Other invalid source arms remain unavailable. The v16 preparation projection conservatively double-counted reserved grammar roles before grammar admission; the preserved budget note identifies that overlap, while actual admission recomputes the binding live300 ceiling.\n',
      table(['Study','Disposition counts','Valid finished'],[['Original197',json.dumps(primary['actual_native_status']['counts']),primary['actual_native_status']['valid_finished']],[f"Later{len(r.coverage_plan())}",json.dumps(r.coverage_status()['coverage_counts']),r.coverage_status()['coverage_valid_finished']]]),
      ('Actual paired source reviews found that precursor pools and provenance survived exchange traces but were missing from selected summaries. Eight separate v18 roles add three new exchanges, three summary-only builders and two reviews; precursor and route stages are reused unchanged. The root freezes a literal preservation capsule; exchanges receive it, builders receive only the actual selected summary plus common J0 facts. All six transmission/construction roles use explicitly larger10000-word transport caps, versus earlier1800; this tests preservation, not matched creativity efficacy or equal compute. Original incomplete summaries and independent grades remain visible. The prospectively frozen v2 root budget amendment raises only the later cumulative ceiling from300 to310 for this coverage and two completion audits; the actual native goal is unbudgeted. Aggregate later coverage is75+5+10+8=98, with original197 and separate grammar14 retained:309 admitted scheduled dispositions.\n' if provenance_admitted else ''),
      ('Actual literal transmission verification: '+link('frozen-pool and assigned-packet checks',r.p('reports/PROVENANCE-FIDELITY-VERIFICATION.v1.json'))+'. Complete arrays and source metadata survive actual exchange, received summary and builder output. This certifies literal retention in assigned artifacts, not semantic invention or hidden-access behavior.\n' if provenance_admitted else ''),
      ('All three v18 summary-only builders reconstruct a known clip operation with two active modeled actions. Earlier source-completion SHARED/DISTINCT endpoints chose known head-loop constructions with six actions, and the clarified UNION endpoint chose a known stem-sleeve with six. The actual fresh ordinary reference COV-ORD-O-J0-builder already used two active actions. This later reconstruction difference recovers the ordinary action-count floor under a larger, explicitly aided information handoff; it does not isolate a creative-method effect, equal compute, compression efficiency or an invention absent from upstream pools.\n' if provenance_admitted else ''),
      '## Ordinary reference endpoints\n',
      table(['Role','Actual endpoint'],[[link(j['job_id'],r.p('raw/'+j['job_id']+'.json')) if r.p('raw/'+j['job_id']+'.json').exists() else j['job_id'],endpoint(r,j)] for j in ordinary if j['role']=='builder']),
      ('Separate grammar coverage was actually admitted and executed on JG to clarify the first AC03 grammar boundary. Its14 new roles use an explicitly closed original production and preserve all original AC03 dispositions. This is application coverage, not retroactive original-case efficacy.\n' if grammar_admitted else 'The conditional explicit-grammar coverage package remains unrun and supplies no result.\n'),
      '## Twenty-card application matrix\n',
      'Application is independent of feasible outcome, matched addition, full-upstream originality, burden and learning. Differing assessments remain displayed separately. Later reviews preserve original strategy bytes while adding fresh ordinary controls and a separately identified fresh paired AC04 ordering study.\n',
      table(['Card','Operation','First review dispositions','Later ordinary review dispositions','Separate grammar dispositions','Earlier method IDs'],[[x['strategy_id'],x['title'],', '.join(v['assessment']['application']+(' [invalid review]' if not v['valid'] else '') for v in x['first_independent_reviews']) or 'unavailable',', '.join(v['assessment']['application']+(' [invalid review]' if not v['valid'] else '') for v in x['later_control_coverage_reviews']) or 'unavailable',', '.join(v['assessment']['application']+(' [invalid review]' if not v['valid'] else '') for v in x['grammar_application_coverage_reviews']) or 'unrun',', '.join(x['old_method_ids']) or 'Dedicated controlled intervention'] for x in rows]),
      '## Endpoint and contrast records\n']
    for x in rows:
        parts += [f"### {x['strategy_id']}. {x['title']}\n",table(['Arm / fixture','Actual final operation or selection'],[[v['job']['arm']+' / '+v['job']['case_id'],link(v['job']['job_id'],r.p('raw/'+v['job']['job_id']+'.json'))+': '+v['summary']] for v in x['native_endpoints']])]
        contrast=[]
        if x['native_arrangement_coverage_endpoints']:
            parts += ['Separate prospectively matched-count arrangement coverage endpoints (J0; original comparison unchanged):\n',table(['Arm / fixture','Actual later endpoint'],[[v['job']['arm']+' / '+v['job']['case_id'],link(v['job']['job_id'],r.p('raw/'+v['job']['job_id']+'.json'))+': '+v['summary']] for v in x['native_arrangement_coverage_endpoints']])]
        if x['native_additional_control_endpoints']:
            parts += ['Separate later control and fidelity endpoints:\n',table(['Arm / fixture','Actual later endpoint'],[[v['job']['arm']+' / '+v['job']['case_id'],link(v['job']['job_id'],r.p('raw/'+v['job']['job_id']+'.json'))+': '+v['summary']] for v in x['native_additional_control_endpoints']])]
        if x['strategy_id']=='AC11':
            for trial in adjacent_trials:
                parts += ['Actual post-attack shared-construction model trials: '+link(trial['job_id'],trial['path'])+'. One observed native reconstruction, identical operations at all settings, followed by deterministic paired replay. This isolates preference eligibility, without three separate searches or a whole-method effect estimate.\n',table(['Soft setting','Hard replay','Active actions','Impacts','Preference satisfied'],[[z['setting'],z['replay']['status'],z['replay'].get('action_count'),z['replay'].get('impact_actions'),z['replay'].get('soft_preference_satisfied')] for z in trial['actual_model_record']['trial_replays']])]
        if x['native_grammar_endpoints']:
            parts += ['Separate grammar coverage endpoints (JG; original results unchanged):\n',table(['Arm / fixture','Actual later endpoint'],[[v['job']['arm']+' / '+v['job']['case_id'],link(v['job']['job_id'],r.p('raw/'+v['job']['job_id']+'.json'))+': '+v['summary']] for v in x['native_grammar_endpoints']])]
        for scope,key in [('Original','first_independent_reviews'),('Later control coverage','later_control_coverage_reviews'),('Separate grammar application coverage','grammar_application_coverage_reviews')]:
            for v in x[key]:
                a=v['assessment'];validity='' if v['valid'] else 'INVALID reviewer draw; unadmitted raw assessment: '
                parts.append(f"**{scope}, {link(v['review_job'],r.p('raw/'+v['review_job']+'.json'))}:** {validity}{a['application']}; {a['reason']} Learning/human ceiling: {a['learning_or_human_limit']}\n")
                for c in a['comparisons']:
                    contrast.append([scope+' '+v['review_job'],' vs '.join(c['arm_pair']),c['available'] if v['valid'] else 'Invalid reviewer; raw '+cell(c['available']),addition_display(c) if v['valid'] else 'Unadmitted raw assessment '+cell(c['qualified_addition']),c['result']+' Upstream: '+c['upstream_overlap']+' Usefulness: '+c['usefulness']+' Burden: '+c['burden']])
        parts.append(table(['Review scope','Contrast','Available','Qualified addition (raw assessment)','Evidence-bound finding'],contrast))
    ceilings=read(r.p('reports/MODEL-CEILINGS.v1.json'))
    parts += ['## Fixture limits and interpretation\n',
      table(['Case','Minimum active actions','Basis'],[[v['case_id'],'Impossible' if v['impossible_under_supplied_mechanics'] else v['minimum_non_idle_actions'],v['lower_bound_argument']] for v in ceilings['reference_rows']]),
      'These lower bounds are root-authored unscored witnesses with actual pure replay, never native strategy outputs or novelty additions. They show why an optimal familiar construction can tie a creative method on workload even when the method opens other representations or mechanisms. The fixtures deliberately disclose supported affordances to every applicable condition. Results are local to these closed synthetic models; they do not prove that creativity lacks value in richer settings.\n',
      'The academically motivated ingredients are investigated as mechanisms and moderators: available knowledge/relations, flexible descriptions, admissible conventions, independent contributions, constructive criticism, development/evaluation, usable feedback and retained procedures. No universal necessary-and-sufficient creativity recipe is established. Originality and effectiveness are criteria; a procedural output still requires comparison and evidence.\n',
      'AC08 tests actual agent history availability; human incubation is unrun. AC16 tests external procedure cards, active practice and fresh holdouts; a fresh no-card agent has no teacher state and cannot establish unassisted learned retention. AC17 tests a one-field external method revision, with both arms receiving the same old failure feedback. These results establish at most artifact retrieval/transfer/adaptation. Human delayed learning, model weight change and durable default workflow improvement remain unmeasured.\n',
      'AC18 uses actual user preferences, but modeled operator actions cannot establish beneficiary relief or adoption. AC20 actually changes routed synthetic source packs, and the union control exposes information differences; distinct role names and lexical variation alone do not establish source or mechanism diversity. Fixed-pool AC15/19 evaluate selection, without credit for generation.\n',
      'Earlier-method instructions were rerun on current fixtures for matched local contrasts. Historical conceptual lineage and selectively read archived raw outputs supply a different comparison; heterogeneous old scores are never subtracted from new scores. Source inventory/hash coverage does not certify exhaustive semantic inspection.\n',
      '## Integrity, costs and reusable output\n',
      f"Verification: **{integrity['status']}**. Preserved sources include the 48 primary protocol files and 6568 historical JSON/Markdown files, plus the prospective primary clarity amendment and separate later control protocols. {sum(p['bytes'] for p in output_sizes)} raw output bytes and {sum(p['normalized_words'] or 0 for p in output_sizes)} normalized JSON words are measurable. Per-role model tokens, hidden search/compute and hardware execution cost are unavailable. Aggregate native-goal token/time bookkeeping can be recorded separately at final publication; it includes root planning and cannot allocate compute fairly between methods. Equal caps and search slots do not prove equal compute.\n",
      'The academic cards and bibliography remain reusable preparation snapshots. Actual run artifacts add evidence, rather than installing a global skill or changing defaults. Persistent external method cards have explicit retrieval conditions and applicability/refusal limits.\n',
      'Machine evidence: '+', '.join(link(n,r.p(p)) for n,p in [('first results','reports/RESULTS.v1.json'),('original plus later results','reports/RESULTS.v2.json'),('model bounds','reports/MODEL-CEILINGS.v1.json'),('original contract','CONTRACT.md'),('later control contract','coverage/CONTRACT.v10.md'),('first source freeze','preparation/FREEZE.v1.json')])+'.\n']
    save(r.p('reports/EXECUTION-RESULTS.v1.md'),'\n'.join(parts).encode())
    print(json.dumps({'saved':['reports/RESULTS.v2.json','reports/EXECUTION-RESULTS.v1.md'],'actual_native_calls':len(r.invocations()),'completion_audits_still_required':True}))
if __name__=='__main__':main()
