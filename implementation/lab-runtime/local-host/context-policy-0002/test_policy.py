"""Disposable dummy-byte tests. No valid grant, key, or protected input exists here."""
import ast
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import held_policy as H
import projector as P

DUMMY = b'{"not_a_policy":true}\n'
AUTH_PIN = 'a' * 64
POLICY_PIN = 'b' * 64

def fixture(root, raw=DUMMY):
    root = Path(root)
    policy = root / 'private-root'
    policy.mkdir(exist_ok=True, mode=0o700)
    (root / 'source-root').mkdir(exist_ok=True, mode=0o700)
    leaf = policy / 'permission.json'
    leaf.write_bytes(raw)
    leaf.chmod(0o600)
    return leaf

def pin(raw=DUMMY):
    return hashlib.sha256(raw).hexdigest()

def source_for(leaf):
    return leaf.parent.parent / 'source-root'

def read(leaf, digest=None):
    return H.read_policy_bytes(leaf, leaf.parent, source_for(leaf), digest or pin(), os.geteuid(), os.getegid())

class PolicyGuardTests(unittest.TestCase):
    def test_bounded_attached_good_dummy(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read(fixture(tmp)), DUMMY)

    def test_digest_and_mode_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            with self.assertRaisesRegex(H.PolicyRefused, 'digest differs'):
                read(leaf, '0' * 64)
            leaf.chmod(0o644)
            with self.assertRaisesRegex(H.PolicyRefused, 'bounded single-link'):
                read(leaf)

    def test_leaf_symlink_and_fifo_refuse_without_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            target = Path(tmp) / 'target'
            leaf.rename(target)
            leaf.symlink_to(target)
            with self.assertRaises(H.PolicyRefused):
                read(leaf)
            leaf.unlink()
            os.mkfifo(leaf)
            with self.assertRaises(H.PolicyRefused):
                read(leaf)

    def test_oversize_refuses_before_any_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = b'x' * (H.POLICY_LIMIT + 1)
            leaf = fixture(tmp, raw)
            with mock.patch.object(H._policy_os, 'read', side_effect=AssertionError('read after oversize')):
                with self.assertRaisesRegex(H.PolicyRefused, 'bounded single-link'):
                    read(leaf, pin(raw))

    def test_real_effective_uid_split_refuses_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            opened = []
            with mock.patch.object(H._policy_os, 'getuid', return_value=1000), \
                 mock.patch.object(H._policy_os, 'geteuid', return_value=1001), \
                 mock.patch.object(H._policy_os, 'open', side_effect=lambda *a, **k: opened.append(a)):
                with self.assertRaisesRegex(H.PolicyRefused, 'identity split'):
                    H.read_policy_bytes(leaf, leaf.parent, source_for(leaf), pin(), 1000, os.getgid())
            self.assertEqual(opened, [])

    def test_real_effective_gid_split_refuses_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            opened = []
            with mock.patch.object(H._policy_os, 'getgid', return_value=1000), \
                 mock.patch.object(H._policy_os, 'getegid', return_value=1001), \
                 mock.patch.object(H._policy_os, 'open', side_effect=lambda *a, **k: opened.append(a)):
                with self.assertRaisesRegex(H.PolicyRefused, 'identity split'):
                    H.read_policy_bytes(leaf, leaf.parent, source_for(leaf), pin(), os.getuid(), 1000)
            self.assertEqual(opened, [])

    def test_wrong_selected_gid_refuses_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            opened = []
            with mock.patch.object(H._policy_os, 'open', side_effect=lambda *a, **k: opened.append(a)):
                with self.assertRaisesRegex(H.PolicyRefused, 'selected effective UID/GID'):
                    H.read_policy_bytes(leaf, leaf.parent, source_for(leaf), pin(), os.geteuid(), os.getegid() + 1)
            self.assertEqual(opened, [])

    def test_growth_during_read_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            original = H._policy_read_bounded
            state = {'called': False}
            def grow(fd, identity):
                if not state['called']:
                    state['called'] = True
                    with leaf.open('ab') as output:
                        output.write(b'x')
                return original(fd, identity)
            with mock.patch.object(H, '_policy_read_bounded', side_effect=grow):
                with self.assertRaises(H.PolicyRefused):
                    read(leaf)

    def test_path_swap_between_reads_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            original = H._policy_read_bounded
            state = {'called': False}
            def swap(fd, identity):
                raw = original(fd, identity)
                if not state['called']:
                    state['called'] = True
                    leaf.rename(leaf.parent / 'old')
                    fixture(tmp)
                return raw
            with mock.patch.object(H, '_policy_read_bounded', side_effect=swap):
                with self.assertRaisesRegex(H.PolicyRefused, 'attachment changed'):
                    read(leaf)

    def test_uid_change_after_cleanup_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            uid = os.getuid()
            state = {'uid': uid, 'calls': 0}
            original = H._policy_close
            def closing(fds):
                out = original(fds)
                state['calls'] += 1
                if state['calls'] == 1:
                    state['uid'] = uid + 1
                return out
            with mock.patch.object(H._policy_os, 'getuid', return_value=uid), \
                 mock.patch.object(H._policy_os, 'geteuid', side_effect=lambda: state['uid']), \
                 mock.patch.object(H, '_policy_close', side_effect=closing):
                with self.assertRaisesRegex(H.PolicyRefused, 'changed during cleanup'):
                    read(leaf)
            self.assertEqual(state['calls'], 4)

    def test_gid_change_during_read_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            gid = os.getgid()
            state = {'gid': gid, 'calls': 0}
            original = H._policy_read_bounded
            def change_after_read(fd, identity):
                raw = original(fd, identity)
                state['calls'] += 1
                if state['calls'] == 2:
                    state['gid'] = gid + 1
                return raw
            with mock.patch.object(H._policy_os, 'getgid', return_value=gid), \
                 mock.patch.object(H._policy_os, 'getegid', side_effect=lambda: state['gid']), \
                 mock.patch.object(H, '_policy_read_bounded', side_effect=change_after_read):
                with self.assertRaisesRegex(H.PolicyRefused, 'changed during read'):
                    read(leaf)
            self.assertEqual(state['calls'], 2)

    def test_close_fault_attempts_every_descriptor_and_refuses_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            attempted = []
            actual_close = os.close
            def uncertain_close(fd):
                attempted.append(fd)
                actual_close(fd)
                if len(attempted) == 1:
                    raise OSError(5, 'synthetic uncertain close')
            with mock.patch.object(H._policy_os, 'close', side_effect=uncertain_close):
                with self.assertRaises(H.PolicyCleanupRefused) as caught:
                    read(leaf)
            self.assertEqual(len(attempted), 2 * (len(leaf.parts) + len(source_for(leaf).parts)))
            self.assertEqual(len(caught.exception.cleanup_errors), 1)

    def test_private_root_mode_and_location_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            root = leaf.parent
            root.chmod(0o755)
            with self.assertRaisesRegex(H.PolicyRefused, 'directory mode'):
                read(leaf)
            root.chmod(0o700)
            with self.assertRaisesRegex(H.PolicyRefused, 'external private policy'):
                H.read_policy_bytes(leaf, root, root, pin(), os.geteuid(), os.getegid())

    def test_policy_root_inside_source_root_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            with self.assertRaisesRegex(H.PolicyRefused, 'external private policy'):
                H.read_policy_bytes(leaf, leaf.parent, Path(tmp), pin(),
                                    os.geteuid(), os.getegid())

    def test_policy_root_contains_source_root_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            nested_source = leaf.parent / 'nested-source'
            nested_source.mkdir()
            with self.assertRaisesRegex(H.PolicyRefused, 'external private policy'):
                H.read_policy_bytes(leaf, leaf.parent, nested_source, pin(),
                                    os.geteuid(), os.getegid())

    def test_source_symlink_alias_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            alias = Path(tmp) / 'alias-source'
            alias.symlink_to(source_for(leaf), target_is_directory=True)
            with self.assertRaises(OSError):
                H.read_policy_bytes(leaf, leaf.parent, alias, pin(),
                                    os.geteuid(), os.getegid())

    def test_policy_root_symlink_alias_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            alias = Path(tmp) / 'alias-policy'
            alias.symlink_to(leaf.parent, target_is_directory=True)
            with self.assertRaises(OSError):
                H.read_policy_bytes(alias / 'permission.json', alias, source_for(leaf), pin(),
                                    os.geteuid(), os.getegid())

    def test_synthetic_inode_aliases_refuse_both_directions(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            original = H._policy_open_source
            info = os.stat(leaf.parent, follow_symlinks=False)
            alias_identity = (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)
            for position in (-1, -2):
                with self.subTest(position=position):
                    def alias_source(source_root):
                        fds, identities = original(source_root)
                        modified = list(identities)
                        modified[position] = alias_identity
                        return fds, tuple(modified)
                    with mock.patch.object(H, '_policy_open_source', side_effect=alias_source):
                        with self.assertRaisesRegex(H.PolicyRefused, 'roots alias or contain'):
                            read(leaf)

    def test_source_ancestor_rename_refuses_same_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            parent = Path(tmp) / 'selected-source-parent'
            selected_source = parent / 'root'
            selected_source.mkdir(parents=True)
            original = H._policy_read_bounded
            state = {'swapped': False}
            def rename_ancestor(fd, identity):
                raw = original(fd, identity)
                if not state['swapped']:
                    state['swapped'] = True
                    parent.rename(Path(tmp) / 'old-source-parent')
                    selected_source.mkdir(parents=True)
                return raw
            with mock.patch.object(H, '_policy_read_bounded', side_effect=rename_ancestor):
                with self.assertRaisesRegex(H.PolicyRefused, 'Source root attachment changed'):
                    H.read_policy_bytes(leaf, leaf.parent, selected_source, pin(),
                                        os.geteuid(), os.getegid())

    def test_policy_root_rename_refuses_same_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            leaf = fixture(tmp)
            selected_root = leaf.parent
            selected_source = source_for(leaf)
            original = H._policy_read_bounded
            state = {'swapped': False}
            def rename_root(fd, identity):
                raw = original(fd, identity)
                if not state['swapped']:
                    state['swapped'] = True
                    selected_root.rename(Path(tmp) / 'old-private-root')
                    selected_root.mkdir(mode=0o700)
                    replacement = selected_root / 'permission.json'
                    replacement.write_bytes(DUMMY)
                    replacement.chmod(0o600)
                return raw
            with mock.patch.object(H, '_policy_read_bounded', side_effect=rename_root):
                with self.assertRaisesRegex(H.PolicyRefused, 'attachment changed'):
                    H.read_policy_bytes(leaf, selected_root, selected_source, pin(),
                                        os.geteuid(), os.getegid())

class ProjectionTests(unittest.TestCase):
    def test_exact_projection_and_call_sites(self):
        code, proof = P.project_control(AUTH_PIN, POLICY_PIN)
        self.assertEqual(proof['projected_sha256'], P.sha(code))
        self.assertTrue(proof['byte_inverse'])
        self.assertEqual(proof['policy_read_sites'], 3)
        tree = ast.parse(code)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'HostChannel')
        methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        for name in ('policy_guard', 'authenticate', 'permission'):
            body = ast.get_source_segment(code.decode(), methods[name])
            self.assertIn('read_policy_bytes(', body)
            self.assertNotIn('self.path.read_bytes()', body)
        guard = ast.get_source_segment(code.decode(), methods['policy_guard'])
        self.assertLess(guard.index('host runtime identity split'), guard.index('FACT_SCOPE.package_guard'))
        self.assertEqual(code.count(b'def read_policy_bytes('), 1)
        self.assertIn(b"v['host_uid'] == os.geteuid()", code)

    def test_effect_and_grant_refusals(self):
        for name in ('construct_policy', 'final_context_source_manifest', 'launch_context'):
            with self.subTest(name=name), self.assertRaises(P.Refused):
                getattr(P, name)()

if __name__ == '__main__':
    unittest.main()
