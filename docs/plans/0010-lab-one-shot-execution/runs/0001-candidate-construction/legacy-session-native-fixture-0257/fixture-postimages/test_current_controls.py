from .legacy_fixture_selection import *
"""Independently current controls and explicit expired predecessor refusal."""
import unittest,tempfile
from pathlib import Path
from .protocol import *
from .auth import ReaderChannel,now,instant
from .fixtures import provision
from .legacy_context_sessions import D,R
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
        self.assertEqual(source.sha(raw),old['sha256']);self.assertEqual(source.parse(raw)['expires_at'],EXPECTED_PREVIOUS_EXPIRES_AT)
        self.assertEqual(new['principal_ref'],EXPECTED_PRINCIPAL)
        self.assertEqual(new['not_before'],EXPECTED_NOT_BEFORE);self.assertEqual(new['expires_at'],EXPECTED_EXPIRES_AT)
        self.assertEqual(old,EXPECTED_ORIGINAL5_PERIOD)
        self.assertTrue(verify_retained_original_period_chain(source))
    def test_03_exact_current_profile_and_protocol_controls(self):
        self.assertEqual(self.schemas.profile['implemented_operations'],list(SUPPORTED));self.assertEqual(len(SUPPORTED),34)
        self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(LEGACY_SUPPORTED),12)
        self.assertEqual(Path(D.API.__file__).resolve(),HERE.parent/'api-v25/protocol.py')
    def test_04_actual_selected_reader_implementation(self):
        evidence=D.load(D.HERE/'implementation-binding.json')
        self.assertEqual(evidence['entrypoint_ref'],EXPECTED_ENTRYPOINT)
        self.assertEqual(source.sha((ROOT/evidence['code_binding']['ref']).read_bytes()),evidence['code_binding']['sha256'])
        self.assertEqual(D.reader.open_signed.__func__.__name__,'open_signed')
        self.assertEqual(Path(D.reader.adapter.model.__file__).resolve(),HERE.parent/EXPECTED_READER_ROOT/'model.py')
        self.assertIs(D.EL,D.reader.adapter.eligibility)
        self.assertEqual(Path(D.reader.adapter.source.__file__).resolve(),HERE.parent/EXPECTED_READER_ROOT/'base.py')
        self.assertEqual(Path(D.reader.adapter.source.B.__file__).resolve(),D.reader.HERE/'base.py')
        self.assertEqual(evidence["code_binding"]["sha256"],EXPECTED_READER_SHA)
    def test_05_actual_guarded_byte_model_origin_and_body(self):
        from .guarded_reads import model_read_batch,selected_model
        with source.replay_source(PUBLIC_SOURCE_NAME) as view:
            with model_read_batch(view):
                model=selected_model(view)
                self.assertEqual(Path(model.__file__).resolve(),HERE.parent/EXPECTED_READER_ROOT/'model.py')
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
        with source.replay_source(PUBLIC_SOURCE_NAME) as view:
            materials,metadata,target=F.materials_for(view)
            with tempfile.TemporaryDirectory(prefix='cal-R03-current-service-control-') as tmp:
                root=Path(tmp);root.chmod(0o700)
                key,path,pin=F.provision(root,PUBLIC_SOURCE_NAME,materials,metadata,principal=R.PRINCIPAL,projection_control=control(view))
                channel=ReaderChannel(path,pin,self.schemas);authenticated=channel.authenticate(proof(key,channel.challenge))
                self.assertEqual(authenticated['context']['principal_ref'],R.PRINCIPAL)
                service=Service(view,channel,self.schemas)
                try:
                    self.assertIs(service.sessions.source,view.custody_signed_sources)
                    self.assertIs(service.sessions.source.sources.__class__,D.EL.ExactSources)
                    self.assertEqual(service.sessions.live,{})
                finally:service.close();key=None
            self.assertFalse(root.exists())
    def test_07_exact_new_episode_Work_Product_and_ten_relations(self):
        mapping=D.load(D.MAPPED.HERE/'packages/0001/mapping.json');headers=[r['artifact'] for r in mapping['rows']]
        work=[h for h in headers if h['identity_ref']==R.WORK];self.assertEqual(len(work),1);self.assertEqual(work[0]['version_ref'],R.WORK+'@'+R.VERSION)
        product=[h for h in headers if h['identity_ref']=='product:cyberalchemy-lab'];self.assertEqual(len(product),1);self.assertEqual(product[0]['version_ref'],'product:cyberalchemy-lab@current-episode-0004.candidate.1')
        edges=[h for h in headers if h['version_ref'] in EXPECTED_RELATION_VERSIONS];self.assertEqual(len(edges),10)
        self.assertEqual(len({h['version_ref'] for h in edges}),10)
    def test_08_actual_policy_revocation_inside_fact_scope(self):
        with scoped_service(self.schemas) as (view,channel,service,path):
            original=path.read_bytes();bridge=service.sessions.bridge
            with D.FACT_SCOPE.read_scope(view.custody_signed_sources,D.EL,bridge,producer=D,
                                        package_checks=[(D.verify_source,bridge.delivery_pin)]):
                try:
                    path.write_bytes(original+b' ')
                    with self.assertRaisesRegex(ValueError,'revoked or changed'):channel.guard()
                finally:path.write_bytes(original)

    def test_09_actual_nested_dispatch_refused_without_effect(self):
        with scoped_service(self.schemas) as (view,channel,service,path):
            from . import example_fixture as F
            before={p.relative_to(service.vault.root).as_posix():source.sha(p.read_bytes())
                    for p in service.vault.root.rglob('*') if p.is_file()}
            bridge=service.sessions.bridge
            with D.FACT_SCOPE.read_scope(view.custody_signed_sources,D.EL,bridge,producer=D,
                                        package_checks=[(D.verify_source,bridge.delivery_pin)]):
                request=F.call(channel.context,'lab.status',__import__(__package__+'.handlers',fromlist=['cut']).cut(view))
                result=service.call(compact(request))
                self.assertEqual(result['schema_version'],'lab-api-transport-error/v1-candidate')
                self.assertEqual(result['code'],'unauthenticated-channel')
            after={p.relative_to(service.vault.root).as_posix():source.sha(p.read_bytes())
                   for p in service.vault.root.rglob('*') if p.is_file()}
            self.assertEqual(before,after);self.assertEqual(service.sessions.live,{})

    def test_10_actual_borrowed_selection_keeps_live_permission(self):
        with scoped_service(self.schemas) as (view,channel,service,path):
            bridge=service.sessions.bridge;before=bridge.permission()
            with D.FACT_SCOPE.read_scope(view.custody_signed_sources,D.EL,bridge,producer=D,
                                        package_checks=[(D.verify_source,bridge.delivery_pin)]):
                self.assertIs(D.FACT_SCOPE.policy_scope(channel).producer,D)
                self.assertEqual(bridge.permission(),before)
                self.assertEqual(bridge.permission().max_session_seconds,900)
                self.assertEqual(channel.guard()['role_assignment_bindings'],[])
            self.assertIsNone(D.FACT_SCOPE.policy_scope(channel))

    def test_11_actual_source_corruption_refused_before_release(self):
        with scoped_service(self.schemas) as (view,channel,service,path):
            bridge=service.sessions.bridge;original=view.data['config']['scope_ref']
            try:
                with self.assertRaises(ValueError):
                    with D.FACT_SCOPE.read_scope(view.custody_signed_sources,D.EL,bridge,producer=D,
                                                package_checks=[(D.verify_source,bridge.delivery_pin)]) as facts:
                        view.data['config']['scope_ref']='project:owned-scope-corruption'
                        row=next(iter(facts.records.values()));facts.get(row.artifact)
            finally:view.data['config']['scope_ref']=original
            view.custody_signed_sources.guard()


from contextlib import contextmanager
@contextmanager
def scoped_service(schemas):
    from . import example_fixture as F
    from .service import Service
    from .auth import ReaderChannel
    from .projection_refresh import control
    with source.replay_source(PUBLIC_SOURCE_NAME) as view:
        materials,metadata,target=F.materials_for(view)
        with tempfile.TemporaryDirectory(prefix='cal-R03-scoped-service-control-') as tmp:
            root=Path(tmp);root.chmod(0o700)
            key,path,pin=F.provision(root,PUBLIC_SOURCE_NAME,materials,metadata,
                                   principal=R.PRINCIPAL,projection_control=control(view))
            channel=ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge))
            service=Service(view,channel,schemas)
            try:yield view,channel,service,path
            finally:service.close();key=None
        source.require(not root.exists(),'owned control private root remains')
