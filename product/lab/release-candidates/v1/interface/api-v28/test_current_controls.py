"""Independently current controls and explicit expired predecessor refusal."""
import unittest,tempfile
from pathlib import Path
from .protocol import *
from .auth import ReaderChannel,now,instant
from .fixtures import provision
from .custody_context_sessions import D,R
PROFILE=None
class CurrentControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.schemas=Schemas(PROFILE)
    def test_01_expired_legacy_source_refuses_new_session_grant(self):
        with tempfile.TemporaryDirectory(prefix='cal-R03-expired-source-refusal-') as tmp:
            root=Path(tmp);root.chmod(0o700)
            key,path,pin=provision(root,'fresh-participation',principal='principal:R03-fresh-reader')
            old=source.parse((HERE.parent/'session-participation-v2/packages/0001/period.json').read_bytes())
            self.assertGreaterEqual(now(),instant(old['expires_at']))
            with self.assertRaisesRegex(Exception,'retained absolute Assignment interval'):ReaderChannel(path,pin,self.schemas)
        self.assertFalse(root.exists())
    def test_02_new_source_keeps_original_expired_period_exact(self):
        new=D.load(D.reader.HERE/'packages/0001/period.json');old=new['original_expired_period_binding'];raw=source.original(old)
        self.assertEqual(source.sha(raw),old['sha256']);self.assertEqual(source.parse(raw)['expires_at'],'2026-10-10T02:45:14.443492+00:00')
        self.assertEqual(new['principal_ref'],'principal:R03-current-episode-0002')
        self.assertEqual(new['not_before'],'2026-10-10T05:39:44.044929+00:00');self.assertEqual(new['expires_at'],'2026-10-11T05:39:44.044929+00:00')
    def test_03_exact_current_profile_and_protocol_controls(self):
        self.assertEqual(self.schemas.profile['implemented_operations'],list(SUPPORTED));self.assertEqual(len(SUPPORTED),13)
        self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(LEGACY_SUPPORTED),12)
        self.assertEqual(Path(D.API.__file__).resolve(),HERE.parent/'api-v25/protocol.py')
    def test_04_actual_selected_reader_implementation(self):
        evidence=D.load(D.HERE/'implementation-binding.json')
        self.assertEqual(evidence['entrypoint_ref'],'product/lab/release-candidates/v1/interface/current-source-adapter-v2/reader.py#SelectedReader.open_signed')
        self.assertEqual(source.sha((ROOT/evidence['code_binding']['ref']).read_bytes()),evidence['code_binding']['sha256'])
        self.assertEqual(D.reader.open_signed.__func__.__name__,'open_signed')
        self.assertEqual(Path(D.reader.adapter.model.__file__).resolve(),HERE.parent/'current-source-adapter-v2/model.py')
        self.assertIs(D.EL,D.reader.adapter.eligibility)
        self.assertEqual(Path(D.reader.adapter.source.__file__).resolve(),HERE.parent/'current-source-adapter-v2/base.py')
        self.assertEqual(Path(D.reader.adapter.source.B.__file__).resolve(),D.reader.HERE/'base.py')
    def test_05_actual_guarded_byte_model_origin_and_body(self):
        from .guarded_reads import model_read_batch,selected_model
        with source.replay_source('custody-participation') as view:
            with model_read_batch(view):
                model=selected_model(view)
                self.assertEqual(Path(model.__file__).resolve(),HERE.parent/'current-source-adapter-v2/model.py')
                subject=next(s for s in view.subjects.values() if s['identity']==R.WORK)
                header=model.artifact_ref(view,subject);raw=model.record_bytes(view,subject)[0]
                self.assertEqual(source.sha(raw),header['byte_sha256'])
                self.assertEqual(header['version_ref'],R.WORK+'@'+R.VERSION)
            view.custody_signed_sources.guard()
    def test_06_actual_current_Service_selects_distinct_adapter_and_producer(self):
        from . import example_fixture as F
        from .service import Service
        from .auth import ReaderChannel
        from .fixtures import proof
        from .projection_refresh import control
        with source.replay_source('custody-participation') as view:
            materials,metadata,target=F.materials_for(view)
            with tempfile.TemporaryDirectory(prefix='cal-R03-current-service-control-') as tmp:
                root=Path(tmp);root.chmod(0o700)
                key,path,pin=F.provision(root,'custody-participation',materials,metadata,principal=R.PRINCIPAL,projection_control=control(view))
                channel=ReaderChannel(path,pin,self.schemas);authenticated=channel.authenticate(proof(key,channel.challenge))
                self.assertEqual(authenticated['context']['principal_ref'],R.PRINCIPAL)
                service=Service(view,channel,self.schemas)
                try:
                    self.assertIs(service.sessions.source,view.custody_signed_sources)
                    self.assertIs(service.sessions.source.sources.__class__,D.EL.ExactSources)
                    self.assertEqual(service.sessions.live,{})
                finally:service.close();key=None
            self.assertFalse(root.exists())
