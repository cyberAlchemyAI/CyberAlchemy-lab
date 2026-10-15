"""Exact original runtime schema/core preparation and coupled carrier postimages.

Inputs here are private host selections. This pure helper authenticates no Actor,
grant, current cut or owner. Its simulated postimage is never an admitted source.
Public integration must supply the independently verified actual host projection
and configuration, enforce its transport/policy guards and retain its journal.
"""
import copy
import importlib
import importlib.util
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from . import adapter as A, source_selection as S, prospective as R, catalog_binding as B, predecessor_binding as V, scope_preparation as H

ENGINE = A.HERE.parent / 'custody-correction-v4'
ENGINE_MANIFEST_SHA = '329403eb89eb989a834cba02c7fb09f920d328e8ecdca9a0880660b1e97cbcaa'
PINS_SHA = 'd59fc534f60483fe9df93b2e6d45431d00ccec082332fbf4e76a91b0944e6b4d'
LOADER_SHA = 'f1953bf08d36756810fbc7ec051df5d0e362f745e84644223b9dddd0df1b13ef'


def backend():
    """Use the same original custody engine as the actual current API host."""
    loader_path = ENGINE / 'loader.py'
    pins_path = ENGINE / 'pins.json'
    A.require(A.sha(loader_path.read_bytes()) == LOADER_SHA
              and A.sha(pins_path.read_bytes()) == PINS_SHA,
              'independent original engine loader/pins differ')
    loader_name = '_cal_typed_extension_original_custody_loader_v4'
    if loader_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(loader_name, loader_path)
        loader = importlib.util.module_from_spec(spec)
        sys.modules[loader_name] = loader
        spec.loader.exec_module(loader)
    loader = sys.modules[loader_name]
    A.require(Path(loader.__file__).resolve() == loader_path,
              'unselected original engine verifier')
    loader.verify_engine(loader.EnginePins(**A.parse(pins_path.read_bytes())))
    manifest = ENGINE / 'engine-manifest.json'
    A.require(A.sha(manifest.read_bytes()) == ENGINE_MANIFEST_SHA,
              'independent actual engine manifest differs')
    selected = A.parse(manifest.read_bytes())
    A.require(selected['authority_effect'] == 'none' and selected['actual_owner_outcome'] is None,
              'candidate engine cannot grant authority')
    for row in selected['files']:
        path = A.ROOT / row['path']
        A.require(path.is_relative_to(ENGINE / 'runtime') and path.is_file()
                  and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
                  and A.sha(path.read_bytes()) == row['sha256'], 'actual engine input changed')
    name = '_cal_typed_extension_actual_custody_engine_v4'
    root = ENGINE / 'runtime/lab_runtime'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, root / '__init__.py',
                                                    submodule_search_locations=[str(root)])
        package = importlib.util.module_from_spec(spec); sys.modules[name] = package
        spec.loader.exec_module(package)
    modules = [importlib.import_module(name + '.' + suffix)
               for suffix in ['common', 'operations', 'custody']]
    A.require(all(Path(m.__file__).resolve() == root / (suffix + '.py')
                  for m, suffix in zip(modules, ['common', 'operations', 'custody'])),
              'unselected actual runtime module')
    return modules


