"""Effect-disabled Reader cold-open candidate with an owned container snapshot."""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager, ExitStack
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path('/attempt/root')
TOOL = Path('/tool')
OUT = Path('/attempt/reader-output')
PRODUCER = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001'
SELECTION_SHA = '073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22'
READER_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
MODULE = '_cal_docker_reader_20261020_0001'
PRODUCER_MODULE = '_cal_docker_reader_producer_20261020_0001'
EFFECT_ENABLED = False  # A separately reviewed successor must select a release.
MAX_REPORT = 4 * 1024 * 1024
MAX_RECEIPT = 16 * 1024
MAX_CODE = 1024 * 1024
MAX_INPUT = 512 * 1024 * 1024
MAX_SMALL_INPUT = 8 * 1024 * 1024
MAX_SNAPSHOT_TOTAL = 400 * 1024 * 1024
SNAPSHOT_PARENT = Path('/attempt/tmp')
SNAPSHOT_NAME = 'reader-stage-snapshot-0004'
REQUIRE_SEPARATE_DEVICE = True


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def bounded_encoded(value: object, limit: int) -> bytes:
    """Reject oversized structures before JSON expands a private report."""
    budget = [10000]
    def inspect(item, depth=0):
        budget[0] -= 1
        require(budget[0] >= 0 and depth <= 20, 'private aggregate node/depth bound exceeded')
        if type(item) is str:
            require(len(item) <= limit, 'private aggregate string bound exceeded')
        elif type(item) is dict:
            require(len(item) <= 10000, 'private aggregate mapping bound exceeded')
            for key, child in item.items():
                require(type(key) is str, 'private aggregate key differs')
                inspect(key, depth + 1)
                inspect(child, depth + 1)
        elif type(item) is list:
            require(len(item) <= 10000, 'private aggregate list bound exceeded')
            for child in item:
                inspect(child, depth + 1)
        else:
            require(item is None or type(item) in (bool, int, float),
                    'private aggregate value type differs')
    inspect(value)
    output = bytearray()
    encoder = json.JSONEncoder(sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                               allow_nan=False)
    for chunk in encoder.iterencode(value):
        raw = chunk.encode()
        require(len(output) + len(raw) + 1 <= limit,
                'private aggregate serialization bound exceeded')
        output.extend(raw)
    output.extend(b'\n')
    return bytes(output)


def parse(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def period_current(value: dict, now: dt.datetime | None = None) -> None:
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    require(now.tzinfo is not None, 'Reader wall clock lacks timezone')
    start = dt.datetime.fromisoformat(value['not_before'])
    end = dt.datetime.fromisoformat(value['expires_at'])
    require(start.tzinfo is not None and end.tzinfo is not None and
            start <= now < end and end - start == dt.timedelta(hours=24),
            'Source participation period is not current')


def regular(path: Path) -> bytes:
    with held_directory(path.parent) as chain:
        fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=chain[-1][1])
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_SMALL_INPUT,
                    'unsafe or oversized Reader input')
            chunks, total = [], 0
            while True:
                part = os.read(fd, min(1024 * 1024, before.st_size + 1 - total))
                if not part:
                    break
                chunks.append(part)
                total += len(part)
                require(total <= MAX_SMALL_INPUT, 'Reader input overflowed')
                if total > before.st_size:
                    break
            raw = b''.join(chunks)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=chain[-1][1], follow_symlinks=False)
            require(len(raw) == before.st_size and
                    (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) ==
                    (named.st_dev, named.st_ino) and stat.S_ISREG(named.st_mode),
                    'Reader input attachment changed')
            return raw
        finally:
            os.close(fd)


def hash_regular(path: Path) -> str:
    """Hash a selected large staged file through an anchored FD, without buffering it."""
    with held_directory(path.parent) as chain:
        fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=chain[-1][1])
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_INPUT,
                    'unsafe or oversized staged file')
            digest = hashlib.sha256()
            total = 0
            while True:
                part = os.read(fd, 1024 * 1024)
                if not part:
                    break
                total += len(part)
                require(total <= MAX_INPUT, 'staged file overflowed')
                digest.update(part)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=chain[-1][1], follow_symlinks=False)
            require(total == before.st_size and
                    (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) ==
                    (named.st_dev, named.st_ino) and stat.S_ISREG(named.st_mode),
                    'staged file attachment changed')
            return digest.hexdigest()
        finally:
            os.close(fd)


