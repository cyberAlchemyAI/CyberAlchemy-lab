def verify(response, review, selection, trust):
    """Verify exact authentic response; returns evidence, not a publication effect.

    Always uses actual wall time. Rejected/revised dispositions are verified but
    cannot pass verify_for_publication. Missing actual host inputs fail closed.
    """
    require(type(trust) is TrustContext and type(selection) is Selection,
            'independent installed context and selection required')
    require(trust.usage in ('technical-fixture', 'actual-owner'), 'unselected trust usage')
    for field in ('host_issuer', 'role_issuer', 'mechanism_ref', 'governing_registry_ref'):
        text(getattr(trust, field))
    require(trust.host_issuer != trust.role_issuer and
            trust.host_public_key != trust.role_public_key, 'independent role issuer required')
    for field in ('review_sha256', 'authority_proof_sha256', 'presentation_sha256', 'message_sha256',
                  'displayed_material_sha256', 'role_source_evidence_sha256'):
        pin(getattr(selection, field))
    for field in ('registry_cursor', 'principal_ref', 'scope_ref'):
        text(getattr(selection, field))
    closed(response, ('schema_version', 'authority_proof', 'presentation', 'message'))
    require(response['schema_version'] == VERSION, 'fixture key adapter is not actual owner ingress')
    require(digest(review) == selection.review_sha256, 'independently selected review changed')
    for field, expected in (('authority_proof', selection.authority_proof_sha256),
                            ('presentation', selection.presentation_sha256),
                            ('message', selection.message_sha256)):
        require(digest(response[field]) == expected, 'independently selected evidence changed: ' + field)
    authority = review['authority']
    require(review['authority_sha256'] == digest(authority), 'review authority digest mismatch')
    require(authority['principal_ref'] == selection.principal_ref and
            authority['scope_ref'] == selection.scope_ref, 'review principal/scope mismatch')
    cores = review['independent_cores']
    core_pins = [legacy_core_digest(core) for core in cores]
    require(bool(cores) and review['core_sha256s'] == core_pins and
            len(set(core_pins)) == len(core_pins), 'complete unique member cores required')
    require(len(review['targets']) == len(cores), 'target/member cardinality mismatch')
    roles = authority['owner_roles']
    require(type(roles) is dict and bool(roles), 'governing owner roles missing')
    require(set(roles) <= OWNER_CATEGORIES, 'unknown governing owner category')
    for category, owner in roles.items():
        text(category); text(owner)
    for target, core in zip(review['targets'], cores):
        text(target['category']); text(target['version_ref'])
        text(core['owner_ref']); text(core['target_ref']); text(core['decision_ref'])
        require(target['category'] in roles and core['owner_ref'] == roles[target['category']]
                and core['target_ref'] == target['version_ref'], 'member governing role/target mismatch')
    role = signed(response['authority_proof'], trust.role_issuer, trust.role_public_key)
    closed(role, ('schema_version', 'registry_ref', 'registry_cursor', 'principal_ref', 'scope_ref',
                  'governing_roles', 'authority_sha256', 'source_evidence', 'valid_from', 'valid_until',
                  'resolution', 'permitted_effect'))
    require(role['schema_version'] == 'lab-governing-owner-evidence/v1-candidate' and
            role['registry_ref'] == trust.governing_registry_ref and
            role['registry_cursor'] == selection.registry_cursor and
            role['principal_ref'] == selection.principal_ref and
            role['scope_ref'] == selection.scope_ref and role['governing_roles'] == roles and
            role['authority_sha256'] == digest(authority) and
            role['resolution'] == 'independently-resolved-current-governing-authority' and
            role['permitted_effect'] == 'one-exact-immutable-repository-bundle',
            'current independently selected governing authority required')
    require(type(role['source_evidence']) is list and bool(role['source_evidence']),
            'governing authority source provenance absent')
    require(digest(role['source_evidence']) == selection.role_source_evidence_sha256,
            'independently selected governing source evidence changed')
    refs = []
    for row in role['source_evidence']:
        closed(row, ('ref', 'sha256')); refs.append(text(row['ref'])); pin(row['sha256'])
    require(len(set(refs)) == len(refs), 'duplicate role evidence')
    now = datetime.now(timezone.utc)
    start, end = timestamp(role['valid_from']), timestamp(role['valid_until'])
    require(start <= now < end and now < timestamp(authority['expires_at']), 'expired/current authority absent')
    presentation = signed(response['presentation'], trust.host_issuer, trust.host_public_key)
    closed(presentation, ('schema_version', 'mechanism_ref', 'presentation_id', 'conversation_id',
                          'principal_ref', 'review_sha256', 'authority_sha256', 'bundle_id', 'bundle_path',
                          'decision_core_sha256s', 'displayed_material_sha256', 'presented_at'))
    require(presentation['schema_version'] == 'lab-host-review-presentation/v1-candidate' and
            presentation['mechanism_ref'] == trust.mechanism_ref and
            presentation['principal_ref'] == selection.principal_ref and
            presentation['review_sha256'] == selection.review_sha256 and
            presentation['authority_sha256'] == digest(authority) and
            presentation['bundle_id'] == review['bundle_id'] and
            presentation['bundle_path'] == review['bundle_path'] and
            presentation['decision_core_sha256s'] == core_pins,
            'host did not present this exact review to selected owner')
    require(pin(presentation['displayed_material_sha256']) == selection.displayed_material_sha256,
            'independently selected displayed review material changed')
    text(presentation['presentation_id']); text(presentation['conversation_id'])
    message = signed(response['message'], trust.host_issuer, trust.host_public_key)
    closed(message, ('schema_version', 'mechanism_ref', 'message_id', 'conversation_id', 'principal_ref',
                     'interaction_kind', 'content', 'content_sha256', 'presentation_sha256',
                     'review_sha256', 'authority_proof_sha256', 'selected_outcome', 'recorded_at'))
    require(message['schema_version'] == 'lab-host-owner-message/v1-candidate' and
            message['mechanism_ref'] == trust.mechanism_ref and
            message['interaction_kind'] == 'human-explicit-review-disposition' and
            message['principal_ref'] == selection.principal_ref and
            message['conversation_id'] == presentation['conversation_id'] and
            message['presentation_sha256'] == selection.presentation_sha256 and
            message['review_sha256'] == selection.review_sha256 and
            message['authority_proof_sha256'] == selection.authority_proof_sha256 and
            message['selected_outcome'] in OUTCOMES,
            'explicit independently attested human disposition absent')
    text(message['message_id']); text(message['content'])
    require(message['content_sha256'] == sha256(message['content'].encode('utf-8')).hexdigest(),
            'actual message content digest mismatch')
    shown, spoken = timestamp(presentation['presented_at']), timestamp(message['recorded_at'])
    require(start <= shown <= spoken <= now and spoken < end, 'message/presentation outside authority period')
    return {'schema_version': VERSION, 'authority_effect': 'none', 'usage': trust.usage,
            'review_sha256': selection.review_sha256, 'authority_sha256': digest(authority),
            'message_sha256': selection.message_sha256, 'message_id': message['message_id'],
            'host_issuer': trust.host_issuer, 'mechanism_ref': trust.mechanism_ref,
            'conversation_id': message['conversation_id'], 'selected_outcome': message['selected_outcome'],
            'bundle_id': review['bundle_id'], 'bundle_path': review['bundle_path'],
            'decision_core_sha256s': core_pins}
