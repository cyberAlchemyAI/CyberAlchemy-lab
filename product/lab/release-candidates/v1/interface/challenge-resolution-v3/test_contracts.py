"""Isolated signed-gate/obligation tests; not current-source API qualification."""
import base64
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from . import gate, obligations


class Contracts(unittest.TestCase):
    def setUp(self):
        self.now=datetime.now(timezone.utc)
        self.key=Ed25519PrivateKey.generate()
        self.public=self.key.public_key().public_bytes_raw().hex()
        self.principal={'kind':'principal','node_id':'principal:isolated-resolution-owner',
            'scope_ref':'scope:isolated-resolution','payload':{'status':'active',
            'stable_subject_ref':'ed25519-public-key-sha256:'+hashlib.sha256(bytes.fromhex(self.public)).hexdigest()}}
        self.header=lambda ref:{'scope_ref':self.principal['scope_ref'],'identity_ref':ref,
                                'version_ref':ref+'@1','carrier_ref':'cal.artifact-type.test/v1','byte_sha256':'a'*64}
        self.challenge=self.header('challenge:isolated')
        self.contract=self.header('contract:isolated')
        self.subject=self.header('subject:isolated')
        self.owner=self.header(self.principal['node_id'])
        self.evidence=[{'ref':'evidence:isolated@1','sha256':'b'*64}]
        self.rules={name:'protocol:isolated-'+name for name in ('policy_ref','owner_route','resolution_gate_ref',
                    'unresolved_residue_route','response_period')}
        self.rules.update(response_modes=['explain-and-revise'],eligible_challenger_kinds=['principal'],
                          required_evidence_kinds=['evidence-set'])
        self.control={name:self.rules[name] for name in ('policy_ref','owner_route','resolution_gate_ref',
                     'unresolved_residue_route','response_period')}
        self.control.update(response_seconds=300,response_mode='explain-and-revise',
            response_binding={'ref':'response:isolated','sha256':'c'*64},challenger=self.owner,
            accepted_evidence=[{'binding':self.evidence[0],'artifact':self.header('evidence:isolated'),'kind':'evidence-set'}])
        self.response={'schema_version':'lab-exact-challenge-response/v1-candidate','challenge':self.challenge,
            'challenge_contract':self.contract,'subject':self.subject,'owner_principal':self.owner,
            'response_mode':self.control['response_mode'],'responded_at':(self.now-timedelta(seconds=5)).isoformat(),
            'evidence_bindings':self.evidence,'authority_effect':'none'}
        self.challenge_payload={'challenger_ref':self.principal['node_id'],
            'submitted_at':(self.now-timedelta(seconds=10)).isoformat(),'evidence_refs':[self.evidence[0]['ref']]}
        self.selected=dict(selected_public_key_hex=self.public,recognized_principal=self.principal['node_id'],
            selected_gate_ref=self.rules['resolution_gate_ref'],owner_route=self.rules['owner_route'],
            scope_ref=self.principal['scope_ref'],source_cut={'sequence':1,'digest':'d'*64},
            challenge=self.challenge,resolution_decision=self.header('decision:isolated'),challenge_contract=self.contract,
            subject=self.subject,selected_outcome='prepare-isolated-revision',semantic_proposal_binding=None,
            governance_proposal_binding={'ref':'proposal:isolated','sha256':'e'*64},evidence_bindings=self.evidence,
            consequence_routes=[],response_obligations=self.control,principal_record=self.principal,
            policy_expires_at=(self.now+timedelta(minutes=5)).isoformat(),now=self.now)
        self.payload={name:self.selected[name] for name in ('owner_route','scope_ref','source_cut','challenge',
            'resolution_decision','challenge_contract','subject','selected_outcome','semantic_proposal_binding',
            'governance_proposal_binding','evidence_bindings','consequence_routes','response_obligations')}
        self.payload.update(schema_version='lab-exact-challenge-resolution-gate/v1-candidate',
            gate_ref=self.selected['selected_gate_ref'],principal_ref=self.selected['recognized_principal'],
            not_before=(self.now-timedelta(seconds=1)).isoformat(),expires_at=(self.now+timedelta(minutes=1)).isoformat(),
            permitted_effects=['prepare-exact-challenge-consequences'],
            excluded_effects=['canonical-admission','live-activation','tool-dispatch','challenged-subject-overwrite'],
            authority_effect='none')

    def tearDown(self):
        self.key=None

    def signed(self,payload=None,key=None):
        payload=copy.deepcopy(self.payload if payload is None else payload)
        return {'payload':payload,'signature':base64.b64encode((self.key if key is None else key).sign(gate.encoded(payload))).decode()}

    def verify(self,envelope=None,**changes):
        return gate.verify(self.signed() if envelope is None else envelope,**{**self.selected,**changes})

    def response_check(self,**changes):
        values=dict(control=self.control,rules=self.rules,challenge=self.challenge_payload,challenge_header=self.challenge,
            contract_header=self.contract,subject_header=self.subject,owner_header=self.owner,challenger=self.principal,
            response=self.response,evidence_bindings=self.evidence,now=self.now)
        return obligations.verify(**{**values,**changes})

    def test_01_exact_ephemeral_signature_and_response_obligations(self):
        self.assertEqual(self.verify(),self.payload)
        self.response_check()

    def test_02_altered_bytes_without_resigning(self):
        signed=self.signed();signed['payload']['selected_outcome']='tampered'
        with self.assertRaises(InvalidSignature):self.verify(signed)

    def test_03_other_ephemeral_signer(self):
        with self.assertRaises(InvalidSignature):self.verify(self.signed(key=Ed25519PrivateKey.generate()))

    def test_04_every_selected_signed_field_cannot_supply_its_own_authority(self):
        for field in gate.FIELDS-{'not_before','expires_at'}:
            with self.subTest(field=field):
                value=copy.deepcopy(self.payload);value[field]='substitution'
                with self.assertRaises(ValueError):self.verify(self.signed(value))

    def test_05_closed_envelope_and_payload(self):
        for field in gate.FIELDS:
            with self.subTest(field=field):
                value=copy.deepcopy(self.payload);del value[field]
                with self.assertRaises(ValueError):self.verify(self.signed(value))
        value=self.signed();value['extra']='claim'
        with self.assertRaises(ValueError):self.verify(value)

    def test_06_expired_future_and_policy_ceiling(self):
        for updates in ({'expires_at':self.now.isoformat()},
                        {'not_before':(self.now+timedelta(seconds=1)).isoformat()},
                        {'expires_at':(self.now+timedelta(minutes=6)).isoformat()}):
            with self.subTest(updates=updates):
                value={**self.payload,**updates}
                with self.assertRaises(ValueError):self.verify(self.signed(value))

    def test_07_principal_recognition_key_scope_and_status(self):
        for field,changed in (('scope_ref','scope:foreign'),('node_id','principal:foreign')):
            value=copy.deepcopy(self.principal);value[field]=changed
            with self.assertRaises(ValueError):self.verify(principal_record=value)
        for field,changed in (('status','retired'),('stable_subject_ref','claimed:owner')):
            value=copy.deepcopy(self.principal);value['payload'][field]=changed
            with self.assertRaises(ValueError):self.verify(principal_record=value)

    def test_08_response_route_contract_and_mode(self):
        for field in ('policy_ref','owner_route','resolution_gate_ref','unresolved_residue_route','response_period','response_mode'):
            with self.subTest(field=field):
                control={**self.control,field:'protocol:foreign'}
                with self.assertRaises(ValueError):self.response_check(control=control)

    def test_09_response_exact_subject_and_owner(self):
        for field in ('challenge','challenge_contract','subject','owner_principal','evidence_bindings','response_mode'):
            with self.subTest(field=field):
                response={**self.response,field:'foreign'}
                with self.assertRaises(ValueError):self.response_check(response=response)

    def test_10_response_window_and_actual_clock(self):
        for delta in (-11,1):
            response={**self.response,'responded_at':(self.now+timedelta(seconds=delta)).isoformat()}
            with self.assertRaises(ValueError):self.response_check(response=response)
        challenge={**self.challenge_payload,'submitted_at':(self.now-timedelta(seconds=305)).isoformat()}
        with self.assertRaises(ValueError):self.response_check(challenge=challenge)
        with self.assertRaises(ValueError):self.response_check(control={**self.control,'response_seconds':True})

    def test_11_challenger_and_required_evidence(self):
        with self.assertRaises(ValueError):self.response_check(challenger={**self.principal,'node_id':'principal:foreign'})
        rules={**self.rules,'required_evidence_kinds':['operational-observation']}
        with self.assertRaises(ValueError):self.response_check(rules=rules)
        challenge={**self.challenge_payload,'evidence_refs':['evidence:foreign']}
        with self.assertRaises(ValueError):self.response_check(challenge=challenge)

    def proposals(self):
        common={'actor':{'principal_ref':self.principal['node_id']},'scope_ref':self.principal['scope_ref'],
                'base_cut':self.selected['source_cut'],'source_profile_binding':{'ref':'profile'},
                'workspace_binding':{'ref':'workspace'},'idempotency_key':'key:isolated',
                'challenge_route':'route:isolated','authority_effect':'none'}
        semantic={**common,'targets':[{'artifact':{**self.subject,'version_ref':self.subject['identity_ref']+'@2'},
                    'operation':'revise','predecessor':self.subject}],
                  'connection_proposals':[{'ref':'connection:semantic'}],'evidence_bindings':[self.evidence[0]],
                  'schema_bindings':[{'ref':'schema:semantic'}]}
        governance={**common,'targets':[{'artifact':self.header('residue:isolated'),'operation':'admit','predecessor':None}],
                    'connection_proposals':[{'ref':'connection:governance'}],'evidence_bindings':[self.evidence[0]],
                    'schema_bindings':[{'ref':'schema:governance'}]}
        result={**common,'targets':semantic['targets']+governance['targets'],
                'connection_proposals':semantic['connection_proposals']+governance['connection_proposals'],
                'evidence_bindings':[self.evidence[0]],'schema_bindings':semantic['schema_bindings']+governance['schema_bindings']}
        return result,{'semantic':semantic,'governance':governance}

    def test_12_ordered_axes_and_prospective_subject_revision(self):
        result,branches=self.proposals()
        obligations.composition(result,branches,subject_header=self.subject)
        self.assertEqual(branches['semantic']['targets'][0]['predecessor'],self.subject)

    def test_13_composition_preserves_every_common_field_and_connection(self):
        result,branches=self.proposals()
        for field in result:
            with self.subTest(field=field):
                changed=copy.deepcopy(result);changed[field]=[] if isinstance(result[field],list) else 'foreign'
                with self.assertRaises(ValueError):obligations.composition(changed,branches,subject_header=self.subject)

    def test_14_exact_existing_challenged_version_cannot_be_overwritten(self):
        result,branches=self.proposals()
        branches['semantic']['targets'][0]['artifact']=self.subject
        result['targets']=branches['semantic']['targets']+branches['governance']['targets']
        with self.assertRaises(ValueError):obligations.composition(result,branches,subject_header=self.subject)

    def test_15_revision_cannot_substitute_predecessor(self):
        result,branches=self.proposals()
        branches['semantic']['targets'][0]['predecessor']=self.header('foreign:subject')
        result['targets']=branches['semantic']['targets']+branches['governance']['targets']
        with self.assertRaises(ValueError):obligations.composition(result,branches,subject_header=self.subject)
