#!/usr/bin/env python3
"""Descriptive aggregation of locked confirmation judgments; no new selection."""
import argparse,collections,hashlib,json
from pathlib import Path
from select_finalists import rank_key
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sum_known(values):return sum(values) if all(v is not None for v in values) else None
def summarize(case):
 p=R/'reports'/f'confirmation-{case}-resolved.json';d=read(p)
 assert d['phase']=='confirmation' and d['case_id']==case and d['judgments_locked'] and d['equivalence_review_locked']
 for source in d['sources']:
  sp=Path(source['path']);sp=sp if sp.is_absolute() else R/sp
  assert sha(sp)==source['sha256']
 finalists=read(R/'finalist-freeze.json')['finalists'];conditions=['ordinary','creative']+finalists
 expected={(c,r) for c in conditions for r in [1,2,3]}
 assert len(d['units'])==12 and {(u['condition'],u['repetition']) for u in d['units']}==expected
 assert all(u['assessment_complete'] and u['terminal_status'] in ['completed','execution_failed'] for u in d['units'])
 assert all(not u['post_only'] for u in d['units']),'Explicit extension required to aggregate actual post-only additions'
 families=d['families'];controls=[u for u in d['units'] if u['condition'] in ['ordinary','creative']]
 exposure=all(u['execution_valid'] for u in controls)
 pool={x['family_id'] for u in controls for x in u['raw'] if x.get('intelligible',True)}
 def qualified(x):
  return x['novelty']=='new' and x['usefulness']>=1 and x['fit']=='preserves' and x['observability']==2 and x['retention']=='retained' and x['judgment_resolved'] and families[x['family_id']]['equivalence_status']=='confirmed'
 def exclusive(fid):return not ({fid}|set(families[fid]['uncertain_equivalence_with'])) & pool
 units=[]
 for u in d['units']:
  raw=u['raw'];q=[x for x in raw if qualified(x)];full={x['family_id'] for x in q};aq={x['family_id'] for x in q if x['raw_id'].startswith('A')};first=[]
  for x in sorted([x for x in raw if x['retention']=='retained'],key=rank_key):
   if x['family_id'] not in first:first.append(x['family_id'])
   if len(first)==2:break
  exc={fid for fid in aq if exclusive(fid)}
  shared={x['family_id'] for x in raw if x['raw_id'].startswith('Z')} & aq
  units.append({'unit_id':u['unit_id'],'condition':u['condition'],'repetition':u['repetition'],'execution_valid':u['execution_valid'],'anonymous_packet_id':u['anonymous_packet_id'],'all_intelligible_raw_families':sorted({x['family_id'] for x in raw if x.get('intelligible',True)}),'full_retained_families':sorted({x['family_id'] for x in raw if x['retention']=='retained'}),'full_qualified_families':sorted(full),'first_two_retained_families':first,'qualified_families_in_first_two':sorted(full&set(first)),'qualified_A_families':sorted(aq),'exclusive_qualified_A_candidates':sorted(exc),'exclusive_credit_available':exposure and u['execution_valid'],'exclusive_qualified_A_in_first_two':sorted(exc&set(first)),'shared_Z_A_qualified_families':sorted(shared),'retention':dict(collections.Counter(x['retention'] for x in raw)),'output_words':u['output_words'],'observed_output_words':u.get('observed_output_words',u['output_words']),'post_dispositions':u['post_dispositions'],'unresolved_judgments':[{'raw_id':x['raw_id'],'issues':x['unresolved_judgments']} for x in raw if x['unresolved_judgments']]})
 bycondition={}
 for cond in conditions:
  us=[u for u in units if u['condition']==cond]
  def union(field):return sorted({f for u in us for f in u[field]})
  def recurrence(field):return {f:[u['unit_id'] for u in us if f in u[field]] for f in union(field)}
  bycondition[cond]={'valid_exposure':all(u['execution_valid'] for u in us),'qualified_whole_workflow_union':union('full_qualified_families'),'qualified_whole_workflow_recurrence':recurrence('full_qualified_families'),'qualified_A_union':union('qualified_A_families'),'qualified_A_recurrence':recurrence('qualified_A_families'),'exclusive_qualified_A_candidates':union('exclusive_qualified_A_candidates'),'exclusive_A_recurrence':recurrence('exclusive_qualified_A_candidates'),'first_two_qualified_union':union('qualified_families_in_first_two'),'exclusive_A_first_two_union':union('exclusive_qualified_A_in_first_two'),'shared_Z_A_families':union('shared_Z_A_qualified_families'),'output_words':sum_known([u['output_words'] for u in us]),'observed_output_words':sum_known([u['observed_output_words'] for u in us])}
 contrasts=[]
 for op in finalists:
  for control in ['ordinary','creative']:
   x=set(bycondition[op]['qualified_whole_workflow_union']);y=set(bycondition[control]['qualified_whole_workflow_union'])
   contrasts.append({'operator':op,'control':control,'complete_comparison':bycondition[op]['valid_exposure'] and bycondition[control]['valid_exposure'],'case_union_count_difference':len(x)-len(y),'qualified_family_overlap':sorted(x&y),'operator_qualified_families_outside_this_controls_qualified_set':sorted(x-y),'control_qualified_families_outside_operator_qualified_set':sorted(y-x),'note':'Qualified-set differences are descriptive. Exclusive A credit uses the broader pooled raw control exposure above, including uncertain equivalence.'})
 return {'case_id':case,'phase':'confirmation','status':'descriptive_locked_case_aggregation','conditions':bycondition,'units':units,'paired_case_contrasts':contrasts,'control_pool_all_intelligible_raw_families':sorted(pool),'complete_control_exposure':exposure,'families':families,'unresolved':d['unresolved'],'sources':[{'path':str(p.relative_to(R)),'sha256':sha(p)},{'path':'finalist-freeze.json','sha256':sha(R/'finalist-freeze.json')},{'path':'tools/select_finalists.py','sha256':sha(R/'tools/select_finalists.py')}],'summarizer_sha256':sha(Path(__file__)),'limits':['No new advancement rule, hypothesis test or composite creativity score.','Family IDs are case-local; repeated appearances do not become independent organizations or domains.','Exclusive candidates receive no credit if execution/control exposure is incomplete.','Qualified-set contrasts are not the conservative pooled-control A-attribution test.','Model judgments against incomplete archives; no global originality or executed-world benefit.','Recorded words are output burden, not actual tokens or matched compute.']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('case',choices=['H1','H2','H3','H4']);q=a.parse_args();out=R/'reports'/f'confirmation-{q.case}-summary.json';assert not out.exists(),'Summary already saved; no overwrite'
 result=summarize(q.case);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'output':str(out),'conditions':result['conditions']},indent=2))
