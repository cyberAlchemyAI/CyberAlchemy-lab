"""Independent package closure and native original-byte replay verification."""
from build import *


MANIFEST_FIELDS = set('schema_version task authority_effect actual_owner_outcome visibility core_sha256 counts files source_selection_binding profile_binding claim_ceiling'.split())
ARCHIVE_FIELDS = set('schema_version authority_effect actual_owner_outcome files native_executable_sha256 semantic_cursor governance_cursor private_key_included Session_memory_included ontology_admission source_effects_applied visibility'.split())
INDEX_FIELDS = set('path sha256 kind carrier_ref node_id version_ref schema_binding'.split())
CORE_FIELDS = set('schema_version task authority_effect actual_owner_outcome scope_binding profile_binding selection_binding code_bindings definition_witnesses record_index dispositions selector_observations native_archive_sha256 native_semantic_cursor native_governance_cursor native_checkpoint_parity visibility domain_instances_conformed global_typed_relations_created source_bodies_copied source_effects_applied outside_references excluded_packages deferred_source_epoch claim_ceiling'.split())
DISPOSITION_FIELDS = set('item_id disposition item_kind privacy public_body_export_allowed source_binding record_structure_sha256 outputs blocked_dependency_ids blocked_expected_sha256 contract_fit original_disposition_reason domain_instances_conformed actual_owner_outcome'.split())


def load_package(path):
    path = Path(path)
    require(path.is_dir() and not path.is_symlink()
        and not any(p.is_symlink() for p in path.parents), 'unsafe package root')
    result = {}
    for p in path.rglob('*'):
        require(not p.is_symlink() and (p.is_file() or p.is_dir()), 'unsafe package entry')
        if p.is_file():
            result[p.relative_to(path).as_posix()] = p.read_bytes()
    return result


