"""Focused exact-reference tests for the API76 integration candidate."""
import copy
import hashlib
import importlib.util
import json
import threading
from types import SimpleNamespace
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t03_lesson_domain_resolver', HERE/'lesson_application_references.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


def fixture():
    cut={'commit_sha256':'source-cut-1'}
    lesson={'scope_ref':'project:test','identity_ref':'operational-lesson:one',
            'version_ref':'operational-lesson:one@1','carrier_ref':R.LESSON,
            'byte_sha256':'lesson-original-sha'}
    bind=lambda name:{'ref':'workspace-object:test:'+name,'sha256':name+'-sha'}
    attachment={'source_cut':cut,'principal_ref':'principal:test','session_ref':'session:live',
                'assignment':{'version_ref':'assignment:one@1'},
                'parent_source_binding':{'path':'api/source-manifest.json','sha256':'selected-api-source-sha'},
                'selection_binding':bind('selection'),'applicability_binding':bind('applicability'),
                'instruction_precedence_binding':bind('instruction')}
    selection={'source_cut':cut,'session_ref':'session:live',
               'assignment':attachment['assignment'],
               'instruction_precedence_binding':attachment['instruction_precedence_binding'],
               'items':[{'lesson':lesson,'posture':'selected','expired':False,'conflict_refs':[],
                         'applicability_check_binding':attachment['applicability_binding']}]}
    applicability={'source_cut':cut,'lesson':lesson,'posture':'selected',
                   'expired':False,'conflict_refs':[]}
    instruction={'source_cut':cut,'session_ref':'session:live',
                 'assignment':attachment['assignment'],'veto_lesson_influence':False}
    record={'schema_version':'cyberalchemy-lab-lesson-application/v1',
            'kind':'lesson-application','lifecycle_state':'candidate',
            'authority_effect':'none','scope_ref':'project:test','owner_ref':'principal:test',
            'evidence_refs':[lesson['version_ref']],'successor_refs':[],
            'relation_refs':[{'relation_kind_ref':R.RELATION,'direction':'source',
                              'counterpart_kind':'operational-lesson',
                              'counterpart_ref':lesson['version_ref']}],
            'payload':{'session_ref':'session:live','lesson_revision_ref':lesson['version_ref'],
                       'applicability_assessment_ref':attachment['applicability_binding']['ref'],
                       'intended_influence':'Inspect bounded API30 Project State',
                       'application_posture':'candidate-attributed-no-tool-dispatch',
                       'conflict_refs':[],'override_refs':[]}}
    target={'version_ref':'lesson-application:one@candidate.1','carrier_ref':R.CARRIER,
            'operation':'admit','record':record}
    proposal={'base_cut':cut,'scope_ref':'project:test',
              'targets':[{'artifact':{'version_ref':target['version_ref']}}]}
    routing={'authority_effect':'none','source_cut':cut,'scope_ref':'project:test',
             'proposal_binding':{'ref':'proposal:selected','sha256':'proposal-sha'},
             'selection_binding':attachment['selection_binding'],
             'applicability_binding':attachment['applicability_binding'],
             'instruction_precedence_binding':attachment['instruction_precedence_binding'],
             'intended_influence':'Inspect bounded API30 Project State',
             'schema_version':'lab-lesson-application-routing/v1-candidate',
             'actual_owner_outcome':None,'override_bindings':[],
             'action_bound_refs':['context.get']}
    return {'target':target,'proposal':proposal,'owner':'principal:test','cut':cut,
            'attachment':attachment,'selection':selection,'applicability':applicability,
            'instruction':instruction,'lesson':lesson,'routing':routing}


