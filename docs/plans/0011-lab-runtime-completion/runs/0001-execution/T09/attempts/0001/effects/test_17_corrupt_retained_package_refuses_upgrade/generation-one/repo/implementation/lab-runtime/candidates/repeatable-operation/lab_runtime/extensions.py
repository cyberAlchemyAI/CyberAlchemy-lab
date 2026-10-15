"""Closed typed-extension inspection. Candidate readiness never admits a pair."""
from __future__ import annotations
import copy
from itertools import product
import json
from jsonschema import Draft202012Validator
from .common import RuntimeFault, byte_digest, digest, loads, pointer, require


def check_closed_domain(schema, *, budget=10000):
    """Enumerate bounded qualifier values and enforce every schema constraint."""
    def forbid_open_keywords(node):
        if isinstance(node,dict):
            require(not any(k in node for k in ['$ref','$dynamicRef','patternProperties']),'qualifier references and patterned property names require prior explicit closure')
            for value in node.values():forbid_open_keywords(value)
        elif isinstance(node,list):
            for value in node:forbid_open_keywords(value)
    forbid_open_keywords(schema)
    Draft202012Validator.check_schema(schema)
    def values(s):
        require(isinstance(s,dict), 'qualifier schema must be an object')
        require('$ref' not in s and '$dynamicRef' not in s, 'qualifier references must be resolved before closure inspection')
        if 'const' in s:
            return [copy.deepcopy(s['const'])]
        if 'enum' in s:
            require(s['enum'] and len(s['enum'])<=budget, 'empty or oversized qualifier domain')
            return copy.deepcopy(s['enum'])
        if s.get('type')=='object':
            require(s.get('additionalProperties') is False, 'qualifier property names are not closed')
            properties=s.get('properties',{});required=s.get('required',[])
            require(set(required)<=set(properties), 'required qualifier undeclared')
            keys=sorted(properties);missing=object()
            domains=[values(properties[k]) + ([missing] if k not in required else []) for k in keys]
            count=1
            for domain in domains:
                count*=len(domain)
                require(count<=budget, 'qualifier domain enumeration budget exceeded')
            return [{k:v for k,v in zip(keys,row) if v is not missing} for row in product(*domains)]
        # Free strings/numbers, unconstrained arrays and broad unions are not domains.
        require(False, 'qualifier values require explicit finite enum/const domains')
    candidates=values(schema)
    validator=Draft202012Validator(schema)
    accepted=[v for v in candidates if validator.is_valid(v)]
    require(accepted, 'qualifier constraints make the entire pair unusable')
    return {'candidate_values':len(candidates),'allowed_values':len(accepted),'allowed_values_digest':digest(accepted)}


