"""Compare full independent C04 catalog with actual selected signed candidate replay.

No transport, Actor, key, writable store, owner outcome or public call is created.
The original source reader performs its guarded isolated replay and cleanup.
"""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v45'
TYPED = BASE / 'typed-extension-preparation-v8'
SOURCE = '8931c159d933d0144791542d0357bdf8ba532a3b12bd68f35ab3d5a347a0624d'
TYPED_SOURCE = '21183a4e9e81049ba53f80242ad1f077465dfee0aac5326a34a98b382a595e73'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(p.read_bytes())
def bind(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())}
def package(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    return module
def guard(path, pin):
    assert sha((path / 'source-manifest.json').read_bytes()) == pin
    for r in load(path / 'source-manifest.json')['files']:
        p = ROOT / r['path']
        assert p.is_file() and not p.is_symlink() and not any(a.is_symlink() for a in p.parents)
        assert sha(p.read_bytes()) == r['sha256']
def put(p, v):
    with p.open('x') as f: json.dump(v, f, sort_keys=True, indent=2); f.write('\n')

def main():
    guard(API, SOURCE); guard(TYPED, TYPED_SOURCE)
    package('_cal_typed_actual_source_api45', API)
    P = importlib.import_module('_cal_typed_actual_source_api45.protocol')
    H = importlib.import_module('_cal_typed_actual_source_api45.handlers')
    package('_cal_typed_actual_source_v8', TYPED)
    A = importlib.import_module('_cal_typed_actual_source_v8.adapter')
    S = importlib.import_module('_cal_typed_actual_source_v8.source_selection')
    B = importlib.import_module('_cal_typed_actual_source_v8.catalog_binding')
    inspector = A.kernel()
    profiles = importlib.import_module(inspector.__package__ + '.profiles')
    sources = importlib.import_module(inspector.__package__ + '.sources')
    selection_path = A.KERNEL / 'profiles/selections.json'
    inputs = load(TYPED / 'kernel-inputs.json')['files']
    bound = next(r for r in inputs if r['path'] == selection_path.relative_to(ROOT).as_posix())
    assert sha(selection_path.read_bytes()) == bound['sha256']
    row = next(r for r in load(selection_path)['selections'] if r['name'] == 'd75')
    assert row['profile_sha256'] == 'bb8ab4538a524031924d8fa5c3352c2f9bc1cd66893c39222615160d0c9fd302'
    assert row['review_sha256'] == 'aa9041fe1f8d1a5988f727a752081a62f1ecdcff26a93ace4d615f01776f414c'
    selected = profiles.select(ROOT, **{k: v for k, v in row.items() if k not in ['name', 'source_materials', 'source_bytes']})
    snapshot = sources.capture(selected)
    catalog = S.select_bound_catalog(snapshot, expected_profile_sha256=row['profile_sha256'],
        expected_snapshot_digest=snapshot['snapshot_digest'], evidence_bytes={})
    print(json.dumps({'phase': 'independent-catalog-captured', 'relations': len(catalog['relations']),
                      'current_carriers': len(catalog['endpoints'])}), flush=True)
    with P.source.replay_source('custody-participation') as view:
        C = view.handle.common; projection = view.data['projection']; baseline = view.data['baseline']; config = view.data['config']
        before = C.digest(projection)
        current = {'admitted-current', 'local-admitted-current'}
        actual_refs = {ref for ref, c in projection['contracts'].items() if c['lifecycle_state'] in current}
        relation_mismatches = sorted(ref for ref in set(catalog['relations']) & set(projection['relation_contracts'])
            if projection['relation_contracts'][ref] != snapshot['relation_contracts'][ref])
        descriptor_mismatches = []; schema_mismatches = []; predecessor_mismatches = []
        for ref in sorted(set(catalog['endpoints']) & actual_refs):
            contract = projection['contracts'][ref]
            if contract['artifact'] != catalog['descriptors'][ref]: descriptor_mismatches.append(ref)
            schema = projection['documents'][contract['schema_path']]
            if contract['schema_selector']: schema = inspector.pointer(schema, contract['schema_selector'][1:])
            if schema != catalog['schemas'][ref]: schema_mismatches.append(ref)
        for ref, relation in catalog['relations'].items():
            actual = projection['subjects'].get(relation['version_ref'])
            old = snapshot['subjects'][relation['version_ref']]
            if actual != old: predecessor_mismatches.append(relation['version_ref'])
        comparisons = {'unselected_current_runtime_carriers': sorted(actual_refs - set(catalog['endpoints'])),
            'missing_current_runtime_carriers': sorted(set(catalog['endpoints']) - actual_refs),
            'unselected_runtime_relation_kinds': sorted(set(projection['relation_contracts']) - set(catalog['relations'])),
            'missing_runtime_relation_kinds': sorted(set(catalog['relations']) - set(projection['relation_contracts'])),
            'relation_body_mismatches': relation_mismatches, 'descriptor_mismatches': descriptor_mismatches,
            'complete_schema_mismatches': schema_mismatches, 'complete_relation_predecessor_mismatches': sorted(predecessor_mismatches),
            'baseline_material_mismatches': sorted(k for k, v in snapshot['materials'].items() if baseline['materials'].get(k) != v),
            'unselected_baseline_materials': sorted(set(baseline['materials']) - set(snapshot['materials']))}
        expected = P.source.parse(P.source.original(view.selected['expected_replay_binding']))
        original_baseline = P.source.parse(view.originals['baseline.json'])
        original_config = P.source.parse(view.originals['config.json'])
        assert baseline == original_baseline
        C.verify_seal(original_config)
        original_config_core = {k: v for k, v in original_config.items() if k != 'digest'}
        assert config == original_config_core
        assert P.source.sha(view.originals['config.json']) == expected['config_sha256']
        assert baseline['snapshot_digest'] == expected['baseline_snapshot_digest']
        actual_binding = B.bind_runtime_catalog(catalog, snapshot, baseline=baseline,
            projection=projection, config=config, head=view.data['head']['transaction_digest'],
            expected_profile_sha256=row['profile_sha256'], expected_baseline_digest=C.digest(original_baseline),
            expected_projection_digest=expected['projection_sha256'],
            expected_config_digest=C.digest(original_config_core), expected_head=expected['expected_head'])
        # Hypothetical candidate bodies/Decision identifiers remain explicitly
        # synthetic. Only their preimage is the actual selected signed replay.
        F = importlib.import_module('_cal_typed_actual_source_v8.test_postimage')
        T = importlib.import_module('_cal_typed_actual_source_v8.postimage')
        F.PostimageTests.setUpClass()
        fixture = F.PostimageTests(); fixture.setUp()
        assert fixture.fixture.snapshot_digest == snapshot['snapshot_digest']
        postimage = T.prepare_exact_postimage(fixture.selection, fixture.inspection,
            fixture.impact, fixture.proposal, projection=projection, config=config,
            head=view.data['head']['transaction_digest'], expected_projection_digest=expected['projection_sha256'],
            expected_config_digest=C.digest(original_config_core), expected_head=expected['expected_head'],
            read_material=lambda binding: fixture.materials[binding['ref']],
            independently_selected_schema_paths=fixture.schema_paths,
            independently_selected_catalog_snapshot=snapshot,
            independently_selected_runtime_baseline=baseline,
            expected_runtime_baseline_digest=C.digest(original_baseline),
            expected_catalog_profile_sha256=row['profile_sha256'])
        assert postimage['result'] == 'PASS' and postimage['actual_transactions_written'] == 0
        value = {'schema_version': 'lab-typed-actual-source-comparison/v1-candidate',
            'result': 'BOUND-POSTIMAGE-PASS', 'actual_preimage_candidate_postimage': postimage,
            'candidate_targets_are_hypothetical': True, 'comparisons': comparisons, 'runtime_catalog_binding': actual_binding,
            'actual_expected_replay_pins_used': True, 'actual_original_baseline_and_config_verified': True,
            'selected_source_name': view.selected['name'], 'selected_source_cut': H.cut(view),
            'independent_C04_snapshot_digest': snapshot['snapshot_digest'], 'runtime_baseline_snapshot_digest': baseline['snapshot_digest'],
            'runtime_config_source_snapshot_digest': config['source_snapshot_digest'],
            'equal_snapshot_envelope_digests': snapshot['snapshot_digest'] == baseline['snapshot_digest'],
            'runtime_configuration_digest': C.digest(config), 'runtime_projection_digest': before,
            'actual_HEAD': view.data['head']['transaction_digest'], 'runtime_relation_count': len(projection['relation_contracts']),
            'runtime_current_carrier_count': len(actual_refs), 'independent_profile_binding': selected.controls['profile'],
            'independent_review_binding': {'path': row['review_path'], 'sha256': row['review_sha256']},
            'actual_archive_binding': view.selected['archive_binding'], 'actual_expected_replay_binding': view.selected['expected_replay_binding'],
            'source_binding': bind(API / 'source-manifest.json'), 'typed_source_binding': bind(TYPED / 'source-manifest.json'),
            'script_binding': bind(Path(__file__).resolve()), 'exact_signed_candidate_replay': True,
            'actual_transport_authenticated': False, 'actual_public_calls': 0, 'actual_transactions_written': 0,
            'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False,
            'claim_ceiling': 'Full catalog and hypothetical candidate postimage over actual independently selected signed candidate replay only; not latest repository authority, actual transport/Actor, public typed operation or admission.'}
        assert C.digest(projection) == before
    assert sources.freshness(ROOT, snapshot)['status'] == 'current'
    guard(API, SOURCE); guard(TYPED, TYPED_SOURCE)
    value['original_reader_guarded_exit_completed'] = True
    put(RUN / 'typed-actual-source-comparison-0005.json', value)
    print(json.dumps({'result': value['result'], 'equal_snapshot_envelope_digests': value['equal_snapshot_envelope_digests'],
                      'mismatch_counts': {k: len(v) for k, v in comparisons.items()}}), flush=True)

if __name__ == '__main__': main()
