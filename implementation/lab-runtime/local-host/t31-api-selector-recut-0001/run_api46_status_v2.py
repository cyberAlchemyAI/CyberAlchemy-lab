"""Byte-backed API46 Base lab.status on one fresh current WSL source."""

from datetime import datetime, timezone
import hashlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v46-t31-workflow-current-0002'
SOURCE_SHA = 'caf4aa1f4dbfcc8a5eab336e15704487f3e1913b8d76bfbcfbd88b56204a0969'
PROFILE_SHA = 'a4a2afdf2853f135a473c19b8dd83dc4cd3b587bc00821a227a4790a365c7402'
PACKAGE_NAME = '_cal_t31_api46_pinned_status'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(path, expected=None):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('selected path is not absolute and closed')
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
                raise ValueError('selected file is not regular')
            parts = []
            while block := os.read(fd, 1024 * 1024):
                parts.append(block)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda v: (v.st_dev, v.st_ino, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(attached):
                raise ValueError('selected file changed during capture')
            raw = b''.join(parts)
            if expected is not None and sha(raw) != expected:
                raise ValueError('selected file digest differs: ' + str(path))
            return raw
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def captured_code():
    manifest = json.loads(exact(API / 'source-manifest.json', SOURCE_SHA))
    if len(manifest['files']) != 207:
        raise ValueError('selected API46 source count differs')
    prefix = API.relative_to(ROOT).as_posix() + '/'
    code = {}
    for row in manifest['files']:
        if row['path'].startswith(prefix) and row['path'].endswith('.py'):
            leaf = row['path'][len(prefix):]
            if '/' in leaf or leaf in code:
                raise ValueError('selected API46 module name differs')
            file = API / leaf
            code[leaf] = (file, exact(file, row['sha256']))
    if len(code) != 145 or not {'__init__.py', 'guard.py', 'protocol.py', 'auth.py',
                                 'service.py', 'source_bridge.py'} <= set(code):
        raise ValueError('selected API46 executable closure differs')
    exact(API / 'contract-profile.json', PROFILE_SHA)
    return code


class PinnedAPIFinder(MetaPathFinder, Loader):
    def __init__(self, code):
        self.code = code
        self.loaded = []

    def find_spec(self, fullname, path=None, target=None):
        if fullname != PACKAGE_NAME and not fullname.startswith(PACKAGE_NAME + '.'):
            return None
        leaf = '__init__.py' if fullname == PACKAGE_NAME else fullname[len(PACKAGE_NAME) + 1:] + '.py'
        if leaf not in self.code:
            raise ImportError('unselected API46 module: ' + fullname)
        file, _ = self.code[leaf]
        package = fullname == PACKAGE_NAME
        spec = ModuleSpec(fullname, self, origin=str(file), is_package=package)
        if package:
            spec.submodule_search_locations = [str(API)]
        return spec

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        leaf = '__init__.py' if module.__name__ == PACKAGE_NAME else module.__name__[len(PACKAGE_NAME) + 1:] + '.py'
        file, raw = self.code[leaf]
        module.__file__ = str(file)
        exec(compile(raw, str(file), 'exec', dont_inherit=True), module.__dict__)
        self.loaded.append(leaf)


def main():
    os.umask(0o077)
    expected_runner = globals().get('__selected_runner_sha__')
    if not isinstance(expected_runner, str) or len(expected_runner) != 64:
        raise ValueError('external byte-backed runner selection absent')
    runner = Path(__file__)
    exact(runner, expected_runner)
    code = captured_code()
    if any(name == PACKAGE_NAME or name.startswith(PACKAGE_NAME + '.') for name in sys.modules):
        raise ValueError('ambient API46 module present before selected import')
    finder = PinnedAPIFinder(code)
    sys.meta_path.insert(0, finder)
    __import__(PACKAGE_NAME)
    prefix = PACKAGE_NAME + '.'
    P = __import__(prefix + 'protocol', fromlist=['Schemas'])
    A = __import__(prefix + 'auth', fromlist=['ReaderChannel'])
    S = __import__(prefix + 'service', fromlist=['Service'])
    H = __import__(prefix + 'handlers', fromlist=['cut'])
    F = __import__(prefix + 'example_fixture', fromlist=['materials_for'])
    G = __import__(prefix + 'guard', fromlist=['verify'])
    L = __import__(prefix + 'legacy_fixture_selection', fromlist=['PUBLIC_SOURCE_NAME'])
    C = __import__(prefix + 'projection_refresh', fromlist=['control'])
    G.verify(SOURCE_SHA)
    schemas = P.Schemas(PROFILE_SHA)
    result = {'schema_version': 'lab-T31-API46-authenticated-status/v2-candidate',
              'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
              'selection_sha256': sha(exact(HERE / 'SELECTION-0001.json')),
              'runner_sha256': expected_runner,
              'captured_package_python_modules': len(code),
              'authority_effect': 'none', 'whole_api_qualified': False,
              'workflow_transition_executed': False,
              'started_at_utc': datetime.now(timezone.utc).isoformat()}
    with P.source.replay_source(L.PUBLIC_SOURCE_NAME) as view:
        materials, metadata, _ = F.materials_for(view)
        with tempfile.TemporaryDirectory(prefix='cal-T31-api46-status-', dir='/tmp') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            key, policy, pin = F.provision(root, L.PUBLIC_SOURCE_NAME, materials, metadata,
                                           principal=L.EXPECTED_PRINCIPAL,
                                           projection_control=C.control(view))
            channel = A.ReaderChannel(policy, pin, schemas)
            authenticated = channel.authenticate(F.proof(key, channel.challenge))
            service = S.Service(view, channel, schemas)
            try:
                context = authenticated['context']
                if context['principal_ref'] != L.EXPECTED_PRINCIPAL:
                    raise ValueError('actual authenticated principal differs')
                call = F.call(context, 'lab.status', H.cut(view))
                reply = service.call(P.compact(call))
                if not (reply.get('kind') == 'result' and schemas.valid('api-reply', reply) and
                        reply.get('operation') == 'lab.status' and
                        reply.get('call_id') == call['call_id'] and
                        reply.get('request_binding') == P.binding(
                            'call:' + channel.connection + ':' + call['call_id'], P.compact(call)) and
                        reply['message'].get('schema_version') == 'lab-lab-status-result/v1-candidate' and
                        reply['message'].get('source_cut') == H.cut(view) and
                        reply['message'].get('request_binding', {}).get('sha256') ==
                        sha(P.message_bytes(P.compact(call)))):
                    raise ValueError('selected authenticated Base status refused')
                result.update(status='PASS', source_cut_sha256=sha(P.compact(H.cut(view))),
                              call_sha256=sha(P.compact(call)), reply_sha256=sha(P.compact(reply)),
                              call_id=call['call_id'], reply_call_id=reply['call_id'],
                              inner_request_binding=reply['message']['request_binding'],
                              operation='lab.status', reply_kind=reply['kind'],
                              principal_ref=context['principal_ref'])
            finally:
                service.close()
                channel.close()
                key = None
        if root.exists():
            raise ValueError('owned private status root remained')
        if hasattr(view, 'custody_signed_sources'):
            view.custody_signed_sources.guard()
    G.verify(SOURCE_SHA)
    if len(finder.loaded) < 6 or not {'__init__.py', 'guard.py', 'protocol.py', 'auth.py',
                                      'service.py', 'source_bridge.py'} <= set(finder.loaded):
        raise ValueError('selected API46 runtime modules were not byte-backed')
    result['byte_backed_loaded_modules'] = sorted(finder.loaded)
    for leaf, (file, raw) in code.items():
        exact(file, sha(raw))
    exact(runner, expected_runner)
    result['private_root_removed'] = True
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['claim_ceiling'] = ('One authenticated current-cut API46 Base lab.status on this WSL host; '
                               'no workflow transition, portable package, owner decision, or release.')
    path = HERE / 'RUN-API46-STATUS-0002.json'
    with path.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'receipt_sha256': sha(path.read_bytes())}, sort_keys=True))


if __name__ == '__main__':
    main()