class ExactLessonApplicationReferences(unittest.TestCase):
    def test_exact_current_selected_case(self):
        f=fixture()
        self.assertTrue(R.supported(f['target'],{'schema_version':R.POLICY}))
        rows=R.validate_selected(**f)
        self.assertEqual([r['selector'] for r in rows],
                         ['/payload/lesson_revision_ref','/evidence_refs/0',
                          '/relation_refs/0/counterpart_ref'])
        self.assertTrue(all(r['resolved_ref']==f['lesson'] and r['posture']=='resolved' for r in rows))

    def test_unrelated_carrier_or_policy_remains_unsupported(self):
        f=fixture();t=f['target']
        self.assertFalse(R.supported(t,{'schema_version':'other-policy'}))
        t['carrier_ref']='cal.artifact-type.lesson-outcome-assessment/v1'
        self.assertFalse(R.supported(t,{'schema_version':R.POLICY}))
        t['carrier_ref']=R.CARRIER;t['operation']='withdraw'
        self.assertFalse(R.supported(t,{'schema_version':R.POLICY}))
        t['operation']='admit';t['record']['payload']['conflict_refs']=['lesson:two']
        self.assertFalse(R.supported(t,{'schema_version':R.POLICY}))

    def test_foreign_session_ref_refused(self):
        f=fixture();f['target']['record']['payload']['session_ref']='session:foreign'
        with self.assertRaisesRegex(ValueError,'live Session'):R.validate_selected(**f)

    def test_foreign_assignment_refused(self):
        f=fixture();f['selection']['assignment']={'version_ref':'assignment:foreign@1'}
        with self.assertRaisesRegex(ValueError,'live Assignment'):R.validate_selected(**f)
        f=fixture();f['instruction']['assignment']={'version_ref':'assignment:foreign@1'}
        with self.assertRaisesRegex(ValueError,'live Assignment'):R.validate_selected(**f)

    def test_other_lesson_revision_ref_refused(self):
        f=fixture();f['target']['record']['payload']['lesson_revision_ref']='lesson:foreign@1'
        with self.assertRaisesRegex(ValueError,'revision differs'):R.validate_selected(**f)

    def test_stale_source_cut_refused(self):
        f=fixture();f['proposal']['base_cut']={'commit_sha256':'stale'}
        with self.assertRaisesRegex(ValueError,'source cut'):R.validate_selected(**f)

    def test_foreign_scope_and_owner_refused(self):
        for field,value,reason in [('scope_ref','project:foreign','scope'),
                                   ('owner_ref','principal:foreign','owner')]:
            f=fixture();f['target']['record'][field]=value
            with self.assertRaisesRegex(ValueError,reason):R.validate_selected(**f)

    def test_unselected_applicability_ref_refused(self):
        f=fixture();f['target']['record']['payload']['applicability_assessment_ref']='object:foreign'
        with self.assertRaisesRegex(ValueError,'applicability reference'):R.validate_selected(**f)

    def test_missing_evidence_or_wrong_relation_refused(self):
        f=fixture();f['target']['record']['evidence_refs']=[]
        with self.assertRaisesRegex(ValueError,'evidence references'):R.validate_selected(**f)
        f=fixture();f['target']['record']['relation_refs'][0]['counterpart_ref']='lesson:foreign@1'
        with self.assertRaisesRegex(ValueError,'relation target'):R.validate_selected(**f)

    def test_veto_and_ambiguous_selection_refused(self):
        f=fixture();f['instruction']['veto_lesson_influence']=True
        with self.assertRaisesRegex(ValueError,'vetoes'):R.validate_selected(**f)
        f=fixture();f['selection']['items'].append(copy.deepcopy(f['selection']['items'][0]))
        with self.assertRaisesRegex(ValueError,'ambiguous'):R.validate_selected(**f)

    def test_unselected_routing_or_unattributed_candidate_refused(self):
        f=fixture();f['routing']['intended_influence']='A different task'
        with self.assertRaisesRegex(ValueError,'routing or attributed influence'):
            R.validate_selected(**f)
        f=fixture();f['target']['record']['payload']['application_posture']='operational'
        with self.assertRaisesRegex(ValueError,'routing or attributed influence'):
            R.validate_selected(**f)

    def test_duplicate_proposal_target_refused(self):
        f=fixture();f['proposal']['targets'].append(copy.deepcopy(f['proposal']['targets'][0]))
        with self.assertRaisesRegex(ValueError,'ambiguous'):R.validate_selected(**f)

    def adapter(self, *, corrupt_original=False, omit_selected_resolver=False):
        f=fixture(); raw_lesson=json.dumps({'scope_ref':'project:test','kind':'operational-lesson'}).encode()
        method_path=HERE/'test_resolver.py'
        method={'ref':str(method_path.relative_to(Path.cwd())),
                'sha256':hashlib.sha256(method_path.read_bytes()).hexdigest()}
        authorization=Path.cwd()/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        f['routing']['method_binding']=method
        f['routing']['authorization_basis_binding']={
            'ref':str(authorization.relative_to(Path.cwd())),
            'sha256':hashlib.sha256(authorization.read_bytes()).hexdigest()}
        f['lesson']['byte_sha256']=hashlib.sha256(raw_lesson).hexdigest()
        for row in (f['selection']['items'],):row[0]['lesson']=copy.deepcopy(f['lesson'])
        f['applicability']['lesson']=copy.deepcopy(f['lesson'])
        for key in ('selection','applicability','instruction'):
            f[key]['authority_effect']='none'
        original=json.dumps(f['target']['record'],sort_keys=True).encode()
        content={'content_ref':'candidate:lesson-application',
                 'byte_sha256':hashlib.sha256(original).hexdigest()}
        f['proposal']['targets'][0].update(content=content,
            artifact={'version_ref':f['target']['version_ref'],'carrier_ref':R.CARRIER,
                      'byte_sha256':content['byte_sha256']},
            decision_core_binding={'ref':'core:one','sha256':'core-sha'})
        source=SimpleNamespace(
            sha=lambda raw:hashlib.sha256(raw).hexdigest(),
            original=lambda row:Path.cwd().joinpath(row['path']).read_bytes())
        P=SimpleNamespace(source=source, ROOT=Path.cwd(),
            frame_parse=lambda raw:json.loads(raw),
            compact=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode(),
            binding=lambda ref,raw:{'ref':ref,'sha256':hashlib.sha256(raw).hexdigest()})
        selected={f['attachment'][key]['ref']:json.dumps(f[key.split('_')[0]],sort_keys=True).encode()
                  for key in ('selection_binding','applicability_binding','instruction_precedence_binding')}
        # The instruction key names its selected original directly.
        selected[f['attachment']['instruction_precedence_binding']['ref']]=json.dumps(f['instruction']).encode()
        attachment=SimpleNamespace(expected=f['attachment'],parent=object(),
            material_guard=lambda:None,material=lambda binding:selected[binding['ref']])
        attachment.resource=SimpleNamespace(_lifetime_lock=threading.RLock(),
            bridge=SimpleNamespace(permission=lambda:SimpleNamespace(operations=['context.get'])))
        subject={'effective_state':'local-admitted-current','kind':'operational-lesson'}
        view=SimpleNamespace(data={'projection':object()})
        handlers=SimpleNamespace(view=view,current=lambda:True,resolve_exact=lambda lesson:subject)
        channel=SimpleNamespace(policy={'schema_version':R.POLICY},
            policy_guard=lambda:{'application_control':{'runtime_identities':{'session_ref':'session:live'},
                'routing_binding':{'ref':'routing:one','sha256':'routing-sha'},
                'method_binding':method}},
            guard=lambda:{'principal_ref':'principal:test'})
        vault=SimpleNamespace(material=lambda binding:b'{}' if corrupt_original else original,
            object_read=lambda binding:json.dumps(
                f['proposal'] if binding['ref']=='proposal:selected' else f['routing']).encode())
        host=SimpleNamespace(channel=channel,session_attachment=attachment,handlers=handlers,vault=vault)
        attachment.host=host
        resolver=object.__new__(R.LessonApplicationReferences)
        resolver.host=host;resolver.P=P
        resolver.M=SimpleNamespace(record_bytes=lambda view,row:(raw_lesson,None),
                                   artifact_ref=lambda view,row:f['lesson'])
        resolver.H=SimpleNamespace(cut=lambda view:f['cut'])
        resolver_path=HERE/'lesson_application_references.py'
        selected_row={'path':str(resolver_path.relative_to(Path.cwd())),
                      'sha256':hashlib.sha256(resolver_path.read_bytes()).hexdigest()}
        resolver.G=SimpleNamespace(verify=lambda digest:{'files':[
            {'path':method['ref'],'sha256':method['sha256']}]
            + ([] if omit_selected_resolver else [selected_row])})
        return resolver,f,view

    def test_adapter_resolves_authenticated_originals_only(self):
        resolver,f,view=self.adapter()
        refs,details=resolver.resolve(f['target'],f['proposal'],{'subjects':{}})
        self.assertEqual(len(refs),3)
        self.assertEqual(details['resolved_reference_count'],3)
        self.assertFalse(details['canonical_admission_granted'])
        self.assertEqual(details['live_parent_session_ref'],'session:live')
        self.assertEqual(len(details['input_bindings']),6)

    def test_adapter_refuses_changed_original_bytes(self):
        resolver,f,view=self.adapter(corrupt_original=True)
        with self.assertRaisesRegex(ValueError,'original target bytes differ'):
            resolver.resolve(f['target'],f['proposal'],{'subjects':{}})

    def test_adapter_refuses_unselected_resolver_source(self):
        resolver,f,view=self.adapter(omit_selected_resolver=True)
        with self.assertRaisesRegex(ValueError,'outside selected API Source'):
            resolver.resolve(f['target'],f['proposal'],{'subjects':{}})

    def test_adapter_refuses_other_same_cut_proposal(self):
        resolver,f,view=self.adapter()
        foreign=copy.deepcopy(f['proposal']);foreign['proposal_ref']='another-proposal'
        with self.assertRaisesRegex(ValueError,'differs from independently selected routing'):
            resolver.resolve(f['target'],foreign,{'subjects':{}})

    def test_adapter_refuses_foreign_method_and_authorization(self):
        for field in ('method_binding','authorization_basis_binding'):
            resolver,f,view=self.adapter()
            f['routing'][field]={'ref':'foreign:selected','sha256':'foreign-sha'}
            with self.assertRaisesRegex(ValueError,'selected routing/method/authorization'):
                resolver.resolve(f['target'],f['proposal'],{'subjects':{}})

    def test_adapter_refuses_actions_outside_live_delegation(self):
        resolver,f,view=self.adapter()
        f['routing']['action_bound_refs']=['context.get','tool.dispatch']
        with self.assertRaisesRegex(ValueError,'action bounds exceed live Session delegation'):
            resolver.resolve(f['target'],f['proposal'],{'subjects':{}})


if __name__=='__main__':unittest.main()
