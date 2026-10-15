#!/usr/bin/env python3
"""Bundle packet adapter preserving readable failed outputs without repairing them.

Same frozen shuffle and judge template as blind_packets.py. Adds explicit
terminal-failure accounting and retains invalid-but-readable source artifacts.
"""
import argparse, hashlib, json, random
from pathlib import Path

R = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unit_packet(unit, packet_id):
    raw, sources, failures = [], [], []
    post = None
    uid = unit['unit_id']
    for role in unit['roles']:
        output = R / 'outputs' / uid / f'{role}.json'
        receipt = R / 'receipts' / f'{uid}-{role}.json'
        skipped = R / 'receipts' / f'{uid}-{role}-disposition.json'
        if not receipt.exists():
            assert skipped.exists(), f'{uid}/{role}: work remains pending'
            disposition = read(skipped)
            assert disposition['disposition'] == 'not_executed_dependency_failed'
            assert disposition['native_invocation'] is False and not output.exists()
            dependency = R / disposition['dependency_receipt']
            assert sha(dependency) == disposition['dependency_receipt_sha256']
            assert not read(dependency)['artifact_validation']['valid']
            failures.append({'role': role, 'error': 'not_executed_dependency_failed'})
            continue
        rc = read(receipt)
        assert rc['join_status'] == 'completed', f'{uid}/{role}: native join pending'
        validation = rc['artifact_validation']
        assert output.exists() and sha(output) == validation['sha256']
        data = read(output)
        assert isinstance(data, dict), 'Unreadable role shape needs an explicit separate disposition'
        if role != 'D':
            assert isinstance(data.get('openings'), list), 'Unstructured raw output needs an explicit separate disposition'
        if not validation['valid']:
            failures.append({'role': role, 'error': 'output_contract_validation',
                             'validation_errors': validation['errors']})
        sources.append({'role': role, 'path': str(output.relative_to(R)),
                        'sha256': sha(output), 'execution_valid': validation['valid']})
        if role == 'D':
            post = data
        else:
            raw.append(data)
    packet = {'packet_id': packet_id, 'case_id': unit['case_id'], 'raw': raw,
              'post_distill': post, 'execution_failures': failures}
    mapping = {'packet_id': packet_id, 'unit_id': uid, 'case_id': unit['case_id'],
               'condition': unit['condition'], 'repetition': unit['repetition'],
               'source_outputs': sources, 'execution_valid': not failures}
    return packet, mapping

def build(case):
    schedule = read(R / 'schedule.json')
    rows = [u for u in schedule['units'] if u['phase'] == 'bundle' and u['case_id'] == case]
    assert len(rows) == 8
    case_number = int(case[1:])
    random.Random(schedule['blind_seed'] + 100 + case_number).shuffle(rows)
    # Read/check the whole batch before writing anything; pending work cannot be frozen.
    prepared = [unit_packet(u, f'{case}-P{i:03d}') for i, u in enumerate(rows, 1)]
    base = R / 'blinded' / 'bundle' / case
    assert not (base / 'manifest.json').exists(), 'Packets already frozen'
    base.mkdir(parents=True, exist_ok=True)
    packets, mappings = [], []
    for packet, mapping in prepared:
        path = base / f'{packet["packet_id"]}.json'
        assert not path.exists(), 'Never overwrite a saved packet'
        path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n')
        packets.append({'packet_id': packet['packet_id'], 'file': str(path), 'sha256': sha(path)})
        mappings.append(mapping)
    manifest = {'phase': 'bundle', 'case_id': case, 'packet_count': len(packets),
                'case_path': str(R / 'cases' / f'{case}.json'),
                'archive_path': str(R / 'archives' / f'{case}.json'), 'packets': packets,
                'adapter_sha256': sha(Path(__file__)),
                'failed_units': sum(not m['execution_valid'] for m in mappings)}
    (base / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (R / 'reports' / f'bundle-{case}-blind-mapping.json').write_text(json.dumps(mappings, indent=2) + '\n')
    for judge in [1, 2]:
        order = packets.copy()
        random.Random(schedule['blind_seed'] + 100 + case_number + 1000 * judge).shuffle(order)
        out = R / 'reviews' / f'bundle-{case}-J{judge}.json'
        task = (R / 'prompts/judge.txt').read_text()
        task += '\nExecution-disposition encoding: some packets may contain unchanged readable artifacts with validation errors. Assess the available raw text under the same criteria and preserve the execution-failure disposition. If post_distill is null, its retention cannot be observed: record uncertain with empty post_ids and explain that the stage was not executed. Do not invent or repair an absent output. A failed unit does not establish zero novelty or a successful complete workflow.\n'
        task += f'\nCase: {manifest["case_path"]}\nArchive: {manifest["archive_path"]}\nJudge_id: J{judge}\nPacket order (read each; preserve independence):\n'
        task += json.dumps(order, indent=2)
        task += f'\nExact output file: {out}\nDo not read conditionmapping files or peerreviews. No extra file writes.\n'
        path = R / 'prompts/jobs' / f'judge-bundle-{case}-J{judge}.txt'
        assert not path.exists(), 'Never overwrite a review prompt'
        path.write_text(task)
    return {'packet_count': len(packets), 'failed_units': manifest['failed_units'],
            'manifest': str(base / 'manifest.json')}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('case', choices=['D1', 'D2'])
    args = parser.parse_args()
    print(json.dumps(build(args.case), indent=2))
