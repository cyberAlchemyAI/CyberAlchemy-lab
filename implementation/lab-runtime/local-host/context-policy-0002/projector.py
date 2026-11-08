"""Exact-byte, effect-disabled projection of the reviewed Context AUTH candidate."""
import ast
import hashlib
import json
import os
import stat
from pathlib import Path

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
AUTH = REPO / 'implementation/lab-runtime/local-host/context-auth-guard-0004'
AUTH_FREEZE_SHA = '40baf5d872fdd95ab34238311c26a21dfc12dbb44cd2160487a515b3dbaf473a'
AUTH_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-AUTH-GUARD-INDEPENDENT-STATIC-REVIEW-0004.md'
AUTH_REVIEW_SHA = '01e818c8d17834b1eae7dec77fbaca16e23f3820b737c80d20b08a49ae6f6626'
AUTH_PROJECTOR_SHA = '0331fce1b0bf0c738e3af078a020d543d9295dcdad7f0f5b0cf255c44f570817'
POLICY_READER_SHA = '0565b4a1a559404cf773198bf52e62f444b656084157557319ff0c3b44253a6f'
POLICY_0001_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-policy-0001/freeze.json'
POLICY_0001_FREEZE_SHA = 'b6c898fbc6a76365addadb4e8b7721333371fad9dd443225cd74481ac46269cf'
POLICY_0001_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-POLICY-INDEPENDENT-STATIC-REVIEW-0001.md'
POLICY_0001_REVIEW_SHA = '14521c6133fedd9ccae949b47bc9e74b1f0443ce7e21b4a853c153c75d46c312'

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

def project_control(auth_pin, policy_pin):
    """Return code bytes only; never write/import/launch a Context module."""
    for pin in (auth_pin, policy_pin):
        require(type(pin) is str and len(pin) == 64 and
                all(c in '0123456789abcdef' for c in pin), 'exact future digest required')
    frozen = json.loads(read_pin(AUTH / 'freeze.json', AUTH_FREEZE_SHA))
    read_pin(AUTH_REVIEW, AUTH_REVIEW_SHA)
    read_pin(POLICY_0001_FREEZE, POLICY_0001_FREEZE_SHA)
    read_pin(POLICY_0001_REVIEW, POLICY_0001_REVIEW_SHA)
    member = next(row for row in frozen['files'] if row['path'] == 'projector.py')
    require(member['sha256'] == AUTH_PROJECTOR_SHA, 'reviewed AUTH projector differs')
    predecessor_source = read_pin(AUTH / 'projector.py', AUTH_PROJECTOR_SHA)
    namespace = {'__file__': str(AUTH / 'projector.py'), '__name__': '_exact_frozen_auth_projector'}
    exec(compile(predecessor_source, namespace['__file__'], 'exec'), namespace)
    predecessor, auth_proof = namespace['project_control'](auth_pin)
    reader = read_pin(HERE / 'held_policy.py', POLICY_READER_SHA)
    marker = b'class HostChannel:\n'
    begin = b'        p = self.path\n'
    end = b'        v = EL.parse(raw)\n'
    guarded = (b'        raw = read_policy_bytes(self.path, self.path.parent, ROOT, '
               b'self.policy_sha, os.geteuid(), os.getegid())\n')
    require(predecessor.count(marker) == 1 and predecessor.count(begin) == 1 and
            predecessor.count(end) == 1, 'original HostChannel preimage differs')
    start = predecessor.index(begin)
    finish = predecessor.index(end, start)
    replaced = predecessor[start:finish]
    require(b'p.read_bytes()' in replaced and b'p.stat()' in replaced and
            b'os.getuid()' in replaced, 'original policy guard preimage differs')
    projected = predecessor[:start] + guarded + predecessor[finish:]
    old_binding = b'self.path.read_bytes()'
    new_binding = b'read_policy_bytes(self.path, self.path.parent, ROOT, self.policy_sha, os.geteuid(), os.getegid())'
    require(projected.count(old_binding) == 2, 'original policy binding read sites differ')
    projected = projected.replace(old_binding, new_binding)
    old_uid = b"v['host_uid'] == os.getuid()"
    new_uid = b"v['host_uid'] == os.geteuid()"
    require(projected.count(old_uid) == 1, 'original policy UID check differs')
    projected = projected.replace(old_uid, new_uid)
    guard_start = b"        require(not self.closed, 'closed host channel')\n"
    identity_check = (b"        require(os.getuid() == os.geteuid() and "
                      b"os.getgid() == os.getegid(), 'host runtime identity split')\n")
    require(projected.count(guard_start) == 1, 'original policy entrypoint differs')
    projected = projected.replace(guard_start, guard_start + identity_check, 1)
    projected = projected.replace(marker, reader + b'\n' + marker, 1)
    tree = ast.parse(projected)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'HostChannel')
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    require({'policy_guard', 'authenticate', 'permission'} <= set(methods), 'HostChannel methods differ')
    require(projected.count(b'read_policy_bytes(self.path, self.path.parent, ROOT, self.policy_sha, os.geteuid(), os.getegid())') == 3 and
            projected.count(b'def read_policy_bytes(') == 1 and old_binding not in projected and
            b'p.read_bytes()' not in projected and projected.count(new_uid) == 1,
            'policy guard/call-site projection differs')
    inverse = projected.replace(reader + b'\n' + marker, marker, 1)
    inverse = inverse.replace(guard_start + identity_check, guard_start, 1)
    inverse = inverse.replace(new_uid, old_uid, 1)
    inverse = inverse.replace(guarded + end, replaced + end, 1)
    inverse = inverse.replace(new_binding, old_binding)
    require(inverse == predecessor, 'policy byte inverse differs')
    return projected, {
        'schema_version': 'lab-context-held-policy-projection-proof/v2',
        'status': 'PURE_PROJECTION_ONLY', 'predecessor_sha256': sha(predecessor),
        'projected_sha256': sha(projected), 'held_policy_sha256': POLICY_READER_SHA,
        'reviewed_auth_projector_sha256': AUTH_PROJECTOR_SHA,
        'auth_projection_proof': auth_proof, 'byte_inverse': True,
        'policy_read_sites': 3, 'policy_held_read_implementations': 1,
        'grant_created': False, 'key_created': False, 'policy_created': False,
        'context_launch': 'REFUSED', 'effect': 'NOT_RUN',
    }

def construct_policy(*_args, **_kwargs):
    raise Refused('JIT policy requires fresh Mapper package, current Source period, selected namespace and new key')

def final_context_source_manifest(*_args, **_kwargs):
    raise Refused('fresh Mapper package and same-family source authority required')

def launch_context(*_args, **_kwargs):
    raise Refused('effect-disabled policy candidate')
