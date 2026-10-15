"""Bind a verified C04 catalog to a separately pinned signed runtime projection.

Snapshot formats and executable closures remain distinct. Exact catalog material
and current metadata must match; this pure checker authenticates no host or Actor.
The actual original signed reader must supply and guard these private selections.
"""
import importlib
from . import adapter as A, source_selection as S


def bind_runtime_catalog(selection, snapshot, *, baseline, projection, config, head,
                         expected_profile_sha256, expected_baseline_digest,
                         expected_projection_digest, expected_config_digest, expected_head):
    """Recalculate complete catalogs and every original catalog byte dependency."""
    kernel = A.kernel()
    sources = importlib.import_module(kernel.__package__ + '.sources')
    sources.verify_snapshot(snapshot, expected_profile_sha256=expected_profile_sha256)
    A.require(kernel.digest(baseline) == expected_baseline_digest
              and kernel.digest(projection) == expected_projection_digest
              and kernel.digest(config) == expected_config_digest and head == expected_head,
              'independent actual baseline/projection/configuration/HEAD differs')
    A.require(config['source_snapshot_digest'] == baseline['snapshot_digest'],
              'actual runtime configuration does not select its exact baseline')
    selected = S.select_bound_catalog(snapshot, expected_profile_sha256=expected_profile_sha256,
        expected_snapshot_digest=selection['snapshot_digest'], evidence_bytes=selection['materials'])
    for key in ['relations', 'endpoints', 'descriptors', 'schemas', 'legacy_descriptor_alias_refs']:
        A.require(selection[key] == selected[key], 'verified complete independent catalog selection differs')
    current = {'admitted-current', 'local-admitted-current'}
    actual_refs = {ref for ref, contract in projection['contracts'].items()
                   if contract['lifecycle_state'] in current}
    A.require(actual_refs == set(selected['endpoints']),
              'complete current runtime carrier inventory differs')
    A.require(set(projection['relation_contracts']) == set(selected['relations']),
              'complete current runtime Relation Kind inventory differs')
    dependencies = set()
    predecessor_refs = set()
    definition_refs = set()
    for ref, relation in selected['relations'].items():
        A.require(projection['relation_contracts'][ref] == snapshot['relation_contracts'][ref],
                  'complete runtime Relation Kind body differs')
        predecessor_refs.add(relation['version_ref'])
        dependencies.add(relation['signature_binding']['ref'])
    for ref, descriptor in selected['descriptors'].items():
        actual = projection['contracts'][ref]; original = snapshot['contracts'][ref]
        A.require(actual['artifact'] == descriptor
                  and all(actual[k] == original[k] for k in ['semantic_kind', 'schema_path',
                    'schema_sha256', 'schema_selector', 'artifact_path', 'artifact_sha256']),
                  'complete runtime carrier descriptor or schema selection differs')
        schema = projection['documents'][actual['schema_path']]
        if actual['schema_selector']: schema = kernel.pointer(schema, actual['schema_selector'][1:])
        A.require(schema == selected['schemas'][ref], 'complete runtime carrier schema differs')
        dependencies.update([original['artifact_path'], original['schema_path']])
        if ref in snapshot['subjects']:
            predecessor_refs.add(ref)
        else:
            A.require(ref in selected['legacy_descriptor_alias_refs'],
                      'current carrier lacks exact predecessor or explicit legacy alias')
        definition_refs.update(descriptor.get('semantic_definition_refs', []))
    for ref in definition_refs:
        subject = sources.resolve(snapshot['subjects'], ref)
        A.require(subject['category'] == 'definition', 'catalog semantic binding is not a Definition')
        predecessor_refs.add(subject['version_ref'])
        dependencies.add(subject['source']['path'])
    for ref in sorted(predecessor_refs):
        A.require(projection['subjects'].get(ref) == snapshot['subjects'][ref],
                  'complete runtime catalog predecessor/Definition differs')
    bindings = []
    for path in sorted(dependencies):
        raw = selected['materials'].get(path)
        expected = snapshot['materials'].get(path)
        A.require(type(raw) is bytes and A.sha(raw) == expected
                  and baseline['materials'].get(path) == expected,
                  'exact original catalog material differs between independently selected cuts')
        # The actual immutable baseline's parsed value is bound as well as its
        # original byte digest. Inherited schema selectors never omit the rest
        # of the complete captured schema document from this comparison.
        if path in snapshot['documents']:
            A.require(baseline['documents'].get(path) == snapshot['documents'][path],
                      'actual baseline parsed catalog material differs')
        bindings.append({'ref': path, 'sha256': expected})
    shared_changed = sorted(path for path, digest in snapshot['materials'].items()
                            if baseline['materials'].get(path) != digest)
    extras = sorted(set(baseline['materials']) - set(snapshot['materials']))
    A.require(not set(shared_changed) & dependencies,
              'a catalog dependency cannot be explained as an executable-closure difference')
    return {'schema_version': 'lab-runtime-catalog-binding/v1-candidate', 'result': 'PASS',
        'independent_catalog_snapshot_digest': selection['snapshot_digest'],
        'independent_catalog_profile_sha256': expected_profile_sha256,
        'actual_runtime_baseline_snapshot_digest': baseline['snapshot_digest'],
        'actual_runtime_baseline_digest': expected_baseline_digest,
        'actual_runtime_projection_digest': expected_projection_digest,
        'actual_runtime_config_digest': expected_config_digest, 'actual_runtime_HEAD': head,
        'current_carrier_count': len(actual_refs), 'current_relation_kind_count': len(selected['relations']),
        'exact_catalog_material_bindings': bindings,
        'exact_catalog_predecessor_and_definition_refs': sorted(predecessor_refs),
        'noncatalog_capture_material_differences': shared_changed,
        'runtime_baseline_additional_materials': extras,
        'equal_snapshot_envelope_digests': selection['snapshot_digest'] == baseline['snapshot_digest'],
        'executable_closures_equated': False, 'actual_transport_authenticated': False,
        'live_currentness_established': False, 'actual_transactions_written': 0,
        'actual_public_calls': 0, 'public_handler_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none'}
