"""Read-only/static tests for an unrun public namespace probe candidate."""
import datetime as dt
import errno
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
def selected(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

controller = selected('controller_path_tested',HERE/'controller_path.py')
child = selected('public_probe_child_tested',HERE/'public_probe_child.py')


class ControllerPathTests(unittest.TestCase):
    def test_durable_stage_not_attempt_local_public(self):
        value = controller.plan()
        paths = value['path_adaptation']
        self.assertNotEqual(paths['public_stage_root'],paths['attempt_root']+'/public')
        self.assertEqual(value['mounts'][0]['source'],paths['public_stage_root'])
        self.assertEqual(value['mounts'][0]['target'],'/workspace')
        self.assertEqual(paths['old_root_public_creation'],
                         'REMOVED_FROM_SUCCESSOR_DESIGN')
        self.assertEqual(paths['old_context_role_mkdir'],
                         'FORBIDDEN_STAGE_MUST_PREEXIST')
        self.assertEqual(paths['old_synthetic_source_manifest_write'],
                         'FORBIDDEN_CONTEXT_SOURCE_MUST_BE_REVIEWED')
        self.assertEqual(value['original_output_contract'],
                         '40_LEAVES_39_MANIFEST_RELEASE38_FINISH41')
        self.assertEqual(value['stage_1571'],'UNMATERIALIZED')

    def test_exact_inert_docker_create_argv(self):
        result = controller.probe_argv('a'*32)
        argv = result['create_argv']
        self.assertEqual(argv[:2],['/usr/bin/docker','create'])
        self.assertEqual(argv.count('--mount'),5)
        self.assertTrue(all('readonly' in argv[i+1] for i,arg in enumerate(argv)
                            if arg == '--mount'))
        self.assertFalse(any('dst=/workspace/' in arg for arg in argv))
        self.assertIn('--read-only',argv)
        self.assertEqual(argv[argv.index('--userns')+1],'host')
        self.assertEqual(argv[argv.index('--network')+1],'none')
        self.assertEqual(argv[argv.index('--entrypoint')+1],
                         '/usr/local/bin/python3.14')
        self.assertEqual(argv[-2],result['probe_child_sha256'])
        compile(argv[-3],'<public-probe-bootstrap>','exec',optimize=0)
        compile(argv[-3],'<public-probe-bootstrap>','exec',optimize=2)
        self.assertEqual(json.loads(argv[-1])['token'],'a'*32)
        self.assertFalse(result['docker_invoked'])

    def test_bad_token_and_predecessor_pin_refuse(self):
        with self.assertRaisesRegex(controller.Refused,'FRESH_PROBE_TOKEN_REQUIRED'):
            controller.probe_argv('fixture-token')
        pins = dict(controller.PINS)
        pins[controller.MOUNT_REVIEW] = '0'*64
        with mock.patch.object(controller,'PINS',pins),self.assertRaisesRegex(
                controller.Refused,'CONTROLLER_PREIMAGE_DRIFT'):
            controller.plan()

    def test_attempt_local_public_or_nested_rw_bind_refuse(self):
        predecessor = controller.mounted_predecessor()
        original = predecessor.vector()
        for mutation in ('old-public','nested-rw'):
            altered = dict(original)
            altered['mounts'] = [dict(r) for r in original['mounts']]
            if mutation == 'old-public':
                altered['mounts'][0]['source'] = str(predecessor.DOCKER_ATTEMPT/'public')
            else:
                altered['mounts'].append({'source':'/fixture/output',
                    'target':'/workspace/product','read_only':False})
            with self.subTest(mutation=mutation),mock.patch.object(
                    predecessor,'vector',return_value=altered),mock.patch.object(
                    controller,'mounted_predecessor',return_value=predecessor):
                with self.assertRaises(controller.Refused):
                    controller.plan()

    def test_probe_child_ro_mountinfo_causal(self):
        good = b'121 10 0:44 / /workspace ro,relatime - ext4 /dev/root rw\n'
        self.assertEqual(len(child.mountinfo_ro(good)),64)
        for raw in (good.replace(b'ro,relatime',b'rw,relatime'),
                    good+b'122 121 0:44 / /workspace/product rw - ext4 /dev/root rw\n'):
            with self.assertRaisesRegex(RuntimeError,'WORKSPACE_RO_NO_NESTED_MOUNT'):
                child.mountinfo_ro(raw)

    def test_probe_child_erofs_sentinel_causal(self):
        def error(code):
            def fail(*_args): raise OSError(code,'fixture')
            return fail
        self.assertEqual(child.require_erofs(error(errno.EROFS),lambda _p:False),30)
        with self.assertRaisesRegex(RuntimeError,'EROFS_SENTINEL'):
            child.require_erofs(error(errno.EACCES),lambda _p:False)
        with self.assertRaisesRegex(RuntimeError,'EROFS_SENTINEL'):
            child.require_erofs(error(errno.EROFS),lambda _p:True)
        closed = []
        with self.assertRaisesRegex(RuntimeError,'WRITABLE_CHILD_WORKSPACE'):
            child.require_erofs(lambda *_:42,lambda _p:True,closed.append)
        self.assertEqual(closed,[42])

    def test_source_expiry_refuses(self):
        with self.assertRaises(ValueError):
            controller.plan(dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc))

    def test_all_effect_entrypoints_refuse(self):
        for entry in (controller.launch_public_probe,
                      controller.launch_context_or_cleanup):
            with self.subTest(entry=entry.__name__),self.assertRaises(controller.Refused):
                entry()


if __name__ == '__main__':
    unittest.main()
