#!/usr/bin/env python3
"""Apply the prospective rule to LOCKED human/model-reviewed canonical families.
This script cannot determine semantic equivalence. Its input must cite both
independent judgments and any adjudication establishing that equivalence.
"""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SEED='novelty-2026-10-08-finalists-v1'
CONTROLS={'ordinary','creative'}

def rank_key(row):
    fit={'preserves':0,'uncertain':1,'conditional':2,'violates':3}.get(row['fit'],4)
    raw_order={'Z1':0,'Z2':1,'A1':2,'A2':3}
    return (fit,-row['usefulness'],-row['observability'],raw_order.get(row['raw_id'],9))

def select(data):
    assert data['judgments_locked'] is True
    assert data['equivalence_review_locked'] is True
    assert set(data['cases'])=={'D1','D2'}
    results={};control_pools={};sensitivity={}
    for case,cd in data['cases'].items():
        units=cd['units'];fam=cd['families'];pool=set()
        expected={(c,r) for c in ['ordinary','creative']+[f'N{i:02d}' for i in range(1,13)] for r in [1,2]}
        assert len(units)==28 and {(u['condition'],u['repetition']) for u in units}==expected, 'Incomplete discovery exposure table'
        assert all(u.get('terminal_status') in ['completed','execution_failed'] for u in units), 'Native work still pending'
        assert all(u['assessment_complete'] for u in units), 'Independent review incomplete'
        control_units=[u for u in units if u['condition'] in CONTROLS]
        control_exposure=len(control_units)==4 and all(u['execution_valid'] and u['assessment_complete'] for u in control_units)
        for u in control_units:
            for x in u['raw']+u.get('post_only',[]):
                if x.get('intelligible',True):pool.add(x['family_id'])
        control_pools[case]={'families':sorted(pool),'complete_exposure':control_exposure}
        for u in units:
            rows=sorted([x for x in u['raw'] if x['retention']=='retained'],key=rank_key);seen=set();first=[]
            for x in rows:
                if x['family_id'] not in seen:
                    seen.add(x['family_id']);first.append(x['family_id'])
                if len(first)==2:break
            sensitivity[u['unit_id']]=first
        for n in range(1,13):
            op=f'N{n:02d}';opunits=[u for u in units if u['condition']==op]
            exposure=len(opunits)==2 and {u['repetition'] for u in opunits}=={1,2} and all(u['execution_valid'] and u['assessment_complete'] for u in opunits)
            qualified=set();exclusive=set();recurrence={};shared=set();violations=unresolved=0;words=[]
            for u in opunits:
                unit_families=set()
                for x in u['raw']:
                    f=x['family_id'];fmeta=fam[f]
                    good=(x['raw_id'].startswith('A') and x['novelty']=='new' and x['usefulness']>=1 and x['fit']=='preserves' and x['observability']==2 and x['retention']=='retained' and x['judgment_resolved'] and fmeta['equivalence_status']=='confirmed')
                    if good:
                        qualified.add(f)
                        if not ({f}|set(fmeta.get('uncertain_equivalence_with',[]))) & pool:
                            exclusive.add(f);unit_families.add(f)
                        if any(z['raw_id'].startswith('Z') and z['family_id']==f for z in u['raw']):shared.add(f)
                for f in unit_families:recurrence[f]=recurrence.get(f,0)+1
                violations+=len(set(u.get('recommended_violations',[])))
                unresolved+=len(set(u.get('unresolved_recommended_fit',[])))
                words.append(u.get('output_words'))
            r=results.setdefault(op,{'operator_id':op,'cases':{}})
            r['cases'][case]={'valid_exposure':exposure,'control_exposure':control_exposure,'qualified_A_families':sorted(qualified),'exclusive_families':sorted(exclusive),'recurrence':recurrence,'shared_Z_A_families':sorted(shared),'violations':violations,'unresolved_fit':unresolved,'output_words':sum(words) if len(words)==2 and all(x is not None for x in words) else None}
    for op,r in results.items():
        cs=[r['cases'][c] for c in ['D1','D2']]
        r['eligible']=all(x['valid_exposure'] and x['control_exposure'] and x['exclusive_families'] for x in cs)
        r['dimensions']={'U1':len(cs[0]['exclusive_families']),'U2':len(cs[1]['exclusive_families']),'V':sum(x['violations'] for x in cs),'F':sum(x['unresolved_fit'] for x in cs),'B':sum(x['output_words'] for x in cs) if all(x['output_words'] is not None for x in cs) else None}
        r['tie_key']=hashlib.sha256((SEED+'|'+op).encode()).hexdigest()
    eligible=[r for r in results.values() if r['eligible']]
    # Exact confirmed canonical family sets on both cases define equivalence.
    groups={}
    for r in eligible:
        key=tuple(tuple(r['cases'][c]['exclusive_families']) for c in ['D1','D2']);groups.setdefault(key,[]).append(r)
    reps=[];equivalence_groups=[]
    for group in groups.values():
        group.sort(key=lambda r:r['tie_key']);reps.append(group[0]);equivalence_groups.append([r['operator_id'] for r in group])
    def dominates(x,y):
        a=x['dimensions'];b=y['dimensions']
        if a['B'] is None or b['B'] is None:return False
        av=[a['U1'],a['U2'],-a['V'],-a['F'],-a['B']];bv=[b['U1'],b['U2'],-b['V'],-b['F'],-b['B']]
        return all(i>=j for i,j in zip(av,bv)) and any(i>j for i,j in zip(av,bv))
    nd=[r for r in reps if not any(dominates(x,r) for x in reps if x is not r)]
    nd.sort(key=lambda r:r['tie_key']);selected=[];skips=[]
    unresolved_pairs={frozenset(p) for p in data.get('unresolved_operator_equivalence_pairs',[])}
    for r in nd:
        op=r['operator_id']
        if any(frozenset([op,x]) in unresolved_pairs for x in selected):skips.append(op);continue
        if len(selected)<2:selected.append(op)
    return {'status':'selection_resolved','rule':'reports/preflight-audit.md','seed':SEED,'control_pools':control_pools,'operators':list(results.values()),'confirmed_equivalence_groups':equivalence_groups,'non_dominated':[r['operator_id'] for r in nd],'skipped_ambiguous_equivalence':skips,'finalists':selected,'confirmation_units':0 if not selected else (len(selected)+2)*4*3,'first_two_sensitivity_families':sensitivity,'claim_ceiling':'Prospective local screening rule applied to assessed cases; no causal superiority, global originality, or real-world benefit established.'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('input');a.add_argument('--output',default='reports/finalist-selection.json');args=a.parse_args()
    source=Path(args.input);source=source if source.is_absolute() else R/source
    data=json.loads(source.read_text());result=select(data);result['reviewed_input_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    out=R/args.output;assert not out.exists(),'Selection already frozen; inspect instead of overwrite.';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'finalists':result['finalists'],'confirmation_units':result['confirmation_units']},indent=2))