def inspect_extension(proposal, *, current_relations, endpoint_contracts, evidence_bytes):
    """Prepare a bounded semantic review from exact already-resolved inputs.

    These inputs come from the trusted profile resolver, never caller-authored
    effective-state labels. Wire request/profile binding belongs to API integration.
    This function returns no admission, instance validation or operation permission.
    """
    fields={'schema_version','authority_effect','proposal_ref','scope','ontology_contract_ref','mode','relation_kind_ref','predecessor_version_ref','successor_version_ref','unique_question','axis_ref','allowed_endpoint_pairs','source_kinds','target_kinds','noncollapse_report_binding','owner_ref','contestability_binding','lifecycle_effect','validation_effect','effect_rule'}
    require(set(proposal)==fields and proposal['schema_version']=='lab-closed-extension-proposal/v1-candidate','extension proposal envelope must be closed')
    require(proposal['authority_effect']=='none' and proposal['effect_rule']=='candidate-only; no pair availability or instance admission','extension proposal grants no authority')
    require(proposal['scope'] in ['global','ontology-local'],'connection scope required')
    require((proposal['ontology_contract_ref'] is not None)==(proposal['scope']=='ontology-local'),'local extension must bind exactly one ontology contract')
    require(proposal['mode'] in ['reuse','distinct-kind'],'explicit reuse or distinct-kind mode required')
    require(all(isinstance(proposal[k],str) and proposal[k] for k in ['proposal_ref','relation_kind_ref','successor_version_ref','unique_question','axis_ref','owner_ref','lifecycle_effect','validation_effect']),'extension metadata incomplete')
    require(proposal['successor_version_ref']!=proposal['predecessor_version_ref'],'successor revision must be distinct')
    def evidence(binding):
        require(set(binding)=={'ref','sha256'},'closed evidence binding required')
        require(binding['ref'] in evidence_bytes,'exact extension evidence unavailable')
        raw=evidence_bytes[binding['ref']]
        require(isinstance(raw,bytes) and len(raw)<=8*1024*1024 and byte_digest(raw)==binding['sha256'],'extension evidence byte binding mismatch or 8 MiB limit exceeded')
        return loads(raw)
    report=evidence(proposal['noncollapse_report_binding'])
    require(set(report)=={'schema_version','proposal_ref','question','axis_ref','comparisons','posture','authority_effect'},'noncollapse report must be closed')
    require(report['schema_version']=='lab-extension-noncollapse-review/v1-candidate' and report['proposal_ref']==proposal['proposal_ref'] and report['question']==proposal['unique_question'] and report['axis_ref']==proposal['axis_ref'],'noncollapse report does not bind this question and axis')
    require(report['posture']=='candidate-reasoning-for-owner-review' and report['authority_effect']=='none','candidate reasoning is not an owner outcome')
    comparisons=report['comparisons'];require(isinstance(comparisons,list),'actual comparison rows required')
    expected=set(current_relations)
    require({r['relation_kind_ref'] for r in comparisons}==expected and len(comparisons)==len(expected),'noncollapse evidence must compare the complete selected effective kind inventory')
    for row in comparisons:
        require(set(row)=={'relation_kind_ref','existing_version_ref','existing_question','difference','evidence_binding'},'noncollapse comparison must be closed')
        old=current_relations[row['relation_kind_ref']]
        require(row['existing_version_ref']==old['version_ref'] and row['existing_question']==old['unique_question'],'comparison predecessor mismatch')
        require(isinstance(row['difference'],str) and len(row['difference'].strip())>=20,'actual semantic comparison reasoning required')
        evidence(row['evidence_binding'])
    contest=evidence(proposal['contestability_binding'])
    require(set(contest)=={'owner_ref','challenge_route','covered_subjects','authority_effect'},'contestability evidence must be closed')
    require(contest['owner_ref']==proposal['owner_ref'] and contest['challenge_route'] and contest['authority_effect']=='none','contestability owner/route/effect mismatch')
    require(set(contest['covered_subjects'])=={'relation-kind','endpoint-pair','qualifiers','source-endpoint','target-endpoint','relation-instance'},'contestability must cover all connection subjects')
    old=current_relations.get(proposal['relation_kind_ref'])
    if proposal['mode']=='reuse':
        require(old is not None and old['effective_state']=='admitted-current','effective admitted predecessor unavailable')
        require(old['version_ref']==proposal['predecessor_version_ref'],'effective predecessor version mismatch')
        require(old['unique_question']==proposal['unique_question'] and old['axis_ref']==proposal['axis_ref'],'reuse changes unique question or typed axis; propose a distinct kind')
    else:
        require(old is None and proposal['predecessor_version_ref'] is None,'distinct kind cannot replace an existing identity')
        require(all(r['unique_question']!=proposal['unique_question'] for r in current_relations.values()),'distinct kind duplicates an existing unique question')
    pairs=proposal['allowed_endpoint_pairs'];require(isinstance(pairs,list) and 0 < len(pairs) <= 1000,'exact ordered connection set required within 1000-pair budget')
    seen=set();results=[];pending=set()
    for pair in pairs:
        required={'source_kind','target_kind','source_contract_ref','target_contract_ref','source_role','target_role','qualifier_schema_binding','cross_constraints_binding','canonical_authority','projection_binding'}
        require(set(pair)==required,'exact pair contract must be closed')
        key=(pair['source_kind'],pair['target_kind']);require(key not in seen,'duplicate endpoint pair');seen.add(key)
        require(all(isinstance(v,str) and v and v not in ['*','any','subject','artifact','object'] for v in key),'wildcard/catch-all global endpoint forbidden')
        require(pair['source_role'] and pair['target_role'],'directional endpoint roles required')
        for direction in ['source','target']:
            ref=pair[direction+'_contract_ref'];require(ref in endpoint_contracts,'endpoint contract unresolved')
            contract=endpoint_contracts[ref]
            require(contract['kind']==pair[direction+'_kind'],'endpoint contract kind mismatch')
            require(contract['scope'] in ['carrier','explicit-governed-internal-record'],'endpoint must be a carrier or explicitly governed internal record')
            if contract['scope']=='explicit-governed-internal-record':
                require(contract.get('permitted_relation_kind_ref')==proposal['relation_kind_ref'],'internal record contract not explicitly permitted by this Relation Kind')
            evidence(contract['evidence_binding'])
            if contract['effective_state']!='admitted-current':
                require(contract['effective_state']=='candidate-for-R08','endpoint not eligible even for candidate review')
                pending.add(ref)
        schema=evidence(pair['qualifier_schema_binding']);closure=check_closed_domain(schema)
        if old is not None and 'qualifier_contract' in old and key in {tuple(p) for p in old['allowed_endpoint_pairs']}:
            prior=old['qualifier_contract']
            require(set(prior['required_axes'])<=set(schema.get('required',[])),'predecessor qualifier axes removed')
            compatible=copy.deepcopy(schema)
            compatible.setdefault('allOf',[]).append({'type':'object','properties':prior['properties'],'required':prior['required_axes']})
            require(check_closed_domain(compatible)['allowed_values']==closure['allowed_values'],'successor qualifier values violate predecessor contract')
        constraints=evidence(pair['cross_constraints_binding'])
        require(constraints=={'schema_binding':pair['qualifier_schema_binding'],'constraints':['all JSON Schema constraints in the exact bound qualifier schema'],'authority_effect':'none'},'cross-qualifier constraints must bind the exact enforced schema')
        canonical=pair['canonical_authority']
        require(canonical in ['typed-relation','specialized-carrier'],'exactly one writable relation authority required')
        if canonical=='typed-relation': require(pair['projection_binding'] is None,'generic canonical authority cannot carry a second writable projection')
        else:
            projection=evidence(pair['projection_binding'])
            require(set(projection)=={'specialized_carrier_ref','projection_carrier_ref','projection_mode','writable_authority','authority_effect'},'specialized projection mapping must be closed')
            require(projection['specialized_carrier_ref'] in endpoint_contracts and projection['projection_carrier_ref']=='cal.artifact-type.typed-relation/v3' and projection['projection_mode']=='digest-bound-read-only' and projection['writable_authority']=='specialized-carrier' and projection['authority_effect']=='none','dual writable authority or unbound specialized projection')
            specialized=endpoint_contracts[projection['specialized_carrier_ref']]
            require('relation_authority_contract_binding' in specialized,'specialized carrier has no explicit canonical relation authority contract')
            mapping=evidence(specialized['relation_authority_contract_binding'])
            require(mapping=={**projection,'source_kind':key[0],'target_kind':key[1]},'specialized authority contract does not bind this exact pair')
            if specialized['effective_state']!='admitted-current':
                require(specialized['effective_state']=='candidate-for-R08','specialized canonical carrier unavailable')
                pending.add(projection['specialized_carrier_ref'])
        results.append({'source_kind':key[0],'target_kind':key[1],'qualifier_closure':closure,'canonical_authority':canonical})
    require(set(proposal['source_kinds'])=={x[0] for x in seen} and len(proposal['source_kinds'])==len(set(proposal['source_kinds'])),'source-kind projection differs from exact ordered pair set')
    require(set(proposal['target_kinds'])=={x[1] for x in seen} and len(proposal['target_kinds'])==len(set(proposal['target_kinds'])),'target-kind projection differs from exact ordered pair set')
    if old is not None:
        require(set(tuple(p) for p in old['allowed_endpoint_pairs'])<=seen,'endpoint extension removes predecessor connections')
    return {'schema_version':'lab-extension-inspection/v1-candidate','proposal_ref':proposal['proposal_ref'],'proposal_digest':digest(proposal),'scope':proposal['scope'],'review_posture':'structural-review-ready; semantic owner outcome required','pair_results':results,'pending_endpoint_admission_refs':sorted(pending),'semantic_verdict':'not-issued-by-validator','owner_checkpoint':'R08','globally_available_pairs_added':0,'relation_instances_created':0,'authority_effect':'none','registration_effect':'none'}


