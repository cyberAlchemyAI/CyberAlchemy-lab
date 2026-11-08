"""The first emitter hook must close its private grant around a live Session."""
import hashlib
import importlib.util
import json
import stat
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t03_first_emitter_hook_test', HERE/'first_emitter_hook.py')
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)


class LiveFirstEmitterHook(unittest.TestCase):
    def test_private_grant_and_three_formal_outputs_before_close(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            code = root/'emitter.py'
            code.write_text('''import hashlib,json\nfrom pathlib import Path\nclass NativeFirstEmitter:\n def __init__(self,**kwargs):\n  self.kwargs=kwargs\n def emit(self,host,opening):\n  grant=json.loads(Path(self.kwargs["control_path"]).read_bytes())\n  assert grant["session_ref"]==opening["session_ref"]\n  assert not host.closed\n  receipt={"outputs":[1,2,3],"actual_RAM_memory_accessed":False}\n  raw=json.dumps(receipt).encode()\n  marker=Path(grant["output_root"]).joinpath("emission.json")\n  marker.write_bytes(raw)\n  marker.chmod(0o600)\n  return {"posture":"produced-uncommitted","output_root":grant["output_root"],"receipt":receipt,"receipt_sha256":hashlib.sha256(raw).hexdigest()}\n''')
            evidence = root/'evidence'; evidence.mkdir(mode=0o700)
            now = datetime.now(timezone.utc)
            compact = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
            runtime = SimpleNamespace(
                evidence=evidence,
                api=root/'installed-api',
                api_binding={'sha256':'a'*64},
                profile_binding={'sha256':'b'*64},
                P=SimpleNamespace(compact=compact),
                A=SimpleNamespace(now=lambda:now))
            host = SimpleNamespace(closed=False, channel=SimpleNamespace(
                context={'principal_ref':'principal:test'}, expected_sha='c'*64))
            selected = SimpleNamespace(sources=SimpleNamespace(scope_ref='project:test'),
                                       source_cut={'commit_sha256':'d'*64})
            opened = {'session_ref':'session:test'}
            resource = SimpleNamespace(expires=now+timedelta(minutes=8))
            result = H.emit(runtime, host, selected, opened, resource, code,
                            hashlib.sha256(code.read_bytes()).hexdigest())
            grant_path = evidence/'native-first-emitter-grant.json'
            grant = json.loads(grant_path.read_bytes())
            self.assertEqual(stat.S_IMODE(grant_path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((evidence/'native-first-emission').stat().st_mode), 0o700)
            self.assertEqual(grant['session_ref'], opened['session_ref'])
            self.assertLessEqual(datetime.fromisoformat(grant['expires_at']), resource.expires)
            self.assertEqual(result['formal_output_count'], 3)
            self.assertEqual(result['posture'], 'produced-uncommitted')
            self.assertTrue((evidence/'FIRST-EMISSION.json').is_file())

    def test_changed_emitter_bytes_refused_before_grant(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname); code = root/'emitter.py'; code.write_text('x=1\n')
            runtime = SimpleNamespace(evidence=root, P=SimpleNamespace(), A=SimpleNamespace())
            with self.assertRaisesRegex(ValueError, 'adapter bytes differ'):
                H.emit(runtime, None, None, None, None, code, '0'*64)
            self.assertFalse((root/'native-first-emitter-grant.json').exists())


if __name__ == '__main__':
    unittest.main()
