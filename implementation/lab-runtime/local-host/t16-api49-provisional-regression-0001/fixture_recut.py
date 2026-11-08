"""Versioned, unselected T15/T16 fixture successors for API49 focused testing.

These adapters never change API49 files or redirect a historical source name.
The final API successor must bind their reviewed behavior to its own manifest.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v49-t31-current-guard-0002'
SOURCE_SHA = 'e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1'
PROFILE_SHA = 'dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5'
CURRENT_NAME = 'completion-legacy:legacy-local-ce4d53a6479188a5'
CURRENT_STORE = 'completion-legacy-local-ce4d53a6479188a5'
PROTECTED_SESSION_REF = 'agent-session:first-governed-agent-episode:2026-10-06@candidate.1'
EXPIRED_PERIOD = API.parent / 'session-participation-v2/packages/0001/period.json'
EXPIRED_PERIOD_SHA = '2c0a79e0a8f471114822cc8aed489edf514c7064942442d2670dfdccb2c0a082'
TEST_SOURCE_ROWS = {
    'test_challenge_api.py': '87a176bd0254bed68271749addfc27640d527cc88a6e475bf24f60c790718b17',
    'test_current_controls.py': '44e7821e512a41f2be921910e633c3ac42284f0334f70bcd847144eec28c9ca4',
    'test_preparation_corrected.py': 'd7eaa903b3f62b8b4ab229b83250d52c0078af81fbd40f77039b96ecd7add28c',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_module(module, filename):
    if filename not in TEST_SOURCE_ROWS:
        raise ValueError('unselected fixture source')
    expected = API / filename
    if Path(module.__file__).resolve() != expected or sha(expected.read_bytes()) != TEST_SOURCE_ROWS[filename]:
        raise ValueError('selected fixture origin or byte differs')
    if sha((API / 'source-manifest.json').read_bytes()) != SOURCE_SHA:
        raise ValueError('selected API49 source differs')
    if sha((API / 'contract-profile.json').read_bytes()) != PROFILE_SHA:
        raise ValueError('selected API49 profile differs')
    rows = json.loads((API / 'source-manifest.json').read_bytes())['files']
    expected_row = {'path': expected.relative_to(ROOT).as_posix(), 'sha256': TEST_SOURCE_ROWS[filename]}
    if rows.count(expected_row) != 1:
        raise ValueError('fixture is not uniquely selected by API49')


def current_challenge_setup(original, module):
    """Change only one class's setup source, retaining all inherited test methods."""
    selected_module(module, 'test_challenge_api.py')
    if original is not module.CurrentChallenge or module.P.source.CURRENT_LEGACY_NAME != CURRENT_NAME:
        raise ValueError('current challenge fixture owner or family differs')

    @classmethod
    def setUpClass(cls):
        module.verify(SOURCE_SHA)
        cls.schemas = module.P.Schemas(PROFILE_SHA)
        cls.manager = module.P.source.replay_source(CURRENT_NAME)
        cls.view = cls.manager.__enter__()
        if not module.P.source.current_legacy_view(cls.view):
            cls.manager.__exit__(None, None, None)
            raise ValueError('exact current signed view differs')
        if cls.view.legacy_signed_sources.source_cut['store_ref'] != CURRENT_STORE:
            cls.manager.__exit__(None, None, None)
            raise ValueError('exact current signed cut differs')
        cls.projection = module.P.compact(cls.view.data['projection'])
        cls.witnesses = []

    @classmethod
    def tearDownClass(cls):
        try:
            if module.P.compact(cls.view.data['projection']) != cls.projection:
                raise ValueError('current source projection changed during fixture')
        finally:
            cls.manager.__exit__(None, None, None)
            module.verify(SOURCE_SHA)

    successor = type(original.__name__, (original,),
                     {'setUpClass': setUpClass, 'tearDownClass': tearDownClass})
    successor.__module__ = module.__name__
    successor.__qualname__ = original.__qualname__
    return successor


