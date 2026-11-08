"""No-replace API53: select one exact public schema document as private material."""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v52-t31-agent-context-guard-0003'
NEW = BASE / 'api-integration-v53-t31-schema-material-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api52-original-output-bootstrap-0003/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api53-schema-material-bootstrap-0001/bootstrap.py'
OLD_SOURCE = 'd14fc1c7e1a4bc941873a5b7fc0adb2dcd95ca16383788df25055e6ee5bb9b72'
OLD_PROFILE = 'a7d99f8b9188d1b45de96f6f5b13e2ee1f1fa6ede64121abaf0eb88793e7c0a2'
OLD_ADAPTER_SHA = '1396f1a67865a41f9043db638799a09a6b8e18b40d0f926df8c686d17f2f21c6'
SCHEMA_PATH = 'authority/artifact-types/agent-session/v1/schema.json'
SCHEMA_SHA = 'e05780ad1ee2f87cc4bc288a05cca24c6e0ac35e97771ff689de0ec64d14aae8'
CLAIM = ('Exact selected public AgentSession schema material allowance, current-profile/Work tailored '
         'agent-context instance; no producer output, WorkflowRun append, later consumer, '
         'original 28-transition increment, Work satisfaction, canonical admission or owner effect.')


def sha(raw): return hashlib.sha256(raw).hexdigest()