@contextmanager
def held_directory(path: Path):
    require(path.is_absolute() and '..' not in path.parts, 'unsafe Reader path')
    chain = []
    primary = None
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        chain.append((Path('/'), fd))
        current = Path('/')
        for component in path.parts[1:]:
            fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=chain[-1][1])
            current = current / component
            chain.append((current, fd))
        check_chain(chain)
        yield chain
        check_chain(chain)
    except BaseException as error:
        primary = error
        raise
    finally:
        failures = []
        for name, fd in reversed(chain):
            try:
                os.close(fd)
            except BaseException as error:
                failures.append((str(name), fd, error))
        if failures:
            if primary is not None:
                prior = getattr(primary, 'secondary_close_errors', [])
                primary.secondary_close_errors = prior + failures
                primary.add_note('held Reader directory close failure; custody is UNKNOWN')
            else:
                group = BaseExceptionGroup('held Reader directory close failure; custody is UNKNOWN',
                                           [row[2] for row in failures])
                group.close_failures = failures
                raise group


def check_chain(chain: list[tuple[Path, int]]) -> None:
    for path, fd in chain:
        named = path.lstat()
        held = os.fstat(fd)
        require(stat.S_ISDIR(named.st_mode) and
                (named.st_dev, named.st_ino) == (held.st_dev, held.st_ino),
                'Reader held directory attachment changed')


def selected(*, output_empty: bool = True) -> tuple[dict, dict, dict, dict, dict, list[dict]]:
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    require(ROOT.is_dir() and not ROOT.is_symlink() and OUT.is_dir() and
            not OUT.is_symlink(), 'Reader stage/output state differs')
    if output_empty:
        require(not list(OUT.iterdir()), 'Reader output is not fresh')
    else:
        entries = list(OUT.iterdir())
        require(len(entries) == 1 and entries[0].name == 'receipt.json' and
                entries[0].is_file() and not entries[0].is_symlink(),
                'Reader postreceipt output differs')
    raw = regular(TOOL / 'selection.json')
    require(sha(raw) == SELECTION_SHA, 'Reader selection pin differs')
    selection = parse(raw)
    require(selection['effect'] == 'NOT_RUN' and
            selection['reader_manifest_binding'] == {'path': READER + '/source-manifest.json', 'sha256': READER_SHA},
            'Reader selection shape differs')
    source_raw = regular(ROOT / PRODUCER / 'source-manifest.json')
    package_raw = regular(ROOT / PRODUCER / 'packages/0001/manifest.json')
    reader_raw = regular(ROOT / READER / 'source-manifest.json')
    require(sha(source_raw) == selection['source_manifest_binding']['sha256'] and
            sha(package_raw) == selection['source_package_binding']['sha256'] and
            sha(reader_raw) == READER_SHA, 'selected Source/Reader manifest differs')
    source, package, reader = map(parse, (source_raw, package_raw, reader_raw))
    require(package['source_manifest_binding'] == selection['source_manifest_binding'] and
            reader['producer_source_binding'] == selection['source_manifest_binding'] and
            reader['producer_package_binding'] == selection['source_package_binding'] and
            reader['authority_effect'] == 'none' and reader['actual_owner_outcome'] is None,
            'Source/Reader producer join differs')
    period_raw = regular(ROOT / PRODUCER / 'packages/0001/period.json')
    period = parse(period_raw)
    period_current(period)
    require(period['expires_at'] == selection['episode_expires_at'] and
            package['period_binding']['sha256'] == sha(period_raw),
            'selected Source period differs')
    expected_raw = regular(ROOT / PRODUCER / 'packages/0001/expected-replay.json')
    expected = parse(expected_raw)
    require(expected['expected_head'] == selection['expected_head'] and
            package['expected_replay_binding']['sha256'] == sha(expected_raw),
            'Source signed cut selection differs')
    expected_rows = reader['files'] + package['files'] + [
        {'path': READER + '/source-manifest.json', 'sha256': READER_SHA},
        {'path': PRODUCER + '/packages/0001/manifest.json',
         'sha256': selection['source_package_binding']['sha256']},
    ]
    names = [row['path'] for row in expected_rows]
    require(len(names) == 986 and len(set(names)) == 986, 'Reader staged file count differs')
    files, dirs = set(), set()
    for path in ROOT.rglob('*'):
        mode = path.lstat().st_mode
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), 'Reader stage has nonregular entry')
        (files if stat.S_ISREG(mode) else dirs).add(path.relative_to(ROOT).as_posix())
    expected_dirs = {parent.as_posix() for name in names for parent in Path(name).parents
                     if parent.as_posix() != '.'} | {PRODUCER + '/receipts'}
    require(files == set(names) and dirs == expected_dirs, 'Reader stage inventory differs')
    for row in expected_rows:
        require(hash_regular(ROOT / row['path']) == row['sha256'],
                'Reader selected input differs: ' + row['path'])
    return selection, period, expected, source, reader, expected_rows


