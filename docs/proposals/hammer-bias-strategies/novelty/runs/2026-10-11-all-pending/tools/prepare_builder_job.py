from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];batch=sys.argv[1];branch=sys.argv[2] if len(sys.argv)>2 else 'protected'
ledger=json.loads((R/'receipts/NATIVE-INVOCATIONS.v1.json').read_text())
if not any(x.get('job_id')=='CRITIQUE-'+batch and x.get('join_status')=='completed' for x in ledger['agents']):raise SystemExit('Critic actual FINAL not joined')
critic=json.loads((R/'raw'/('CRITIQUE-'+batch+'.json')).read_text());original=json.loads((R/'preparation/jobs'/('CONSTRUCT-'+batch)/'PAYLOAD.json').read_text());constructor=json.loads((R/'raw'/('CONSTRUCT-'+batch+'.json')).read_text())
ids=[x['strategy_id'] for x in critic['rows']]
if branch!='protected':ids=[i for i in ids if i in ['RT13','RT14','PR10']]
if not ids:raise SystemExit('No declared comparative handoff cards in this batch')
rows=[]
for x in critic['rows']:
 if x['strategy_id'] not in ids:continue
 content=x['handoff'] if branch=='protected' else x['ordinary_summary']
 if branch=='full':content={'original_construction':next(y for y in constructor['rows'] if y['strategy_id']==x['strategy_id']),'full_critique':x}
 rows.append({'strategy_id':x['strategy_id'],'packet':content,'packet_provenance':'Actual first critic output; full branch also contains actual original constructor. Common case facts given equally; method cards omitted.'})
name='BUILD-'+batch+'-'+branch.upper();dst=R/'preparation/jobs'/name;dst.mkdir(exist_ok=False)
payload={'job_id':name,'common_cases':original['cases'],'packets':rows,'output_path':str(R/'raw'/f'{name}.json'),'prior_outputs_available':False,'claim_limit':'Fresh assigned native builder with an instructed read boundary; root/case authors are exposed. Neither FS isolation nor independent cognition/platform authentication is certified. No pure causal handoff effect from unequal upstream contexts.'}
(dst/'PAYLOAD.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
prompt=f"""You are the actual fresh native builder for {name}. Read this PROMPT.md and PAYLOAD.json ONLY. No other role output, method catalog, source archive, parent history, web or helpers. You have common cases and only assigned per-card packets. Write exclusively {payload['output_path']} by first creation. Source/output/report/goal changes forbidden. Maximum400 words per card INCLUDING JSON fields; internal compute unknown.

For every supplied packet actually RECONSTRUCT its operation/analytical artifact in fixed constraints, and produce an inspectable literal candidate, not a suggestion for a future builder. Identify the operative expectation or fractured dependency, fixed outcomes, permitted variable, useful residue, cost/counter/falsifier and source uncertainty. If packet omits a necessary fact, label it missing; never silently retrieve it elsewhere or guess it as given. You may generate an explicitly new candidate if needed, but declare it a new proposal and distinguish it from fidelity. Preserve ordinary equivalents/no-opening findings. For games require rule triggers and finite resources/event ordering; don't replace one-of-three hero, three bosses, acquisition or six-rule authored autoplay envelope. Analytical cases need actual constraints, finite action sequence and separating prediction, not rhetoric alone.

Save job_id,role,source_access,rows. Each row strategy_id,reconstructed_dependency,retained_obligations,missing_obligations,literal_artifact,paper_trace_or_documentary_comparison,cost_counter_falsifier,ordinary_equivalent,provenance(new versus retained),first_attempt_repairs,disposition(applied / source_backed_no_opening / incomplete),outcome_limits. Correct impossible inherited initial states only in YOUR distinct successor artifact, explicitly name the first defect and new reachability witness. Don't retroactively repair a first raw artifact or grade. Use the same supplied facts and extension permission; actual elapsed/output words are not equal compute. No human retention/learning/enjoyment or actual gameplay is measured. Return after substantively saving."""
(dst/'PROMPT.md').write_text(prompt+'\n');print(name,len(ids))