def exact(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed path required')
    handles = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('selected regular input required')
            chunks = []
            while block := os.read(fd, 1024 * 1024):
                chunks.append(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda v: (v.st_dev, v.st_ino, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(named):
                raise ValueError('selected input changed during read')
            return b''.join(chunks)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def digest(path): return sha(exact(path))


def row(path):
    return {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def new_file(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def save(path, value):
    new_file(path, (json.dumps(value, sort_keys=True, indent=2) + '\n').encode())


def replace_exact(raw, old, new, count):
    if raw.count(old) != count:
        raise ValueError('exact API49 edit anchor differs: ' + old[:80])
    return raw.replace(old, new)


def main():
    if digest(OLD / 'source-manifest.json') != OLD_SOURCE or digest(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API49 source/profile differs')
    if digest(OLD_ADAPTER) != OLD_ADAPTER_SHA:
        raise ValueError('frozen API49 assembler differs')
    if NEW.exists() or NEW_ADAPTER.exists():
        raise ValueError('versioned API53 output already exists')
    manifest = json.loads(exact(OLD / 'source-manifest.json'))
    profile = json.loads(exact(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 209 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('API52 selected inventory differs')
    physical = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
                and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                and '__pycache__' not in p.parts and 'receipts' not in p.parts
                and p.suffix != '.pyc'}
    if physical != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API52 physical/source closure differs')
    for selected in own:
        if digest(OLD / selected['path'][len(old_prefix):]) != selected['sha256']:
            raise ValueError('frozen API52 selected byte differs')

    schema = exact(OLD / 'workflow-output-plan.schema.json').decode()
    old_service = old_prefix + 'service.py'
    new_service = new_prefix + 'service.py'
    schema = replace_exact(schema, old_service, new_service, 2)
    registry = exact(OLD / 'workflow_output_registry.py').decode()
    registry = replace_exact(registry, old_prefix + 'workflow_', new_prefix + 'workflow_', 7)
    bridge = exact(OLD / 'source_bridge.py').decode()
    bridge = replace_exact(bridge, '_cal_api52_t31_legacy_local_20261023_0001',
                           '_cal_api53_t31_legacy_local_20261023_0001', 1)
    bridge = replace_exact(bridge, '_cal_api52_t31_source8_local_20261023_0001',
                           '_cal_api53_t31_source8_local_20261023_0001', 1)
    guard = exact(OLD / 'guard.py').decode()
    guard = replace_exact(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(),
                          NEW_ADAPTER.relative_to(ROOT).as_posix(), 1)
    old_helper = "helper_paths.add('implementation/lab-runtime/local-host/t31-api53-schema-material-bootstrap-0001/bootstrap.py')"
    new_helper = old_helper + "\n    helper_paths.add('authority/artifact-types/agent-session/v1/schema.json')"
    guard = replace_exact(guard, old_helper, new_helper, 1)
    workspace = exact(OLD / 'workspace.py').decode()
    allowance = ("SCHEMA_MATERIAL_REF='private:T31:bridge-v1:carrier-document:003'\n"
                 "SCHEMA_MATERIAL_BINDING={'path':'authority/artifact-types/agent-session/v1/schema.json',\n"
                 "                         'sha256':'e05780ad1ee2f87cc4bc288a05cca24c6e0ac35e97771ff689de0ec64d14aae8'}\n"
                 "def privacy_material(ref,raw):\n"
                 "    if ref==SCHEMA_MATERIAL_REF:\n"
                 "        source.require(source.sha(raw)==SCHEMA_MATERIAL_BINDING['sha256']\n"
                 "            and source.original(SCHEMA_MATERIAL_BINDING)==raw,\n"
                 "            'selected exact public schema material differs')\n"
                 "        return\n"
                 "    privacy(source.parse(raw))\n\n")
    workspace = replace_exact(workspace, 'def validate_scope(policy):\n', allowance + 'def validate_scope(policy):\n', 1)
    workspace = replace_exact(workspace, '        privacy(source.parse(raw))\n    actual=',
                              '        privacy_material(ref,raw)\n    actual=', 1)
    workspace = replace_exact(workspace, "raw=read_private(self.root/selected['path']);source.require(source.sha(raw)==b['sha256'],'material changed');privacy(source.parse(raw));return raw",
                              "raw=read_private(self.root/selected['path']);source.require(source.sha(raw)==b['sha256'],'material changed');privacy_material(b['ref'],raw);return raw", 1)
    adapter = exact(OLD_ADAPTER).decode()
    adapter = replace_exact(adapter, OLD.name, NEW.name, 1)
    changed = {'workflow-output-plan.schema.json': schema.encode(),
               'workflow_output_registry.py': registry.encode(),
               'source_bridge.py': bridge.encode(),
               'guard.py': guard.encode(),
               'workspace.py': workspace.encode()}
    NEW_ADAPTER.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    new_file(NEW_ADAPTER, adapter.encode())
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        if name == 'contract-profile.json':
            continue
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        new_file(target, changed.get(name, exact(OLD / name)))
    old_adapter_path = OLD_ADAPTER.relative_to(ROOT).as_posix()
    new_adapter_path = NEW_ADAPTER.relative_to(ROOT).as_posix()
    new_profile_rows = []
    for selected in profile['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_profile_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_profile_rows.append(row(NEW_ADAPTER))
        else:
            new_profile_rows.append(selected)
    if len(new_profile_rows) != 33425 or len({r['path'] for r in new_profile_rows}) != 33425:
        raise ValueError('API53 profile inventory differs')
    profile['files'] = sorted(new_profile_rows, key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)

    new_source_rows = []
    for selected in manifest['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_source_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_source_rows.append(row(NEW_ADAPTER))
        else:
            new_source_rows.append(selected)
    template = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json'
    template_row = row(template)
    profile_rows = {selected['path']: selected['sha256'] for selected in profile['files']}
    if profile_rows.get(template_row['path']) != template_row['sha256'] or template_row not in new_source_rows:
        raise ValueError('original public template absent from selected closure')
    schema_row = row(ROOT / SCHEMA_PATH)
    if schema_row['sha256'] != SCHEMA_SHA or profile_rows.get(SCHEMA_PATH) != SCHEMA_SHA or schema_row in new_source_rows:
        raise ValueError('exact public AgentSession schema row differs')
    new_source_rows.append(schema_row)
    if len(new_source_rows) != 210 or len({r['path'] for r in new_source_rows}) != 210:
        raise ValueError('API53 source inventory differs')
    manifest['files'] = sorted(new_source_rows, key=lambda r: r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    receipt = {'schema_version': 'lab-T31-API53-public-schema-material/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': digest(NEW / 'source-manifest.json'),
               'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows),
               'schema_service_path_replacements': 2, 'staged_origin_replacements': 7,
               'selected_workflow_instance_replaced': False,
               'public_template_source_row': template_row,
               'public_schema_source_row': schema_row,
               'exact_workspace_privacy_allowance': {'ref':'private:T31:bridge-v1:carrier-document:003',
                                                     'binding':schema_row},
               'authority_effect': 'none', 'actual_workflow_transitions': 0,
               'claim_ceiling': CLAIM}
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': digest(NEW / 'source-manifest.json'),
                      'profile_sha256': digest(NEW / 'contract-profile.json'),
                      'adapter_sha256': digest(NEW_ADAPTER),
                      'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows)},
                     sort_keys=True))


if __name__ == '__main__': main()
