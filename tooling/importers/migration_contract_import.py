"""Import an exact source selection into an isolated, contract-checked JSON store."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tooling/validators'))
from migration_contracts import load_registry, REGISTRY


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError('Duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def prepare(plan, source_root):
    registry = load_registry()
    if plan['scope'] != registry['scope'] or plan['registry_sha256'] != digest(ROOT / REGISTRY):
        raise ValueError('Import plan scope or registry differs from admission')
    source = (source_root / plan['source']['path']).resolve()
    if not source.is_relative_to(source_root.resolve()) or digest(source) != plan['source']['sha256']:
        raise ValueError('Source path or hash mismatch')
    rows = read(source)['nodes']
    entries = {x['target_id']: x for x in registry['entries']}
    # The resolver verifies all executable bytes before this engine is imported.
    batch = ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'
    spec = importlib.util.spec_from_file_location('contract_sample_engine', batch / 'engine.py')
    sys.path.insert(0, str(batch))
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    results, accepted, identities = [], [], set()
    for selection in plan['selections']:
        target = selection['target']
        if target not in entries:
            raise ValueError('Unadmitted target: ' + target)
        row = rows[selection['index']]
        if row['id'] != selection['source_id'] or row['id'] in identities:
            raise ValueError('Source identity mismatch or duplicate selection')
        identities.add(row['id'])
        entry = entries[target]
        reasons = []
        kind = target.removeprefix('type.')
        if target not in ['type.product', 'type.product-thesis', 'type.product-capability', 'type.team']:
            raise ValueError('No explicit mapping for target: ' + target)
        schema = read((ROOT / entry['binding']['path']).parent / 'schema.json')
        mapped = {
            'node_id': 'cav2:' + plan['source']['path'] + '#' + row['id'],
            'kind': kind, 'status': 'candidate-unadmitted', 'authority_effect': 'none',
            'scope_ref': plan['scope'], 'owner_ref': row.get('owner_route', ''),
        }
        # Mapping is deliberately restricted; labels do not establish domain instances.
        if kind == 'product' and row.get('role') == 'product':
            for dest, src in {'name': 'label', 'purpose': 'plain_language', 'identity_boundary': 'forbidden_collapse', 'owner_route': 'owner_route'}.items():
                if src in row:
                    mapped[dest] = row[src]
        else:
            reasons.append('No complete instance mapping for source role ' + str(row.get('role')))
        missing = sorted(set(schema['required']) - set(mapped))
        if missing:
            reasons.append('Missing required fields: ' + ', '.join(missing))
        if entry['candidate_definition_dependencies']:
            reasons.append('Candidate Definition dependencies remain unadmitted')
        if row.get('authority_effect') != 'none':
            reasons.append('Source effect requires a separate explicit mapping')
        if not reasons:
            try:
                engine.shape(schema, mapped)
                engine.validate_node(mapped, {mapped['node_id']: mapped})
            except (ValueError, ValidationError) as exc:
                reasons.append('Contract validation failed: ' + str(exc))
        result = {
            'source_id': row['id'], 'target': target,
            'source_binding': {**plan['source'], 'selector': '/nodes/' + str(selection['index'])},
            'contract': entry['contract'], 'status': 'blocked' if reasons else 'imported-candidate',
            'reasons': reasons, 'missing_fields': missing,
            'dependencies': entry['semantic_definition_bindings'], 'source_record': row,
        }
        if not reasons:
            result['record'] = mapped
            accepted.append(mapped)
        results.append(result)
    engine.validate_graph({'schema_version': 'cal-review-graph/v1', 'authority_effect': 'none', 'nodes': accepted, 'relations': []})
    if digest(source) != plan['source']['sha256']:
        raise ValueError('Source changed during import')
    return {
        'schema_version': 'cal-contract-checked-import/v1', 'scope': plan['scope'],
        'registry_sha256': plan['registry_sha256'], 'authority_effect': 'none',
        'source': plan['source'], 'selected': len(results), 'imported': len(accepted),
        'blocked': len(results) - len(accepted), 'records': results,
    }


def run(plan_path, source_root, output):
    result = prepare(read(plan_path), source_root)
    result['plan_sha256'] = digest(plan_path)
    if output.exists():
        raise ValueError('Output already exists; choose a new isolated store')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.contract-import-') as td:
        stage = Path(td) / 'store'
        stage.mkdir()
        (stage / 'import.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        os.rename(stage, output)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--source-root', type=Path, default=ROOT.parent / 'cyberAlchemy-v2')
    args = parser.parse_args()
    try:
        result = run(args.plan, args.source_root, args.output)
    except (ValueError, KeyError, OSError, IndexError) as exc:
        print(json.dumps({'result': 'BLOCK', 'error': str(exc)}))
        return 1
    print(json.dumps({k: result[k] for k in ['selected', 'imported', 'blocked', 'authority_effect']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
