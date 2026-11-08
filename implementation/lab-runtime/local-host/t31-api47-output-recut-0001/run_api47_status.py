"""One fresh authenticated API47 Base lab.status call on the selected WSL cut."""

from datetime import datetime, timezone
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v47-t31-output-current-0001'
SOURCE_SHA = 'de4487eef78b5737cd2f4919c1e7280b5eef2e78dc5beb342cde87cb19651fd1'
PROFILE_SHA = '2c62d15d212b1151ce91928a0f78346d0679725bd9953f972dd86c64af2660f9'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    path = Path(path)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected API47 path linked')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('selected API47 code is not regular')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read()
    finally:
        os.close(fd)
    if sha(raw) != expected:
        raise ValueError('selected API47 code differs')
    return raw


class CapturedApi(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, name, files):
        self.name, self.files = name, files

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.name or fullname.startswith(self.name + '.'):
            if fullname not in self.files:
                raise ModuleNotFoundError('unselected API47 module: ' + fullname)
            return importlib.util.spec_from_loader(fullname, self, is_package=fullname == self.name)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path, raw = self.files[module.__name__]
        module.__file__ = str(path)
        if module.__name__ == self.name:
            module.__path__ = [str(path.parent)]
        exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)


def selected_api():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('run with isolated no-bytecode Python')
    manifest = json.loads(checked(API / 'source-manifest.json', SOURCE_SHA))
    checked(API / 'contract-profile.json', PROFILE_SHA)
    prefix = API.relative_to(ROOT).as_posix() + '/'
    captured = {}
    code_rows = []
    name = '_cal_t31_api47_live_status_' + SOURCE_SHA[:16]
    for row in manifest['files']:
        path = row['path']
        if not path.startswith(prefix) or not path.endswith('.py'):
            continue
        relative = path[len(prefix):]
        if '/' in relative:
            raise ValueError('nested API47 module not in flat selected closure')
        fullname = name if relative == '__init__.py' else name + '.' + relative[:-3]
        if fullname in captured:
            raise ValueError('duplicate API47 module')
        captured[fullname] = (ROOT / path, checked(ROOT / path, row['sha256']))
        code_rows.append(row)
    if len(captured) < 100 or name not in captured or name + '.guard' not in captured:
        raise ValueError('API47 selected Python closure missing')
    if any(loaded == name or loaded.startswith(name + '.') for loaded in sys.modules):
        raise ValueError('preloaded API47 module refused')
    finder = CapturedApi(name, captured)
    sys.meta_path.insert(0, finder)
    importlib.import_module(name)
    guard = importlib.import_module(name + '.guard')
    guard.verify(SOURCE_SHA)
    return name, guard, {'python_modules':len(captured),
                         'selected_code_rows_sha256':sha(json.dumps(code_rows, sort_keys=True, separators=(',', ':')).encode())}


def main():
    os.umask(0o077)
    selected_raw = globals().get('_HELD_RUNNER_SELECTION')
    held_sha = globals().get('_HELD_RUNNER_SHA256')
    if type(selected_raw) is not bytes or type(held_sha) is not str:
        raise ValueError('byte-backed API47 runner selection required')
    runner_selection = json.loads(selected_raw)
    if (runner_selection['runner_binding'] != {'path':str(Path(__file__).relative_to(ROOT)),'sha256':held_sha}
            or sha(Path(__file__).read_bytes()) != held_sha
            or runner_selection['api_source_binding']['sha256'] != SOURCE_SHA
            or runner_selection['api_profile_binding']['sha256'] != PROFILE_SHA):
        raise ValueError('selected API47 runner/source/profile differs')
    name, G, selected_code = selected_api()
    prefix = name + '.'
    P = __import__(prefix + 'protocol', fromlist=['Schemas'])
    A = __import__(prefix + 'auth', fromlist=['ReaderChannel'])
    S = __import__(prefix + 'service', fromlist=['Service'])
    H = __import__(prefix + 'handlers', fromlist=['cut'])
    F = __import__(prefix + 'example_fixture', fromlist=['materials_for'])
    L = __import__(prefix + 'legacy_fixture_selection', fromlist=['PUBLIC_SOURCE_NAME'])
    C = __import__(prefix + 'projection_refresh', fromlist=['control'])
    G.verify(SOURCE_SHA)
    schemas = P.Schemas(PROFILE_SHA)
    result = {'schema_version': 'lab-T31-API47-authenticated-status/v1-candidate',
              'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
              'captured_selected_code': selected_code,
              'runner_selection_sha256':sha(selected_raw),
              'selection_sha256': sha((HERE / 'STATIC-VERIFY-0001.json').read_bytes()),
              'authority_effect': 'none', 'whole_api_qualified': False,
              'workflow_transition_executed': False,
              'started_at_utc': datetime.now(timezone.utc).isoformat()}
    with P.source.replay_source(L.PUBLIC_SOURCE_NAME) as view:
        materials, metadata, _ = F.materials_for(view)
        with tempfile.TemporaryDirectory(prefix='cal-T31-api47-status-', dir='/tmp') as temporary:
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
                if not (reply.get('kind') == 'result' and schemas.valid('api-reply', reply)):
                    raise ValueError('selected authenticated Base status refused')
                result.update(status='PASS', source_cut_sha256=sha(P.compact(H.cut(view))),
                              call_sha256=sha(P.compact(call)), reply_sha256=sha(P.compact(reply)),
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
    if (sha(Path(__file__).read_bytes()) != held_sha or
            sha((HERE/'API47-STATUS-RUNNER-SELECTION-0001.json').read_bytes()) != sha(selected_raw)):
        raise ValueError('selected API47 runner changed during live status')
    result['private_root_removed'] = True
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['claim_ceiling'] = ('One authenticated current-cut API47 Base lab.status on this WSL host; '
                               'no workflow transition, portable package, owner decision, or release.')
    path = HERE / 'RUN-API47-STATUS-0001.json'
    with path.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'receipt_sha256': sha(path.read_bytes())}, sort_keys=True))


if __name__ == '__main__':
    main()
