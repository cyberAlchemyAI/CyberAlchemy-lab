"""Pure exact-byte Context AUTH guard projection; no authorization is selected."""
import ast
import hashlib
import json
import os
import stat
from pathlib import Path

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
PREDECESSOR = REPO / 'implementation/lab-runtime/local-host/context-closure-0001'
FREEZE_SHA = 'd03f9967d80478b669b8600e20f7638705d119327cc1d55309c033e529f4cc8b'
REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-CLOSURE-INDEPENDENT-STATIC-REVIEW-0001.md'
REVIEW_SHA = '5f7177bf13d2bffb4897b8b153c6c72f96fae7a36f0eee3e9ce03e2ff0529d6a'
AUTH_0001_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-auth-guard-0001/freeze.json'
AUTH_0001_FREEZE_SHA = '93764838fc510da2b4d5590fbc56b78757e649931cd03875a43ab3d6547b9429'
AUTH_0001_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-AUTH-GUARD-INDEPENDENT-STATIC-REVIEW-0001.md'
AUTH_0001_REVIEW_SHA = '814f0f5e8cf032984e6a3e8e3d37d7f9e0ec1aa29a2a67f228f68c78151ab757'
AUTH_0002_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-auth-guard-0002/freeze.json'
AUTH_0002_FREEZE_SHA = '7c03ebdf0df3e46bacc236a53b676a89d0affb0d6167415305a1492f1ef53ed2'
AUTH_0002_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-AUTH-GUARD-INDEPENDENT-STATIC-REVIEW-0002.md'
AUTH_0002_REVIEW_SHA = '3a8e7c4da85ecf8dcda06bf126261da8dea61ccc81cd49022dac46fa3c17fd56'
AUTH_0003_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-auth-guard-0003/freeze.json'
AUTH_0003_FREEZE_SHA = '5051cdc38adc51e0030416d0faf4845b12c3d477035a2f8a20febe6b7988582f'
AUTH_0003_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-AUTH-GUARD-INDEPENDENT-STATIC-REVIEW-0003.md'
AUTH_0003_REVIEW_SHA = '6472b0f06b4ce633ded0988b33510b7dfc8974202376cb76ad9ad03c0de41794'
HELD_SHA = 'f7054b285f8eacfbd4c31e097aa1f0fb7a77bb7fe9d0810b733ef00df11a4976'
PATH = 'authorization/context-development.json'


class Refused(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pin(path, pin):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= 4 * 1024 * 1024,
                'frozen input must be bounded regular file')
        parts, total = [], 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, before.st_size + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            require(total <= before.st_size, 'frozen input grew')
            parts.append(chunk)
        after = os.fstat(fd)
        require((before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
                (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
                total == before.st_size, 'frozen input changed during read')
        raw = b''.join(parts)
        require(sha(raw) == pin, 'frozen input digest differs')
        return raw
    finally:
        os.close(fd)


def project_control(pin):
    require(type(pin) is str and len(pin) == 64 and
            all(c in '0123456789abcdef' for c in pin),
            'future exact development authorization digest required')
    freeze = json.loads(read_pin(PREDECESSOR / 'freeze.json', FREEZE_SHA))
    read_pin(REVIEW, REVIEW_SHA)
    read_pin(AUTH_0001_FREEZE, AUTH_0001_FREEZE_SHA)
    read_pin(AUTH_0001_REVIEW, AUTH_0001_REVIEW_SHA)
    read_pin(AUTH_0002_FREEZE, AUTH_0002_FREEZE_SHA)
    read_pin(AUTH_0002_REVIEW, AUTH_0002_REVIEW_SHA)
    read_pin(AUTH_0003_FREEZE, AUTH_0003_FREEZE_SHA)
    read_pin(AUTH_0003_REVIEW, AUTH_0003_REVIEW_SHA)
    member = next(row for row in freeze['files'] if row['path'] == 'closure.py')
    source = read_pin(PREDECESSOR / 'closure.py', member['sha256'])
    namespace = {'__file__': str(PREDECESSOR / 'closure.py'), '__name__': '_exact_frozen_context_closure'}
    exec(compile(source, namespace['__file__'], 'exec'), namespace)
    predecessor = namespace['project_auth_pure'](PATH, pin)
    module = read_pin(HERE / 'held_auth.py', HELD_SHA)
    insertion = ("AUTH_SHA = '" + pin + "'\n").encode()
    old_read = b'raw = AUTH.read_bytes()'
    guarded_read = b'raw = read_auth_bytes(AUTH, ROOT, AUTH_SHA, os.geteuid())'
    require(predecessor.count(insertion) == 1 and predecessor.count(old_read) == 1,
            'frozen provisional AUTH preimage differs')
    projected = predecessor.replace(old_read, guarded_read, 1)
    projected = projected.replace(insertion, insertion + b'\n' + module + b'\n', 1)
    tree = ast.parse(projected)
    functions = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    require(functions.count('read_auth_bytes') == 1 and
            functions.count('_context_development_auth') == 1 and
            projected.count(b'_context_development_auth(self.source.sources.scope_ref)') == 2 and
            projected.count(guarded_read) == 1 and b'AUTH.read_bytes()' not in projected,
            'held AUTH call-site projection differs')
    inverse = projected.replace(insertion + b'\n' + module + b'\n', insertion, 1)
    inverse = inverse.replace(guarded_read, old_read, 1)
    require(inverse == predecessor, 'held AUTH byte inverse differs')
    return projected, {
        'schema_version': 'lab-context-held-auth-projection-proof/v1',
        'status': 'PURE_PROJECTION_ONLY', 'predecessor_sha256': sha(predecessor),
        'projected_sha256': sha(projected), 'held_auth_sha256': HELD_SHA,
        'byte_inverse': True, 'old_auth_read_sites': 2,
        'guarded_auth_read_sites': 2, 'bounded_held_read_implementations': 1,
        'grant_created': False, 'key_created': False, 'policy_created': False,
        'context_launch': 'REFUSED', 'effect': 'NOT_RUN',
    }


def final_context_source_manifest(*_args, **_kwargs):
    raise Refused('fresh same-family authorization and Mapper package required')


def launch_context(*_args, **_kwargs):
    raise Refused('effect-disabled Context AUTH guard candidate')
