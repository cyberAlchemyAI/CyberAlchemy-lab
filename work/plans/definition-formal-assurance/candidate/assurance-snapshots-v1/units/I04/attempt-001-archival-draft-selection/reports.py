"""Read-only, byte-selected coverage. Drafts and projections confer no readiness."""
import importlib.util
import json
from pathlib import Path
import contracts as c
import ir
import resolver as r

BASE = 'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
MAX_MANIFEST_FILES = 10000

class ReportFault(ValueError):
    def __init__(self, code, path=''): self.code=code; self.path=path

def require(condition, code, path=''):
    if not condition: raise ReportFault(code,path)

def reference(root, path):
    return {'path':path,'sha256':r.digest(r.read_bytes(root,path))}

def load(root, ref):
    require(type(ref) is dict and set(ref)=={'path','sha256'},'malformed-reference')
    require(type(ref['sha256']) is str and len(ref['sha256'])==64 and all(x in '0123456789abcdef' for x in ref['sha256']),'malformed-reference-digest')
    raw=r.read_bytes(root,ref['path'])
    require(r.digest(raw)==ref['sha256'],'stale-selected-input',ref['path'])
    return r.parse(raw,ref['path'])

def manifest_inventory(root, ref):
    manifest=load(root,ref)
    require(type(manifest) is dict and set(manifest)=={'schema_version','authority_effect','files','claim_ceiling'},'malformed-delivery-manifest')
    require(manifest['schema_version']=='definition-assurance-delivery-manifest/v1-candidate' and manifest['authority_effect']=='none','invalid-delivery-boundary')
    require(type(manifest['files']) is list and len(manifest['files'])<=MAX_MANIFEST_FILES,'manifest-file-limit')
    selected={}
    for item in manifest['files']:
        require(type(item) is dict and set(item)=={'path','sha256'},'malformed-manifest-row')
        require(item['path'] not in selected,'duplicate-manifest-path',item['path'])
        # Bind bytes without assuming all captured objects are JSON.
        r.components(item['path']); raw=r.read_bytes(root,item['path'])
        require(r.digest(raw)==item['sha256'],'stale-manifest-file',item['path'])
        selected[item['path']]=item
    return selected