def copy_snapshot_member(source: Path, target: Path, expected_sha: str) -> int:
    """Copy one selected file into owned tmpfs and hash both captured/readback bytes."""
    with held_directory(source.parent) as source_chain, held_directory(target.parent) as target_chain:
        source_fd = os.open(source.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=source_chain[-1][1])
        try:
            before = os.fstat(source_fd)
            require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_INPUT,
                    'snapshot source is unsafe or oversized')
            target_fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                                dir_fd=target_chain[-1][1])
            try:
                digest, total = hashlib.sha256(), 0
                while True:
                    chunk = os.read(source_fd, 1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    require(total <= MAX_INPUT, 'snapshot source overflowed')
                    digest.update(chunk)
                    view = memoryview(chunk)
                    while view:
                        written = os.write(target_fd, view)
                        require(written > 0, 'snapshot target write made no progress')
                        view = view[written:]
                after = os.fstat(source_fd)
                named = os.stat(source.name, dir_fd=source_chain[-1][1], follow_symlinks=False)
                require(total == before.st_size and digest.hexdigest() == expected_sha and
                        (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) ==
                        (named.st_dev, named.st_ino) and stat.S_ISREG(named.st_mode),
                        'snapshot captured source bytes differ')
                os.fchmod(target_fd, 0o400)
                os.fsync(target_fd)
            finally:
                os.close(target_fd)
            os.fsync(target_chain[-1][1])
            require(hash_regular(target) == expected_sha, 'snapshot target readback differs')
            return total
        finally:
            os.close(source_fd)


def snapshot_directory_names(rows: list[dict]) -> set[str]:
    files = {row['path'] for row in rows}
    require(len(files) == 986 and len(rows) == 986,
            'snapshot requires exact selected 986 files')
    return {parent.as_posix() for name in files for parent in Path(name).parents
            if parent.as_posix() != '.'} | {PRODUCER + '/receipts'}


def mkdir_snapshot(path: Path) -> None:
    with held_directory(path.parent) as chain:
        os.mkdir(path.name, 0o700, dir_fd=chain[-1][1])
        fd = os.open(path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=chain[-1][1])
        try:
            state = os.fstat(fd)
            require(state.st_uid == os.getuid() and state.st_mode & 0o777 == 0o700,
                    'snapshot directory owner or mode differs')
            os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(chain[-1][1])


def cleanup_snapshot(snapshot: Path, identity: tuple[int, int]) -> None:
    """Delete only through the held, identity-checked original snapshot root."""
    with held_directory(snapshot.parent) as chain:
        parent_fd = chain[-1][1]
        root_fd = os.open(snapshot.name, os.O_RDONLY | os.O_DIRECTORY |
                          os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
        try:
            held = os.fstat(root_fd)
            named = os.stat(snapshot.name, dir_fd=parent_fd, follow_symlinks=False)
            require(stat.S_ISDIR(held.st_mode) and
                    (held.st_dev, held.st_ino) == identity == (named.st_dev, named.st_ino),
                    'owned snapshot root attachment differs before cleanup')

            def remove_children(directory_fd: int) -> None:
                # A moved root never redirects these mutations into its replacement.
                for name in sorted(os.listdir(directory_fd)):
                    require(name not in ('', '.', '..', '/') and '/' not in name,
                            'snapshot cleanup name differs')
                    before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                    if stat.S_ISDIR(before.st_mode):
                        child_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY |
                                           os.O_NOFOLLOW | os.O_CLOEXEC,
                                           dir_fd=directory_fd)
                        try:
                            held_child = os.fstat(child_fd)
                            require((before.st_dev, before.st_ino) ==
                                    (held_child.st_dev, held_child.st_ino),
                                    'snapshot cleanup child attachment differs')
                            remove_children(child_fd)
                        finally:
                            os.close(child_fd)
                        named_child = os.stat(name, dir_fd=directory_fd,
                                              follow_symlinks=False)
                        require((before.st_dev, before.st_ino) ==
                                (named_child.st_dev, named_child.st_ino),
                                'snapshot cleanup child changed before removal')
                        os.rmdir(name, dir_fd=directory_fd)
                    else:
                        require(stat.S_ISREG(before.st_mode),
                                'snapshot cleanup found nonregular entry')
                        named_child = os.stat(name, dir_fd=directory_fd,
                                              follow_symlinks=False)
                        require((before.st_dev, before.st_ino) ==
                                (named_child.st_dev, named_child.st_ino),
                                'snapshot cleanup child changed before removal')
                        os.unlink(name, dir_fd=directory_fd)
                    os.fsync(directory_fd)

            remove_children(root_fd)
            named = os.stat(snapshot.name, dir_fd=parent_fd, follow_symlinks=False)
            require((named.st_dev, named.st_ino) == identity,
                    'owned snapshot root changed during cleanup')
            os.rmdir(snapshot.name, dir_fd=parent_fd)
            os.fsync(parent_fd)
        finally:
            os.close(root_fd)
    require(not snapshot.exists(), 'owned snapshot cleanup unconfirmed')


@contextmanager
def stage_snapshot(rows: list[dict]):
    """Keep every selected byte inside an owner-only tmpfs root for cold-open."""
    snapshot = SNAPSHOT_PARENT / SNAPSHOT_NAME
    mkdir_snapshot(snapshot)  # Exact no-replace name; no retry.
    identity = (snapshot.stat().st_dev, snapshot.stat().st_ino)
    primary = None
    try:
        require(not REQUIRE_SEPARATE_DEVICE or snapshot.stat().st_dev != ROOT.stat().st_dev,
                'snapshot is not on a separate selected tmpfs device')
        directories = snapshot_directory_names(rows)
        for name in sorted(directories, key=lambda value: (len(Path(value).parts), value)):
            mkdir_snapshot(snapshot / name)
        total = 0
        for row in sorted(rows, key=lambda item: item['path']):
            total += copy_snapshot_member(ROOT / row['path'], snapshot / row['path'],
                                          row['sha256'])
            require(total <= MAX_SNAPSHOT_TOTAL, 'snapshot total exceeds selected tmpfs bound')
        yield snapshot
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            cleanup_snapshot(snapshot, identity)
        except BaseException as cleanup_error:
            if primary is None:
                raise
            raise BaseExceptionGroup('snapshot work and cleanup both failed',
                                     [primary, cleanup_error]) from primary


def fresh_module_namespace() -> None:
    require(not any(k == MODULE or k.startswith(MODULE + '.') or
                    k == PRODUCER_MODULE or k.startswith(PRODUCER_MODULE + '.')
                    for k in sys.modules), 'stale Reader/Source module namespace present')
    role, producer = ROOT / READER, ROOT / PRODUCER
    for name, module in tuple(sys.modules.items()):
        origin = getattr(module, '__file__', None)
        if isinstance(origin, str):
            path = Path(origin).resolve()
            require(not path.is_relative_to(role) and not path.is_relative_to(producer),
                    'stale Reader/Source module alias present: ' + name)


@contextmanager
def held_code_snapshot(source: dict, reader: dict):
    """Hold and hash the exact bytes that the scoped loader will execute."""
    with ExitStack() as stack:
        members = {}
        for prefix, stem, rows in ((MODULE, READER, reader['files']),
                                   (PRODUCER_MODULE, PRODUCER, source['files'])):
            for row in rows:
                relative = Path(row['path'])
                if relative.parent != Path(stem) or relative.suffix != '.py':
                    continue
                suffix = '' if relative.name == '__init__.py' else '.' + relative.stem
                name = prefix + suffix
                require(name not in members, 'duplicate selected code module')
                path = ROOT / relative
                chain = stack.enter_context(held_directory(path.parent))
                fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                             dir_fd=chain[-1][1])
                stack.callback(os.close, fd)
                metadata = os.fstat(fd)
                require(stat.S_ISREG(metadata.st_mode) and metadata.st_size <= MAX_CODE,
                        'selected code exceeds module bound')
                raw = os.read(fd, metadata.st_size + 1)
                named = os.stat(path.name, dir_fd=chain[-1][1], follow_symlinks=False)
                require(len(raw) == metadata.st_size and sha(raw) == row['sha256'] and
                        (metadata.st_dev, metadata.st_ino) == (named.st_dev, named.st_ino),
                        'selected code snapshot differs')
                members[name] = {'path': path, 'raw': raw, 'sha256': row['sha256'],
                                 'fd': fd, 'chain': chain, 'identity':
                                 (metadata.st_dev, metadata.st_ino), 'executed_sha256': None}
        require({MODULE, MODULE + '.adapter', MODULE + '.base', MODULE + '.eligibility',
                 MODULE + '.inspection', MODULE + '.model', MODULE + '.reader',
                 PRODUCER_MODULE, PRODUCER_MODULE + '.base', PRODUCER_MODULE + '.cold',
                 PRODUCER_MODULE + '.records'} <= set(members),
                'selected code snapshot lacks required modules')
        check_snapshot(members)
        yield members
        check_snapshot(members)