def read_native(archive, pin):
    """Restore only exact native events; never restore Agent memory or keys."""
    exe = Path(pin['path'])
    require(exe.is_file() and not exe.is_symlink() and sha(exe.read_bytes()) == pin['sha256'],
        'native executable differs from independent pin')
    with tempfile.TemporaryDirectory(prefix='cal-O05-cold-native-') as tmp:
        root = Path(tmp)
        require(not root.is_relative_to(ROOT), 'cold native store must be outside repository')
        for family in ('semantic', 'governance'):
            (root / family).mkdir()
        for name, b in archive['files'].items():
            require(re.fullmatch(r'(semantic|governance)/[0-9]{8}-ontology-(semantic|governance):O05:[1-9][0-9]*\.json', name)
                is not None and name.split('/')[0] == name.split('-ontology-')[1].split(':')[0],
                'unselected native archive entry')
            require(set(b) == {'sha256', 'base64_original_bytes'}, 'closed native byte binding required')
            raw = base64.b64decode(b['base64_original_bytes'], validate=True)
            require(sha(raw) == b['sha256'], 'native original event bytes differ')
            p = safe(root, name)
            with p.open('xb') as stream:
                stream.write(raw)
        before = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
        process = subprocess.run([str(exe), 'read', str(root / 'semantic'), str(root / 'governance'),
            str(archive['semantic_cursor'])], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        require(process.returncode == 0, 'native cold replay rejected: ' + process.stderr.decode(errors='replace'))
        after = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
        require(before == after, 'cold replay mutated original events')
        replay = parse(process.stdout)
        require(replay['result'] == 'PASS' and replay['checkpoint_parity'] == 'PASS', 'native replay parity incomplete')
    require(not root.exists(), 'cold native store cleanup incomplete')
    return replay


def validate_payload(files, translator, expected_manifest_sha256, native=True):
    """Require an independent package pin plus source, schema and native joins."""
    translator.guard()
    require(type(files) is dict and all(type(k) is str and type(v) is bytes for k, v in files.items()),
        'closed byte map required')
    require('manifest.json' in files and sha(files['manifest.json']) == expected_manifest_sha256,
        'independently pinned package manifest differs')
    manifest = parse(files['manifest.json'])
    require(set(manifest) == MANIFEST_FIELDS and manifest['schema_version'] == 'lab-O05-package-manifest/v1-candidate',
        'closed package manifest required')
    require(manifest['task'] == 'O05' and manifest['authority_effect'] == 'none'
        and manifest['actual_owner_outcome'] is None and manifest['visibility'] == 'private-candidate-metadata',
        'package posture cannot infer authority or publicity')
    rows = manifest['files']
    require(type(rows) is list and all(set(b) == {'path', 'sha256'} for b in rows), 'closed output bindings required')
    require(len({b['path'] for b in rows}) == len(rows), 'duplicate package binding')
    require(set(files) == {b['path'] for b in rows} | {'manifest.json'}, 'package file closure differs')
    for b in rows:
        require(not Path(b['path']).is_absolute() and '\\' not in b['path']
            and Path(b['path']).as_posix() == b['path'] and '..' not in Path(b['path']).parts,
            'unsafe output binding path')
        require(sha(files[b['path']]) == b['sha256'], 'original output bytes differ')
    core = parse(files['core.json']); index = parse(files['record-index.json'])
    require(set(core) == CORE_FIELDS and core['task'] == 'O05'
        and core['schema_version'] == 'lab-O05-exact-adaptation-core/v1-candidate', 'closed adaptation core required')
    require(sha(files['core.json']) == manifest['core_sha256'], 'adaptation core digest differs')
    require(core['scope_binding'] == translator.scope_binding and core['profile_binding'] == translator.profile_binding
        and core['selection_binding'] == translator.scope['selection_binding']
        and manifest['source_selection_binding'] == translator.scope['selection_binding']
        and manifest['profile_binding'] == translator.profile_binding, 'package source/profile/scope join differs')
    require(core['definition_witnesses'] == translator.definition_witnesses
        and core['code_bindings'] == translator.code_bindings, 'Definition or adapter byte closure differs')
    require(core['actual_owner_outcome'] is None and core['authority_effect'] == 'none'
        and core['visibility'] == manifest['visibility'], 'adaptation core posture differs')
    for k in ('domain_instances_conformed', 'global_typed_relations_created',
              'source_bodies_copied', 'source_effects_applied'):
        require(core[k] == 0, 'unauthorized adaptation effect: ' + k)
    require(core['excluded_packages'] == translator.selection['excluded_packages']
        and core['deferred_source_epoch'] == translator.selection['standalone_product_successor']
        and core['outside_references'] == translator.selection['unresolved_questions'], 'source gaps/epochs dropped')
    require(core['selector_observations'] == translator.selectors(), 'literal selector evidence differs')
    require(type(index) is list and all(set(r) == INDEX_FIELDS for r in index), 'closed carrier index required')
    require(len({r['node_id'] for r in index}) == len(index)
        and len({r['path'] for r in index}) == len(index), 'duplicate carrier identity or bytes')
    expected_counts = {'source': 131, 'ontology-node': 38, 'ontology-edge': 50, 'generated-output': 1}
    require(manifest['counts'] == expected_counts
        and dict(collections.Counter(r['kind'] for r in index)) == expected_counts, 'carrier disposition counts differ')
    require(core['record_index'] == [r for r in index if r['kind'] != 'generated-output'], 'core output index differs')
    records = {}; by_path = {}
    for row in index:
        require(row['kind'] in SCHEMA_REFS and row['carrier_ref'] == SCHEMA_REFS[row['kind']]
            and row['schema_binding'] == translator.schema_bindings[row['carrier_ref']], 'unselected exact carrier schema')
        require(row['path'] == 'records/' + row['kind'] + '/' + sha(row['node_id'].encode()) + '.json',
            'carrier path/identity join differs')
        require(row['version_ref'] == row['node_id'] + '@1.0.0-candidate.1'
            and sha(files[row['path']]) == row['sha256'], 'carrier revision/byte binding differs')
        record = parse(files[row['path']]); schema(record, row['schema_binding'])
        require(record['node_id'] == row['node_id'] and record['kind'] == row['kind'], 'carrier identity/kind differs')
        records[row['version_ref']] = record; by_path[row['path']] = row
    expected_files = {r['path'] for r in index} | {'core.json', 'record-index.json',
        'native.snapshot', 'reproducibility.json', 'manifest.json'}
    require(set(files) == expected_files, 'private body or unselected file included')
    dispositions = core['dispositions']; items = translator.selection['items']
    require(len(dispositions) == len(items) == 140, 'source item accounting incomplete')
    source_records = {}; specs = {}; by_item = {}
    for disposition, item in zip(dispositions, items):
        require(set(disposition) == DISPOSITION_FIELDS, 'closed source disposition required')
        require(disposition['item_id'] == item['item_id'] and disposition['item_kind'] == item['item_kind']
            and disposition['disposition'] == item['disposition'] and disposition['privacy'] == item['privacy']
            and disposition['source_binding'] == item['source_binding']
            and disposition['record_structure_sha256'] == item.get('record_structure_sha256')
            and disposition['original_disposition_reason'] == item['reason']
            and disposition['contract_fit'] == item['contract_fit'], 'source item disposition/provenance/fit differs')
        require(disposition['blocked_dependency_ids'] == item.get('unresolved_dependency_ids', [])
            and disposition['domain_instances_conformed'] == 0 and disposition['actual_owner_outcome'] is None
            and disposition['public_body_export_allowed'] is False, 'source dependencies or posture collapsed')
        outputs = disposition['outputs']
        require(all(row == by_path.get(row['path']) for row in outputs), 'disposition output is not exact package row')
        by_item[item['item_id']] = outputs
        if item['disposition'] == 'block':
            require(not outputs and disposition['blocked_expected_sha256'] == item['expected_sha256'],
                'blocked expected revision fabricated or replaced')
            continue
        require(disposition['blocked_expected_sha256'] is None, 'resolved source relabeled blocked')
        wanted_kinds = ['source'] + (['ontology-node'] if item['item_kind'] == 'node'
            else ['ontology-edge'] if item['item_kind'] == 'relation' else [])
        require([r['kind'] for r in outputs] == wanted_kinds, 'item uses an unintended Lab carrier')
        expected_source = translator.source_record(item)
        require(records[outputs[0]['version_ref']] == expected_source, 'source metadata carrier differs from original')
        source_records[item['item_id']] = expected_source
        if item['item_kind'] == 'node':
            specs[item['legacy_identity']] = translator.node(item, expected_source)
    node_specs = list(specs.values()); edges = [translator.edge(i, specs) for i in items if i['item_kind'] == 'relation']
    all_specs = node_specs + edges
    archive = parse(files['native.snapshot'])
    require(set(archive) == ARCHIVE_FIELDS and archive['schema_version'] == 'lab-O05-private-native-archive/v1-candidate'
        and archive['visibility'] == 'private-candidate-metadata' and archive['authority_effect'] == 'none'
        and archive['actual_owner_outcome'] is None, 'closed private native archive required')
    for k in ('private_key_included', 'Session_memory_included', 'ontology_admission'):
        require(archive[k] is False, 'forbidden native archive content or authority')
    require(archive['source_effects_applied'] == 0 and archive['semantic_cursor'] == archive['governance_cursor'] == 88
        and archive['native_executable_sha256'] == translator.scope['native_executable']['sha256'], 'native source/effect/cursor differs')
    require(core['native_archive_sha256'] == sha(files['native.snapshot'])
        and core['native_semantic_cursor'] == core['native_governance_cursor'] == 88
        and core['native_checkpoint_parity'] == 'PASS', 'native archive/core join differs')
    families = {'semantic': [], 'governance': []}
    for family in families:
        for cursor in range(1, 89):
            name = f'{family}/{cursor:08d}-ontology-{family}:O05:{cursor}.json'
            require(name in archive['files'], 'exact original native event missing')
            b = archive['files'][name]
            require(set(b) == {'sha256', 'base64_original_bytes'}, 'closed native original byte binding required')
            raw = base64.b64decode(b['base64_original_bytes'], validate=True)
            require(sha(raw) == b['sha256'], 'original native event bytes changed')
            families[family].append(parse(raw))
    require(len(archive['files']) == 176, 'unselected native event or private file included')
    for i, (spec, semantic, governance) in enumerate(zip(all_specs, families['semantic'], families['governance'])):
        draft = semantic_draft(spec['state'], i + 1)
        require(set(semantic) == set(draft) and all(semantic[k] == v for k, v in draft.items() if k != 'event_digest'),
            'native semantic state/source/endpoint tuple differs')
        stub = object.__new__(NativeCandidateStore); stub.translator = translator
        provenance = translator.scope['selection_binding']['path'] + '#item=' + quote(spec.get('item_id',
            spec.get('item', {}).get('item_id', '')), safe='')
        expected_governance = governance_draft(stub, semantic, i + 1, provenance)
        require(set(governance) == set(expected_governance)
            and all(governance[k] == v for k, v in expected_governance.items() if k != 'event_digest'),
            'native governance exact tuple, confidence or candidate posture differs')
        if i < 38:
            expected = translator.node_record(spec, semantic, governance); item_id = spec['item_id']
        else:
            expected = translator.edge_record(spec, semantic); item_id = spec['item']['item_id']
        require(records[by_item[item_id][1]['version_ref']] == expected,
            'rich ontology carrier differs from original native event/source profile')
    generated = records[OUTPUT_REF]
    require({k: v for k, v in generated.items() if k not in ('payload', 'relation_refs')} == {
        'schema_version': 'cyberalchemy-lab-generated-output/v2', 'kind': 'generated-output',
        'node_id': OUTPUT_REF.split('@')[0], 'name': 'O05 exact selected legacy metadata adaptation',
        'lifecycle_state': 'candidate', 'authority_effect': 'none', 'owner_ref': OWNER,
        'scope_ref': translator.profile['namespace'], 'evidence_refs': [translator.scope['selection_binding']['path']],
        'challenge_route': OWNER, 'successor_refs': [], 'claim_ceiling': translator.profile['claim_ceiling']},
        'generated output candidate identity/posture differs')
    require(generated['payload']['output_digest'] == 'sha256:' + manifest['core_sha256']
        and generated['payload']['generator_ref'] == bind(HERE / 'build.py')['path'] + '#sha256=' + bind(HERE / 'build.py')['sha256']
        and generated['payload']['reproducibility_receipt_ref'] == translator.scope['output_root'] + '/reproducibility.json',
        'generated output source/compiler/digest join differs')
    source_refs = [r['node_id'] + '@1.0.0-candidate.1' for r in source_records.values()]
    require(generated['payload']['input_refs'] == source_refs
        and generated['relation_refs'] == [{'relation_kind_ref': 'relation.derives-from', 'direction': 'source',
            'counterpart_kind': 'source', 'counterpart_ref': r} for r in source_refs],
        'generated output derivation closure differs')
    reproduction = parse(files['reproducibility.json'])
    require(set(reproduction) == set('schema_version authority_effect actual_owner_outcome core_sha256 profile_binding generator_binding meaning independent_rebuild_verified'.split())
        and reproduction['schema_version'] == 'lab-O05-build-reproduction/v1-candidate'
        and reproduction['authority_effect'] == 'none' and reproduction['actual_owner_outcome'] is None,
        'closed reproduction candidate posture required')
    require(reproduction['core_sha256'] == manifest['core_sha256'] and reproduction['independent_rebuild_verified'] is False
        and reproduction['profile_binding'] == translator.profile_binding
        and reproduction['generator_binding'] == bind(HERE / 'build.py'), 'reproduction inputs or proof ceiling differs')
    actual_replay = read_native(archive, translator.scope['native_executable']) if native else None
    if actual_replay is not None:
        require(actual_replay['semantic_events'] == families['semantic']
            and actual_replay['governance_events'] == families['governance'], 'original native replay differs')
    translator.guard()
    return {'result': 'PASS', 'authority_effect': 'none', 'actual_owner_outcome': None,
        'carriers_checked': len(index), 'counts': manifest['counts'], 'items_reconciled': len(items),
        'blocked_revisions': 9, 'native_semantic_events': 88, 'native_governance_events': 88,
        'native_replay_verified': native, 'selector_statuses': dict(collections.Counter(r['status']
            for r in core['selector_observations'])), 'source_bodies_copied': 0,
        'domain_instances_conformed': 0, 'global_typed_relations_created': 0,
        'core_sha256': manifest['core_sha256']}


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: check.py package-path independent-manifest-sha256')
    with signed_catalog() as (catalog, operations):
        translator = SourceTranslation(catalog, operations)
        print(json.dumps(validate_payload(load_package(sys.argv[1]), translator, sys.argv[2]), sort_keys=True))
