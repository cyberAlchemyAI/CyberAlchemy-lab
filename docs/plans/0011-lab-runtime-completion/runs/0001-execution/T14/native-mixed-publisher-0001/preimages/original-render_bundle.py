def render_bundle(prepared, response, authority):
    """Deterministic actual carrier postimages; stable cores exclude these hashes."""
    review = prepared['review']; verify_response(response, review, authority); verify_generator(review)
    validate = list(Draft202012Validator(load(SCHEMA)).iter_errors(review))
    require(not validate, 'invalid promotion review: ' + '; '.join(e.message for e in validate[:3]))
    files = dict(prepared['materials'])
    require(review['material_sha256s'] == {p:byte_digest(raw) for p,raw in files.items()}, 'reviewed material closure changed')
    context = loads(files['validation/context.json']); identities = loads(files['validation/identities.json'])
    root = authority.bundle_path; token = authority.bundle_id
    db = 'decision-bundle:' + token; cp = 'decision-checkpoint:' + token
    boundary = 'authority-boundary:' + token; txid = 'admission-transaction:' + token
    receipt_ref = root + '/receipts/application.json'; auth_path = root + '/authorization.json'
    cores = review['independent_cores']; core_refs = [c['decision_ref'] for c in cores]
    records, decisions, scopes = {}, [], []
    for i,c in enumerate(cores):
        files[f'decision-cores/{i:04d}.json'] = encoded(c)
        dsid = 'decision-scope:' + token + ':' + str(i)
        d = _record(context, authority, 'decision', c['decision_ref'], 'Exact repository ' + c['effect_kind'])
        d.update(owner_ref=c['owner_ref'])
        d['payload'].update(decision_maker_ref=authority.principal_ref, declared_effect_refs=[c['effect_kind']],
            evidence_basis_refs=[auth_path], selected_outcome=c['selected_outcome'], subject_refs=[c['target_ref']])
        d['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'source', 'counterpart_kind': 'decision-bundle', 'counterpart_ref': db}]
        scope = _record(context, authority, 'decision-scope', dsid, 'Exact independent repository Decision scope')
        scope.update(owner_ref=c['owner_ref']); scope['payload'].update(permitted_effects=[c['effect_kind']],
            subject_kind_refs=[review['targets'][i]['kind']], subject_refs=[c['target_ref']],
            excluded_effects=['runtime-activation', 'service-start', 'external-publication', 'deployment'])
        scope['relation_refs'] = [{'relation_kind_ref': 'relation.scopes-authority-over', 'direction': 'target', 'counterpart_kind': 'authority-boundary', 'counterpart_ref': boundary}]
        records[f'instances/governance/decision-{i:04d}.json'] = d
        records[f'instances/governance/decision-scope-{i:04d}.json'] = scope
        decisions.append(d); scopes.append(scope)
    b = _record(context, authority, 'authority-boundary', boundary, 'Independently authorized repository boundary')
    b['payload'].update(accountable_principal_ref=authority.principal_ref, owner_role_ref='role:repository-owner',
        authority_scope_ref=authority.scope_ref, allowed_effect_kinds=[c['effect_kind'] for c in cores],
        challenge_route_ref=authority.challenge_route, effective_period='exact-review:' + digest(review))
    b['relation_refs'] = [{'relation_kind_ref': 'relation.scopes-authority-over', 'direction': 'source', 'counterpart_kind': 'decision-scope', 'counterpart_ref': s['node_id']} for s in scopes]
    records['instances/governance/authority-boundary.json'] = b
    bundle = _record(context, authority, 'decision-bundle', db, 'One response covering independent repository Decisions')
    bundle['payload'].update(bundle_digest=digest(cores), checkpoint_ref=cp, all_targets_materialized=True,
        ordered_decisions=[{'decision_ref': c['decision_ref'], 'decision_core_sha256': byte_digest(encoded(c)),
            'owner_ref': c['owner_ref'], 'scope_ref': scopes[i]['node_id'], 'effect_kind': c['effect_kind'],
            'selected_outcome': c['selected_outcome'], 'target_refs': [c['target_ref']],
            'target_digests': [{'target_ref': c['target_ref'], 'sha256': c['target_sha256']}]} for i,c in enumerate(cores)])
    bundle['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'target', 'counterpart_kind': 'decision', 'counterpart_ref': d['node_id']} for d in decisions]
    records['instances/governance/decision-bundle.json'] = bundle
    checkpoint = _record(context, authority, 'decision-checkpoint', cp, 'Resolved exact repository owner response')
    checkpoint['payload'].update(decision_bundle_ref=db, workflow_instance_ref='repository-promotion:' + token,
        workflow_profile_ref='candidate-profile:exact-repository-publication/v1', resolved_preference_ref=None,
        opened_at=response['approved_at'], closed_at=response['approved_at'])
    records['instances/governance/decision-checkpoint.json'] = checkpoint
    old_state = context['state']; stateid = 'project-state:' + token
    state = _record(context, authority, 'project-state', stateid, 'Project State after exact repository transaction')
    state['payload'].update(cursor='repository-admission:' + token,
        decision_refs=list(dict.fromkeys(old_state['payload']['decision_refs'] + core_refs)),
        artifact_refs=list(dict.fromkeys(old_state['payload']['artifact_refs'] + [root + '/' + t['record_path'] for t in review['targets']])),
        state_digest='sha256:' + digest({'predecessor': old_state['payload']['state_digest'], 'review': digest(review), 'cores': review['core_sha256s']}))
    state['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'source', 'counterpart_kind': 'project', 'counterpart_ref': state['payload']['project_ref']},
        {'relation_kind_ref': 'relation.successor-of', 'direction': 'source', 'counterpart_kind': 'project-state', 'counterpart_ref': old_state['node_id']},
        {'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
    records['instances/project-state.json'] = state
    history = copy.deepcopy(context['histories'])
    sem = history['project-semantic-event-history']['payload']; gov = history['project-governance-event-history']['payload']
    cursor = len(sem['events']) + 1; g_cursor = len(gov['events']) + 1
    event = {'event_id': 'project-semantic-event:' + token, 'cursor': cursor,
        'previous_event_digest': sem['events'][-1]['event_digest'], 'change_kind': 'exact-repository-promotion',
        'predecessor_state_ref': old_state['node_id'], 'predecessor_state_digest': old_state['payload']['state_digest'],
        'resulting_state_ref': stateid, 'resulting_state_digest': state['payload']['state_digest'],
        'material_refs': [{'path': root + '/' + t['record_path'], 'sha256': t['record_sha256']} for t in review['targets']],
        'record_ref': root + '/review.json', 'semantic_summary': 'Exact independently reviewed repository target effects; no runtime activation.'}
    event['event_digest'] = digest(event)
    governance_event = {'event_id': 'project-governance-event:' + token, 'governance_cursor': g_cursor,
        'previous_event_digest': gov['events'][-1]['event_digest'],
        'semantic_event_ref': {'semantic_event_id': event['event_id'], 'semantic_event_digest': event['event_digest'], 'semantic_cursor': cursor},
        'decision_ref': db, 'authorization_ref': auth_path, 'authorization_sha256': byte_digest(encoded(response)),
        'policy_ref': authority.policy_ref, 'challenge_contract_ref': authority.challenge_route,
        'upstream_governance_evidence_refs': core_refs, 'record_ref': root + '/review.json',
        'governance_summary': 'One separate exact repository owner response for independent stable cores.'}
    governance_event['event_digest'] = digest(governance_event)
    for kind, e, watermark in [('project-semantic-event-history', event, 'latest_cursor'), ('project-governance-event-history', governance_event, 'latest_governance_cursor')]:
        files['prior/' + kind + '.json'] = encoded(context['histories'][kind])
        h = history[kind]; h.update(owner_ref='role:repository-owner', scope_ref=authority.scope_ref, evidence_refs=[auth_path], claim_ceiling=authority.claim_ceiling)
        h['payload']['events'].append(e); h['payload'][watermark] = len(h['payload']['events'])
        h['payload']['chain_digest'] = digest([x['event_digest'] for x in h['payload']['events']])
        h['relation_refs'] = [{'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
        records['instances/' + kind + '.json'] = h
    files['prior/project-state.json'] = encoded(old_state); validate_histories(history)
    index = {'schema_version': 'lab-selected-repository-target-index/v1-candidate', 'authority_effect': 'none',
        'coverage': 'selected authored targets only; not complete repository catalog', 'replay_source': False,
        'entries': [{'version_ref': t['version_ref'], 'identity_ref': t['identity'], 'category': t['category'],
            'semantic_kind': t['kind'], 'carrier_type_ref': t['carrier_ref'], 'decision_ref': t['decision_ref'],
            'path': root + '/' + t['record_path'], 'sha256': t['record_sha256'],
            'predecessor_ref': t['predecessor_ref'], 'lifecycle_state': 'withdrawn' if t['operation'] == 'withdraw' else 'admitted-current'} for t in review['targets']]}
    files['instance-index.json'] = encoded(index)
    generated = _record(context, authority, 'generated-output', 'generated-output:' + token, 'Selected target index')
    generated['payload'].update(generator_ref='generator-package:' + digest(review['generator_binding']),
        input_refs=[t['version_ref'] for t in review['targets']], output_digest='sha256:' + byte_digest(files['instance-index.json']),
        reproducibility_receipt_ref=receipt_ref)
    generated['relation_refs'] = [{'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
    records['instances/generated-output.json'] = generated
    transaction = _record(context, authority, 'admission-transaction', txid, 'Exact repository Admission Transaction')
    transaction['payload'].update(project_ref=state['payload']['project_ref'], decision_bundle_ref=db,
        decision_core_refs=[{'decision_ref': c['decision_ref'], 'decision_core_sha256': byte_digest(encoded(c)), 'selected_outcome': c['selected_outcome']} for c in cores],
        review_bundle_digest=digest(review), resolved_bundle_digest=digest(cores), authorization_evidence_ref=auth_path,
        authorization_evidence_sha256=byte_digest(encoded(response)), input_state_ref=old_state['node_id'], input_state_sha256=byte_digest(encoded(old_state)),
        admission_targets=[{'target_ref': c['target_ref'], 'target_sha256': c['target_sha256'], 'effect_kind': c['effect_kind']} for c in cores],
        deterministic_consequences=[{'consequence_kind': r['kind'], 'consequence_ref': r['node_id'], 'output_sha256': byte_digest(encoded(r)), 'declared_input_ref': db} for r in [state, *history.values(), generated]],
        application_state='applied', application_receipt_ref=receipt_ref, rollback_ref='repository-recovery:immutable-bundle:' + token,
        runtime_activations=0, external_effect_refs=[])
    transaction['relation_refs'] = [{'relation_kind_ref': 'relation.governed-by', 'direction': 'source', 'counterpart_kind': 'policy', 'counterpart_ref': authority.policy_ref}]
    records['instances/governance/admission-transaction.json'] = transaction
    # Stage all generated subjects before validating exact-version connections.
    subjects = copy.deepcopy(context['subjects'])
    old_state_entry = next(e for e in subjects.values() if e['identity'] == old_state['node_id'])
    def entry(record, path):
        version = record['node_id'] + '@repository.' + token
        return version, {'identity': record['node_id'], 'version_ref': version, 'category': 'typed-relation' if record['kind'] == 'typed-relation' else 'artifact-instance',
            'kind': record['kind'], 'carrier_ref': _carrier(context, record['kind']), 'effective_state': 'admitted-current',
            'record': record, 'decision_ref': core_refs, 'source': {'path': root + '/' + path, 'sha256': byte_digest(encoded(record))}}
    for path, r in records.items():
        if r['kind'] in ['project-state', 'project-semantic-event-history', 'project-governance-event-history']:
            for old in subjects.values():
                if old['identity'] == r['node_id'] or (r['kind'] == 'project-state' and old['kind'] == 'project-state'):
                    old['effective_state'] = 'admitted-historical'
        v,e = entry(r, path); subjects[v] = e
    project = next(e for e in subjects.values() if e['identity'] == state['payload']['project_ref'])
    def endpoint(record):
        e = next(e for e in subjects.values() if e['record'] is record)
        return {'ref': e['identity'], 'kind': e['kind'], 'version_ref': e['version_ref']}
    connections = [(endpoint(state), {'ref': old_state_entry['identity'], 'kind': old_state_entry['kind'], 'version_ref': old_state_entry['version_ref']}, 'relation.successor-of', {'succession_effect': 'continues-and-supersedes-current-state'}),
        (endpoint(state), {'ref': project['identity'], 'kind': project['kind'], 'version_ref': project['version_ref']}, 'relation.member-of', {'membership_role': 'durable-project-state'})]
    for result in [state, *history.values(), generated]:
        connections.append((endpoint(transaction), endpoint(result), 'relation.materializes-consequence', {
            'consequence_role': result['kind'], 'output_digest': 'sha256:' + byte_digest(encoded(result)), 'application_receipt_ref': receipt_ref}))
    for i,(source, target, predicate, qualifiers) in enumerate(connections):
        r = _record(context, authority, 'typed-relation', 'typed-relation:' + token + ':' + str(i), 'Deterministic ' + predicate)
        r['schema_version'] = context['contracts'][_carrier(context, 'typed-relation')]['instance_discriminator']['value']
        r['payload'].update(relation_kind_ref=predicate, source=source, target=target, qualifiers=qualifiers,
            relation_lifecycle_state='active', relation_evidence_refs=[auth_path])
        records[f'instances/typed-relations/{i:04d}.json'] = r
        v,e = entry(r, f'instances/typed-relations/{i:04d}.json'); subjects[v] = e
    for path, record in records.items():
        carrier = _carrier(context, record['kind']); category = 'typed-relation' if record['kind'] == 'typed-relation' else 'artifact-instance'
        validate_promotion_record(record, category, carrier, context, identities, subjects)
        files[path] = encoded(record)
    for t in review['targets']:
        validate_promotion_record(loads(files[t['record_path']]), t['category'], t['carrier_ref'], context, identities, subjects)
    receipt = {'schema_version': 'lab-repository-publication-receipt/v1-candidate', 'bundle_id': token,
        'review_digest': digest(review), 'authorization_sha256': byte_digest(encoded(response)),
        'decision_core_sha256s': review['core_sha256s'], 'semantic_cursor': cursor, 'governance_cursor': g_cursor,
        'outputs': [{'path': p, 'sha256': byte_digest(raw)} for p,raw in sorted(files.items()) if p.startswith(('targets/', 'instances/'))],
        'runtime_activations': 0, 'external_effects': 0, 'commit_point': 'atomic-no-replace-immutable-bundle-directory'}
    files['receipts/application.json'] = encoded(receipt)
    files['review.json'] = encoded(review); files['authorization.json'] = encoded(response)
    manifest = {'schema_version': 'lab-immutable-repository-bundle/v1-candidate', 'bundle_id': token,
        'review_digest': digest(review), 'authority_sha256': digest(authority.core()),
        'current_project_state_ref': stateid, 'current_project_state_sha256': byte_digest(files['instances/project-state.json']),
        'decision_refs': core_refs, 'decision_checkpoint_ref': cp, 'runtime_activations': 0, 'external_effect_refs': [],
        'files': {p:byte_digest(raw) for p,raw in sorted(files.items())}}
    files['bundle.json'] = encoded(manifest)
    return files, manifest
