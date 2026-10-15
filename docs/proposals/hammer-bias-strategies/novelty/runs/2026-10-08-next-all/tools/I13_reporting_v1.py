"""I13 reporting over unchanged locked judgments; no new semantic assessment."""
from collections import Counter
import composition_i13_runtime_v2 as z

FIELDS = ('intelligible','novelty','usefulness','observability','fit','support','contract','family_confirmed')

def statuses(rows):
    return dict(Counter(s for r in rows for s in r['field_status'].values()))

def raw_qualified(row):
    if any(row['field_status'].get(k) not in z.RESOLVED for k in FIELDS):
        return None
    v = row['values']
    return (v['intelligible'] is True and v['novelty']=='new' and v['usefulness']>=1 and
            v['observability']==2 and v['fit']=='preserves' and v['support']!='unsupported' and
            v['contract']=='met' and v['family_confirmed'] is True)

def retention_outcome(row):
    # Preserve the frozen helper result and separately disclose null semantics.
    return {'source_card_id':row['identity']['source_card_id'],
            'status':z.retention_status(row),'values':row['values'],
            'field_status':row['field_status']}

def case_evidence(context, lock, views):
    z.require(z.identical(lock['carried_raw_rows'],context['carried_raw_rows']), 'exact original raw carry')
    z.require(z.identical(views,z.build_views_and_memberships(context,lock)), 'unchanged deterministic view calculation')
    raw = {r['identity']['card_id']:r for r in context['carried_raw_rows'] if r['table']=='raw_rows'}
    pools = {}
    for name,p in context['producers'].items():
        ids = list(p['local_to_original'].values())
        qualified = [raw_qualified(raw[x]) for x in ids]
        pools[name] = {'original_raw_job_id':p['job_id'],'original_source_ids':ids,
                       'raw_source_cards':len(ids),'qualified_locked_cards':sum(v is True for v in qualified),
                       'unresolved_qualification_cards':sum(v is None for v in qualified),
                       'zero_new_creation_or_assessment_credit':True}
    units = []
    for u,detail in zip(lock['D_units'],views['details']):
        jid=u['unit_id']
        rows=[r for r in lock['fresh_rows'] if r['identity'].get('compressor_id')==jid or
              r['identity'].get('unit_id')==jid or
              r['identity'].get('card_id','').startswith(jid+':') or
              r['identity'].get('post_card_id','').startswith(jid+':')]
        ret=[r for r in rows if r['table']=='retention_rows']
        post=[r for r in rows if r['table']=='post_rows']
        pairs=[r for r in rows if r['table']=='source_pairs']
        contract=[r for r in rows if r['table']=='unit_rows']
        units.append({'job_id':jid,'pool':u['pool'],'compressor':u['compressor'],
                      'execution':u['execution'],'retention_rows':[retention_outcome(r) for r in ret],
                      'retention_statuses':dict(Counter(z.retention_status(r) for r in ret)),
                      'post_cards':len(post),'post_new_assertion_true':sum(r['values']['new_assertion'] is True for r in post),
                      'post_new_assertion_unresolved':sum(r['values']['new_assertion'] is None for r in post),
                      'source_pair_relations':dict(Counter(r['values']['relation'] if r['values']['relation'] is not None else 'unresolved' for r in pairs)),
                      'unit_contract_rows':contract,'fresh_semantic_field_statuses':statuses(rows),
                      'views':detail['views'],'optional_proposals':detail['optional_proposals'],
                      'burden':detail['burden'],'identical_source_sets_by_two_source_design':detail['identical_source_sets_by_two_source_design']})
    comparisons=[]
    for pool in z.POOLS:
        chosen=[u for u in units if u['pool']==pool]
        first,second=next(u for u in chosen if u['compressor']=='ordinary_D'),next(u for u in chosen if u['compressor']=='source_D')
        a={r['source_card_id']:r['status'] for r in first['retention_rows']}
        b={r['source_card_id']:r['status'] for r in second['retention_rows']}
        z.require(set(a)==set(b)==set(pools[pool]['original_source_ids']), 'paired compression full own source set')
        pairs=[{'source_card_id':x,'ordinary_D':a[x],'source_D':b[x],
                'assessable_retention_comparison':a[x] in ('retained','lost') and b[x] in ('retained','lost')}
               for x in pools[pool]['original_source_ids']]
        comparisons.append({'pool':pool,'source_comparisons':pairs,
                            'all_retention_comparisons_assessable':all(p['assessable_retention_comparison'] for p in pairs),
                            'retained_difference_source_minus_ordinary':sum(v=='retained' for v in b.values())-sum(v=='retained' for v in a.values())
                            if all(p['assessable_retention_comparison'] for p in pairs) else None})
    cells=[]
    for u in units:
        for view_name in z.VIEWS:
            selected=u['views'][view_name]
            cells.append({'pool':u['pool'],'compressor':u['compressor'],'view':view_name,
                          'status':u['views']['status'],'source_ids':selected,
                          'selected_source_count':len(selected) if selected is not None else None,
                          'selected_qualified_alternative_eligible_count':sum(x in u['views'].get('eligible_ids',[]) for x in selected)
                          if selected is not None else None})
    all_evaluable=all(c['status']=='evaluable' for c in cells)
    metrics={}
    for outcome in ['selected_source_count','selected_qualified_alternative_eligible_count']:
        ys={(c['pool']=='backcast',c['compressor']=='source_D',c['view']=='alternative'):c[outcome] for c in cells}
        names={'generation_main':[0],'compression_main':[1],'view_main':[2],
               'generation_x_compression':[0,1],'generation_x_view':[0,2],
               'compression_x_view':[1,2],'generation_x_compression_x_view':[0,1,2]}
        metrics[outcome]={name:sum((1 if sum(key[j] for j in dims)%2==len(dims)%2 else -1)*value
                                     for key,value in ys.items())/(2**(3-len(dims))) if all_evaluable else None
                          for name,dims in names.items()}
    return {'case_id':context['case_id'],'source_context_sha256':context['context_sha256'],
            'creation_valid':context['creation_valid'],'diagnostic_only':context['diagnostic_only'],
            'old_post_failure_preserved':context['old_post_failure'],
            'generic_context_preserved':context['generic_context_preserved'],'raw_creation_credit':0,
            'reused_original_raw_pools':pools,'carried_raw_rows':len(context['carried_raw_rows']),
            'carried_raw_semantic_field_statuses':statuses(context['carried_raw_rows']),
            'fresh_rows_by_table':dict(Counter(r['table'] for r in lock['fresh_rows'])),
            'fresh_semantic_field_statuses':statuses(lock['fresh_rows']),
            'fresh_scalar_unresolved_fields':sum(s=='scalar_unresolved' for r in lock['fresh_rows'] for s in r['field_status'].values()),
            'fresh_family_unresolved_fields':sum(s=='family_unresolved' for r in lock['fresh_rows'] for s in r['field_status'].values()),
            'independent_review_complete':lock['independent_review_complete'],'units':units,
            'compression_comparisons':comparisons,'view_cells':cells,
            'factorial_completely_evaluable':all_evaluable,'factorial_deterministic_exposure_contrasts':metrics,
            'factorial_claim':'Within supplied locked source exposure only; incomplete factorial yields null effects. Generation pools reused, no newly randomized generation effect. No human benefit.',
            'view_statuses':dict(Counter(c['status'] for c in cells)),
            'disputes':lock['disputes'],'new_raw_semantic_grades':0,
            'forced_family_merges':0,'native_view_judgment_credit':0}

