"""Cold readback of one actual API41 inherited guarded-read result."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v41-current-source8-0001'
SOURCE_SHA = '69c872681c53ff02ba5d38ef0f80d866d75f0b9e8c6b6d5d214b9adc2ba70961'
PROFILE_SHA = '18ed4a8a577679211ee5f530ea8148fc18cb0dd0a29ef16de73d6ea761eb9860'
TEST_SHA = '0c15a40694a78185d866b669afe752f1634180f537e3bd18d78ada4cea970b4d'
LOG_SHA = '7ce591de635ba95fbba5b6d6a72c9e2e0ac12e5b72aa63eea0b0d5f8c9241d90'
EXPECTED = re.compile(
    r'test_snapshot_header_mutation_rejected '\
    r'\(__main__\.CurrentGuardedReads\.test_snapshot_header_mutation_rejected\) \.\.\. ok\n'
    r'\n-+\nRan 1 test in 84\.681s\n\nOK\n'
)


def sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError('selected API41 readback input missing or linked')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    selected = [(API / 'source-manifest.json', SOURCE_SHA),
                (API / 'contract-profile.json', PROFILE_SHA),
                (HERE / 'test_current_guarded_reads.py', TEST_SHA),
                (HERE / 'working/targeted-snapshot-header-0002.log', LOG_SHA)]
    if any(sha(path) != expected for path, expected in selected):
        raise ValueError('API41 targeted readback input changed')
    log = selected[-1][0].read_text()
    if EXPECTED.fullmatch(log) is None:
        raise ValueError('targeted guarded-read test did not terminate 1/1 PASS')
    result = {
        'schema': 'cal-API41-current-guarded-read-targeted-readback/v1',
        'result': 'PASS',
        'tested_method': 'CurrentGuardedReads.test_snapshot_header_mutation_rejected',
        'actual_tests_run': 1,
        'actual_elapsed_seconds': 84.681,
        'api_source_manifest_sha256': SOURCE_SHA,
        'api_profile_sha256': PROFILE_SHA,
        'test_source_sha256': TEST_SHA,
        'test_log_sha256': LOG_SHA,
        'claim_ceiling': 'One inherited snapshot-header mutation refusal on current Source8; no whole guarded-read class or historical Source5 claim.',
    }
    output = HERE / 'working/targeted-result-0002.json'
    if output.exists():
        raise ValueError('targeted readback result already exists')
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': result['result'], 'actual_tests_run': 1}, sort_keys=True))


if __name__ == '__main__':
    main()