def check_snapshot(members: dict) -> None:
    for member in members.values():
        check_chain(member['chain'])
        held = os.fstat(member['fd'])
        named = os.stat(member['path'].name, dir_fd=member['chain'][-1][1],
                        follow_symlinks=False)
        require(stat.S_ISREG(named.st_mode) and
                (held.st_dev, held.st_ino) == (named.st_dev, named.st_ino) == member['identity'] and
                held.st_size == len(member['raw']), 'selected code attachment changed')


class SealedLoader(importlib.abc.Loader):
    def __init__(self, name: str, member: dict):
        self.name, self.member = name, member

    def create_module(self, _spec):
        return None

    def exec_module(self, module):
        member = self.member
        require(sha(member['raw']) == member['sha256'], 'sealed executed code differs')
        module.__file__ = str(member['path'])
        module.__loader__ = self
        if member['path'].name == '__init__.py':
            module.__path__ = [str(member['path'].parent)]
        member['executed_sha256'] = sha(member['raw'])
        exec(compile(member['raw'], str(member['path']), 'exec', dont_inherit=True),
             module.__dict__)


class SealedFinder(importlib.abc.MetaPathFinder):
    def __init__(self, members: dict):
        self.members = members
        self.loaders = {name: SealedLoader(name, member) for name, member in members.items()}
        for name, member in members.items():
            member['loader'] = self.loaders[name]

    def find_spec(self, fullname, _path=None, _target=None):
        if fullname in self.members:
            member = self.members[fullname]
            return importlib.util.spec_from_loader(fullname, self.loaders[fullname],
                                                   origin=str(member['path']),
                                                   is_package=member['path'].name == '__init__.py')
        if any(fullname.startswith(prefix + '.') for prefix in (MODULE, PRODUCER_MODULE)):
            raise ImportError('unselected Reader/Source module name')
        return None