def coverage(root, snapshot_ref, delivery_ref):
    root=r.resolve_root(root); snapshot=load(root,snapshot_ref); r.verify(snapshot,root)
    selected=manifest_inventory(root,delivery_ref); reads={snapshot_ref['path']:snapshot_ref,delivery_ref['path']:delivery_ref}
    def bound(path):
        require(path in selected,'missing-selected-report-input',path)
        reads[path]=selected[path]; return load(root,selected[path])
    require(snapshot_ref['path'] in selected and r.same_json(selected[snapshot_ref['path']],snapshot_ref),'snapshot-outside-selected-manifest')
    current={x['definition_id']:{k:x[k] for k in ['definition_id','version_ref','path','sha256']} for x in snapshot['current_entries']}
    require(len(current)==len(snapshot['current_entries']),'duplicate-current-identity')
    counterpart_path=BASE+'/units/A04/correspondence.py'
    require(counterpart_path in selected,'missing-correspondence-checker')
    spec=importlib.util.spec_from_file_location('candidate_report_correspondence',root/counterpart_path)
    co=importlib.util.module_from_spec(spec);spec.loader.exec_module(co)
    rows=[];totals={k:0 for k in ['source_units','mapped_clauses','encoded_clauses','explanatory_clauses','deferred_clauses','required_populations','unresolved_populations','selected_assumptions']}
    premises=[];remaining=[]
    draft_paths={p for p in selected if p.startswith(BASE+'/definitions/') and p.endswith('/t.json')}
    expected_draft_paths={BASE+'/definitions/'+identity+'/t.json' for identity in current}
    require(draft_paths<=expected_draft_paths,'noncurrent-definition-draft-in-report-selection')
    for identity,source in sorted(current.items()):
        prefix=BASE+'/definitions/'+identity+'/'
        row={'definition_id':identity,'source':source,'draft_status':'missing','whole_translation':'pending',
             'owner_fidelity':'pending','whole_definition_proof':None,'semantic_ready':False}
        if prefix+'t.json' not in selected:
            remaining.append(identity);rows.append(row);continue
        envelope=bound(prefix+'t.json');valid=c.validate(envelope,'interpretation')
        require(valid['status']=='structurally-valid','invalid-interpretation',prefix+'t.json')
        core=envelope['payload'];require(r.same_json(core['source'],source),'draft-source-substitution',identity)
        packet=bound(prefix+'correspondence.json');require(r.same_json(packet['interpretation'],core),'packet-core-substitution',identity)
        account=co.check(packet,snapshot);require(account['character_accounting_complete'] is True,'incomplete-source-accounting',identity)
        typed=bound(prefix+'static-ir.json');ir.verify_ir(typed)
        require(r.same_json(typed,ir.compile_interpretation(core,snapshot)),'draft-ir-substitution',identity)
        receipt=bound(prefix+'receipt.json');cover=bound(prefix+'coverage-row.json')
        require(receipt['authority_effect']=='none' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False
                and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending','unsupported-whole-acceptance',identity)
        require(r.same_json(cover['source'],source) and cover['semantic_ready'] is False,'coverage-source-or-status-substitution',identity)
        for key,name in [('interpretation_ref','t.json'),('correspondence_ref','correspondence.json'),('static_ir_ref','static-ir.json')]:
            require(r.same_json(cover[key],selected[prefix+name]),'coverage-reference-substitution',identity)
        disposition={k:sum(x['disposition']==k for x in core['clauses']) for k in ['encoded','explanatory','deferred']}
        counts={'source_units':account['source_units'],'mapped_clauses':len(core['clauses']),
                **{k+'_clauses':n for k,n in disposition.items()},
                'required_populations':sum(x['requirement']=='required' for x in core['populations']),
                'unresolved_populations':sum(x['requirement']=='unresolved' for x in core['populations']),
                'selected_assumptions':len(core['assumptions'])}
        for k,n in counts.items():totals[k]+=n
        premises.extend({'definition_id':identity,'assumption':x} for x in core['assumptions'])
        row.update({'draft_status':'source-accounted-typed-partial','counts':counts,
                    'interpretation_ref':selected[prefix+'t.json'],'correspondence_ref':selected[prefix+'correspondence.json'],
                    'review_ref':cover['review_ref'],'deferred_clause_ids':[x['clause_id'] for x in core['clauses'] if x['disposition']=='deferred'],
                    'unresolved_population_ids':[x['population_id'] for x in core['populations'] if x['requirement']=='unresolved'],
                    'pending_findings':[x['finding_id'] for x in packet['source_precedence']['conflicts']],
                    'dependency_closure':packet['dependency_closure']['status']})
        rows.append(row)
    projection_summary=bound(BASE+'/units/I03/worked-summary.json');projection_cases=[];projection_ids=None;failures=[]
    for case,details in sorted(projection_summary['cases'].items()):
        for ref in [details['selection_ref'],details['output_ref']]:
            require(r.same_json(selected.get(ref['path']),ref),'projection-reference-outside-manifest',ref['path'])
        selection=bound(details['selection_ref']['path']);result=bound(details['output_ref']['path']);ids=[]
        for ref in selection['input_ir_refs']:
            require(r.same_json(selected.get(ref['path']),ref),'projection-ir-outside-manifest',ref['path'])
            typed=bound(ref['path']);ir.verify_ir(typed);source=typed['source']
            require(r.same_json(current.get(source['definition_id']),source),'projection-source-substitution',source['definition_id']);ids.append(source['definition_id'])
        require(len(ids)==len(set(ids)),'duplicate-projection-source')
        ids=sorted(ids)
        if projection_ids is None:projection_ids=ids
        require(ids==projection_ids,'projection-cases-source-denominator-mismatch')
        cov=result['coverage'];missing=sorted(set(current)-set(ids))
        require(cov['global_current_source_nodes']==len(current) and cov['selected_logical_sources']==len(ids)
                and cov['missing_current_interpretations']==missing,'projection-coverage-denominator-substitution')
        require(result['semantic_ready'] is False and result['mechanized_proof'] is False,'projection-promoted-to-whole-proof')
        observations=[{'obligation_id':x['obligation_id'],'status':x['status'],'native_status':x.get('native_status')}
                      for x in result['results'] if x['status']!='checked-model-witness']
        # Keep the established checker status labels, including bounded failure.
        failures.extend({'case':case,**x} for x in details['failed_or_unresolved_queries'])
        projection_cases.append({'case':case,'recorded_status':result['status'],'query_count':len(result['results']),
                                 'recorded_failed_or_unresolved':details['failed_or_unresolved_queries'],
                                 'query_statuses':observations,'pending_source_clauses':cov['pending_source_clauses'],
                                 'assumption_accounts':result['assumption_accounts'],'result_ref':details['output_ref']})
    foundation=bound(BASE+'/definitions/cal.definition.semantic-primitive/foundation-draft-review.json')
    require(foundation['counts']=={k:totals[k] for k in foundation['counts']},'foundation-coverage-denominator-mismatch')
    draft_ids=sorted(x['definition_id'] for x in rows if x['draft_status']!='missing')
    union=sorted(set(draft_ids)|set(projection_ids or []))
    report={'schema_version':'definition-assurance-coverage-report/v1-candidate','authority_effect':'none',
            'status':'candidate-coverage-inspected','semantic_ready':False,'goal_status':'active',
            'source_currentness':'exact-selected-live-local-bytes','current_definitions':len(current),
            'admitted_source_versions':len(current)+len(snapshot['historical_entries']),
            'per_definition_partial_drafts':len(draft_ids),'owner_accepted_whole_translations':0,'whole_definition_proofs':0,
            'whole_definition_missing_drafts':remaining,'whole_definition_rows':rows,'foundation_counts':totals,
            'selected_premises':premises,'remaining_premise_review':'Assumption selection and deferred/normative/temporal premises require owner review; no missing premise is supplied automatically.',
            'projection':{'identity_count':len(projection_ids or []),'identities':projection_ids or [],'cases':projection_cases,
                          'missing_projection_identities':sorted(set(current)-set(projection_ids or [])),
                          'whole_definition_credit':0,'evidence_scope':'Recorded finite seven-source projection results; no fresh provider execution or model verification in report.'},
            'identities_with_either_partial_draft_or_projection':union,'union_is_whole_translation_coverage':False,
            'recorded_failures_or_unresolved_queries':failures,
            'foundation_obligations':{'family_result':foundation['F01_T_family_result'],'joint_exit':foundation['F01_joint_review_exit'],
                                      'missing_counterpart_packets':foundation['missing_counterpart_packets'],'unresolved_cycles':foundation['unresolved_cycles']},
            'next_unit':{'candidate':'I05.1','prerequisites':['I04','A10'],'readiness':'Consult DAG and closing receipts; report does not discharge prerequisite tasks.'},
            'delivery_ref':delivery_ref,'selected_input_refs':sorted(reads.values(),key=lambda x:x['path']),
            'manifest_file_count':len(selected),'claim_ceiling':'Verified selected bytes, source accounting and typing plus recorded projection outcomes. No fresh solver/model run, accepted source fidelity, semantic closure, aligned whole-source consistency or episode completion.'}
    # Closing checks catch source, manifest, selected-input or selection-file changes.
    for ref in reads.values():load(root,ref)
    manifest_inventory(root,delivery_ref);r.verify(snapshot,root)
    return report

def human(value):
    if value.get('schema_version')!='definition-assurance-coverage-report/v1-candidate':
        return json.dumps(value,indent=2,sort_keys=True,allow_nan=False)
    lines=['Candidate formalization coverage',f"Current definitions: {value['current_definitions']}; admitted source versions: {value['admitted_source_versions']}",
           f"Partial definition drafts: {value['per_definition_partial_drafts']}; missing drafts: {len(value['whole_definition_missing_drafts'])}",
           f"Owner-accepted whole translations: {value['owner_accepted_whole_translations']}; whole-definition proofs: {value['whole_definition_proofs']}",
           'Semantic readiness: false; full episode remains incomplete.',
           f"Separate finite projection: {value['projection']['identity_count']} identities; whole-definition credit: 0.",
           f"Recorded failed/unresolved projection queries: {len(value['recorded_failures_or_unresolved_queries'])}",
           '','Definition | Draft | Encoded | Deferred | Required populations | Unresolved populations']
    for row in value['whole_definition_rows']:
        n=row.get('counts',{});lines.append(' | '.join(str(x) for x in [row['definition_id'],row['draft_status'],n.get('encoded_clauses','—'),n.get('deferred_clauses','—'),n.get('required_populations','—'),n.get('unresolved_populations','—')]))
    lines.extend(['','Remaining premises: '+value['remaining_premise_review'],
                  'Next candidate unit: '+value['next_unit']['candidate']+'; '+value['next_unit']['readiness'],value['claim_ceiling']])
    return '\n'.join(lines)
