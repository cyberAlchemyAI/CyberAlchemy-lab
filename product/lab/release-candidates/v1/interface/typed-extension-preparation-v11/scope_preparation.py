"""One exact coupled typed candidate under an unprovisioned scope hypothesis.

Called after the private host's complete catalog, representation, schema, core
and coupling checks. This supplies no operational scope grant or owner outcome.
Actual inputs stay unchanged; every body and target reaches the original engine.
"""
import copy
from jsonschema import Draft202012Validator
from . import adapter as A


def prepare_hypothesis(selection, inspection, impact, wire_proposal, runtime, *,
                       projection, config, head, catalog_binding,
                       public_predecessor_binding, profile_bytes, expected_profile_sha256):
    from .postimage import backend
    C, O, _ = backend()
    before = C.digest(projection)
    actual_config_digest = C.digest(config)
    wire_digest = C.digest(wire_proposal)
    runtime_digest = C.digest(runtime)
    A.require(type(profile_bytes) is bytes and A.sha(profile_bytes) == expected_profile_sha256,
              'independent typed scope profile pin differs')
    profile = A.parse(profile_bytes)
    schema = A.parse((A.HERE / 'scope-preparation-profile.schema.json').read_bytes())
    A.require(Draft202012Validator(schema).is_valid(profile),
              'closed candidate-only typed scope profile required')
    A.require(profile['runtime_admission_authorized'] is False
              and profile['actual_owner_outcome'] is None and profile['authority_effect'] == 'none',
              'scope profile cannot grant admission')
    A.require(catalog_binding is not None and public_predecessor_binding is not None
              and catalog_binding['result'] == public_predecessor_binding['result'] == 'PASS',
              'complete catalog and public predecessor binding required for scope preparation')
    expected_sources = {
        'catalog_snapshot_digest': selection['snapshot_digest'],
        'catalog_profile_sha256': catalog_binding['independent_catalog_profile_sha256'],
        'runtime_baseline_digest': catalog_binding['actual_runtime_baseline_digest'],
        'runtime_projection_digest': before,
        'runtime_config_digest': actual_config_digest,
        'runtime_head': head,
        'representation_profile_sha256': public_predecessor_binding['representation_profile_sha256']}
    A.require(profile['source_bindings'] == expected_sources,
              'independent typed scope source/current/profile pins differ')
    A.require(profile['proposal_structural_sha256'] == wire_digest,
              'complete typed scope wire proposal differs')
    A.require(profile['inspection_structural_sha256'] == C.digest(inspection)
              and profile['impact_structural_sha256'] == C.digest(impact),
              'typed scope inspection/impact differs')
    versions = [target['artifact']['version_ref'] for target in wire_proposal['targets']]
    A.require(profile['ordered_target_version_refs'] == versions
              and len(versions) == len(set(versions))
              and versions == [target['version_ref'] for target in runtime['targets']],
              'complete ordered typed scope target group differs')
    A.require(profile['ordered_decision_core_bindings']
              == [target['decision_core_binding'] for target in wire_proposal['targets']]
              and profile['schema_bindings'] == wire_proposal['schema_bindings'],
              'complete typed scope schema/core binding inventory differs')
    storage = profile['storage_scope_ref']; domain = profile['semantic_scope_ref']
    A.require(storage == config['scope_ref'] == wire_proposal['scope_ref'] == runtime['scope_ref']
              and storage != domain, 'typed scope hypothesis requires exact distinct storage/domain scopes')
    A.require(all(target['category'] in ('artifact-type', 'relation-kind')
                  and target['operation'] in ('admit', 'revise') for target in runtime['targets']),
              'typed scope profile cannot cover another category/effect')
    scopes = {target['record']['scope_ref'] for target in runtime['targets']
              if target['record'] is not None and 'scope_ref' in target['record']}
    A.require(scopes == {domain}, 'declared semantic scope differs from complete typed target bodies')
    # Preserve the actual refusal. No generic failure may be reinterpreted as
    # missing domain configuration, and actual operational preparation never
    # becomes ready through this private candidate helper.
    try:
        O.prepare(projection, runtime, head, config)
    except C.RuntimeFault as error:
        A.require(str(error) == 'target outside authorized scope',
                  'original backend error is not the exact declared scope refusal')
        actual_refusal = str(error)
    else:
        raise A.WireFault('actual preparation passed; no scope hypothesis is applicable')
    hypothetical_config = copy.deepcopy(config); hypothetical_config['scope_ref'] = domain
    hypothetical_runtime = copy.deepcopy(runtime); hypothetical_runtime['scope_ref'] = domain
    post, cores = O.prepare(projection, hypothetical_runtime, head, hypothetical_config)
    A.require(C.digest(projection) == before and C.digest(config) == actual_config_digest
              and C.digest(wire_proposal) == wire_digest and C.digest(runtime) == runtime_digest,
              'typed scope hypothesis changed actual original inputs')
    evidence = {'schema_version': 'lab-typed-scope-preparation-evidence/v1-candidate',
                'profile_sha256': expected_profile_sha256, 'actual_preparation_result': 'REFUSED',
                'actual_scope_refusal': actual_refusal, 'storage_scope_ref': storage,
                'semantic_scope_ref': domain, 'configuration_status': 'hypothetical-unprovisioned',
                'hypothetical_configuration_digest': C.digest(hypothetical_config),
                'hypothetical_runtime_proposal_digest': C.digest(hypothetical_runtime),
                'complete_ordered_target_version_refs': versions,
                'source_projection_unchanged': True, 'actual_configuration_unchanged': True,
                'public_headers_and_original_body_bytes_unchanged': True,
                'operational_preparation_ready': False, 'runtime_admission_authorized': False,
                'actual_runtime_grant': False, 'actual_transactions_written': 0,
                'actual_public_calls': 0, 'actual_owner_outcome': None, 'authority_effect': 'none'}
    return post, cores, evidence