def prepare_exact_postimage(selection, inspection, impact, proposal, *,
                            projection, config, head, expected_projection_digest,
                            expected_config_digest, expected_head, read_material,
                            independently_selected_schema_paths,
                            independently_selected_catalog_snapshot=None,
                            independently_selected_runtime_baseline=None,
                            expected_runtime_baseline_digest=None,
                            expected_catalog_profile_sha256=None,
                            independently_selected_representation_profile_bytes=None,
                            expected_representation_profile_sha256=None,
                            read_source_material=None,
                            independently_selected_scope_preparation_profile_bytes=None,
                            expected_scope_preparation_profile_sha256=None):
    """Compare every raw target/core with the unchanged original runtime result.

The registration body and contract remain separate inputs. Their exact schema
bytes, instance discriminator, endpoint roles and Decision cores are checked as
one complete proposed transaction. No durable objects or transactions are made.
"""
    C, O, K = backend()
    before = C.digest(projection)
    A.require(before == expected_projection_digest and C.digest(config) == expected_config_digest
              and head == expected_head, 'independent current projection/configuration/head differs')
    A.require(proposal['scope_ref'] == config['scope_ref'], 'proposal scope differs from host configuration')
    catalog_binding = None
    A.require((independently_selected_scope_preparation_profile_bytes is None)
              == (expected_scope_preparation_profile_sha256 is None),
              'typed scope preparation inputs must be complete')
    if independently_selected_catalog_snapshot is None:
        A.require(independently_selected_runtime_baseline is None
                  and expected_runtime_baseline_digest is None and expected_catalog_profile_sha256 is None,
                  'runtime catalog binding inputs must be complete')
        A.require(config['source_snapshot_digest'] == selection['snapshot_digest'],
                  'host configuration and selected semantic snapshot differ')
    else:
        A.require(independently_selected_runtime_baseline is not None
                  and expected_runtime_baseline_digest is not None and expected_catalog_profile_sha256 is not None,
                  'runtime catalog binding inputs must be complete')
        catalog_binding = B.bind_runtime_catalog(selection, independently_selected_catalog_snapshot,
            baseline=independently_selected_runtime_baseline, projection=projection, config=config, head=head,
            expected_profile_sha256=expected_catalog_profile_sha256,
            expected_baseline_digest=expected_runtime_baseline_digest,
            expected_projection_digest=expected_projection_digest,
            expected_config_digest=expected_config_digest, expected_head=expected_head)
    public_predecessor_binding = None
    if independently_selected_representation_profile_bytes is None:
        A.require(expected_representation_profile_sha256 is None and read_source_material is None,
                  'public predecessor representation inputs must be complete')
    else:
        A.require(catalog_binding is not None and expected_representation_profile_sha256 is not None
                  and read_source_material is not None,
                  'public predecessor representation inputs must be complete')
        public_predecessor_binding = V.bind_public_predecessors(proposal, projection=projection,
            baseline=independently_selected_runtime_baseline, config=config,
            representation_profile_bytes=independently_selected_representation_profile_bytes,
            expected_profile_sha256=expected_representation_profile_sha256,
            read_source_material=read_source_material)
    current = ('admitted-current', 'local-admitted-current')
    # The host-selected current projection must still contain the independently
    # resolved original carrier and Relation Kind facts; no candidate shadowing.
    for ref, old in selection['relations'].items():
        record = projection['relation_contracts'].get(ref)
        original = A.parse(selection['materials'][old['signature_binding']['ref']])
        A.require(record == original,
                  'current projection Relation Kind differs from selected catalog')
    for ref, descriptor in selection['descriptors'].items():
        contract = projection['contracts'].get(ref)
        A.require(contract is not None and contract['lifecycle_state'] in current
                  and contract['artifact'] == descriptor,
                  'current projection carrier differs from selected catalog')
        schema = projection['documents'][contract['schema_path']]
        if contract['schema_selector']:
            schema = C.pointer(schema, contract['schema_selector'][1:])
        A.require(schema == selection['schemas'][ref],
                  'current projection carrier schema differs from selected catalog')
    A.require(set(independently_selected_schema_paths)
              == {b['ref'] for b in proposal['schema_bindings']},
              'schema destination inventory differs from independent host selection')
    prospective, pending = R.resolve_prospective_carriers(
        selection, inspection, proposal, read_material=read_material,
        independently_selected_schema_paths=independently_selected_schema_paths)
    actual_impact = S.assess_carrier_impacts(prospective, inspection)
    A.require(impact == actual_impact,
              'complete independently calculated carrier impact differs')
    runtime_targets, originals, schemas, schema_bytes, expected_cores = [], {}, {}, {}, []
    for binding in proposal['schema_bindings']:
        raw = read_material(binding)
        A.require(type(raw) is bytes and A.sha(raw) == binding['sha256'], 'schema original bytes differ')
        A.require(binding['ref'] in independently_selected_schema_paths,
                  'schema destination lacks independent host selection')
        path = independently_selected_schema_paths[binding['ref']]
        A.require(path.startswith('runtime/schemas/') and path.endswith('.json')
                  and '..' not in Path(path).parts and path not in schemas,
                  'schema material must select one exact unique runtime schema path')
        schemas[path] = A.parse(raw); schema_bytes[path] = raw
    for target in proposal['targets']:
        header = A.public_header(target['artifact'])
        A.require(header['scope_ref'] == proposal['scope_ref'], 'target header scope differs')
        metadata_raw = read_material(target['candidate_binding'])
        A.require(A.sha(metadata_raw) == target['candidate_binding']['sha256'], 'metadata binding differs')
        metadata = A.parse(metadata_raw)
        A.require(set(metadata) == {'schema_version', 'category', 'decision_ref', 'contract'}
                  and metadata['schema_version'] == 'lab-candidate-target-metadata/v1-candidate',
                  'closed original target metadata required')
        record = None
        if target['operation'] != 'withdraw':
            content = target['content']
            raw = read_material({'ref': content['content_ref'], 'sha256': content['byte_sha256']})
            A.require(type(raw) is bytes and A.sha(raw) == header['byte_sha256'] == content['byte_sha256']
                      and len(raw) == content['size_bytes'] and content['media_type'] == 'application/json',
                      'exact target content/header bytes differ')
            record = A.parse(raw); originals[header['version_ref']] = raw
            if metadata['category'] == 'artifact-type':
                slot = projection['contracts']['cal.artifact-type.artifact-type/v3']
                schema = projection['documents'][slot['schema_path']]['properties']['registered_types']['items']
                A.require(Draft202012Validator(schema).is_valid(record),
                          'original registered-type slot schema refused descriptor body')
                A.require(record['artifact_type_ref'] == header['version_ref']
                          and record['artifact_type_ref'].rsplit('/', 1)[0] == header['identity_ref'],
                          'registered descriptor body/header identity differs')
            else:
                carrier = projection['contracts'][header['carrier_ref']]
                field = carrier['artifact'].get('instance_contract', {}).get('identity_field')
                A.require(C.identity(record, field) == header['identity_ref'], 'body/header identity differs')
        predecessor = target['predecessor']
        if predecessor is not None:
            prior = projection['subjects'].get(predecessor['version_ref'])
            A.require(prior is not None and prior['effective_state'] in current
                      and prior['identity'] == predecessor['identity_ref']
                      and (public_predecessor_binding is not None
                           or (prior['carrier_ref'] == predecessor['carrier_ref']
                               and prior['source']['sha256'] == predecessor['byte_sha256']))
                      and predecessor['scope_ref'] == proposal['scope_ref'],
                      'exact current predecessor header differs')
        entry = {'category': metadata['category'], 'operation': target['operation'],
                 'version_ref': header['version_ref'], 'carrier_ref': header['carrier_ref'],
                 'record': record, 'predecessor_ref': predecessor['version_ref'] if predecessor else None,
                 'decision_ref': metadata['decision_ref'], 'contract': metadata['contract'],
                 'content': K.content_entry(originals[header['version_ref']]) if record is not None else None}
        core = {'decision_ref': metadata['decision_ref'], 'category': metadata['category'],
                'operation': target['operation'], 'version_ref': header['version_ref'],
                'target_digest': C.digest(entry)}
        core_raw = read_material(target['decision_core_binding'])
        A.require(A.sha(core_raw) == target['decision_core_binding']['sha256']
                  and core_raw == C.encoded(core), 'exact original stable Decision core differs')
        expected_cores.append(core); runtime_targets.append(entry)
    runtime = {'schema_version': 'lab-runtime-proposal/v1', 'proposal_id': proposal['proposal_ref'],
               'expected_head': head, 'source_snapshot_digest': config['source_snapshot_digest'],
               'scope_ref': proposal['scope_ref'], 'policy_ref': config['policy_ref'],
               'challenge_route': config['challenge_route'], 'schemas': schemas, 'targets': runtime_targets}
    runtime = K.with_originals(runtime, originals, schema_bytes, exact_schema_bytes=True)
    scope_preparation = None
    if independently_selected_scope_preparation_profile_bytes is None:
        post, cores = O.prepare(projection, runtime, head, config)
    else:
        post, cores, scope_preparation = H.prepare_hypothesis(selection, inspection, impact,
            proposal, runtime, projection=projection, config=config, head=head,
            catalog_binding=catalog_binding, public_predecessor_binding=public_predecessor_binding,
            profile_bytes=independently_selected_scope_preparation_profile_bytes,
            expected_profile_sha256=expected_scope_preparation_profile_sha256)
    A.require(cores == expected_cores and C.digest(projection) == before,
              'backend cores differ or pure preparation changed original projection')
    successors = S.resolve_impacted_successors(impact, proposal, read_material)
    replacements = dict(zip(impact['required_current_carrier_refs'], successors))
    future = copy.deepcopy(prospective)
    for ref in pending['pending_endpoint_admission_refs']:
        contract = post['contracts'].get(ref)
        A.require(contract is not None and contract['lifecycle_state'] == 'local-admitted-current'
                  and contract['artifact'] == prospective['descriptors'][ref],
                  'prospective descriptor differs from complete original backend postimage')
        schema = post['documents'][contract['schema_path']]
        A.require(contract['schema_selector'] is None and schema == prospective['schemas'][ref],
                  'prospective complete schema differs from original backend postimage')
        # The runtime's local state exists only in this hypothetical copy. Keep
        # the public-facing endpoint explicitly pending the real owner decision.
        A.require(future['endpoints'][ref]['effective_state'] == 'candidate-for-R08',
                  'prospective endpoint cannot be presented as current admission')
    for old_ref, header in replacements.items():
        ref = header['version_ref']; contract = post['contracts'][ref]
        A.require(contract['lifecycle_state'] == 'local-admitted-current'
                  and post['contracts'][old_ref]['lifecycle_state'] == 'local-admitted-historical',
                  'simulated carrier succession is incomplete')
        # Resolve through actual backend output, preserving the original raw schema
        # identity. The old ref denotes the selected predecessor during review.
        future['descriptors'][old_ref] = contract['artifact']
        schema = post['documents'][contract['schema_path']]
        if contract['schema_selector']:
            schema = C.pointer(schema, contract['schema_selector'][1:])
        future['schemas'][old_ref] = schema
    remaining = S.assess_carrier_impacts(future, inspection)
    A.require(not remaining['required_current_carrier_refs'],
              'proposed carrier schemas/ordered roles do not close the extension postimage')
    A.require(C.digest(projection) == before, 'postimage checks changed actual source')
    backend()
    return {'schema_version': 'lab-typed-extension-postimage-checks/v1-candidate',
            'result': 'PASS', 'original_projection_digest': before,
            'simulated_postimage_digest': C.digest(post), 'runtime_proposal_digest': C.digest(runtime),
            'ordered_stable_core_bindings': [t['decision_core_binding'] for t in proposal['targets']],
            'target_count': len(runtime_targets), 'affected_carrier_successor_refs': successors,
            'pending_endpoint_admission_refs': pending['pending_endpoint_admission_refs'],
            'prospective_candidate_bindings': pending['candidate_bindings'],
            'runtime_catalog_binding': catalog_binding,
            'public_predecessor_binding': public_predecessor_binding,
            'scope_preparation': scope_preparation,
            'operational_preparation_ready': False,
            'runtime_admission_authorized': False,
            'all_prospective_original_backend_checks': True,
            'all_target_schema_and_core_checks': True, 'all_affected_schema_and_ordered_roles_closed': True,
            'original_target_and_schema_bytes_retained': True,
            'source_projection_unchanged': True, 'simulated_effective_states_are_not_admission': True,
            'actual_transactions_written': 0, 'globally_available_pairs_added': 0,
            'relation_instances_created': 0, 'actual_owner_outcome': None,
            'live_currentness_established': False, 'public_handler_qualified': False, 'authority_effect': 'none'}
