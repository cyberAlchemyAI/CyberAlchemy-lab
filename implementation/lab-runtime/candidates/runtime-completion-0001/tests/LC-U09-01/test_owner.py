"""Isolated signed fixtures; no authentic owner credential, message or effect."""
import argparse,copy,json,os,sys,tempfile,unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
S=Path(__file__).absolute().parents[2];R=S.parents[3]
DEPS=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
sys.path[:0]=[str(S/'contracts'),str(S/'selectors'),str(S/'owner_ingress'),str(DEPS)]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from lab_contracts.codec import canonical,sha,Refusal
from lab_selectors.anchors import RootAnchor,AnchoredReader,identity
from lab_owner.contracts import VERSION,signing,OUTCOMES
from lab_owner.verifier import verify_fixture,verify_actual,Capture
from lab_owner.replay import reserve_fixture

TEMP=None
NOW=1800000000

def sample(s):
    if 'const' in s:return s['const']
    if 'enum' in s:return s['enum'][0]
    if 'anyOf' in s:return sample(s['anyOf'][-1])
    t=s.get('type')
    if t=='object':return {k:sample(s['properties'][k]) for k in s['required']}
    if t=='array':return [sample(s['items']) for _ in range(s.get('minItems',0))]
    if t=='null':return None
    if t=='string':return 'fixture-value'
    raise ValueError('unsupported fixture sample')

