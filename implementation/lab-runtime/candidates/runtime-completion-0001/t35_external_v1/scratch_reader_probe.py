"""Fixture-only historical Reader execution after a verified disposable Source build.

The two children share one owned scratch tree. The second child receives the
completed family and sparse selected snapshot read-only; neither child has a
protected Source8 root or the interactive checkout mounted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile

from . import constructor_paths, role_stage, scratch_source_probe as source
from .held_paths import _parse_closed
from .path_contract import check_binding, require


FAMILY = PurePosixPath('/work/out/legacy-fixture-source')
SNAPSHOT = PurePosixPath('/work/snapshot')
SOURCE_REL = 'source/source-manifest.json'
PACKAGE_REL = 'source/packages/0001/manifest.json'
READER_REL = 'reader/source-manifest.json'

READER_RUNNER = '''import hashlib,importlib.util,json,sys
from pathlib import Path
for forbidden in ('/home/vlad_','/var/lib/cyberalchemy-lab','/run/cyberalchemy-lab'):
    if Path(forbidden).exists():raise RuntimeError('forbidden host root visible in Reader namespace')
sys.path.insert(0,'/work/snapshot')
family=Path('/work/out/legacy-fixture-source')
reader_root=family/'reader'
spec=importlib.util.spec_from_file_location('_t35_scratch_reader',reader_root/'__init__.py',submodule_search_locations=[str(reader_root)])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
Reader=__import__(spec.name+'.reader',fromlist=['SelectedReader']).SelectedReader
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
reader_pin=sha(reader_root/'source-manifest.json')
source_pin=sha(family/'source/source-manifest.json')
package_pin=sha(family/'source/packages/0001/manifest.json')
selected_reader=Reader(reader_pin,source_pin,package_pin)
selected_reader.guard();selected_reader.package(source_pin,package_pin)
with selected_reader.open_signed(source_pin,package_pin) as selected:
    if type(selected) is not selected_reader.adapter.SignedSources or type(selected.view) is not selected_reader.Inspection:
        raise RuntimeError('Reader selected a different local type')
    selected.guard()
    count=len(selected.records)
    report=selected.closure_report()
    if (report['authority_effect']!='none' or report['actual_owner_outcome'] is not None or
            report['included_current_instances']!=count or
            report['accounted_subjects']<count):
        raise RuntimeError('Reader closure report exceeds fixture result')
    report_sha=hashlib.sha256(json.dumps(report,sort_keys=True,allow_nan=False).encode()).hexdigest()
    scope_sha=hashlib.sha256(selected.sources.scope_ref.encode()).hexdigest()
refused=0
for bad in (('0'*64,source_pin,package_pin),(reader_pin,'0'*64,package_pin),(reader_pin,source_pin,'0'*64)):
    try:Reader(*bad).package(bad[1],bad[2])
    except ValueError:refused+=1
    else:raise RuntimeError('Reader accepted a wrong independent pin')
print(json.dumps({'result':'PASS-fixture-reader','reader_manifest_sha256':reader_pin,
    'source_manifest_sha256':source_pin,'source_package_manifest_sha256':package_pin,
    'actual_distinct_local_types':True,'selected_record_count':count,
    'scope_ref_sha256':scope_sha,'closure_report_sha256':report_sha,
    'accounted_subject_count':report['accounted_subjects'],
    'wrong_independent_pin_refusals':refused,
    'sandbox_host_checkout_absent':True,'sandbox_protected_roots_absent':True,
    'authority_effect':'none','actual_owner_outcome':None},sort_keys=True),flush=True)
'''

READER_BRIDGE = '''"""Closed read bridge for disposable read-only Reader sandbox only."""
import functools,hashlib,json,os,stat
from pathlib import Path,PurePosixPath
SNAPSHOT=Path('/work/snapshot')
FAMILY=Path('/work/out/legacy-fixture-source')
SOURCE=FAMILY/'source/source-manifest.json'
PACKAGE=FAMILY/'source/packages/0001/manifest.json'
READER=FAMILY/'reader/source-manifest.json'
STAGE=SNAPSHOT/'_t35_stage_selection.json'
SOURCE_SHA='__SOURCE_SHA__'
PACKAGE_SHA='__PACKAGE_SHA__'
READER_SHA='__READER_SHA__'
STAGE_SHA='__STAGE_SHA__'
def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('duplicate Reader selection key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite Reader selection')))
def _rows(value):
    if type(value) is not list:raise ValueError('Reader selection rows must be a list')
    result={}
    for row in value:
        if (type(row) is not dict or set(row)!={'path','sha256'} or
                type(row['path']) is not str or type(row['sha256']) is not str or
                len(row['sha256'])!=64 or
                any(c not in '0123456789abcdef' for c in row['sha256'])):
            raise ValueError('closed Reader selection row required')
        path=row['path'];p=PurePosixPath(path)
        if p.as_posix()!=path or '..' in p.parts or '\\\\' in path or path in result:
            raise ValueError('ambiguous Reader selection path')
        result[path]=row['sha256']
    return result
@functools.lru_cache(maxsize=1)
def _source():
    raw=SOURCE.read_bytes()
    if _sha(raw)!=SOURCE_SHA:raise ValueError('selected Source manifest pin differs')
    value=_parse(raw)
    if value['authority_effect']!='none' or value['actual_owner_outcome'] is not None:
        raise ValueError('Source manifest exceeds fixture authority')
    return _rows(value['files'])
@functools.lru_cache(maxsize=1)
def _stage():
    raw=STAGE.read_bytes()
    if _sha(raw)!=STAGE_SHA:raise ValueError('selected stage control pin differs')
    rows=_rows(_parse(raw))
    if len(rows)!=30 or any(_source().get(name)!=digest for name,digest in rows.items()):
        raise ValueError('exact 30 Source-selected stage leaves required')
    return rows
@functools.lru_cache(maxsize=1)
def _package():
    raw=PACKAGE.read_bytes()
    if _sha(raw)!=PACKAGE_SHA:raise ValueError('selected Source package pin differs')
    value=_parse(raw)
    if (value['authority_effect']!='none' or value['actual_owner_outcome'] is not None or
            value['public_package_export_allowed'] is not False):
        raise ValueError('Source package exceeds fixture authority')
    rows=_rows(value['files'])
    prefix=str(FAMILY/'source/packages/0001')+'/'
    if len(rows)!=36 or any(not name.startswith(prefix) for name in rows):
        raise ValueError('Source package member selection differs')
    return rows
@functools.lru_cache(maxsize=1)
def _reader():
    raw=READER.read_bytes()
    if _sha(raw)!=READER_SHA:raise ValueError('selected Reader manifest pin differs')
    value=_parse(raw)
    if (set(value)!={'schema_version','files','environment','construction_status',
            'fixture_only','authority_effect','actual_owner_outcome','shared_API_qualified',
            'producer_source_binding','producer_package_binding','implementation_entrypoint_ref',
            'original_Source8_permission_transferred'} or
            value['schema_version']!='lab-current-fixture-reader-source/v1-candidate' or
            value['construction_status']!='construction-bound-unqualified' or
            value['environment']!={'python':'3.14.4','jsonschema':'4.19.2','cryptography':'46.0.5'} or
            value['fixture_only'] is not True or value['authority_effect']!='none' or
            value['actual_owner_outcome'] is not None or value['shared_API_qualified'] is not False or
            value['original_Source8_permission_transferred'] is not False):
        raise ValueError('Reader manifest claims differ')
    if (value['producer_source_binding']!={'path':str(SOURCE),'sha256':SOURCE_SHA} or
            value['producer_package_binding']!={'path':str(PACKAGE),'sha256':PACKAGE_SHA} or
            value['implementation_entrypoint_ref']!=str(FAMILY/'reader/reader.py')+'#SelectedReader.open_signed'):
        raise ValueError('Reader producer or entrypoint binding differs')
    expected=dict(_source())
    expected.update(_stage())
    expected[str(SOURCE)]=SOURCE_SHA
    expected[str(PACKAGE)]=PACKAGE_SHA
    expected.update(_package())
    rows=_rows(value['files'])
    if rows!=expected:raise ValueError('Reader manifest has missing or unselected input')
    return rows
def read(row):
    if type(row) is not dict or set(row)!={'path','sha256'} or type(row['path']) is not str:
        raise ValueError('closed Reader input required')
    name=row['path'];p=PurePosixPath(name)
    if p.as_posix()!=name or '..' in p.parts or '\\\\' in name:raise ValueError('noncanonical Reader input')
    if p.is_absolute():
        if FAMILY not in Path(name).parents:raise ValueError('Reader output outside family')
        path=Path(name)
        if path==READER:allowed=READER_SHA
        elif path==SOURCE:allowed=SOURCE_SHA
        elif path==PACKAGE:allowed=PACKAGE_SHA
        else:allowed=_reader().get(name)
        if allowed!=row['sha256']:raise ValueError('Reader output not selected')
    else:
        if _source().get(name)!=row['sha256']:raise ValueError('Reader Source/API row not selected')
        path=SNAPSHOT/name
    if path.is_symlink() or any(a.is_symlink() for a in path.parents):raise ValueError('Reader input alias')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>64*1024*1024:
            raise ValueError('Reader input type or size differs')
        raw=bytearray()
        while len(raw)<before.st_size:
            chunk=os.read(fd,min(1024*1024,before.st_size-len(raw)))
            if not chunk:raise ValueError('Reader input truncated')
            raw.extend(chunk)
        after=os.fstat(fd);attached=path.stat(follow_symlinks=False)
        key=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        if key(before)!=key(after) or key(before)!=key(attached) or _sha(raw)!=row['sha256']:
            raise ValueError('Reader selected input changed')
        return bytes(raw)
    finally:os.close(fd)
def verify_inputs(rows,*,selected_external=()):
    selected=_reader()
    if type(rows) is not list:raise ValueError('Reader input rows required')
    external=[r for r in rows if r['path'].startswith('/')]
    if selected_external:
        if external!=list(selected_external):raise ValueError('Reader external selection differs')
    elif any(selected.get(r['path'])!=r['sha256'] for r in external):
        raise ValueError('unselected Reader external row')
    for row in rows:read(row)
    return len(rows)
def run_native(*a,**k):raise RuntimeError('native effects unavailable in Reader probe')
'''


def _json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def _selected_reader_rows(source_manifest: bytes, package_manifest: bytes,
                          source_sha: str, package_sha: str) -> list[dict]:
    source_value = _parse_closed(source_manifest)
    package_value = _parse_closed(package_manifest)
    selected: dict[str, dict] = {}
    for row in [*source_value['files'],
                {'path': str(FAMILY / SOURCE_REL), 'sha256': source_sha},
                {'path': str(FAMILY / PACKAGE_REL), 'sha256': package_sha},
                *package_value['files']]:
        check_binding(row, kind='output' if row['path'].startswith('/') else 'source_api',
                      family=FAMILY if row['path'].startswith('/') else None)
        require(row['path'] not in selected,
                'Reader input selection duplicate or digest conflict')
        selected[row['path']] = row
    require(len(package_value['files']) == 36 and len(selected) > 1700,
            'Reader exact Source and package closure absent')
    return [selected[name] for name in sorted(selected)]


def _reader_manifest(source_raw: bytes, package_raw: bytes) -> bytes:
    source_sha, package_sha = source._sha(source_raw), source._sha(package_raw)
    return _json({
        'schema_version': 'lab-current-fixture-reader-source/v1-candidate',
        'files': _selected_reader_rows(source_raw, package_raw, source_sha, package_sha),
        'environment': {'python': '3.14.4', 'jsonschema': '4.19.2', 'cryptography': '46.0.5'},
        'construction_status': 'construction-bound-unqualified',
        'fixture_only': True, 'authority_effect': 'none', 'actual_owner_outcome': None,
        'shared_API_qualified': False,
        'producer_source_binding': {'path': str(FAMILY / SOURCE_REL), 'sha256': source_sha},
        'producer_package_binding': {'path': str(FAMILY / PACKAGE_REL), 'sha256': package_sha},
        'implementation_entrypoint_ref': str(FAMILY / 'reader/reader.py') + '#SelectedReader.open_signed',
        'original_Source8_permission_transferred': False,
    })


def _reader_bridge(source_sha: str, package_sha: str, reader_sha: str,
                   stage_sha: str) -> bytes:
    for value in (source_sha, package_sha, reader_sha, stage_sha):
        require(len(value) == 64 and all(c in '0123456789abcdef' for c in value),
                'exact Reader selection digest required')
    text = READER_BRIDGE
    for marker, digest in (('__SOURCE_SHA__', source_sha), ('__PACKAGE_SHA__', package_sha),
                           ('__READER_SHA__', reader_sha), ('__STAGE_SHA__', stage_sha)):
        require(text.count(marker) == 1, 'Reader bridge pin preimage differs')
        text = text.replace(marker, digest)
    compile(text, '<disposable-reader-bridge>', 'exec', optimize=0)
    compile(text, '<disposable-reader-bridge>', 'exec', optimize=2)
    return text.encode()


def _sandbox_argv(snapshot: Path, family_host: Path, runner: str,
                  *, package_host: Path | None = None) -> list[str]:
    argv = [str(source.BWRAP), '--die-with-parent', '--unshare-all', '--clearenv',
            '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'HOME', '/nonexistent',
            '--setenv', 'TMPDIR', '/tmp', '--setenv', 'LC_ALL', 'C.UTF-8',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev',
            '--tmpfs', '/tmp', '--dir', '/work', '--dir', '/work/out',
            '--ro-bind', str(snapshot), str(SNAPSHOT),
            '--ro-bind', str(family_host), str(FAMILY)]
    if package_host is not None:
        argv += ['--bind', str(package_host), str(FAMILY / 'source/packages')]
    return argv + ['--chdir', '/work', '--', '/usr/bin/python3', '-I', '-B',
                   str(SNAPSHOT / runner)]


def _source_package_verified(family_host: Path, pre: dict[str, str],
                             pre_dirs: set[str], expected_members: set[str],
                             stdout: bytes) -> tuple[bytes, dict[str, str], set[str]]:
    post = source._tree_files(family_host)
    dirs = source._tree_dirs(family_host)
    prefix = 'source/packages/0001/'
    expected = set(pre) | {prefix + name for name in expected_members} | {prefix + 'manifest.json'}
    require(set(post) == expected and all(post[name] == digest for name, digest in pre.items()) and
            dirs == pre_dirs | {'source/packages/0001', 'source/packages/0001/artifacts',
                                'source/packages/0001/setup-artifacts'},
            'Source builder disposable post-tree differs')
    package_raw = (family_host / PACKAGE_REL).read_bytes()
    package_sha = source._sha(package_raw)
    lines = stdout.splitlines()
    require(len(lines) == 2, 'Source builder must emit two closed success records')
    builder, runner = (_parse_closed(line) for line in lines)
    require(type(builder) is dict and set(builder) ==
            {'result', 'package_binding', 'actual_original_targets', 'records'} and
            builder['result'] == 'PASS' and builder['package_binding'] ==
            {'path': str(FAMILY / PACKAGE_REL), 'sha256': package_sha} and
            builder['actual_original_targets'] == 23 and builder['records'] == 21,
            'Source builder success record differs')
    require(type(runner) is dict and set(runner) ==
            {'sandbox_host_checkout_absent', 'sandbox_protected_roots_absent',
             'source_package_manifest_sha256'} and
            runner['sandbox_host_checkout_absent'] is True and
            runner['sandbox_protected_roots_absent'] is True and
            runner['source_package_manifest_sha256'] == package_sha,
            'Source child namespace record differs')
    package = _parse_closed(package_raw)
    require(type(package) is dict and set(package) ==
            {'schema_version', 'files', 'source_manifest_binding', 'archive_binding',
             'expected_replay_binding', 'period_binding', 'episode_contract_binding',
             'visibility', 'public_package_export_allowed', 'authority_effect',
             'actual_owner_outcome'} and
            package['schema_version'] == 'lab-owned-current-participation-package/v1-candidate' and
            package['visibility'] == 'private-candidate-original-custody' and
            package['public_package_export_allowed'] is False and
            package['authority_effect'] == 'none' and package['actual_owner_outcome'] is None,
            'Source package authority or schema differs')
    rows = package['files']
    require(type(rows) is list and len(rows) == 36 and
            {PurePosixPath(row['path']).relative_to(FAMILY / 'source/packages/0001').as_posix()
             for row in rows} == expected_members,
            'Source package member names differ')
    for row in rows:
        check_binding(row, kind='output', family=FAMILY)
        suffix = PurePosixPath(row['path']).relative_to(FAMILY).as_posix()
        require(post[suffix] == row['sha256'], 'Source package member bytes differ')
    core = {
        'source_manifest_binding': SOURCE_REL,
        'archive_binding': prefix + 'branch.snapshot',
        'expected_replay_binding': prefix + 'expected-replay.json',
        'period_binding': prefix + 'period.json',
        'episode_contract_binding': 'source/episode-contract.json',
    }
    require(all(package[key] == {'path': str(FAMILY / suffix), 'sha256': post[suffix]}
                for key, suffix in core.items()), 'Source package core bindings differ')
    result = _parse_closed((family_host / 'source/packages/0001/build-result.json').read_bytes())
    require(result['result'] == 'PASS' and result['owned_store_and_key_removed'] is True and
            result['private_keys_exported'] is False and result['canonical_effects_applied'] == 0,
            'Source builder result exceeds fixture ceiling')
    return package_raw, post, dirs


def _reader_output(stdout: bytes, *, reader_sha: str, source_sha: str,
                   package_sha: str) -> dict:
    lines = stdout.splitlines()
    require(len(lines) == 1 and len(stdout) <= 4096, 'one bounded Reader result required')
    value = _parse_closed(lines[0])
    require(type(value) is dict and set(value) ==
            {'result', 'reader_manifest_sha256', 'source_manifest_sha256',
             'source_package_manifest_sha256', 'actual_distinct_local_types',
             'selected_record_count', 'scope_ref_sha256', 'closure_report_sha256',
             'accounted_subject_count', 'wrong_independent_pin_refusals',
             'sandbox_host_checkout_absent', 'sandbox_protected_roots_absent',
             'authority_effect', 'actual_owner_outcome'} and
            value['result'] == 'PASS-fixture-reader' and
            value['reader_manifest_sha256'] == reader_sha and
            value['source_manifest_sha256'] == source_sha and
            value['source_package_manifest_sha256'] == package_sha and
            value['actual_distinct_local_types'] is True and
            type(value['selected_record_count']) is int and
            1 <= value['selected_record_count'] <= 512 and
            type(value['accounted_subject_count']) is int and
            value['selected_record_count'] <= value['accounted_subject_count'] and
            type(value['scope_ref_sha256']) is str and len(value['scope_ref_sha256']) == 64 and
            type(value['closure_report_sha256']) is str and
            len(value['closure_report_sha256']) == 64 and
            value['wrong_independent_pin_refusals'] == 3 and
            value['sandbox_host_checkout_absent'] is True and
            value['sandbox_protected_roots_absent'] is True and
            value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None,
            'Reader child result differs from closed fixture success')
    return value


def probe() -> dict:
    require(source.BWRAP.is_file() and source._sha(source.BWRAP.read_bytes()) == source.BWRAP_SHA,
            'exact selected bwrap executable differs')
    version = subprocess.check_output([str(source.BWRAP), '--version'], text=True).strip()
    require(version == 'bubblewrap 0.11.1', 'selected bwrap version differs')
    with tempfile.TemporaryDirectory(prefix='lc-u02-05-reader-probe-') as scratch:
        root = Path(scratch)
        snapshot, output = root / 'snapshot', root / 'output'
        snapshot.mkdir(); output.mkdir()
        rows, captured = source._source_rows()
        source._copy_snapshot(snapshot, rows, captured)
        (snapshot / '_t35_source_runner.py').write_text(source.SANDBOX_RUNNER)
        (snapshot / '_t35_reader_runner.py').write_text(READER_RUNNER)
        layout = role_stage.DisposableLayout(FAMILY, SNAPSHOT, 'legacy-fixture-source')
        staged = role_stage.stage_rows(layout, lambda name: captured[name])
        family_host = output / 'legacy-fixture-source'
        for row in staged:
            name = PurePosixPath(row['output']['path']).name
            raw = row['bytes']
            if row['role'] == 'source' and name.endswith('.py'):
                raw = source._unsealed_source(captured[row['input']['path']], layout, name)
            row['bytes'] = raw
            row['output'] = source._bind(Path(row['output']['path']), raw)
            leaf = family_host / row['role'] / Path(row['output']['path']).relative_to(
                str(FAMILY / row['role']))
            leaf.parent.mkdir(parents=True, exist_ok=True); leaf.write_bytes(raw)
        from datetime import datetime, timedelta, timezone
        original_episode = _parse_closed(captured[str(source.EXTRA_INPUTS[0])])
        now = datetime.now(timezone.utc)
        episode = {key: value.replace('R03-legacy-session-fixture-0257',
                                      'completion-legacy-fixture-source')
                   if type(value) is str else value for key, value in original_episode.items()}
        episode['not_before'] = (now - timedelta(minutes=1)).isoformat()
        episode['expires_at'] = (now + timedelta(hours=23, minutes=59)).isoformat()
        episode['purpose'] = 'Disposable Source and Reader fixture only; no host authority.'
        episode_raw = _json(episode)
        (family_host / 'source/episode-contract.json').write_bytes(episode_raw)
        role_raw = b'{"schema_version":"lab-T35-disposable-native-role/v1","authority_effect":"none"}\n'
        (family_host / 'source/context-native-role.json').write_bytes(role_raw)
        control = {
            'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
            'authority_effect': 'none', 'instance': layout.instance,
            'output_family_path': str(FAMILY),
            'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                              for item in staged],
            'episode_binding': source._bind(Path(FAMILY / 'source/episode-contract.json'), episode_raw),
            'current_role_binding': source._bind(Path(FAMILY / 'source/context-native-role.json'), role_raw),
            'status': 'staged-unqualified',
        }
        construction_raw = (json.dumps(control, sort_keys=True, separators=(',', ':')) + '\n').encode()
        (family_host / 'construction-selection.json').write_bytes(construction_raw)
        stage_map = constructor_paths.stage_30_membership(layout, staged,
            {'episode_contract': episode_raw, 'context_native_role': role_raw,
             'construction_selection': construction_raw})
        stage_rows = [stage_map[name] for name in sorted(stage_map)]
        require(len(stage_rows) == 30, 'exact Source/Reader stage selection required')
        stage_control = (json.dumps(stage_rows, sort_keys=True, separators=(',', ':')) + '\n').encode()
        (snapshot / '_t35_stage_selection.json').write_bytes(stage_control)
        source_manifest = _json({
            'schema_version': 'lab-T35-disposable-source-probe/v1-inactive',
            'files': sorted([*rows.values(), *stage_rows], key=lambda row: row['path']),
            'environment': {'python': '3.14.4', 'jsonschema': '4.19.2', 'cryptography': '46.0.5'},
            'authority_effect': 'none', 'actual_owner_outcome': None, 'fixture_only': True,
        })
        (family_host / SOURCE_REL).write_bytes(source_manifest)
        source_bridge = (source.SCRATCH_BRIDGE.replace('__SOURCE_MANIFEST_SHA__',
                         source._sha(source_manifest)).replace('__STAGE_SELECTION_SHA__',
                         source._sha(stage_control))).encode()
        (snapshot / '_t35_external_runtime_capture.py').write_bytes(source_bridge)
        package_host = family_host / 'source/packages'; package_host.mkdir()
        pre = source._tree_files(family_host)
        pre_dirs = source._tree_dirs(family_host)
        require(set(pre) == {Path(name).relative_to(FAMILY).as_posix() for name in stage_map} |
                {SOURCE_REL}, 'Source/Reader pre-effect tree differs')
        expected_members = source._historical_package_names(
            captured[source.HISTORICAL_SOURCE_PACKAGE['path']])
        source_argv = _sandbox_argv(snapshot, family_host, '_t35_source_runner.py',
                                    package_host=package_host)
        source_rc, source_stdout, source_stderr = source._run_bounded(source_argv)
        require(source_rc == 0, 'fixture Source child failed or timed out')
        package_raw, source_post, source_dirs = _source_package_verified(
            family_host, pre, pre_dirs, expected_members, source_stdout)
        package_sha = source._sha(package_raw)
        reader_manifest = _reader_manifest(source_manifest, package_raw)
        reader_sha = source._sha(reader_manifest)
        (family_host / READER_REL).write_bytes(reader_manifest)
        reader_pre = source._tree_files(family_host)
        reader_dirs = source._tree_dirs(family_host)
        require(set(reader_pre) == set(source_post) | {READER_REL} and
                all(reader_pre[name] == digest for name, digest in source_post.items()) and
                reader_dirs == source_dirs,
                'Reader manifest changed selected Source package or tree')
        reader_bridge = _reader_bridge(source._sha(source_manifest), package_sha,
                                       reader_sha, source._sha(stage_control))
        (snapshot / '_t35_external_runtime_capture.py').write_bytes(reader_bridge)
        reader_argv = _sandbox_argv(snapshot, family_host, '_t35_reader_runner.py')
        reader_rc, reader_stdout, reader_stderr = source._run_bounded(reader_argv)
        reader_post = source._tree_files(family_host)
        reader_post_dirs = source._tree_dirs(family_host)
        tree_unchanged = reader_post == reader_pre and reader_post_dirs == reader_dirs
        require(reader_rc == 0 and tree_unchanged,
                'Reader child failed or changed read-only family tree')
        result = _reader_output(reader_stdout, reader_sha=reader_sha,
                                source_sha=source._sha(source_manifest), package_sha=package_sha)
        summary = {
            'status': 'PASS-fixture-reader',
            'selected_input_count': len(rows),
            'selected_input_selection_sha256': source._sha((json.dumps(
                [rows[name] for name in sorted(rows)], sort_keys=True,
                separators=(',', ':')) + '\n').encode()),
            'source_package_manifest_sha256': package_sha,
            'source_manifest_sha256': source._sha(source_manifest),
            'reader_manifest_sha256': reader_sha,
            'source_bridge_sha256': source._sha(source_bridge),
            'reader_bridge_sha256': source._sha(reader_bridge),
            'source_runner_sha256': source._sha(source.SANDBOX_RUNNER.encode()),
            'reader_runner_sha256': source._sha(READER_RUNNER.encode()),
            'stage_selection_sha256': source._sha(stage_control),
            'bwrap_sha256': source.BWRAP_SHA, 'bwrap_version': version,
            'source_argv_shape': ['<sparse-snapshot>' if a == str(snapshot) else
                                  '<disposable-family>' if a == str(family_host) else
                                  '<disposable-package>' if a == str(package_host) else a
                                  for a in source_argv],
            'reader_argv_shape': ['<sparse-snapshot>' if a == str(snapshot) else
                                  '<disposable-family>' if a == str(family_host) else a
                                  for a in reader_argv],
            'source_post_leaf_count': len(source_post),
            'reader_pre_leaf_count': len(reader_pre),
            'reader_post_leaf_count': len(reader_post),
            'reader_family_tree_unchanged': tree_unchanged,
            'source_stdout_bytes': len(source_stdout),
            'source_stdout_sha256': source._sha(source_stdout),
            'source_stderr_bytes': len(source_stderr),
            'source_stderr_sha256': source._sha(source_stderr),
            'reader_stdout_bytes': len(reader_stdout),
            'reader_stdout_sha256': source._sha(reader_stdout),
            'reader_stderr_bytes': len(reader_stderr),
            'reader_stderr_sha256': source._sha(reader_stderr),
            'reader_selected_record_count': result['selected_record_count'],
            'reader_accounted_subject_count': result['accounted_subject_count'],
            'reader_closure_report_sha256': result['closure_report_sha256'],
            'reader_wrong_pin_refusals': result['wrong_independent_pin_refusals'],
            'reader_scope_ref_sha256': result['scope_ref_sha256'],
            'private_signer_exported': False,
            'protected_source_used': False,
            'claim_ceiling': 'disposable-Source-then-read-only-Reader-only',
        }
    require(not root.exists(), 'Reader probe scratch root remained after cleanup')
    summary['scratch_cleaned_after_return'] = True
    return summary


if __name__ == '__main__':
    print(json.dumps(probe(), sort_keys=True, indent=2))
