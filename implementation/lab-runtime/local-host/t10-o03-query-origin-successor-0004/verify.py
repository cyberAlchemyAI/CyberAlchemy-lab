"""Cold join of byte-backed O03 runs to frozen response receipts."""
import hashlib
import json
from pathlib import Path
import secure_query

HERE = Path(__file__).resolve().parent
OLD = secure_query.OLD
CODE_SHA = '13f889f60430ebf53818bd9e4648e184dcbb23a2f3456ed01f0af014efa21676'
CASES = {
    'current-specialist-owner': ('CURRENT-SECURE-RESULT.json', '827bbc856d2aac3b0db3ae448d072ec2820e08e045060a231fc0b6a18fb09278',
                                 'run-current-0002', 'c4da8c121facbbc859c000d3ae0f165681ee5777e2d38e95b49d97c9e8fa48f2'),
    'historical-d73-slice': ('HISTORICAL-SECURE-RESULT.json', '0014984d40050d471547dc780f6a312747963235dc6ae29ee42cdf4fe8c784c7',
                             'run-historical-0001', 'ccc8442df4de6e8096602e77d7a0fae3ddc89f184eea5c02634a4faa7079f5f9'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    if sha((HERE / 'secure_query.py').read_bytes()) != CODE_SHA:
        raise ValueError('byte-backed query runner code changed')
    checked = {}
    with secure_query.selected_modules() as (runner, _):
        for scope, (name, expected, previous, previous_sha) in CASES.items():
            path = HERE / name
            if path.is_symlink() or sha(path.read_bytes()) != expected:
                raise ValueError('retained secure query result changed')
            result = json.loads(path.read_bytes())
            predecessor_path = OLD / previous / 'RESULT.json'
            if predecessor_path.is_symlink() or sha(predecessor_path.read_bytes()) != previous_sha:
                raise ValueError('frozen query receipt changed')
            original = runner.verify_result(predecessor_path.parent)
            expected_answers = {key: row['response_digest'] for key, row in original['queries'].items()}
            if (set(result) != {'answer_digests', 'authority_effect', 'loader_sha256', 'module_execution',
                                'probe_sha256', 'query_control_sha256', 'query_run_sha256', 'scope',
                                'selected_governed_models'} or
                    result['scope'] != scope or result['answer_digests'] != expected_answers or
                    result['loader_sha256'] != secure_query.LOADER_SHA or
                    result['probe_sha256'] != secure_query.PROBE_SHA or
                    result['query_control_sha256'] != secure_query.CONTROL_SHA or
                    result['query_run_sha256'] != secure_query.QUERY_SHA or
                    result['module_execution'] != 'compiled from selected bytes with ambient modules displaced' or
                    result['authority_effect'] != 'none' or result['selected_governed_models'] != 0):
                raise ValueError('secure query/original answer join differs')
            checked[scope] = {'secure_result_sha256': expected, 'original_receipt_sha256': previous_sha,
                              'answer_digests': expected_answers}
    return {'schema_version': 'lab-T10-O03-byte-backed-origin-join/v1',
            'secure_runner_sha256': CODE_SHA, 'scopes': checked,
            'o05_source_scope_selected': False, 'authority_effect': 'none',
            'selected_governed_models': 0}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
