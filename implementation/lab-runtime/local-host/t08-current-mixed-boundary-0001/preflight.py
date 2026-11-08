"""Construct the exact technical selector and exercise pure coverage refusals."""

import copy
import json
from pathlib import Path
import tempfile
import sys
import traceback

import run_boundary as R


def run():
    p, g, tests, host, content = R.modules()
    source_name = R.API + '/source-manifest.json'
    profile_name = R.API + '/contract-profile.json'
    source_raw = R.selected(source_name, R.SOURCE_SHA)
    profile_raw = R.selected(profile_name, R.PROFILE_SHA)
    source_binding = {'ref': source_name, 'sha256': R.SOURCE_SHA}
    profile_binding = {'ref': profile_name, 'sha256': R.PROFILE_SHA}
    cut = {'branch_ref': 'technical:T08-current-mixed/branch',
           'store_ref': 'technical:T08-current-mixed/store', 'commit_sequence': 0,
           'commit_sha256': R.sha(b'T08-current-mixed-technical-branch'),
           'source_profile_sha256': R.PROFILE_SHA, 'streams': []}
    with tempfile.TemporaryDirectory(prefix='cal-t08-full-preflight-', dir='/tmp') as dirname:
        root = Path(dirname)
        root.chmod(0o700)
        template = root / 'template'
        template.mkdir(mode=0o700)
        private = root / 'private'
        private.mkdir(mode=0o700)
        policy, eligibility, physical = R.policy_material(
            tests, template, source_binding, profile_binding, cut)
        reader, anchor, selector, roots, policy_raw, eligibility_raw, scope_raw = R.make_reader(
            p, source_raw, profile_raw, source_binding, profile_binding, cut,
            policy, eligibility, physical, private)
        semantic = {'anchor': {
            'policy_binding': {'ref': 'technical:T08-mixed/policy', 'sha256': R.sha(policy_raw)},
            'eligibility_binding': {'ref': 'technical:T08-mixed/eligibility',
                                    'sha256': R.sha(eligibility_raw)},
            'source_binding': source_binding, 'profile_binding': profile_binding,
            'source_cut': cut, 'allowed_states': ['candidate-current']},
            'policy_file_id': 'policy', 'declared_edges': [R.EDGE],
            'root_refs': [R.EDGE['source']]}
        reader, anchor, binding, scope, selector = R.full_content_reader(
            p, content, reader, selector, roots, semantic,
            source_binding, profile_binding, cut, private)
        if '--port-constructor' in sys.argv:
            try:
                content.PrivateHistoricalContent((private / 'scope-full.json').read_bytes(),
                                                 binding, reader, p, g, R.ROOT)
            except BaseException as error:
                print(json.dumps({'result': 'REFUSED', 'failure_class': type(error).__name__,
                                  'frames': [{'file': Path(frame.filename).name,
                                              'line': frame.lineno, 'function': frame.name}
                                             for frame in traceback.extract_tb(error.__traceback__)],
                                  'authority_effect': 'none'}, sort_keys=True))
                raise SystemExit(1)
            print(json.dumps({'result': 'PASS-port-constructor-only',
                              'reader_boundary_executed': False, 'authority_effect': 'none'},
                             sort_keys=True))
            return None
        original = {row['original_binding']['path']: row['original_binding']['sha256']
                    for row in scope['coverage']}
        history = p.parse(R.selected(*content.HISTORICAL25))
        historical25 = {row['binding']['path']: row['binding']['sha256']
                        for row in history['rows']}

        def check(coverage, entries):
            return content.check_coverage_current(original, coverage, entries,
                                                  reader.roots, R.ROOT, historical25)

        positive = check(scope['coverage'], reader.files)
        negatives = {}
        historical_native_id = next(row['file_id'] for row in scope['coverage']
                                    if row['original_binding']['path'] == content._base.NATIVE_ORIGINAL)
        for name, coverage, entries in (
            ('missing-historical-edge', scope['coverage'][:-1], reader.files),
            ('substituted-historical-proof',
             [dict(row, original_binding={'path': row['original_binding']['path'],
                                           'sha256': '0' * 64}) if i == 0 else row
              for i, row in enumerate(scope['coverage'])], reader.files),
            ('changed-native-historical-alternate', scope['coverage'],
             {**reader.files, historical_native_id:
              {**reader.files[historical_native_id], 'sha256': '0' * 64}}),
        ):
            try:
                check(coverage, entries)
            except ValueError:
                negatives[name] = 'REFUSED'
            else:
                raise ValueError('pure selected coverage negative accepted: ' + name)
        return {'schema_version': 'lab-T08-current-mixed-full-selector-preflight/v1-candidate',
                'result': 'PASS-constructor-and-pure-coverage',
                'selected_files': len(reader.files), 'selected_roots': len(reader.roots),
                'historical_coverage_rows': len(scope['coverage']),
                'historical_mapping': positive, 'negative_checks': negatives,
                'protected_reader_constructor_passed': True,
                'protected_reader_boundary_executed': False,
                'historical_content_verified': False,
                'semantic_graph_executed': False,
                'authority_effect': 'none', 'T08_complete': False}


if __name__ == '__main__':
    result = run()
    if result is not None:
        print(json.dumps(result, sort_keys=True, indent=2))