@contextmanager
def sealed_imports(members: dict):
    """Catch both normal imports and the frozen Reader base's explicit producer spec."""
    finder = SealedFinder(members)
    original = importlib.util.spec_from_file_location
    def spec_from_file_location(name, location, *args, **kwargs):
        if name in members or any(name.startswith(prefix + '.')
                                  for prefix in (MODULE, PRODUCER_MODULE)):
            require(name in members and str(location) == str(members[name]['path']),
                    'selected module spec path differs')
            return finder.find_spec(name)
        return original(name, location, *args, **kwargs)
    sys.meta_path.insert(0, finder)
    importlib.util.spec_from_file_location = spec_from_file_location
    try:
        yield finder
    finally:
        importlib.util.spec_from_file_location = original
        sys.meta_path.remove(finder)


def module_origins(source: dict, reader: dict, *, snapshot: dict | None = None) -> None:
    """Check all loaded selected namespaces against staged paths and hashes."""
    for prefix, root, rows, required in (
        (MODULE, ROOT / READER, reader['files'],
         {'', '.adapter', '.base', '.eligibility', '.inspection', '.model', '.reader'}),
        (PRODUCER_MODULE, ROOT / PRODUCER, source['files'],
         {'', '.base', '.cold', '.records'}),
    ):
        mapping = {}
        for row in rows:
            path = Path(row['path'])
            if path.parent == Path(READER if prefix == MODULE else PRODUCER) and path.suffix == '.py':
                suffix = '' if path.name == '__init__.py' else '.' + path.stem
                mapping[prefix + suffix] = row
        present = {name for name in sys.modules
                   if name == prefix or name.startswith(prefix + '.')}
        require({prefix + suffix for suffix in required} <= present and
                present <= set(mapping), 'selected module namespace differs')
        for name in present:
            module = sys.modules[name]
            row = mapping[name]
            expected_path = ROOT / row['path']
            require(getattr(module, '__file__', None) == str(expected_path) and
                    sha(regular(expected_path)) == row['sha256'],
                    'selected module origin or bytes differ: ' + name)
            if snapshot is not None:
                require(name in snapshot and module.__loader__ is snapshot[name]['loader'] and
                        snapshot[name]['executed_sha256'] == row['sha256'],
                        'selected executed module bytes differ: ' + name)
            if name == prefix:
                require(list(getattr(module, '__path__', ())) == [str(root)],
                        'selected package search path differs')
    for name, module in tuple(sys.modules.items()):
        origin = getattr(module, '__file__', None)
        if isinstance(origin, str):
            path = Path(origin).resolve()
            require(not (path.is_relative_to(ROOT / READER) and
                         not (name == MODULE or name.startswith(MODULE + '.'))) and
                    not (path.is_relative_to(ROOT / PRODUCER) and
                         not (name == PRODUCER_MODULE or name.startswith(PRODUCER_MODULE + '.'))),
                    'selected module has an unexpected alias')


