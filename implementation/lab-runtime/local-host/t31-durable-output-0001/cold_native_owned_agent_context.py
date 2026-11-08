"""Separate-process original-byte consumer of the two actual workflow commits."""
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'), str(HERE)]
import output_store as S

def need(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    need(sys.flags.isolated and sys.dont_write_bytecode, 'isolated no-bytecode consumer required')
    receipt_path = Path(sys.argv[1])
    raw = receipt_path.read_bytes()
    need(S.sha(raw) == sys.argv[2], 'selected actual workflow result differs')
    result = json.loads(raw)
    # Restore the retained original files without regenerating any transaction.
    # The inherited journal deliberately accepts /tmp roots only.
    restored_parent = Path(tempfile.mkdtemp(prefix='cal-T31-archived-cold-'))
    restored_parent.chmod(0o700)
    restored = restored_parent/'workflow'
    shutil.copytree(Path(result['journal_archive']), restored)
    store = S.OutputJournal(restored, result['journal_config_sha256'])
    head, run_raw = store.replay()
    need(head['sequence'] == 2 and json.loads(run_raw)['state'] == 'session-ready', 'original terminal state differs')
    producer = S.read_owned(Path(result['private_persisted_inputs'])/'producer-emission.json')
    need(S.sha(producer) == result['actual_producer_receipt_sha256'], 'actual producer original differs')
    emission = json.loads(producer)
    original_headers = {r['artifact']['version_ref']: r['artifact'] for r in emission['outputs']}
    consumed = []
    for sequence, kinds in ((1, {'cal.artifact-type.context-view/v1', 'cal.artifact-type.ontology-view/v1'}),
                            (2, {'cal.artifact-type.agent-session/v1'})):
        rows = store.consume(sequence)
        need({h['carrier_ref'] for h, body in rows} == kinds, 'original transition carrier closure differs')
        for header, body in rows:
            need(original_headers[header['version_ref']] == header and S.sha(body) == header['byte_sha256'],
                 'cold consumer differs from actual original producer bytes')
            consumed.append({'sequence': sequence, 'artifact': header, 'byte_size': len(body), 'sha256': S.sha(body)})
    negatives = []
    with tempfile.TemporaryDirectory(prefix='cal-T31-cold-isolated-') as folder:
        isolated = Path(folder)/'journal'
        shutil.copytree(store.root, isolated)
        target = isolated/'outputs'/consumed[0]['sha256']
        target.write_bytes(target.read_bytes()+b' ')
        try:
            S.OutputJournal(isolated, result['journal_config_sha256'])
        except (ValueError, OSError):
            negatives.append('changed-original-output-refused-on-cold-open')
        else:
            raise ValueError('changed actual output accepted')
    # No live source, Reader, Session, memory or expired producer grant is used.
    print(json.dumps({'result': 'PASS-independent-two-commit-native-output-consumer',
                      'selected_result_sha256': S.sha(raw), 'journal_head': head,
                      'consumed': consumed, 'isolated_negative_cases': negatives,
                      'retained_original_archive_restored_for_cold_read': True,
                      'runtime_capability_reconstructed': False, 'source_currentness_claimed': False,
                      'canonical_admissions': 0, 'actual_owner_outcome': None}, sort_keys=True))
    shutil.rmtree(restored_parent)

if __name__ == '__main__':
    main()
