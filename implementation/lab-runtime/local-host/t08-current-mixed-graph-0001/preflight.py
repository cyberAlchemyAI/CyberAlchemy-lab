"""Fast exact seventh selection proof for the 13 original graph input files."""

import json
from pathlib import Path
import tempfile

import run as R


def inspect():
    p, g, tests, host, content = R.modules()
    source = p.parse(R.selected(R.API + '/source-manifest.json', R.SOURCE_SHA))
    profile = p.parse(R.selected(R.API + '/contract-profile.json', R.PROFILE_SHA))
    rows = {(row['path'], row['sha256'])
            for row in source['files'] + profile['files']}
    cut = {
        'branch_ref': 'technical:T08-current-mixed/branch',
        'store_ref': 'technical:T08-current-mixed/store',
        'commit_sequence': 0,
        'commit_sha256': R.sha(b'T08-current-mixed-technical-branch'),
        'source_profile_sha256': R.PROFILE_SHA, 'streams': []}
    with tempfile.TemporaryDirectory(prefix='cal-t08-mixed-preflight-', dir='/tmp') as place:
        parent = Path(place)
        parent.chmod(0o700)
        policy, eligibility, physical = R.policy_material(
            tests, parent,
            {'ref': R.API + '/source-manifest.json', 'sha256': R.SOURCE_SHA},
            {'ref': R.API + '/contract-profile.json', 'sha256': R.PROFILE_SHA}, cut)
        bindings = [{'file_id': file_id, 'path': path,
                     'sha256': R.sha((R.ROOT / path).read_bytes())}
                    for file_id, path in sorted(physical.items())]
        R.need(all((row['path'], row['sha256']) in rows for row in bindings),
               'original graph input absent or changed from seventh selection')
        R.need(len({row['path'] for row in bindings}) == len(bindings) == 13,
               'closed original graph file set differs')
        return {
            'schema_version': 'lab-T08-current-mixed-graph-preflight/v1-candidate',
            'result': 'PASS-exact-public-graph-input-selection',
            'source_sha256': R.SOURCE_SHA, 'profile_sha256': R.PROFILE_SHA,
            'source_row_count': len(source['files']),
            'profile_row_count': len(profile['files']),
            'selected_graph_files': bindings,
            'graph_policy_node_count': len(policy['nodes']),
            'graph_policy_profile_count': len(policy['profiles']),
            'graph_policy_declaration_count': len(policy['declarations']),
            'technical_cut_only': True, 'whole_reader_executed': False,
            'host_guard_executed': False, 'authority_effect': 'none',
            'T08_complete': False}


if __name__ == '__main__':
    print(json.dumps(inspect(), sort_keys=True, indent=2))
