"""Read back two actual API41 native-reader origin refusals."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v41-current-source8-0001'
SELECTED = {
    API / 'source-manifest.json': '69c872681c53ff02ba5d38ef0f80d866d75f0b9e8c6b6d5d214b9adc2ba70961',
    API / 'contract-profile.json': '18ed4a8a577679211ee5f530ea8148fc18cb0dd0a29ef16de73d6ea761eb9860',
    HERE / 'test_current_guarded_reads.py': '0c15a40694a78185d866b669afe752f1634180f537e3bd18d78ada4cea970b4d',
    HERE / 'working/targeted-reader-negatives-0001.log': '52c34b3659cc672963b08272d333f48a4f1dd4ea51c3f39568d41896e32216c3',
}
METHODS = ('test_changed_native_reader_class_refused', 'test_changed_native_reader_origin_refused')


def main():
    for path, expected in SELECTED.items():
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('selected current native-reader negative input differs')
    log = (HERE / 'working/targeted-reader-negatives-0001.log').read_text()
    for method in METHODS:
        row = method + ' (__main__.CurrentGuardedReads.' + method + ') ... ok'
        if log.count(row) != 1:
            raise ValueError('actual reader refusal test did not PASS exactly once')
    if len(re.findall(r'\btest_[^\n]+\.\.\. ok\b', log)) != 2 or not log.endswith('Ran 2 tests in 63.311s\n\nOK\n'):
        raise ValueError('two-case reader-negative test result differs')
    result = {
        'schema': 'cal-API41-current-native-reader-negative-readback/v1',
        'result': 'PASS', 'actual_tests_run': 2, 'actual_elapsed_seconds': 63.311,
        'methods': list(METHODS),
        'selected_bindings': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': digest}
                              for path, digest in SELECTED.items()],
        'claim_ceiling': 'Current Source8 reader class/origin refusal with actual native replay; no whole guarded-read class claim.',
    }
    out = HERE / 'working/targeted-reader-negatives-result-0001.json'
    if out.exists():
        raise ValueError('native reader negative result already exists')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': 'PASS', 'actual_tests_run': 2}, sort_keys=True))


if __name__ == '__main__':
    main()
