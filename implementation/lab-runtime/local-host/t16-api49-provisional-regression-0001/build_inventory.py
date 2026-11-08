"""Closed, provisional 323/345 inherited API regression inventory."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v49-t31-current-guard-0002'
OLD = ROOT / 'product/lab/release-candidates/v1/interface/api-v96'
PLAN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-plan-0274.json'
MAP = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-map-0270.py'
OUT = HERE / 'INVENTORY-0001.json'
PINS = {
    'source': 'e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1',
    'profile': 'dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5',
    'plan': 'b04c3f6a9953765b807adf4f8ef72b480c6c51985a1b1c563535395f86b8ac40',
    'map': '33e3155ac98f12eeeb407f52182de9b2cd7abba14671674c68b67c7dd9ade314',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    for key, path in [('source', API / 'source-manifest.json'), ('profile', API / 'contract-profile.json'),
                      ('plan', PLAN), ('map', MAP)]:
        if digest(path) != PINS[key]:
            raise ValueError(key + ' selected byte differs')
    spec = importlib.util.spec_from_file_location('_cal_t16_exact_map', MAP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old = module.discover(OLD)
    current = module.discover(API)
    plan = json.loads(PLAN.read_bytes())
    old_ids = set(old['methods'])
    ids = set(current['methods'])
    expected = set(plan['all_declared_methods'])
    if not (len(old_ids) == 323 and len(ids) == len(expected) == 345 and old_ids <= ids and ids == expected):
        raise ValueError('323/345 inherited method set differs')
    buckets = {'sequential:' + k: v for k, v in plan['sequential_classes'].items()}
    buckets.update({'worker:' + k: v for k, v in plan['workers'].items()})
    listed = [name for names in buckets.values() for name in names]
    if len(listed) != len(set(listed)) or set(listed) != ids:
        raise ValueError('class bucket coverage differs')
    for bucket, names in buckets.items():
        classes = {name.rsplit('.', 1)[0] for name in names}
        if len(classes) != 1 or classes != {bucket.split(':', 1)[1]} and bucket.startswith('sequential:'):
            raise ValueError('whole class bucket differs')
        one = next(iter(classes))
        if set(names) != set(current['classes'][one]['methods']):
            raise ValueError('class method coverage differs')
    rows = {name: {'ast_sha256': row['method_ast_sha256'], 'file': row['file'],
                   'class': row['class'], 'method': row['method']}
            for name, row in current['methods'].items()}
    changed = sorted(name for name in old_ids if old['methods'][name]['method_ast_sha256'] != rows[name]['ast_sha256'])
    value = {
        'schema_version': 'lab-t16-api49-provisional-inventory/v1',
        'api_directory': API.relative_to(ROOT).as_posix(),
        'selected_source_sha256': PINS['source'], 'selected_profile_sha256': PINS['profile'],
        'historical_plan_sha256': PINS['plan'], 'historical_map_sha256': PINS['map'],
        'historical_original_source_sha256': plan['original_source_sha256'],
        'historical_original_profile_sha256': plan['original_profile_sha256'],
        'original_declared_methods': sorted(old_ids), 'current_declared_methods': sorted(ids),
        'inherited_original_count': 323, 'current_count': 345,
        'added_methods': sorted(ids - old_ids), 'changed_original_method_asts': changed,
        'methods': rows, 'buckets': buckets,
        'test_files': {name: digest(API / name) for name in current['modules']},
        'source_manifest_file_count': len(json.loads((API / 'source-manifest.json').read_bytes())['files']),
        'test_execution_performed': False, 't15_final_freeze_selected': False,
        't16_full_qualification': False, 'authority_effect': 'none',
    }
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    value = build()
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    if args.verify:
        if OUT.read_bytes() != raw:
            raise ValueError('retained inventory differs')
    else:
        with OUT.open('xb') as stream:
            stream.write(raw)
    print(json.dumps({'inventory_sha256': hashlib.sha256(raw).hexdigest(),
                      'original': len(value['original_declared_methods']),
                      'current': len(value['current_declared_methods']),
                      'buckets': len(value['buckets']),
                      'changed_original_asts': len(value['changed_original_method_asts'])}))


if __name__ == '__main__':
    main()