def aggregate(signed: object, report: dict, loaded: object) -> dict:
    report_raw = bounded_encoded(report, MAX_REPORT)
    require(type(report) is dict and type(report.get('carrier_counts')) is dict and
            type(report.get('missing_current_carriers')) is list and
            len(report_raw) <= MAX_REPORT, 'Reader closure report exceeds bounded shape')
    allowed = set(loaded.adapter.CARRIERS)
    counts = report['carrier_counts']
    require(set(counts) == allowed and
            all(type(value) is int and 0 <= value <= 10000 for value in counts.values()) and
            sum(counts.values()) == len(signed.records) and
            all(row.artifact['carrier_ref'] in allowed for row in signed.records),
            'Reader current carrier accounting differs')
    actual = {carrier: sum(row.artifact['carrier_ref'] == carrier for row in signed.records)
              for carrier in allowed}
    require(actual == counts, 'Reader carrier count differs')
    required = {'cal.artifact-type.goal/v1',
                'cal.artifact-type.coordination-context/v2',
                'cal.artifact-type.project-state/v2'}
    require(set(report['missing_current_carriers']) ==
            {carrier for carrier in required if counts[carrier] == 0} and
            len(report['missing_current_carriers']) == len(set(report['missing_current_carriers'])),
            'Reader missing-carrier result differs')
    require(type(report.get('accounted_subjects')) is int and
            report['accounted_subjects'] == len(signed.dispositions) and
            type(report.get('included_current_instances')) is int and
            report['included_current_instances'] == len(signed.records) and
            report.get('authority_effect') == 'none' and
            report.get('actual_owner_outcome') is None,
            'Reader closure aggregate differs')
    return {'accounted_subjects': len(signed.dispositions),
            'current_records': len(signed.records),
            'schemas': len(signed.schemas),
            'missing_current_carriers': sorted(report['missing_current_carriers']),
            'private_closure_report_sha256': sha(report_raw)}