class Fixture:
    def __init__(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='owned-owner-',dir=TEMP);self.path=Path(self.tmp.name)
        self.replay=self.path/'replay';self.replay.mkdir(mode=0o700)
        self.bindings=[];self.n=0;self.now=NOW
        self.keys={name:Ed25519PrivateKey.from_private_bytes(bytes([i])*32) for i,name in enumerate(['review','host','role','effect'],1)}
        self.issuers={name:{'issuer_ref':'fixture-'+name,'public_key':key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()} for name,key in self.keys.items()}
        self.schemas={};self.schema_bindings={}
        for key,name in [('assignment','role-assignment'),('role','role'),('boundary','authority-boundary')]:
            p=R/f'authority/artifact-types/{name}/v1/schema.json';self.schemas[key]=json.loads(p.read_bytes());self.schema_bindings[key]=self.bound(p,'repo',R)
        self.trust={'schema_version':'lab-owner-enrollment/v2','usage':'technical-fixture','issuers':self.issuers,
          'host_mechanism':'fixture-host-v2','role_registry':'fixture-role-registry','registry_cursor':'cursor-current','max_age_seconds':120,
          'native_schemas':self.schema_bindings,'replay_root':{'root_id':'replay','path':str(self.replay),'identity':identity(self.replay.stat())}}
        basis=self.put(b'fixture independent role source, no actual authority')
        a=sample(self.schemas['assignment']);a.update(node_id='assignment:owner',assignee_ref='person:owner',assignee_kind='person-reference',role_ref='role:owner',scope_ref='scope:repo',assignment_state='active',period={'start':'2020-01-01T00:00:00Z','end':None})
        r=sample(self.schemas['role']);r.update(node_id='role:owner',scope_ref='scope:repo',authority_boundary='boundary:repo',lifecycle_state='active')
        b=sample(self.schemas['boundary']);b.update(node_id='boundary:repo',scope_ref='scope:repo',lifecycle_state='active')
        b['payload'].update(accountable_principal_ref='human:owner',owner_role_ref='role:owner',authority_scope_ref='scope:repo',allowed_effect_kinds=['publish'],excluded_effect_kinds=['deploy'],revocation_state='not-revoked',effective_period='authoritatively-resolved-fixture-period')
        self.assignment=a;self.original_role=r;self.boundary=b
        self.correspondence={'schema_version':'lab-principal-assignee-resolution/v2','registry_ref':'fixture-role-registry','registry_cursor':'cursor-current','principal_ref':'human:owner','assignee_ref':'person:owner','assignee_kind':'person-reference','basis_bindings':[basis],'period':{'start':NOW-100,'end':NOW+100}}
        self.revocation={'schema_version':'lab-owner-current-revocation/v2','registry_ref':'fixture-role-registry','registry_cursor':'cursor-current','assignment_ref':'assignment:owner','role_ref':'role:owner','boundary_ref':'boundary:repo','state':'not-revoked','checked_at':NOW-10,'valid_until':NOW+90,'basis_bindings':[basis]}
        material=self.put(b'exact fixture display');target=self.put(b'exact fixture target');source=self.put(b'fixture source');profile=self.put(b'fixture profile');env=self.put(b'fixture environment');base=self.put(b'fixture base')
        owner={'owner_id':'owner:one','principal_ref':'human:owner','assignee_ref':'person:owner','role_ref':'role:owner','boundary_ref':'boundary:repo','scope_ref':'scope:repo','target_refs':['target:one']}
        self.core={'schema_version':'lab-owner-review-core/v2','review_id':'review:one','source_binding':source,'profile_binding':profile,'environment_binding':env,'base_binding':base,'targets':[{'target_ref':'target:one','member_binding':target,'effect_kinds':['publish']}],'owner_matrix':[owner],'material_bindings':[material],'evidence_bindings':[],'artifact_meaning':'Fixture member only','limitations':['No actual human approval or effect'],'required_permission_kinds':[]}
        self.operation='operation:one';self.outcome='approve';self.with_effect=True;self.role_changes={};self.presentation_changes={};self.disposition_changes={};self.effect_changes={};self.operator=[]
        self.refresh()
    def close(self):self.tmp.cleanup()
    def bound(self,p,root='fixture',base=None):
        raw=p.read_bytes();b={'kind':'execution','root_id':root,'relative_path':str(p.relative_to(base or self.path)),'sha256':sha(raw),'size_bytes':len(raw)};self.bindings.append(b);return b
    def put(self,v):
        self.n+=1;p=self.path/f'{self.n:05}.json';p.write_bytes(v if type(v) is bytes else canonical(v));return self.bound(p)
    def sign(self,p,duty):
        e={'schema_version':VERSION,'issuer_ref':self.issuers[duty]['issuer_ref'],'algorithm':'Ed25519-lowerhex-canonical-v2','payload':p,'signature':'0'*128}
        e['signature']=self.keys[duty].sign(signing(e)).hex();return self.put(e)
    def refresh(self):
        self.review=self.sign(self.core,'review')
        role={'schema_version':'lab-owner-role-attestation/v2','registry_ref':'fixture-role-registry','registry_cursor':'cursor-current','principal_ref':'human:owner','assignee_ref':'person:owner','role_ref':'role:owner','boundary_ref':'boundary:repo','scope_ref':'scope:repo','assignment_binding':self.put(self.assignment),'role_binding':self.put(self.original_role),'boundary_binding':self.put(self.boundary),'correspondence_binding':self.put(self.correspondence),'revocation_binding':self.put(self.revocation),'period':{'start':NOW-90,'end':NOW+90},'boundary_period_text':self.boundary['payload']['effective_period'],'effective_period_resolution':{'kind':'authoritative-period-resolution','period':{'start':NOW-100,'end':NOW+100},'review_core_sha256':None},'effect_kinds':['publish']}
        role.update(self.role_changes);self.role=self.sign(role,'role')
        p={'schema_version':'lab-owner-presentation/v2','mechanism_ref':'fixture-host-v2','principal_ref':'human:owner','session_id':'session:one','event_id':'presentation:one','nonce':'nonce:one','review_binding':self.review,'material_bindings':self.core['material_bindings'],'presented_at':NOW-20};p.update(self.presentation_changes);self.presentation=self.sign(p,'host')
        d={'schema_version':'lab-owner-disposition/v2','mechanism_ref':'fixture-host-v2','principal_ref':'human:owner','session_id':'session:one','event_id':'message:one','presentation_binding':self.presentation,'role_attestation_binding':self.role,'review_binding':self.review,'material_bindings':self.core['material_bindings'],'target_refs':['target:one'],'scope_ref':'scope:repo','outcome':self.outcome,'message_binding':self.put(b'fixture message bytes'),'recorded_at':NOW-10,'operation_id':self.operation};d.update(self.disposition_changes);self.disposition=self.sign(d,'host')
        effect={'schema_version':'lab-owner-effect-authorization/v2','operation_id':self.operation,'review_binding':self.review,'target_bindings':self.core['targets'],'positive_disposition_bindings':[self.disposition],'operator_permission_bindings':self.operator,'period':{'start':NOW-50,'end':NOW+50}};effect.update(self.effect_changes)
        self.selection={'schema_version':'lab-owner-selection/v2','disposition_profile':'t26-original-v1','operation_id':self.operation,'review_binding':self.review,'review_core':copy.deepcopy(self.core),'owner_inputs':[{'owner_id':'owner:one','principal_ref':'human:owner','presentation_binding':self.presentation,'role_attestation_binding':self.role,'disposition_binding':self.disposition}],'effect_authorization_binding':self.sign(effect,'effect') if self.with_effect else None,'operator_permission_bindings':self.operator}
        self.enrollment=self.put(self.trust);self.selected=self.put(self.selection)
    def reader(self):
        prior=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02/dispatch-proposal-0002.json'
        if sha(prior.read_bytes())!='478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864':raise RuntimeError('independent root changed')
        pin=next(r for r in json.loads(prior.read_bytes())['roots'] if r['root_id']=='repository')
        return AnchoredReader([RootAnchor('repo',pin['path'],pin['identity']),RootAnchor('fixture',str(self.path),identity(self.path.stat()))],list({canonical(b):b for b in self.bindings}.values()))
    def verify(self):return verify_fixture(self.reader(),self.enrollment,self.selected,now=self.now)
    def reserve(self):return reserve_fixture(self.reader(),self.enrollment,self.selected,now=self.now)

