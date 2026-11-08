"""Rebind the reviewed boundary helper to the disjoint API33 reader successor."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'implementation/lab-runtime/local-host/t35-phase-observer-current-reader-0001'
OLD_API = 'product/lab/release-candidates/v1/interface/api-integration-v33-t35-current-reader-0001/'
NEW_API = 'product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002/'
OLD_OBSERVER_SHA = 'ca9462797c085885bf45f26b3c3790afd9292227e1e41bde47adbba6ecb7d448'
OLD_SELECTION_SHA = '903956f1cdd1bc4825a83d1ecdc63870c4966202fc14192a1c97c44708adff75'
OLD_MANIFEST_SHA = 'b7fe1be6e05c48856791fe010b0ba007c38424d552b3007c33b59e8729eda827'
NEW_MANIFEST_SHA = '094d456fb4cddca37a83b03f1562b26afc3527d98d4bede752a69a0f63b7884f'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    observer = (OLD / 'observe.py').read_bytes()
    selection = (OLD / 'selected-boundaries.json').read_bytes()
    if sha(observer) != OLD_OBSERVER_SHA or sha(selection) != OLD_SELECTION_SHA:
        raise ValueError('reviewed predecessor changed')
    if sha((ROOT / (OLD_API + 'source-manifest.json')).read_bytes()) != OLD_MANIFEST_SHA:
        raise ValueError('API33 predecessor changed')
    if sha((ROOT / (NEW_API + 'source-manifest.json')).read_bytes()) != NEW_MANIFEST_SHA:
        raise ValueError('API33 reader successor changed')
    changed = observer.replace(OLD_API.encode(), NEW_API.encode())
    changed = changed.replace(OLD_MANIFEST_SHA.encode(), NEW_MANIFEST_SHA.encode())
    if changed.count(b'compile(path.read_bytes(), str(path), "exec", dont_inherit=True)') != 1:
        raise ValueError('corrected observer compiler shape changed')
    if changed == observer or OLD_API.encode() in changed or OLD_MANIFEST_SHA.encode() in changed:
        raise ValueError('observer replacement incomplete')
    (HERE / 'observe.py').write_bytes(changed)
    selected = json.loads(selection)
    selected['api_source_manifest_binding'] = {'path': NEW_API + 'source-manifest.json',
                                                'sha256': NEW_MANIFEST_SHA}
    for item in selected['boundaries']:
        if item['path'].startswith(OLD_API):
            item['path'] = NEW_API + item['path'][len(OLD_API):]
            item['sha256'] = sha((ROOT / item['path']).read_bytes())
    (HERE / 'selected-boundaries.json').write_text(json.dumps(selected, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'observer_sha256': sha(changed),
                      'selection_sha256': sha((HERE / 'selected-boundaries.json').read_bytes()),
                      'boundary_count': len(selected['boundaries'])}, sort_keys=True))


if __name__ == '__main__':
    main()