def run() -> dict:
    global ROOT
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    selection, _, expected, source_manifest, reader_manifest, rows = selected()
    original_root = ROOT
    with stage_snapshot(rows) as snapshot_root:
        ROOT = snapshot_root
        try:
            snap_selection, _, snap_expected, snap_source, snap_reader, snap_rows = selected()
            require((snap_selection, snap_expected, snap_source, snap_reader, snap_rows) ==
                    (selection, expected, source_manifest, reader_manifest, rows),
                    'owned snapshot selection differs')
            fresh_module_namespace()
            with held_code_snapshot(snap_source, snap_reader) as code_snapshot:
                with sealed_imports(code_snapshot):
                    return _run_sealed(snap_selection, snap_expected, snap_source,
                                       snap_reader, code_snapshot)
        finally:
            ROOT = original_root


def _run_sealed(selection: dict, expected: dict, source_manifest: dict,
                reader_manifest: dict, snapshot: dict) -> dict:
    role = ROOT / READER
    spec = importlib.util.spec_from_file_location(MODULE, role / '__init__.py',
                                                   submodule_search_locations=[str(role)])
    require(spec is not None and spec.loader is not None, 'Reader module spec unavailable')
    package = importlib.util.module_from_spec(spec)
    sys.modules[MODULE] = package
    spec.loader.exec_module(package)
    loaded = __import__(MODULE + '.reader', fromlist=['SelectedReader'])
    module_origins(source_manifest, reader_manifest, snapshot=snapshot)
    reader = loaded.SelectedReader(READER_SHA,
                                   selection['source_manifest_binding']['sha256'],
                                   selection['source_package_binding']['sha256'])
    with reader.open_signed(reader.source_pin, reader.package_pin) as signed:
        require(type(signed) is loaded.adapter.SignedSources and
                type(signed.view) is loaded.Inspection, 'actual Reader type differs')
        # This is deliberately inside the cold-open context, after actual
        # Source/Reader construction and before the signed guard.
        period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
        module_origins(source_manifest, reader_manifest, snapshot=snapshot)
        signed.guard()
        report = signed.closure_report()
        summary = aggregate(signed, report, loaded)
        result = {
            'schema_version': 'lab-disposable-reader-receipt/v1-private',
            'reader_manifest_sha256': READER_SHA,
            'source_manifest_sha256': reader.source_pin,
            'source_package_manifest_sha256': reader.package_pin,
            'expected_head': expected['expected_head'],
            'source_cut_sha256': sha(encoded(signed.source_cut)),
            **summary,
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': 'Disposable exact-pinned Source cold-open and fresh Reader diagnostic only.',
        }
        require(len(encoded(result)) <= MAX_RECEIPT, 'Reader aggregate receipt exceeds bound')
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    selected()  # Recheck every staged input, including private archive, after close.
    module_origins(source_manifest, reader_manifest, snapshot=snapshot)
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    raw = encoded(result)
    fd = os.open(OUT / 'receipt.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    output_fd = os.open(OUT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(output_fd)
    finally:
        os.close(output_fd)
    require((OUT / 'receipt.json').read_bytes() == raw and
            {p.name for p in OUT.iterdir()} == {'receipt.json'}, 'Reader receipt differs')
    selected(output_empty=False)  # Full postreceipt 986-file rehash.
    module_origins(source_manifest, reader_manifest, snapshot=snapshot)
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    return {'result': 'PASS_READER_PRIVATE', 'receipt_sha256': sha(raw),
            'reader_manifest_sha256': READER_SHA, 'source_package_manifest_sha256': reader.package_pin}


if __name__ == '__main__':
    require(sys.argv[1:] == ['--execute-reviewed-one-shot'], 'reviewed one-shot flag required')
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    print(json.dumps(run(), sort_keys=True))
