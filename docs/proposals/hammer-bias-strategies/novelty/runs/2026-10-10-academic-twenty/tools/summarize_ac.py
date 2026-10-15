#!/usr/bin/env python3
"""Derive transparent counts/contrast tables from actual immutable observations.

Does not invoke models, invent scores, or replace independent semantic review.
"""
import collections, hashlib, json
from pathlib import Path
from ac_runtime import ROOT, Runtime, read, save, words
def family(case,c):
    a=c.get('actions',[]);ops={x.get('op') for x in a if isinstance(x,dict)}
    if case['domain']=='W':
        update=case.get('update_boundary')
        return 'version-aware-cached-report' if update is not None and any(x.get('op')=='read' and x.get('arg')=='A' and x.get('tick',0)>=update for x in a) else 'cached-report'
    f=[]
    if 'tap' in ops:f.append('pins')
    if any(x.get('op')=='install' and x.get('arg')=='C' for x in a):f.append('clip')
    if 'insert' in ops:f.append('stem-sleeve')
    if 'route' in ops and 'place' in ops:f.append('head-loop')
    if any(x.get('op')=='install' and x.get('arg')=='Q' for x in a):f.append('alternate-sleeve-Q')
    return '+'.join(f) if f else 'no-supported-retainer'
def derive(root=ROOT):
    r=Runtime(root);status=r.status();jobs=r.plan();rows=[];raws={};outputs=[]
    for j in jobs:
        jid=j['job_id'];p=r.p('raw/'+jid+'.json')
        if not p.exists():continue
        try:v=read(p)
        except Exception:continue
        if not isinstance(v,dict):continue
        raws[jid]=v;outputs.append({'job_id':jid,'artifact':'main','normalized_words':words(v),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'state':r.state(jid)['disposition'],'valid':r.state(jid)['valid']})
        side=r.p('raw/'+jid+'.arrangements.json')
        if side.exists():outputs.append({'job_id':jid,'artifact':'arrangement_sidecar','normalized_words':words(read(side)),'bytes':side.stat().st_size,'sha256':hashlib.sha256(side.read_bytes()).hexdigest(),'state':r.state(jid)['disposition'],'valid':r.state(jid)['valid']})
    for ac in [f'AC{i:02d}' for i in range(1,21)]:
        own=[j for j in jobs if j['strategy_id']==ac];review=[];native=[]
        for j in jobs:
            if j['role']=='review' and j['job_id'] in raws:
                review.extend({'review_job':j['job_id'],'review_valid':r.state(j['job_id'])['valid'],'assessment':x} for x in raws[j['job_id']].get('strategy_reviews',[]) if isinstance(x,dict) and x.get('strategy_id')==ac)
        valid_review=[x for x in review if x['review_valid']];disps=[x['assessment']['application'] for x in valid_review]
        coverage='unknown'
        if len(disps)==2 and all(x in ['applied','explicit_no_opening'] for x in disps):coverage='independently-covered'
        elif len(disps)==2 and len(set(disps))==1:coverage=disps[0]
        elif disps:coverage='reviewer-disagreement'
        for j in own:
            jid=j['job_id'];v=raws.get(jid);rp=r.p('replays/'+jid+'.json')
            if not v or not rp.exists():continue
            case=r.effective_case(j);played=read(rp);replays={x['candidate_id']:x['replay'] for x in played.get('candidate_replays',[])}
            for c in v.get('candidates',[]) if isinstance(v.get('candidates'),list) else []:
                if not isinstance(c,dict):continue
                out=replays.get(c.get('id'),{'status':'unknown'})
                native.append({'job_id':jid,'role':j['role'],'arm':j['arm'],'case_id':j['case_id'],'candidate_id':c.get('id'),'causal_family_heuristic':family(case,c),'replay_status':out['status'],'action_count':out.get('action_count'),'soft_preference_satisfied':out.get('soft_preference_satisfied'),'errors':out.get('errors',[]),'candidate_validity':r.state(jid)['valid']})
        final=[x for x in native if x['role'] in ['builder','transfer']]
        selections={j['arm']:raws[j['job_id']].get('selection') for j in own if j['role']=='selection' and j['job_id'] in raws}
        rows.append({'strategy_id':ac,'planned_roles':len(own),'actual_calls':sum(r.state(j['job_id'])['disposition'] in ['spawned','finished','failed'] for j in own),'valid_roles':sum(r.state(j['job_id'])['disposition']=='finished' and r.state(j['job_id'])['valid'] for j in own),'gated_roles':[j['job_id'] for j in own if r.state(j['job_id'])['disposition']=='gated'],'application_dispositions':disps,'coverage_derived':coverage,'independent_reviews':review,'all_native_candidate_replays':native,'final_candidate_replays':final,'selection_results':selections,'numerical_addition_not_automatically_inferred':True})
    return {'schema_version':'academic-twenty.derived-results.v1','actual_native_status':status,'strategy_results':rows,'output_size_measurements':outputs,'word_total':sum(x['normalized_words'] for x in outputs),'byte_total':sum(x['bytes'] for x in outputs),'actual_model_tokens':'unavailable','hidden_compute':'unavailable','statistical_population_inference':'not supported; single fixtures, shared/dependent baselines','mechanism_family_heuristic_limit':'Action tags aid inspection; they do not adjudicate semantic novelty, selection, frame changes or lineage.','first_reviews_preserved':True}
def main():
    v=derive()
    if not v['actual_native_status']['terminal']:
        print(json.dumps({'status':'live; no result artifact written','counts':v['actual_native_status']['counts'],'valid_finished':v['actual_native_status']['valid_finished'],'application_reviews_available':{x['strategy_id']:x['application_dispositions'] for x in v['strategy_results'] if x['application_dispositions']}},indent=2));return
    save(ROOT/'reports/RESULTS.v1.json',v)
    print(json.dumps({'saved':'reports/RESULTS.v1.json','actual_native_calls':v['actual_native_status']['total_native_with_prep_coordinator'],'coverage':collections.Counter(x['coverage_derived'] for x in v['strategy_results']),'review_dispositions':{x['strategy_id']:x['application_dispositions'] for x in v['strategy_results']}},indent=2))
if __name__=='__main__':main()