class Tests(unittest.TestCase):
    def setUp(self):self.f=Fixture()
    def tearDown(self):self.f.close()
    def test_positive_fixture_never_authorizes_actual_effect(self):
        r=self.f.verify();self.assertTrue(r['positive_effect_contract_verified']);self.assertFalse(r['actual_effect_authorized']);self.assertEqual(r['authority_effect'],'none')
    def test_actual_provider_absent_refuses_without_read(self):
        with self.assertRaisesRegex(Refusal,'ACTUAL_G07'):verify_actual(None,None,None)
        self.f.trust['usage']='actual-owner';self.f.refresh()
        with self.assertRaisesRegex(Refusal,'ACTUAL_G07'):self.f.verify()
    def test_nonpositive_vocabulary_is_preserved(self):
        f=self.f;f.with_effect=False
        for outcome in OUTCOMES-{'approve'}:
            f.outcome=outcome;f.refresh();r=f.verify();self.assertEqual(r['owner_results'][0]['outcome'],outcome);self.assertFalse(r['positive_effect_contract_verified'])
    def test_nonpositive_cannot_authorize_even_with_valid_effect_signature(self):
        for outcome in OUTCOMES-{'approve'}:
            self.f.outcome=outcome;self.f.refresh()
            with self.assertRaisesRegex(Refusal,'POSITIVE_DISPOSITIONS'):self.f.verify()
    def test_revise_and_stop_are_not_normalized_across_original_profiles(self):
        f=self.f;f.with_effect=False;f.outcome='revise';f.refresh();r=f.verify()['owner_results'][0]
        self.assertEqual(r['outcome'],'revise');self.assertFalse(r['profile_supported']);self.assertEqual(r['profile_status'],'unsupported-nonpositive-gated')
        f.outcome='stop';f.refresh();self.assertTrue(f.verify()['owner_results'][0]['profile_supported'])
        f.selection['disposition_profile']='c07-v1';f.selected=f.put(f.selection);r=f.verify()['owner_results'][0]
        self.assertEqual(r['outcome'],'stop');self.assertFalse(r['profile_supported'])

    def test_alias_key_and_issuer_identity_cannot_merge_host_role_duties(self):
        f=self.f;original=copy.deepcopy(f.trust['issuers']['role'])
        f.trust['issuers']['role']['public_key']=f.trust['issuers']['host']['public_key'];f.refresh()
        with self.assertRaisesRegex(Refusal,'ISSUER_DUTY'):f.verify()
        f.trust['issuers']['role']=original;f.trust['issuers']['role']['issuer_ref']=f.trust['issuers']['host']['issuer_ref'];f.refresh()
        with self.assertRaisesRegex(Refusal,'ISSUER_DUTY'):f.verify()

    def test_missing_effect_authorization_stays_observation(self):
        self.f.with_effect=False;self.f.refresh();self.assertFalse(self.f.verify()['positive_effect_contract_verified'])
    def test_forged_signature_and_payload_supplied_key_refuse(self):
        f=self.f;e=json.loads((f.path/f.disposition['relative_path']).read_bytes());e['signature']='0'*128
        b=f.put(e);f.selection['owner_inputs'][0]['disposition_binding']=b;f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'SIGNATURE_INVALID'):f.verify()
        e['public_key']=f.issuers['host']['public_key'];f.selection['owner_inputs'][0]['disposition_binding']=f.put(e);f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'CLOSED_FIELDS'):f.verify()
    def test_host_and_role_duties_must_be_separate(self):
        self.f.trust['issuers']['role']=self.f.trust['issuers']['host'];self.f.refresh()
        with self.assertRaisesRegex(Refusal,'ISSUER_DUTY'):self.f.verify()
    def test_signature_algorithm_is_not_autodetected(self):
        f=self.f;e=json.loads((f.path/f.presentation['relative_path']).read_bytes());e['algorithm']='base64-challenge';b=f.put(e)
        f.selection['owner_inputs'][0]['presentation_binding']=b;f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'ALGORITHM'):f.verify()
    def test_wrong_principal_and_session_refuse(self):
        f=self.f;f.disposition_changes={'principal_ref':'human:wrong'};f.refresh()
        with self.assertRaisesRegex(Refusal,'DISPOSITION_IDENTITY'):f.verify()
        f.disposition_changes={'session_id':'session:wrong'};f.refresh()
        with self.assertRaisesRegex(Refusal,'DISPOSITION_IDENTITY'):f.verify()
    def test_display_target_and_source_are_exact(self):
        f=self.f;f.presentation_changes={'material_bindings':[f.put(b'changed display')]};f.refresh()
        with self.assertRaisesRegex(Refusal,'PRESENTED_BYTES'):f.verify()
        f.presentation_changes={};f.refresh();f.selection['review_core']['source_binding']=f.put(b'changed source');f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'CURRENT_REVIEW'):f.verify()
        f.disposition_changes={'target_refs':['future:target']};f.refresh()
        with self.assertRaisesRegex(Refusal,'DISPOSITION_SCOPE'):f.verify()
    def test_current_bytes_cannot_drift_after_presentation(self):
        f=self.f;b=f.core['targets'][0]['member_binding'];(f.path/b['relative_path']).write_bytes(b'changed bytes')
        with self.assertRaises(Refusal):f.verify()
    def test_original_assignee_role_boundary_joins(self):
        f=self.f
        for obj,key in [(f.assignment,'assignee_ref'),(f.assignment,'role_ref'),(f.original_role,'authority_boundary')]:
            old=obj[key];obj[key]='wrong';f.refresh()
            with self.assertRaises(Refusal):f.verify()
            obj[key]=old
    def test_revoked_suspended_and_retired_refuse(self):
        f=self.f
        for obj,key,val in [(f.assignment,'assignment_state','suspended'),(f.original_role,'lifecycle_state','retired'),(f.boundary['payload'],'revocation_state','revoked'),(f.revocation,'state','revoked')]:
            old=obj[key];obj[key]=val;f.refresh()
            with self.assertRaises(Refusal):f.verify()
            obj[key]=old
    def test_correspondence_and_scope_cannot_be_inferred_from_key(self):
        f=self.f;f.correspondence['principal_ref']='other';f.refresh()
        with self.assertRaisesRegex(Refusal,'PRINCIPAL_ASSIGNEE'):f.verify()
        f.correspondence['principal_ref']='human:owner';f.boundary['scope_ref']='other';f.refresh()
        with self.assertRaisesRegex(Refusal,'ORIGINAL_SCOPE'):f.verify()
    def test_excluded_effect_and_missing_effect_scope_refuse(self):
        f=self.f;f.boundary['payload']['excluded_effect_kinds']=['publish'];f.refresh()
        with self.assertRaisesRegex(Refusal,'EFFECT_BOUNDARY'):f.verify()
        f.boundary['payload']['excluded_effect_kinds']=[];f.role_changes={'effect_kinds':['deploy']};f.refresh()
        with self.assertRaisesRegex(Refusal,'EFFECT_BOUNDARY'):f.verify()
    def test_period_and_fresh_revocation_are_current(self):
        f=self.f;f.now=NOW+200
        with self.assertRaises(Refusal):f.verify()
        f.now=NOW;f.revocation['valid_until']=NOW;f.refresh()
        with self.assertRaisesRegex(Refusal,'REVOCATION_STALE'):f.verify()
    def test_presentation_and_message_order_and_freshness(self):
        f=self.f;f.presentation_changes={'presented_at':NOW+1};f.refresh()
        with self.assertRaisesRegex(Refusal,'PRESENTATION_STALE'):f.verify()
        f.presentation_changes={'presented_at':NOW-200};f.refresh()
        with self.assertRaisesRegex(Refusal,'PRESENTATION_STALE'):f.verify()
    def test_required_operator_permission_cannot_be_omitted(self):
        self.f.core['required_permission_kinds']=['release'];self.f.refresh()
        with self.assertRaisesRegex(Refusal,'REQUIRED_OPERATOR_PERMISSION'):self.f.verify()
    def test_wrong_operation_effect_authorization_refuses(self):
        self.f.effect_changes={'operation_id':'other'};self.f.refresh()
        with self.assertRaisesRegex(Refusal,'EFFECT_EXACT_TARGET'):self.f.verify()
    def test_exact_review_native_period_is_acyclic(self):
        f=self.f;digest=sha(canonical(f.core));f.boundary['payload']['effective_period']='exact-review:'+digest
        f.role_changes={'effective_period_resolution':{'kind':'exact-review','period':{'start':NOW-100,'end':NOW+100},'review_core_sha256':digest}};f.refresh();self.assertTrue(f.verify()['positive_effect_contract_verified'])
        f.role_changes['effective_period_resolution']['review_core_sha256']='0'*64;f.refresh()
        with self.assertRaisesRegex(Refusal,'EXACT_REVIEW_PERIOD'):f.verify()
    def test_replay_reserves_event_and_survives_lost_reply(self):
        f=self.f;r=f.reserve();self.assertEqual(len(r['reservation_files']),3)
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()
        self.assertEqual(len(list(f.replay.iterdir())),3)
    def test_replay_event_identity_does_not_include_operation_or_target(self):
        f=self.f;f.reserve();f.operation='operation:other';f.refresh()
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()
    def test_replay_new_message_cannot_reuse_presentation_nonce(self):
        f=self.f;f.reserve();f.disposition_changes={'event_id':'message:two'};f.presentation_changes={'event_id':'presentation:two'};f.refresh()
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()
        self.assertEqual(len(list(f.replay.iterdir())),5)
    def test_host_event_cannot_cross_presentation_message_namespaces(self):
        f=self.f;f.reserve();f.disposition_changes={'event_id':'presentation:one'}
        f.presentation_changes={'event_id':'presentation:new','nonce':'nonce:new'};f.refresh()
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()

    def test_presentation_and_message_event_ids_must_be_distinct(self):
        self.f.disposition_changes={'event_id':'presentation:one'};self.f.refresh()
        with self.assertRaisesRegex(Refusal,'DUPLICATE_HOST_EVENT'):self.f.verify()

    def test_unverified_ingress_cannot_consume_host_event(self):
        f=self.f;e=json.loads((f.path/f.disposition['relative_path']).read_bytes());e['signature']='0'*128
        f.selection['owner_inputs'][0]['disposition_binding']=f.put(e);f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'SIGNATURE_INVALID'):f.reserve()
        self.assertEqual(list(f.replay.iterdir()),[])

    def test_signed_negative_event_cannot_be_reused_as_approval(self):
        f=self.f;f.outcome='stop';f.with_effect=False;f.refresh();f.reserve()
        f.outcome='approve';f.with_effect=True;f.refresh()
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()

    def test_retained_reservation_refuses_in_distinct_reaped_process(self):
        f=self.f;f.reserve();pid=os.fork()
        if pid==0:
            try:f.reserve()
            except Refusal as exc:os._exit(0 if str(exc)=='HOST_EVENT_ALREADY_RESERVED' else 3)
            except BaseException:os._exit(4)
            os._exit(2)
        waited,status=os.waitpid(pid,0)
        self.assertEqual(waited,pid);self.assertTrue(os.WIFEXITED(status));self.assertEqual(os.WEXITSTATUS(status),0)
        self.assertFalse(Path('/proc',str(pid)).exists())

    def test_replay_wrong_or_symlink_root_refuses(self):
        f=self.f;old=f.replay;old.rename(f.path/'old-replay');old.symlink_to(f.path/'old-replay',target_is_directory=True)
        with self.assertRaises((Refusal,OSError)):f.reserve()
    def test_nonpositive_reservations_preserve_outcome(self):
        f=self.f;f.with_effect=False;f.outcome='stop';f.refresh();r=f.reserve()
        data=json.loads((f.replay/r['reservation_files'][0]).read_bytes());self.assertEqual(data['owner_results'][0]['outcome'],'stop')
    def test_operator_permission_exact_positive_and_wrong_scope(self):
        f=self.f;f.core['required_permission_kinds']=['release'];f.refresh()
        permission={'schema_version':'lab-owner-operator-permission/v2','operation_id':f.operation,'review_binding':f.review,'target_bindings':f.core['targets'],'period':{'start':NOW-30,'end':NOW+30},'permission_kind':'release'}
        def install():
            f.selection['operator_permission_bindings']=[f.sign(permission,'effect')]
            e=json.loads((f.path/f.selection['effect_authorization_binding']['relative_path']).read_bytes())['payload']
            e['operator_permission_bindings']=f.selection['operator_permission_bindings'];f.selection['effect_authorization_binding']=f.sign(e,'effect');f.selected=f.put(f.selection)
        install();self.assertTrue(f.verify()['positive_effect_contract_verified'])
        permission['operation_id']='other';install()
        with self.assertRaisesRegex(Refusal,'OPERATOR_SCOPE'):f.verify()

    def test_all_independent_owners_required_for_multiowner_review(self):
        f=self.f;first=copy.deepcopy(f.core['owner_matrix'][0]);second=copy.deepcopy(first)
        second['owner_id']='owner:second';second['principal_ref']='human:second';f.core['owner_matrix'].append(second);f.refresh()
        with self.assertRaisesRegex(Refusal,'OWNER_INPUT_COVERAGE'):f.verify()
        # Independently signed second-owner originals preserve the same target.
        r=json.loads((f.path/f.role['relative_path']).read_bytes())['payload'];r['principal_ref']='human:second'
        b=copy.deepcopy(f.boundary);b['payload']['accountable_principal_ref']='human:second';r['boundary_binding']=f.put(b)
        co=copy.deepcopy(f.correspondence);co['principal_ref']='human:second';r['correspondence_binding']=f.put(co);rb=f.sign(r,'role')
        p=json.loads((f.path/f.presentation['relative_path']).read_bytes())['payload'];p.update(principal_ref='human:second',event_id='presentation:second',nonce='nonce:second');pb=f.sign(p,'host')
        d=json.loads((f.path/f.disposition['relative_path']).read_bytes())['payload'];d.update(principal_ref='human:second',event_id='message:second',presentation_binding=pb,role_attestation_binding=rb);db=f.sign(d,'host')
        f.selection['owner_inputs'].append({'owner_id':'owner:second','principal_ref':'human:second','presentation_binding':pb,'role_attestation_binding':rb,'disposition_binding':db})
        e=json.loads((f.path/f.selection['effect_authorization_binding']['relative_path']).read_bytes())['payload'];e['positive_disposition_bindings'].append(db);f.selection['effect_authorization_binding']=f.sign(e,'effect');f.selected=f.put(f.selection)
        self.assertEqual(len(f.verify()['owner_results']),2)
        e['positive_disposition_bindings'].pop();f.selection['effect_authorization_binding']=f.sign(e,'effect');f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'POSITIVE_DISPOSITION_COVERAGE'):f.verify()

    def test_replay_concurrent_reservation_has_one_winner(self):
        f=self.f
        def attempt():
            try:f.reserve();return 'reserved'
            except Refusal:return 'refused'
        with ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(lambda _:attempt(),range(2)))
        self.assertEqual(sorted(out),['refused','reserved']);self.assertEqual(len(list(f.replay.iterdir())),3)

    def test_replay_storage_failure_retains_consumption(self):
        f=self.f
        with patch('lab_owner.replay.os.fsync',side_effect=OSError('fixture fsync failure')):
            with self.assertRaises(OSError):f.reserve()
        self.assertEqual(len(list(f.replay.iterdir())),1)
        with self.assertRaisesRegex(Refusal,'ALREADY_RESERVED'):f.reserve()

    def test_legacy_key_adapter_and_chat_text_cannot_be_ingress(self):
        f=self.f
        for value in [{'human_conversation_outcome':None,'signature':'0'*128},b'please approve this plan']:
            f.selection['owner_inputs'][0]['disposition_binding']=f.put(value);f.selected=f.put(f.selection)
            with self.assertRaises(Refusal):f.verify()

    def test_signature_canonical_unicode_and_no_newline_hex(self):
        f=self.f;f.core['artifact_meaning']='Física \u2603 \n explicit bytes';f.refresh();self.assertTrue(f.verify()['positive_effect_contract_verified'])
        e=json.loads((f.path/f.disposition['relative_path']).read_bytes());e['signature']+='\n';f.selection['owner_inputs'][0]['disposition_binding']=f.put(e);f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'HEX_ENCODING'):f.verify()

    def test_registry_cursor_and_original_schema_are_selected(self):
        f=self.f;f.role_changes={'registry_cursor':'stale'};f.refresh()
        with self.assertRaisesRegex(Refusal,'ROLE_REGISTRY'):f.verify()
        f.role_changes={};f.assignment['unselected_authority_flag']=True;f.refresh()
        with self.assertRaisesRegex(Refusal,'NATIVE_SCHEMA'):f.verify()

    def test_control_bound_refuses_before_reader_and_large_original_is_byte_bound(self):
        f=self.f;huge=copy.deepcopy(f.selected);huge['size_bytes']=1024*1024+1
        class Spy:
            calls=0
            def read(self,*args,**kwargs):self.calls+=1;raise AssertionError('must not read')
        spy=Spy()
        with self.assertRaisesRegex(Refusal,'CONTROL_ENVELOPE_BOUND'):Capture(spy).load(huge)
        self.assertEqual(spy.calls,0)
        f.core['profile_binding']=f.put(b'x'*(1024*1024+1));f.refresh();self.assertTrue(f.verify()['positive_effect_contract_verified'])

    def test_one_principal_can_hold_distinct_selected_owner_scopes(self):
        from lab_owner.contracts import review
        f=self.f;row=copy.deepcopy(f.core['owner_matrix'][0]);row['owner_id']='owner:second-scope';row['scope_ref']='scope:second';row['role_ref']='role:second';row['boundary_ref']='boundary:second'
        f.core['owner_matrix'].append(row);review(f.core)
        f.refresh()
        with self.assertRaisesRegex(Refusal,'OWNER_INPUT_COVERAGE'):f.verify()

    def test_current_member_changed_during_verification_refuses(self):
        f=self.f;delegate=f.reader();source=f.core['source_binding'];late=f.selection['effect_authorization_binding']
        class MutatingReader:
            changed=False
            def read(self,b,**kwargs):
                raw=delegate.read(b,**kwargs)
                if b==late and not self.changed:
                    self.changed=True;(f.path/source['relative_path']).write_bytes(b'changed-after-first-read')
                return raw
        with self.assertRaises(Refusal):verify_fixture(MutatingReader(),f.enrollment,f.selected,now=NOW)

    def test_closed_fields_and_boolean_time_refuse(self):
        f=self.f;f.selection['chat_approval']=True;f.selected=f.put(f.selection)
        with self.assertRaisesRegex(Refusal,'CLOSED_FIELDS'):f.verify()
        f.refresh();f.now=True
        with self.assertRaisesRegex(Refusal,'TIME_INTEGER'):f.verify()
    def test_missing_owner_and_duplicate_target_refuse(self):
        f=self.f;f.selection['owner_inputs']=[];f.selected=f.put(f.selection)
        with self.assertRaises(Refusal):f.verify()
        f.core['targets'].append(copy.deepcopy(f.core['targets'][0]));f.refresh()
        with self.assertRaises(Refusal):f.verify()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True);args=p.parse_args();TEMP=Path(args.temp_root)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    sys.exit(0 if result.wasSuccessful() else 1)