def inspect_bound_extension(proposal, *, snapshot, expected_profile_sha256,
                            expected_snapshot_digest, candidate_endpoint_contracts,
                            evidence_bytes):
    """Resolve effective inputs from an independently pinned C04 source snapshot."""
    import base64
    from .sources import verify_snapshot
    verify_snapshot(snapshot, expected_profile_sha256=expected_profile_sha256)
    require(snapshot['snapshot_digest']==expected_snapshot_digest,'independent semantic snapshot pin mismatch')
    actual_evidence=dict(evidence_bytes)
    for path,raw in snapshot['byte_contents'].items():
        captured=base64.b64decode(raw,validate=True)
        require(path not in actual_evidence or actual_evidence[path]==captured,'candidate evidence cannot replace captured canonical bytes')
        actual_evidence[path]=captured
    subjects=snapshot['subjects']
    relations={}
    for ref,record in snapshot['relation_contracts'].items():
        entries=[e for e in subjects.values() if e['category']=='relation-kind' and e['record']['payload']['relation_kind_id']==ref and e['effective_state']=='admitted-current']
        require(len(entries)==1,'effective Relation Kind predecessor ambiguous or unavailable')
        entry=entries[0]
        require(entry['record']==record,'effective Relation Kind record disagrees with source capture')
        payload=record['payload']
        relations[ref]={'version_ref':entry['version_ref'],'effective_state':entry['effective_state'],'unique_question':payload['unique_question'],'axis_ref':payload['axis_id'],'allowed_endpoint_pairs':[(p['source_kind'],p['target_kind']) for p in payload['allowed_endpoint_pairs']],'qualifier_contract':payload['qualifier_contract']}
    endpoints={}
    for ref,c in snapshot['contracts'].items():
        if c['lifecycle_state']!='admitted-current':continue
        path=c['schema_path']
        endpoints[ref]={'kind':c['semantic_kind'],'scope':'carrier','effective_state':'admitted-current','evidence_binding':{'ref':path,'sha256':snapshot['materials'][path]}}
    for ref,c in candidate_endpoint_contracts.items():
        require(ref not in endpoints,'candidate endpoint cannot shadow current admitted contract')
        require(c['effective_state']=='candidate-for-R08','candidate endpoint cannot assert admission')
        endpoints[ref]=c
    return inspect_extension(proposal,current_relations=relations,endpoint_contracts=endpoints,evidence_bytes=actual_evidence)
