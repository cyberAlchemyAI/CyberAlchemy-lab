"""Read-only exact-input/unit/span/owner-pending validation of the review packet."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parent.parent;sys.path[:0]=[str(ROOT/'craft/formalization/candidates/definition-assurance-v1'),str(BASE/'units/A07'),str(BASE/'units/A04')]
import ir
import pilot_spec as p
import correspondence as cc


def bound(ref):
    raw=p.r.read_bytes(ROOT,ref['path'])
    if hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('Stale review binding: '+ref['path'])
    return raw


def load(ref):return json.loads(bound(ref))


def pointer(doc,selector):
    value=doc
    for key in selector.split('/')[1:]:
        key=key.replace('~1','/').replace('~0','~');value=value[int(key)] if isinstance(value,list) else value[key]
    return value


def main():
    packet=json.loads((BASE/'pilot-v2/fidelity-review.json').read_bytes());context=json.loads((UNIT/'context.json').read_bytes())
    for row in context['sources']:bound(row)
    if packet['schema_version']!='definition-assurance-pilot-fidelity-review/v2-candidate' or packet['authority_effect']!='none' or packet['semantic_ready'] is not False or packet['review_status']!='pending-attributable-owner-review' or packet['goal_status']!='active':raise ValueError('Review authority/readiness mismatch')
    subject=packet['review_subject']
    if ir.digest(subject)!=packet['review_subject_sha256']:raise ValueError('Review subject digest mismatch')
    for key in ['source_spec_ref','evidence_ref','semantics_contract_ref','upstream_receipt_ref','upstream_delivery_manifest_ref','required_set_ref','independent_selection_ref']:bound(subject[key])
    manifest=load(subject['upstream_delivery_manifest_ref'])
    if len(manifest['files'])!=493:raise ValueError('Prior delivery denominator changed')
    for row in manifest['files']:bound(row)
    spec=load(subject['source_spec_ref']);evidence=load(subject['evidence_ref']);source=p.bind_sources(spec,ROOT);snapshot=load(spec['snapshot_ref'])
    if packet['counts']!={'selected_definitions':7,'partial_definition_reviews':7,'whole_source_units':166,'interpretation_choices':3,'accepted_partial_owner_reviews':0,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'current_definitions_in_episode':183,'admitted_source_versions':189}:raise ValueError('Review/full-episode denominator mismatch')
    if not p.r.same_json(subject['source_refs'],spec['sources']) or not p.r.same_json(subject['source_packet_refs'],spec['source_packets']):raise ValueError('Selected source identity mismatch')
    cards=packet['definition_reviews'];units=packet['whole_source_clause_inventory'];keys={row['review_clause_key'] for row in units}
    if len(cards)!=7 or len({row['source']['definition_id'] for row in cards})!=7 or len(units)!=166 or len(keys)!=166:raise ValueError('Duplicate/omitted source or clause')
    expected_keys=set();source_checks=[]
    for item in spec['source_packets']:
        selected=item['source'];document=load({key:selected[key] for key in ['path','sha256']});original=load(item['packet_ref']);stored_check=load(item['check_ref']);replayed=cc.check(original,snapshot,required_conflicts=[row['finding_id'] for row in original['source_precedence']['conflicts']])
        if not p.r.same_json(stored_check,replayed) or not replayed['character_accounting_complete'] or replayed['semantic_ready']:raise ValueError('Source accounting changed')
        source_checks.append(replayed);card=next(row for row in cards if row['source']==selected);rule=next(row for row in spec['source_rules'] if row['source']==selected)
        if not p.r.same_json(card['partial_rule'],rule) or card['partial_rule_sha256']!=ir.digest(rule) or pointer(spec,card['partial_rule_selector'])!=rule or card['source_classification']!=document['classification'] or card['source_scope']!=document['scope']:raise ValueError('Partial meaning/classification substitution')
        owner=card['semantic_owner']
        if owner['role_ref']!=document['semantic_owner_ref'] or owner['authority_scope_ref']!=document['scope']['authority_scope_ref'] or owner['accountable_principal_ref'] is not None or owner['principal_binding_evidence_ref'] is not None or card['partial_fidelity_decision']['status']!='pending' or any(value is not None for key,value in card['partial_fidelity_decision'].items() if key!='status'):raise ValueError('Owner attribution/acceptance fabricated')
        if owner not in packet['source_reviewers'] or card['whole_definition_fidelity']!='unresolved-no-owner-accepted-translation' or not card['known_omissions_and_losses']:raise ValueError('Source owner/loss record omitted')
        by_clause={row['clause_id']:row for row in original['interpretation']['clauses']};pairs={row['clause_id']:row for row in original['correspondence']};source_units={row['unit_id']:row for row in original['source_units']};expected_card_keys=set()
        for identifier,clause in by_clause.items():
            key=selected['version_ref']+':'+identifier;expected_keys.add(key);expected_card_keys.add(key);row=next(row for row in units if row['review_clause_key']==key);pair=pairs[identifier];unit=source_units[pair['unit_id']];text=pointer(document,unit['selector'])
            if row['source']!=selected or row['source_unit']!=unit or row['source_clause']!=clause or row['packet_ref']!=item['packet_ref'] or row['retained_excerpt']!=pair['excerpt'] or row['retained_excerpt']!=text or row['end_character']!=len(text) or unit['length_characters']!=len(text) or p.r.digest(text.encode())!=unit['text_sha256']:raise ValueError('Retained source text/correspondence substitution: '+key)
            if row['fidelity_status']!='pending' or row['owner_decision'] is not None or clause['formal_statement'] is not None or clause['disposition']!='unresolved':raise ValueError('Whole clause fidelity fabricated')
        if expected_card_keys!=set(card['whole_source_clause_keys']):raise ValueError('Definition clause denominator mismatch')
        for span in rule['source_spans']:
            text=pointer(document,span['selector'])[span['start_character']:span['end_character']]
            if text!=span['excerpt'] or p.r.digest(text.encode())!=span['excerpt_sha256']:raise ValueError('Source rule-span substitution')
    if expected_keys!=keys or sum(row['source_units'] for row in source_checks)!=166:raise ValueError('Whole source accounting denominator differs')
    for decision in packet['source_precedence_decisions']:
        alternative=next(row for row in spec['interpretation_alternatives'] if row['finding_id']==decision['finding_id'])
        if alternative!=decision['exact_candidate_alternative'] or pointer(spec,decision['candidate_selector'])!=alternative or ir.digest(alternative)!=decision['candidate_alternative_sha256']:raise ValueError('Interpretation alternative changed')
        if decision['selected_option'] is not None or decision['owner_disposition']!='pending' or decision['owner_review_evidence_ref'] is not None or decision['agent_recommendation_is_owner_decision'] is not False:raise ValueError('Recommendation became owner approval')
    if {row['finding_id'] for row in packet['source_precedence_decisions']}!={row['finding_id'] for row in spec['interpretation_alternatives']}:raise ValueError('Interpretation choice missing')
    coupling=packet['selected_coupling']
    if coupling['exact_candidate']!=spec['selected_coupling'] or pointer(spec,coupling['candidate_selector'])!=spec['selected_coupling'] or coupling['candidate_sha256']!=ir.digest(spec['selected_coupling']) or coupling['owner_fidelity_status']!='pending' or coupling['owner_decision'] is not None or coupling['owner_evidence_ref'] is not None:raise ValueError('Coupling substitution/owner approval fabricated')
    if packet['conditional_assumptions']!=spec['conditional_assumptions'] or packet['candidate_logical_rules']!=spec['logical_rules'] or packet['candidate_record_types']!=spec['record_types'] or packet['dependency_closure']!=spec['dependencies']:raise ValueError('Candidate assumptions/type/rule/closure loss')
    if packet['logical_evidence_summary']['logical_results']!=evidence['logical_results'] or packet['shared_code_and_execution_trust']!=evidence['trust_assumptions'] or packet['administrative_and_semantic_gates']!=evidence['administrative_and_semantic_gates']:raise ValueError('Evidence/trust/gate substitution')
    if packet['semantic_admission']['status']!='not-requested-by-this-fidelity-packet' or packet['semantic_admission']['admission_decision_ref'] is not None or packet['semantic_admission']['owner_evidence_ref'] is not None or packet['semantic_admission']['authority_effect']!='none':raise ValueError('Semantic admission fabricated')
    if not packet['review_response_contract']['separate_semantic_admission'] or 'new absent candidate iteration' not in packet['review_response_contract']['rejection_route']:raise ValueError('Revision/admission boundary lost')
    if packet['review_subject_sha256'] not in (UNIT/'OWNER-REVIEW.md').read_text():raise ValueError('Human review lacks exact subject digest')
    print(json.dumps({'result':'PASS-for-exact-pending-review-packet','authority_effect':'none','semantic_ready':False,'review_subject_sha256':packet['review_subject_sha256'],'selected_sources':7,'source_units':166,'partial_review_cards':7,'interpretation_choices':3,'exact_source_spans':sum(len(row['partial_rule']['source_spans']) for row in cards),'pending_gates':11,'logical_existential_results_presented':11,'source_binding':source,'prior_candidate_files_preserved':493,'owner_review_status':'pending','owner_accepted_partial_reviews':0,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'goal_status':'active'},indent=2,sort_keys=True))


if __name__=='__main__':main()
