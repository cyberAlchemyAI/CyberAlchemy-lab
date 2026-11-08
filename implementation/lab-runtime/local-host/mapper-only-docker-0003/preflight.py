"""Read-only Mapper selector preflight; always refuses dispatch without a PASS Reader."""
from __future__ import annotations

import json
import resource
import subprocess
from pathlib import Path

import construct

READER_UNKNOWN = Path('/tmp/cal-reader-only-dev-20261020-0001-unified3/evidence/reader-once.terminal.json')
EXTERNAL = construct.LOCAL / 'reader-only-unified-0003-effect-observation/external-exec.json'
STAGE_TERMINAL = construct.STAGE / 'evidence/stage-terminal.json'
STAGE_FREEZE = construct.LOCAL / 'fresh-reader-docker-0008/freeze.json'


def inspect() -> dict:
    state, generated = construct.build()
    saved = json.loads((construct.HERE / 'selection.json').read_bytes())
    construct.require(saved == dict(state, mapper_manifest_sha256=saved['mapper_manifest_sha256']),
                      'selected Mapper construction changed')
    target = construct.HERE / 'generated' / construct.NEW
    construct.require({p.name for p in target.iterdir()} == set(generated) | {'source-manifest.json'},
                      'Mapper generated source inventory differs')
    for name, raw in generated.items():
        construct.require((target / name).read_bytes() == raw, 'Mapper projected bytes changed: ' + name)
    manifest_raw = construct.canonical(state['manifest'])
    construct.require((target / 'source-manifest.json').read_bytes() == manifest_raw and
                      construct.digest(manifest_raw) == saved['mapper_manifest_sha256'],
                      'Mapper source manifest changed')
    for path, expected in (
        (READER_UNKNOWN, state['reader_predecessor']['reader_unified3_terminal_sha256']),
        (EXTERNAL, state['reader_predecessor']['reader_unified3_external_exit_sha256']),
        (STAGE_TERMINAL, state['reader_predecessor']['stage_terminal_sha256']),
        (STAGE_FREEZE, state['reader_predecessor']['stage_freeze_sha256']),
    ):
        construct.require(construct.digest(path.read_bytes()) == expected,
                          'selected predecessor evidence changed: ' + path.name)
    unknown = json.loads(READER_UNKNOWN.read_bytes())
    external = json.loads(EXTERNAL.read_bytes())
    construct.require(unknown['overall'] == 'UNKNOWN' and external['exit_code'] == 2 and
                      saved['reader_predecessor']['reader_cold_open_pass_receipt'] is None,
                      'Reader prerequisite state changed; reselect in a new unit')
    construct.require(not construct.ATTEMPT.exists(), 'selected Mapper attempt occupied')
    archive_permission, traversed = construct.selected_stage_permissions()
    construct.permission_gate(saved['container_identity'],
                              archive_owner=archive_permission,
                              package_owner=(1000, 1000, 0o700),
                              scratch_owner=(1000, 1000, 0o700),
                              traversed=traversed)
    image = subprocess.run(['docker', 'image', 'inspect',
                            saved['selected_image']['id'], '--format',
                            '{{.Config.User}}|{{.Id}}|{{.Os}}|{{.Architecture}}'],
                           capture_output=True, text=True, timeout=10, check=True)
    construct.require(image.stdout.strip() ==
                      '20001:20001|sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874|linux|amd64',
                      'selected Docker image identity or default user differs')
    fs = construct.os.statvfs(construct.ATTEMPT.parent)
    construct.resource_gate(resource.getrlimit(resource.RLIMIT_NOFILE)[0],
                            fs.f_bavail * fs.f_frsize, fs.f_favail,
                            construct.ATTEMPT.exists())
    return {'result': 'HOLD_READER_COLD_OPEN', 'effect': 'NOT_RUN',
            'source_manifest_sha256': saved['mapper_manifest_sha256'],
            'static_rows': len(state['manifest']['files']),
            'reader_terminal': 'UNKNOWN', 'reader_external_exit': 2,
            'fresh_attempt_absent': True,
            'native_container_load_proved': False,
            'selected_effective_container_user': '1000:1000',
            'selected_userns': 'host',
            'staged_archive_mode_owner': '1000:1000/0600',
            'claim_ceiling': 'Inert public-only Mapper construction with one synthetic Docker access probe; no private archive read, native, Reader or Mapper effect.'}


if __name__ == '__main__':
    print(json.dumps(inspect(), sort_keys=True))
