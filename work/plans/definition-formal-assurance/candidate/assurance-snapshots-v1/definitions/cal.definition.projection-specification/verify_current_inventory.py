"""Current ninety-four-draft inventory and joint declared closure, without owner promotion."""
import json
import build_candidate as b
import dependencies as d
import verifier as v
from static_snapshot_reuse import StaticSnapshotReuse
def inventory(snapshot,reuse):
    context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);b.r.verify(snapshot,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'verify_current_inventory.py',b.IMPL/'dependencies.py',b.IMPL/'ir.py',b.IMPL/'verifier.py',b.BASE/'units/A04/correspondence.py',b.UNIT/'static_snapshot_reuse.py',b.UNIT/'static-snapshot-reuse-checks.json']]
    rows=[];packets=[];refs=[];counts={k:0 for k in ['source_units','mapped_clauses','encoded_clauses','explanatory_clauses','deferred_clauses','required_populations','unresolved_populations']}
    existing=list(sorted((b.BASE/'definitions').glob('*/t.json')))
    if len(existing)!=94:raise ValueError('Unexpected current candidate draft denominator')
    witnesses=[]
    for path in existing:
        unit=path.parent;envelope=json.loads(path.read_bytes());core=envelope['payload'];packet=json.loads((unit/'correspondence.json').read_bytes());typed=json.loads((unit/'static-ir.json').read_bytes())
        if not b.r.same_json(core['source'],b.source_ref(snapshot,core['source']['definition_id'])) or not b.r.same_json(packet['interpretation'],core) or not b.r.same_json(typed,b.ir.compile_interpretation(core,snapshot)):raise ValueError('Source/core/IR substitution')
        account=b.co.check(packet,snapshot)
        if not account['character_accounting_complete'] or core['source_fidelity']!='pending' or core['assumptions'] or packet['assumption_links']:raise ValueError('Incomplete correspondence or invented acceptance/assumptions')
        T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
        controls=json.loads((unit/'model-controls.json').read_bytes())
        model=None
        for case in controls['results']:
            candidate=case.get('model')
            if candidate is None:continue
            try:
                evaluator=v.Denotation(typed['declarations'],candidate)
                satisfied=all(evaluator.truth(x['formal_statement']) for x in T)
                inhabited=all(evaluator.truth(x['statement']) for x in I)
            except v.VerificationFault:continue
            if satisfied and inhabited:
                if b.ir.digest(candidate)!=case['model_sha256']:raise ValueError('Selected model digest substituted')
                model=candidate;break
        if model is None:raise ValueError('No independently evaluated supplied partial T/I witness')
        local={'source_units':account['source_units'],'mapped_clauses':len(core['clauses']),**{name+'_clauses':sum(x['disposition']==name for x in core['clauses']) for name in ['encoded','explanatory','deferred']},
               'required_populations':len(I),'unresolved_populations':sum(x['requirement']=='unresolved' for x in core['populations'])}
        for key,value in local.items():counts[key]+=value
        refs += [b.ref(p) for p in [path,unit/'correspondence.json',unit/'static-ir.json',unit/'model-controls.json']]
        rows.append({'definition_id':core['source']['definition_id'],'source':core['source'],'counts':local,'draft_status':'partial','source_fidelity':'pending','whole_definition_translation':'pending','whole_definition_proof':None,'semantic_ready':False,'selected_model_sha256':b.ir.digest(model)})
        witnesses.append({'definition_id':core['source']['definition_id'],'T_clauses_satisfied':len(T),'I_populations_satisfied':len(I),'model_sha256':b.ir.digest(model),'scope':'one independently evaluated supplied model for this qualified partial theory; no shared-meaning consistency claim'})
        packets.append(packet)
    prior_counts=json.loads((b.BASE/'definitions/cal.definition.generated-output/current-inventory.json').read_bytes())['counts'];local=json.loads((b.UNIT/'denominator.json').read_bytes());expected={k:prior_counts[k]+local[k] for k in counts}
    if counts!=expected:raise ValueError('Ninety-four-draft exact incremental count drift')
    roots=[x['source'] for x in rows];graph=d.compile_graph(snapshot,roots,packets,live_root=b.ROOT)
    selection={'authority_effect':'none','snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'root_sources':roots,'packet_refs':[b.ref(p.parent/'correspondence.json') for p in existing],'cycle_policies':[],'required_edges':None}
    ids={x['definition_id'] for x in rows};current={x['definition_id'] for x in snapshot['current_entries']};missing=sorted(current-ids)
    reuse.finish();reuse_observation=reuse.report()
    report={'schema_version':'definition-assurance-current-draft-inventory/v1-candidate','authority_effect':'none','status':'PASS-for-ninety-four-partial-drafts-and-selected-independent-witnesses',
            'static_snapshot_verification_reuse':reuse_observation,'all_per_definition_T_I_models_freshly_evaluated':True,'checker_bindings':bindings,'input_refs':refs,'runtime_bindings':runtime,'current_definitions':len(current),'admitted_source_versions':len(current)+len(snapshot['historical_entries']),
            'partial_drafts':len(rows),'missing_current_drafts':missing,'counts':counts,'draft_rows':rows,'selected_model_checks':witnesses,
            'joint_declared_graph':{'nodes':len(graph['nodes']),'edges':len(graph['edges']),'missing_counterpart_packets':graph['missing_or_quarantined_interpretations'],'cycles':graph['cycle_reviews'],'edge_denominator':graph['edge_denominator']},
            'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending',
            'next_definition_priority':'F04-T.cal.definition.representation-revision','reporting_update_required':'I04 report retains its exact eight-draft selected inventory; separate scoped update needed for changing draft counts.',
            'claim_ceiling':'Exact current draft inventory and fresh evaluation of one supplied T/I model per draft. No common-carrier or meaning-aligned combined model, owner fidelity, semantic closure, native enumeration or episode completion.'}
    prior=json.loads((b.BASE/'definitions/cal.definition.generated-output/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+refs+bindings);b.r.verify(snapshot,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    if '--write' in b.sys.argv:
        for n,x in [('current-inventory.json',report),('current-dependency-selection.json',selection),('current-dependency-graph.json',graph)]:b.put(n,x)
    else:
        for n,x in [('current-inventory.json',report),('current-dependency-selection.json',selection),('current-dependency-graph.json',graph)]:
            if not b.r.same_json(json.loads((b.UNIT/n).read_bytes()),x):raise ValueError('Fresh inventory/closure differs')
    print(json.dumps({'result':report['status'],'partial_drafts':len(rows),'missing_current_drafts':len(missing),**counts,
                      'joint_graph_nodes':len(graph['nodes']),'joint_graph_edges':len(graph['edges']),'joint_missing_counterparts':len(graph['missing_or_quarantined_interpretations']),
                      'joint_unclassified_cycles':len(graph['cycle_reviews']),'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False},indent=2,sort_keys=True))
def main():
    snapshot=b.snapshot()
    with StaticSnapshotReuse(b.r,snapshot) as reuse:inventory(snapshot,reuse)
if __name__=='__main__':main()