def expired_original_control(original, module):
    """Keep the inherited test ID while proving the two ordered old refusals."""
    selected_module(module, 'test_current_controls.py')
    if original is not module.CurrentControls:
        raise ValueError('expired-source fixture owner differs')

    def test_01_expired_legacy_source_refuses_new_session_grant(self):
        raw = EXPIRED_PERIOD.read_bytes()
        self.assertEqual(sha(raw), EXPIRED_PERIOD_SHA)
        old = module.source.parse(raw)
        self.assertGreaterEqual(datetime.now(timezone.utc),
                                datetime.fromisoformat(old['expires_at'].replace('Z', '+00:00')))
        with tempfile.TemporaryDirectory(prefix='cal-T16-expired-original-') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            key, path, pin = module.provision(root, 'fresh-participation',
                                              principal='principal:R03-fresh-reader')
            with self.assertRaisesRegex(ValueError, '^selected R02 participation environment differs$'):
                module.ReaderChannel(path, pin, self.schemas)
            selected = object.__new__(module.ReaderChannel)
            selected.path, selected.expected_sha, selected.schemas = path, pin, self.schemas
            with self.assertRaisesRegex(ValueError,
                    '^historical fresh source host window exceeds retained absolute Assignment interval$'):
                selected.policy_guard(check_source=False)
            key = None
        self.assertFalse(root.exists())

    successor = type(original.__name__, (original,),
                     {'test_01_expired_legacy_source_refuses_new_session_grant':
                      test_01_expired_legacy_source_refuses_new_session_grant})
    successor.__module__ = module.__name__
    successor.__qualname__ = original.__qualname__
    return successor


def current_protected_session_subject(view, source):
    """Select a current signed protected Session without opening historical cut authority."""
    if not source.current_legacy_view(view) or view.legacy_signed_sources.source_cut['store_ref'] != CURRENT_STORE:
        raise ValueError('current signed Session view differs')
    rows = [item for item in view.subjects.values()
            if item['kind'] == 'agent-session' and item['version_ref'] == PROTECTED_SESSION_REF
            and item['record'].get('payload', {}).get('session_memory')]
    if len(rows) != 1:
        raise ValueError('exact current protected Session witness unavailable')
    return rows[0]


def current_protected_preparation(original, module, controls):
    """Preserve the two protected-Session assertions on a fresh current cut."""
    selected_module(module, 'test_preparation_corrected.py')
    selected_module(controls, 'test_current_controls.py')
    if original is not module.CorrectedPreparation:
        raise ValueError('protected-Session fixture owner differs')
    protocol = __import__(module.__package__ + '.protocol', fromlist=['compact'])
    model = __import__(module.__package__ + '.artifact_model', fromlist=['artifact_ref'])
    fixtures = __import__(module.__package__ + '.fixtures', fromlist=['call'])
    handlers = __import__(module.__package__ + '.handlers', fromlist=['cut'])

    def test_historical_source_session_memory_never_returns_as_body(self):
        with controls.scoped_service(self.schemas) as (view, channel, service, _):
            subject = current_protected_session_subject(view, protocol.source)
            call = fixtures.call(channel.context, 'artifact.inspect', handlers.cut(view),
                                 artifact=model.artifact_ref(view, subject), include=['body'])
            reply = service.call(protocol.compact(call))
            self.assertEqual(reply['message']['code'], 'unauthorized', reply)
            self.assertNotIn('envelope', reply['message'])

    def test_protected_source_session_exact_metadata_remains_inspectable(self):
        with controls.scoped_service(self.schemas) as (view, channel, service, _):
            subject = current_protected_session_subject(view, protocol.source)
            call = fixtures.call(channel.context, 'artifact.inspect', handlers.cut(view),
                                 artifact=model.artifact_ref(view, subject),
                                 include=['contract', 'lifecycle', 'gaps'])
            reply = service.call(protocol.compact(call))
            self.assertEqual(reply['kind'], 'result', reply)
            self.assertIsNone(reply['message']['envelope'])

    successor = type(original.__name__, (original,), {
        'test_historical_source_session_memory_never_returns_as_body':
            test_historical_source_session_memory_never_returns_as_body,
        'test_protected_source_session_exact_metadata_remains_inspectable':
            test_protected_source_session_exact_metadata_remains_inspectable})
    successor.__module__ = module.__name__
    successor.__qualname__ = original.__qualname__
    return successor
