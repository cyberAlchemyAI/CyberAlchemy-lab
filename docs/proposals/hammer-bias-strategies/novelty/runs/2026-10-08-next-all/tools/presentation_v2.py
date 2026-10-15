"""Fixed-pool deterministic views. Never creates candidates or semantic grades."""
FIT={'preserves':0,'uncertain':1,'conditional':2,'violates':3}
def views(candidates, context_complete=True):
    required=['id','fit','usefulness','observability','intelligible','support','novelty','contract','retention','family_id','family_confirmed','uncertain_links']
    if not context_complete:return {'status':'not_evaluable','cause':'incomplete_execution_or_dual_review_context','ordinary':None,'alternative':None}
    missing=[c.get('id') for c in candidates if any(k not in c or c[k] is None for k in required)]
    if missing:return {'status':'not_evaluable','cause':'unresolved_ranking_or_family_fields','candidate_ids':missing,'ordinary':None,'alternative':None}
    if any(not c['family_confirmed'] or c['uncertain_links'] for c in candidates):
        return {'status':'not_evaluable','cause':'uncertain_family_context','ordinary':None,'alternative':None}
    if len({c['id'] for c in candidates})!=len(candidates):raise ValueError('candidate IDs must be unique')
    pool=sorted(candidates,key=lambda c:(FIT[c['fit']],-c['usefulness'],-c['observability'],c.get('raw_order',0),c['id']))
    retained=[c for c in pool if c['retention']=='retained']
    ordinary=[]
    for c in retained:
        if all(c['family_id']!=x['family_id'] for x in ordinary):ordinary.append(c)
        if len(ordinary)==2:break
    eligible=[c for c in retained if c['intelligible'] and c['novelty']=='new' and c['usefulness']>=1 and c['observability']==2 and c['fit']=='preserves' and c['support']!='unsupported']
    alternative=list(ordinary)
    if ordinary:
        others=[c for c in eligible if c['family_id']!=ordinary[0]['family_id']]
        if others:alternative=[ordinary[0],others[0]]
    selected=lambda cs:[c['id'] for c in cs]
    oi,ai=selected(ordinary),selected(alternative)
    return {'status':'evaluable','ordinary':oi,'alternative':ai,'first_unchanged':(oi[:1]==ai[:1]),'eligible_ids':selected(eligible),'entering_ids':[x for x in ai if x not in oi],'displaced_ids':[x for x in oi if x not in ai],'same_candidate_pool':True,'eligible_absence_is_not_failure':not bool(eligible),'claim':'Deterministic exposure only; no human decision value measured.'}
