#!/usr/bin/env python3
"""Verify literal actual transmission, without semantic novelty grading."""
import hashlib, json
from ac_runtime import read, sha, require, encoded, now
from ac_provenance_fidelity_runtime_v18 import Runtime
from summarize_ac import family

def check(r=None):
    r = r or Runtime()
    r.integrity()
    rows = []
    for arm in ['SHARED', 'DISTINCT', 'UNION']:
        expected = read(r.p('coverage/provenance-fidelity/capsules/' + arm + '.json'))
        case = read(r.p('inputs/cases/J0.json'))
        require(hashlib.sha256(encoded(case)).hexdigest() == expected['case_sha256_canonical_encoded'], 'Literal case hash')
        nodes = []
        for pool in expected['pools']:
            path = r.p('raw/' + pool['job_id'] + '.json')
            body = read(path)
            require(sha(path) == pool['raw_sha256'] and body['candidates'] == pool['candidates'], 'Unchanged literal precursor array')
            nodes.extend(pool['job_id'] + '#' + c['id'] for c in pool['candidates'])
        require(len(nodes) == len(set(nodes)) == 12, 'Job-qualified precursor identities must avoid candidate-ID collisions')
        for route in expected['source_routes']:
            p = r.p('prompts/' + route['job_id'] + '.payload.json')
            require(sha(p) == route['payload_sha256'], 'Actual source allocation packet hash')
            packet = read(p)
            for bank in route['source_banks']:
                require(sha(bank['original_path']) == bank['original_file_sha256'], 'Original source file hash')
                received = packet['routed_sources'][bank['selector_key']]
                require(hashlib.sha256(encoded(received['body'])).hexdigest() == bank['body_sha256_canonical_encoded'], 'Actually supplied selector body hash')
        ex = 'COV-PROVENANCE-' + arm + '-exchange'; build = 'COV-PROVENANCE-' + arm + '-builder'
        for jid in [ex, build]:
            require(r.state(jid)['terminal'] and r.state(jid)['valid'], 'Actual valid native transmission role required')
            w = read(r.p('receipts/jobs/' + jid + '.native-final.json'))
            require(w['observation'] == 'actual_FINAL' and w['handle'] == r.state(jid)['handle'], 'Actual observed native FINAL required')
        exchange = read(r.p('raw/' + ex + '.json')); builder = read(r.p('raw/' + build + '.json'))
        a = json.loads(exchange['handoff']['summary']); b = json.loads(builder['handoff']['summary'])
        packet = read(r.p('prompts/' + build + '.payload.json'))
        require('received_roles' not in packet and 'required_transmission_capsule' not in packet, 'Summary-only assigned builder packet')
        received = packet['received_handoffs'][ex]
        require(received == exchange['handoff']['summary'], 'Actual selected summary received unchanged')
        require(expected == a['capsule'] == json.loads(received)['capsule'] == b['capsule'], 'Full capsule survives actual exchange/input/builder')
        replays = {x['candidate_id']: x['replay'] for x in read(r.p('replays/' + build + '.json'))['candidate_replays']}
        rows.append({'arm': arm, 'literal_twelve_precursors_retained': True, 'qualified_precursor_nodes': nodes, 'source_allocation_hashes_match': True, 'actual_summary_only_packet': True, 'selected_summary_received_sha256_utf8': hashlib.sha256(received.encode()).hexdigest(), 'builder_retained_capsule_equal': True, 'builder_candidates': [{'id': c['id'], 'family_heuristic': family(case, c), 'stipulated_replay_status': replays[c['id']]['status'], 'model_action_count': replays[c['id']].get('action_count')} for c in builder['candidates']], 'exchange_raw_path': str(r.p('raw/' + ex + '.json')), 'builder_raw_path': str(r.p('raw/' + build + '.json'))})
    return {'status': 'pass', 'utc': now(), 'actual_rows': rows, 'role_count': 6, 'not_native_execution_or_semantic_grading': True, 'limits': ['Literal equality and assigned input evidence, not hidden-access authentication', '10000-word transport cap is larger than earlier1800; not matched efficacy or equal compute', 'Original incomplete handoffs and all first grades preserved', 'Copied precursor mechanisms were already supplied; no new-invention inference']}

if __name__ == '__main__': print(json.dumps(check()))
