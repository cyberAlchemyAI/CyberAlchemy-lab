"""No-replace API50: select one current-source instantiation of agent-context.

The immutable API49 predecessor pins a public workflow example whose
decision-profile is a zero-hash placeholder. This successor permits only a
current decision-profile header and Work input for its first transition;
the original transition, states, and Context/Ontology output pair remain exact.
"""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v49-t31-current-guard-0002'
NEW = BASE / 'api-integration-v50-t31-agent-context-instance-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api49-current-guard-bootstrap-0002/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api50-original-output-bootstrap-0001/bootstrap.py'
OLD_SOURCE = 'e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1'
OLD_PROFILE = 'dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5'
OLD_ADAPTER_SHA = '8eb20c56a330cdb05fdaea7287901e6605b252f776aedaf2ebd6ac6d515a0325'
CLAIM = ('Source-pinned T31 agent-context template instantiation for current profile and Work input; '
         'no original producer output, WorkflowRun append, later consumer, Work satisfaction, '
         'portable installation, canonical admission, or owner effect.')


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
        raise ValueError('versioned API49 output already exists')
    manifest = json.loads(exact(OLD / 'source-manifest.json'))
    profile = json.loads(exact(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 208 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('API49 selected inventory differs')
    physical = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
                and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                and '__pycache__' not in p.parts and 'receipts' not in p.parts
                and p.suffix != '.pyc'}
    if physical != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API49 physical/source closure differs')
    for selected in own:
        if digest(OLD / selected['path'][len(old_prefix):]) != selected['sha256']:
            raise ValueError('frozen API49 selected byte differs')

    schema = exact(OLD / 'workflow-output-plan.schema.json').decode()
    old_service = old_prefix + 'service.py'
    new_service = new_prefix + 'service.py'
    schema = replace_exact(schema, old_service, new_service, 2)
    registry = exact(OLD / 'workflow_output_registry.py').decode()
    registry = replace_exact(registry, old_prefix + 'workflow_', new_prefix + 'workflow_', 7)
    bridge = exact(OLD / 'source_bridge.py').decode()
    bridge = replace_exact(bridge, '_cal_api49v2_t31_legacy_local_20261023_0001',
                           '_cal_api50_t31_legacy_local_20261023_0001', 1)
    bridge = replace_exact(bridge, '_cal_api49v2_t31_source8_local_20261023_0001',
                           '_cal_api50_t31_source8_local_20261023_0001', 1)
    producer = exact(OLD / 'workflow_producer_outputs.py').decode()
    producer = replace_exact(producer,
        "need(message['definition_binding']['sha256']==registry['definition_binding']['sha256'],'exact original workflow definition differs')",
        "selected_workflow_instance(self.host,self.factory,ref,message['definition_binding'],registry)", 1)
    producer = replace_exact(producer,
        "run=parse(raw);b=selected_transition(ref)['definition_binding'];definition_raw=read_public(b)\n"
        "        need(sha(definition_raw)==b['sha256'] and (b['path'],b['sha256'])in source_rows,'original definition source differs')\n"
        "        definition=parse(definition_raw)",
        "run=parse(raw);registry=selected_transition(ref)\n"
        "        definition=selected_workflow_instance(host,host.workflow_producer_factory,ref,builder.grant['definition_binding'],registry,authorization=authorization)", 1)
    marker = "def current_invocation(host,authorization,read_public,source_rows):"
    producer = replace_exact(producer, marker, exact(Path(__file__).with_name('selected_instance.py')).decode() + '\n\n' + marker, 1)
    compile(producer, str(NEW / 'workflow_producer_outputs.py'), 'exec', dont_inherit=True)
    guard = exact(OLD / 'guard.py').decode()
    guard = replace_exact(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(),
                          NEW_ADAPTER.relative_to(ROOT).as_posix(), 1)
    adapter = exact(OLD_ADAPTER).decode()
    adapter = replace_exact(adapter, OLD.name, NEW.name, 1)
    changed = {'workflow-output-plan.schema.json': schema.encode(),
               'workflow_output_registry.py': registry.encode(),
               'source_bridge.py': bridge.encode(),
               'workflow_producer_outputs.py': producer.encode(),
               'guard.py': guard.encode()}
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
        raise ValueError('API49 v2 profile inventory differs')
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
    if len(new_source_rows) != 208 or len({r['path'] for r in new_source_rows}) != 208:
        raise ValueError('API49 v2 source inventory differs')
    manifest['files'] = sorted(new_source_rows, key=lambda r: r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    receipt = {'schema_version': 'lab-T31-API50-agent-context-instance-rebind/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': digest(NEW / 'source-manifest.json'),
               'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows),
               'schema_service_path_replacements': 2, 'staged_origin_replacements': 7,
               'selected_workflow_instance_replaced': True,
               'authority_effect': 'none', 'actual_workflow_transitions': 0,
               'claim_ceiling': CLAIM}
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': digest(NEW / 'source-manifest.json'),
                      'profile_sha256': digest(NEW / 'contract-profile.json'),
                      'adapter_sha256': digest(NEW_ADAPTER),
                      'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows)},
                     sort_keys=True))


if __name__ == '__main__': main()
