"""Real complete source inventory plus bounded inert eligibility counterexamples."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

S=Path(__file__).absolute().parents[2]
R=S.parents[3]
DEPS=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
sys.path[:0]=[str(S/'contracts'),str(S/'selectors'),str(S/'evidence_index'),str(DEPS)]
from lab_contracts.codec import canonical, sha, Refusal
from lab_selectors.anchors import RootAnchor, AnchoredReader, identity
from lab_evidence.inventory import build
from lab_evidence.common import digest
from lab_evidence.eligibility import evaluate, core_digest, Evaluation, policy
from lab_evidence.history import historical
from lab_evidence.invalidation import invalidate
from lab_evidence.retention import persist

TEMP=None


def bound(path,root='repo',base=R):
    raw=path.read_bytes()
    return {'kind':'execution','root_id':root,'relative_path':str(path.relative_to(base)),
            'sha256':sha(raw),'size_bytes':len(raw)}


class Fixture:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-index-',dir=TEMP)
        self.path=Path(self.temp.name);self.bindings=[];self.counter=0
        self.inventory_binding=bound(S/'evidence_index/original-inventory-selection.json')
        self.history_binding=bound(S/'evidence_index/historical-selection.json')
        # Exact literals are independently checked by the outer development and
        # coordinator source guard before this test module is imported.
        for selected in [self.inventory_binding,self.history_binding]:
            self.bindings.append(selected)
            self.bindings.extend(d['binding'] for d in json.loads((R/selected['relative_path']).read_bytes())['documents'])
        self.inventory=build(self.reader(),self.inventory_binding)
        self.selection=self.put({'schema_version':'fixture-selection/v1','revision':1})
        self.subject=self.put({'schema_version':'fixture-code/v1','body':'owned inert fixture'})
        self.subjects=[{'role':'code','binding':self.subject}];self.task_subjects=[]
        self.policies=[]
        for occurrence in self.inventory.occurrences:
            self.policies.append({'occurrence_id':occurrence['id'],'dispositions':[
                {'task_id':task,'resolution':'context' if occurrence['role']=='context' else 'required',
                 'allowed_stages':['inert-contract'],'required_roles':['code'],
                 'terminal_kinds':['process'],'allowed_dispositions':['approve','reject','defer','stop'] if task=='T26' else ['not-applicable'],
                 'requires_timing':True,'required_terminal_kinds':[],'required_proofs':[{'stage':'inert-contract','terminal_kind':'process'}],
                 'proof_rule_ids':['fixture-only'],
                 'scope_occurrence_ids':[] if occurrence['role']=='context' else [occurrence['id']],
                 'basis_occurrence_ids':[occurrence['id']],'later_owner_units':[],'gate_ids':[],
                 'independent_review':True,'deferred_to':None,'rationale':'Inert evaluator fixture only; not native task proof.'}
                 for task in occurrence['candidate_owners']]})
        self.deferrals=[];self.records=[];self.enrollments=[]

    def close(self):self.temp.cleanup()

    def put(self,value,raw=False):
        self.counter+=1;p=self.path/f'{self.counter:05}.json'
        data=value if raw else canonical(value)
        with p.open('xb') as f:f.write(data)
        b=bound(p,'fixture',self.path);self.bindings.append(b);return b

    def reader(self):
        unique={canonical(b):b for b in self.bindings}
        return AnchoredReader([RootAnchor('repo',str(R),identity(R.stat())),
            RootAnchor('fixture',str(self.path),identity(self.path.stat()))],list(unique.values()))

    def policy(self):
        p={'schema_version':'lab-criterion-policy/v1','inventory_binding':self.inventory_binding,
           'inventory_digest':digest(self.inventory.view()),'entries':self.policies,
           'deferral_authorizations':self.deferrals,'mapping_bindings':[],
           'acceptance_phases':[{'acceptance_id':o['selector']['heading'],'occurrence_id':o['id'],
               'candidate_tasks':[t for t in o['candidate_owners'] if t not in {'T26','T27','T28','T29','T30'}],
               'later_tasks':[t for t in o['candidate_owners'] if t in {'T26','T27','T28','T29','T30'}],
               'candidate_closure_task':'T25' if o['selector']['heading'] in {'AC05','AC13'} else 'T24',
               'basis_occurrence_ids':[o['id']]} for o in self.inventory.occurrences if o['document_id']=='acceptance']}
        review={'schema_version':'lab-policy-review/v1','policy_core_digest':digest(p),
                'outcome':'PASS','reviewer_identity':'fixture-policy-reviewer',
                'author_identity':'fixture-policy-author','scope':'criterion-interpretation'}
        self.policy_review=self.put(review);p['interpretation_review_binding']=self.policy_review
        self.last_policy=self.put(p);return self.last_policy

    def evidence(self,task='T00',outcome='PASS',change=None,review_change=None,terminal_change=None,
                 kind='process',stage='inert-contract',disposition='not-applicable',scope_ids=None):
        if task=='T26' and disposition=='not-applicable':disposition='approve'
        ids=[e['occurrence_id'] for e in self.policies for d in e['dispositions']
             if d['task_id']==task and d['resolution']=='required']
        if scope_ids is not None:ids=scope_ids
        by_id={o['id']:o for o in self.inventory.occurrences}
        acids=set()
        for oid in ids:
            occurrence=by_id[oid]
            acids.update([occurrence['selector']['heading']] if occurrence['document_id']=='acceptance'
                         else self.inventory.summary['task_acceptance'][task])
        eid=f'fixture-{task}-{self.counter}'
        native=self.put(b'Original inert observation, not a native runtime qualification.',raw=True)
        attempt=self.put({'schema_version':'lab-evidence-attempt/v1','attempt_id':eid,
            'selection_binding':self.selection,'case_id':'inert-fixture','stage':stage})
        command=self.put({'schema_version':'lab-evidence-command/v1','evidence_id':eid,
            'selection_binding':self.selection,'attempt_binding':attempt,'case_id':'inert-fixture',
            'stage':stage,'argv':['fixture-no-exec'] if kind=='process' else None,'command_kind':kind,
            'environment_bindings':[],'original_binding':native})
        terminal={'schema_version':'lab-evidence-terminal/v1','evidence_id':eid,
            'selection_binding':self.selection,'command_binding':command,'outcome':outcome,
            'actual_exit':(0 if outcome=='PASS' else 1 if outcome in {'FAIL','ERROR'} else None) if kind=='process' else None,'cleanup':'clean',
            'terminal_kind':kind,'observation_disposition':disposition,
            'effect_state':'owned-inert','original_binding':native}
        if terminal_change:terminal.update(terminal_change)
        terminal_binding=self.put(terminal)
        timing=self.put({'schema_version':'lab-evidence-timing/v1','command_binding':command,
                         'elapsed_ns':100 if kind=='process' else None,'original_binding':native})
        record={'schema_version':'lab-evidence-record/v1','evidence_id':eid,'task_id':task,
            'original_obligation_ids':ids,'acceptance_condition_ids':sorted(acids),
            'case_id':'inert-fixture','evidence_stage':stage,'observation_disposition':disposition,
            'subject_bindings':copy.deepcopy(self.subjects)+next((copy.deepcopy(x['subject_bindings']) for x in self.task_subjects if x['task_id']==task),[]),
            'selection_binding':self.selection,'attempt_binding':attempt,'outcome':outcome,
            'claim_ceiling':'Synthetic evaluator proof only','input_bindings':[],
            'command_binding':command,'terminal_binding':terminal_binding,'timing_binding':timing,
            'state_observation_bindings':[],'invalidation_rule':'exact-selected-consumer-closure/v1',
            'privacy_class':'reviewed-public-receipt','author_identity':'fixture-evidence-author'}
        if change:record.update(change)
        review={'schema_version':'lab-evidence-review/v1','evidence_core_digest':core_digest(record),
            'reviewer_identity':'fixture-evidence-reviewer','author_identity':'fixture-evidence-author',
            'outcome':'PASS','task_id':record['task_id'],'occurrence_ids':record['original_obligation_ids'],
            'selection_binding':record['selection_binding'],'stage':record['evidence_stage'],
            'claim_ceiling':record['claim_ceiling']}
        if review_change:review.update(review_change)
        rb=self.put(review);record['review_binding']=rb
        self.records.append(self.put(record))
        self.enrollments.append({'review_binding':rb,'reviewer_identity':'fixture-evidence-reviewer',
            'author_identity':'fixture-evidence-author','evidence_core_digest':core_digest(record)})
        return record

    def context(self):
        public=list({canonical(b):b for b in self.bindings}.values())
        return self.put({'schema_version':'lab-eligibility-context/v1','selection_binding':self.selection,
            'subject_bindings':copy.deepcopy(self.subjects),
            'evidence_bindings':self.records,'review_enrollments':self.enrollments,
            'policy_review_binding':self.policy_review,'policy_reviewer_identity':'fixture-policy-reviewer',
            'policy_author_identity':'fixture-policy-author','public_retention_bindings':public,
            'privacy_class':'reviewed-public-selector','task_subject_bindings':copy.deepcopy(self.task_subjects)})

    def evaluate(self):
        p=self.policy();c=self.context();self.last_context=c
        return evaluate(self.reader(),self.inventory_binding,p,c)

    def graph(self,unknown=False):
        nodes=[{'id':t,'kind':'task','task_id':t,'acceptance_id':None} for t in self.inventory.summary['tasks']]
        nodes += [{'id':f'AC{i:02}','kind':'acceptance','task_id':None,'acceptance_id':f'AC{i:02}'} for i in range(1,14)]
        nodes += [{'id':name,'kind':kind,'task_id':None,'acceptance_id':None}
                  for name,kind in [('code','subject'),('unrelated','subject'),('proof','evidence'),('aggregate','aggregate')]]
        edges=[{'producer':e['from'],'consumer':e['to'],'kind':'acceptance-dependency'}
               for e in self.inventory.summary['edges']]
        edges += [{'producer':t,'consumer':a,'kind':'acceptance-dependency'}
                  for t,acids in self.inventory.summary['task_acceptance'].items() for a in acids]
        edges += [{'producer':'code','consumer':'proof','kind':'dynamic-input'},
                  {'producer':'proof','consumer':'T00','kind':'selected-input'},
                  {'producer':'T30','consumer':'aggregate','kind':'selected-input'}]
        return {'schema_version':'lab-evidence-consumer-graph/v1','inventory_binding':self.inventory_binding,
            'nodes':nodes,'edges':edges,'unmapped_subjects':['unrelated','code'] if unknown else ['unrelated']}


class IndexTests(unittest.TestCase):
    def setUp(self):self.f=Fixture()
    def tearDown(self):self.f.close()

    def test_real_full_inventory_roundtrip_and_distinct_clauses(self):
        f=self.f;i=f.inventory
        self.assertEqual(i.summary['body_count'],122)
        self.assertEqual(i.summary['dag_acceptance_occurrences'],110)
        self.assertGreater(i.summary['criterion_count'],110)
        self.assertEqual(len(i.summary['edges']),73)
        for b,raw in i.originals:self.assertEqual(i.original_bytes(b),raw)
        for o in i.occurrences:
            if o['selector']['kind']=='byte-span':
                raw=i.original_bytes(o['source_binding']);s=o['selector']
                self.assertEqual(raw[s['start']:s['end']].decode(),o['text'])
        headings={o['selector'].get('heading') for o in i.occurrences if o['role']!='context'}
        for h in ['Preserved acceptance obligations','Acceptance in this phase',
                  'Implementation detail: ordered rules','Acceptance and validation strategy',
                  'Deferred admitted-operation obligation']:self.assertIn(h,headings)
        self.assertEqual(len([o for o in i.occurrences if o['document_id']=='acceptance']),13)

    def test_missing_or_substituted_original_body_refuses(self):
        f=self.f;selected=json.loads((R/f.inventory_binding['relative_path']).read_bytes())
        selected['documents'].pop()
        bad=f.put(selected)
        with self.assertRaisesRegex(Refusal,'BODY_COVERAGE'):build(f.reader(),bad)
        selected=json.loads((R/f.inventory_binding['relative_path']).read_bytes())
        selected['documents'][-1]['binding']=selected['documents'][-2]['binding']
        bad=f.put(selected)
        with self.assertRaisesRegex(Refusal,'BODY_PATH'):build(f.reader(),bad)

    def test_policy_omission_reorder_renumber_refuse(self):
        f=self.f
        for mode in ['omit','reorder','renumber']:
            original=copy.deepcopy(f.policies)
            if mode=='omit':f.policies.pop()
            if mode=='reorder':f.policies[0],f.policies[1]=f.policies[1],f.policies[0]
            if mode=='renumber':f.policies[0]['occurrence_id']='f'*64
            with self.assertRaisesRegex(Refusal,'POLICY_OCCURRENCE_COVERAGE'):f.evaluate()
            f.policies=original

    def test_unresolved_native_interpretation_never_passes(self):
        f=self.f
        for e in f.policies:
            for d in e['dispositions']:
                if d['resolution']=='required':d['resolution']='unresolved'
        out=f.evaluate().projection
        self.assertTrue(all(t['status']=='INELIGIBLE' for t in out['tasks'].values()))
        self.assertTrue(all(a['status']=='PENDING' for a in out['acceptance'].values()))

    def test_complete_t00_fixture_is_eligible_but_not_its_descendants(self):
        f=self.f;f.evidence();out=f.evaluate().projection
        self.assertEqual(out['tasks']['T00']['status'],'ELIGIBLE')
        self.assertEqual(out['tasks']['T01']['status'],'INELIGIBLE')

    def test_missing_criterion_does_not_close(self):
        f=self.f
        ids=[e['occurrence_id'] for e in f.policies for d in e['dispositions']
             if d['task_id']=='T00' and d['resolution']=='required']
        f.evidence(change={'original_obligation_ids':ids[:-1]})
        self.assertEqual(f.evaluate().projection['tasks']['T00']['status'],'INELIGIBLE')

    def test_wrong_cut_stage_subject_ac_refuse(self):
        f=self.f
        for change in [{'selection_binding':f.subject},{'evidence_stage':'final-qualification'},
                       {'subject_bindings':[{'role':'code','binding':f.selection}]},
                       {'acceptance_condition_ids':['AC99']}]:
            f.records=[];f.enrollments=[];f.evidence(change=change)
            out=f.evaluate().projection
            self.assertFalse(out['evidence'][0]['eligible'])
            self.assertEqual(out['tasks']['T00']['status'],'INELIGIBLE')

    def test_review_must_match_external_enrollment(self):
        f=self.f
        for change in [{'reviewer_identity':'invented-independent-reviewer'},
                       {'author_identity':'invented-author'},{'occurrence_ids':[]},
                       {'evidence_core_digest':'a'*64},{'outcome':'FAIL'}]:
            f.records=[];f.enrollments=[];f.evidence(review_change=change)
            self.assertEqual(f.evaluate().projection['tasks']['T00']['status'],'INELIGIBLE')

    def test_missing_review_enrollment_refuses(self):
        f=self.f;f.evidence();f.enrollments=[]
        self.assertFalse(f.evaluate().projection['evidence'][0]['eligible'])

    def test_terminal_mismatch_unknown_cleanup_and_bool_exit_refuse(self):
        f=self.f
        for change in [{'command_binding':f.subject},{'outcome':'ERROR'},
                       {'cleanup':'unknown'},{'effect_state':'unknown'},
                       {'actual_exit':False},{'actual_exit':None},{'actual_exit':9}]:
            f.records=[];f.enrollments=[];f.evidence(terminal_change=change)
            self.assertFalse(f.evaluate().projection['evidence'][0]['eligible'])

    def test_all_negative_outcomes_retained_and_cannot_close(self):
        f=self.f
        for outcome in ['FAIL','ERROR','UNKNOWN','NOT_RUN','BLOCKED']:f.evidence(outcome=outcome)
        result=f.evaluate();self.assertEqual([e['outcome'] for e in result.projection['evidence']],
                                            ['FAIL','ERROR','UNKNOWN','NOT_RUN','BLOCKED'])
        originals={canonical(b):raw for b,raw in result.originals}
        for b in f.records:self.assertEqual(sha(originals[canonical(b)]),b['sha256'])
        self.assertEqual(result.projection['tasks']['T00']['status'],'INELIGIBLE')

    def test_pass_does_not_overrule_same_scope_negative(self):
        f=self.f;f.evidence(outcome='FAIL');f.evidence()
        out=f.evaluate().projection
        self.assertEqual(out['tasks']['T00']['status'],'INELIGIBLE')
        self.assertIn('CONFLICTED',{c['status'] for c in out['criteria'] if c['task_id']=='T00'})

    def test_current_retention_is_exact_no_replace(self):
        f=self.f;f.evidence(outcome='UNKNOWN');result=f.evaluate();p=f.path/'retained';p.mkdir()
        anchor=RootAnchor('owned',str(p),identity(p.stat()))
        receipt=persist(result,anchor,reader=f.reader(),expected_disclosure=f.last_context,
                        expected_inventory=f.inventory_binding,expected_policy=f.last_policy)
        self.assertEqual(receipt['cleanup'],'retained-owned')
        for b,raw in result.originals:self.assertEqual((p/(b['sha256']+'.original')).read_bytes(),raw)
        with self.assertRaisesRegex(Refusal,'RETENTION_ROOT_NOT_EMPTY'):
            persist(result,anchor,reader=f.reader(),expected_disclosure=f.last_context,
                        expected_inventory=f.inventory_binding,expected_policy=f.last_policy)

    def test_readable_original_without_public_disclosure_selection_refuses(self):
        f=self.f;f.evidence();p=f.policy();c=f.context()
        value=json.loads(f.reader().read(c));value['public_retention_bindings']=[
            b for b in value['public_retention_bindings'] if b!=f.records[0]]
        changed=f.put(value)
        with self.assertRaisesRegex(Refusal,'PUBLIC_RETENTION_NOT_SELECTED'):
            evaluate(f.reader(),f.inventory_binding,p,changed)

    def test_caller_constructed_evaluation_cannot_bypass_public_retention(self):
        f=self.f;f.evidence();result=f.evaluate()
        extra=f.put(b'Unapproved but readable inert marker.',raw=True)
        forged=Evaluation(result.projection,(*result.originals,(extra,f.reader().read(extra))))
        p=f.path/'not-retained';p.mkdir();anchor=RootAnchor('owned',str(p),identity(p.stat()))
        with self.assertRaisesRegex(Refusal,'RETENTION_NOT_AUTHORIZED'):
            persist(forged,anchor,reader=f.reader(),expected_disclosure=f.last_context,
                        expected_inventory=f.inventory_binding,expected_policy=f.last_policy)
        self.assertEqual(list(p.iterdir()),[])
        value=json.loads(f.reader().read(result.projection['context_binding']))
        value['arbitrary_extra_payload']='This must not enter an enclosing-record export exception.'
        malformed=f.put(value)
        with self.assertRaisesRegex(Refusal,'CLOSED_FIELDS'):
            persist(result,anchor,reader=f.reader(),expected_disclosure=malformed,
                    expected_inventory=f.inventory_binding,expected_policy=f.last_policy)
        self.assertEqual(list(p.iterdir()),[])

    def test_historical_closed_selector_and_all_originals_retain(self):
        f=self.f;result=historical(f.reader(),f.history_binding);p=f.path/'history-retained';p.mkdir()
        receipt=persist(result,RootAnchor('owned',str(p),identity(p.stat())),
                        reader=f.reader(),expected_disclosure=f.history_binding)
        self.assertEqual(receipt['result'],'PASS')
        for b,raw in result.originals:self.assertEqual((p/(b['sha256']+'.original')).read_bytes(),raw)

    def test_malformed_public_negative_original_retained_only_when_selected(self):
        f=self.f;b=f.put(b'{bad public fixture JSON',raw=True);f.records.append(b)
        result=f.evaluate();self.assertFalse(result.projection['evidence'][0]['eligible'])
        self.assertIn(b,[x for x,_ in result.originals])

    def test_real_history_preserves_scopes_and_missing_terminal(self):
        f=self.f;result=historical(f.reader(),f.history_binding);records=result.projection['records']
        self.assertFalse(result.projection['current_eligibility_conferred'])
        self.assertEqual([x['historical_status'] for x in records],['complete']*3)
        self.assertFalse(records[0]['runtime_tests_executed'])
        self.assertEqual(records[1]['terminal_accounting'],'unavailable-explicit')
        self.assertEqual(records[2]['terminal_accounting'],'focused31-exit0')
        self.assertIn('future final API/live regression',records[2]['scope'])

    def test_dynamic_invalidation_and_all_original_task_ac_edges(self):
        f=self.f;g=f.put(f.graph());new=f.put({'schema_version':'changed/v1','v':2})
        old=f.put({'schema_version':'lab-invalidation-selection/v1','subjects':[
            {'subject':'code','binding':f.subject},{'subject':'unrelated','binding':f.selection}]})
        changed=f.put({'schema_version':'lab-invalidation-selection/v1','subjects':[
            {'subject':'code','binding':new},{'subject':'unrelated','binding':f.selection}]})
        out=invalidate(f.reader(),f.inventory_binding,g,old,changed)
        self.assertIn('proof',out['stale']);self.assertIn('T30',out['stale']);self.assertIn('AC13',out['stale'])
        self.assertNotIn('unrelated',out['stale'])
        bad=f.graph();bad['edges'].pop(0);b=f.put(bad)
        with self.assertRaisesRegex(Refusal,'MISSING_ORIGINAL_DEPENDENCY'):
            invalidate(f.reader(),f.inventory_binding,b,old,changed)

    def test_unknown_consumer_mapping_invalidates_aggregates(self):
        f=self.f;g=f.put(f.graph(unknown=True));new=f.put({'schema_version':'changed/v1','v':2})
        a=f.put({'schema_version':'lab-invalidation-selection/v1','subjects':[
            {'subject':'code','binding':f.subject},{'subject':'unrelated','binding':f.selection}]})
        b=f.put({'schema_version':'lab-invalidation-selection/v1','subjects':[
            {'subject':'code','binding':new},{'subject':'unrelated','binding':f.selection}]})
        out=invalidate(f.reader(),f.inventory_binding,g,a,b)
        self.assertTrue(out['conservative_unknown_mapping']);self.assertIn('aggregate',out['stale'])
        self.assertEqual(len([s for s in out['stale'] if s.startswith('T')]),36)

    def test_missing_ac_invalidation_node_refuses(self):
        f=self.f;graph=f.graph();graph['nodes']=[n for n in graph['nodes'] if n['id']!='AC13']
        g=f.put(graph)
        with self.assertRaisesRegex(Refusal,'INVALIDATION_AC_COVERAGE'):
            invalidate(f.reader(),f.inventory_binding,g,f.selection,f.selection)

    def test_t24_local_disposition_does_not_close_final_ac(self):
        f=self.f;source=next(o for o in f.inventory.occurrences if o['document_id']=='completion:T24'
            and o['selector'].get('heading')=='Implementation detail / ordered rules'
            and 'final package/privacy/recovery AC05/AC13 clauses' in o['text'])
        acids={o['id']:o['selector']['heading'] for o in f.inventory.occurrences if o['document_id']=='acceptance'}
        for e in f.policies:
            if acids.get(e['occurrence_id']) in {'AC05','AC13'}:
                for d in e['dispositions']:
                    if d['task_id']=='T24':d.update(resolution='deferred',deferred_to='T25')
        for acid in ['AC05','AC13']:
            f.deferrals.append({'source_occurrence_id':source['id'],'from_task':'T24',
                'to_task':'T25','acceptance_id':acid,'scope':'final-package'})
        for task in f.inventory.summary['tasks']:
            if task not in {'T25','T26','T27','T28','T29','T30'}:f.evidence(task=task)
        out=f.evaluate().projection
        self.assertEqual(out['tasks']['T24']['status'],'ELIGIBLE')
        self.assertEqual(out['tasks']['T24']['pending_downstream'],2)
        self.assertEqual(out['tasks']['T25']['status'],'INELIGIBLE')
        self.assertEqual(out['acceptance']['AC05']['status'],'PENDING')
        self.assertEqual(out['acceptance']['AC13']['status'],'PENDING')
        for task in ['T25','T26','T27','T28','T29','T30']:f.evidence(task=task)
        final=f.evaluate().projection
        self.assertEqual(final['tasks']['T30']['status'],'ELIGIBLE')
        self.assertEqual(final['acceptance']['AC05']['status'],'PASS')
        self.assertEqual(final['acceptance']['AC13']['status'],'PASS')
        self.assertEqual(final['tasks']['T24']['pending_downstream'],2)
        self.assertEqual(final['acceptance']['AC05']['resolved_deferrals'][0]['to_task'],'T25')

    def test_arbitrary_done_criterion_deferral_refuses(self):
        f=self.f
        e=next(e for e in f.policies if any(d['task_id']=='T00' and d['resolution']=='required' for d in e['dispositions']))
        e['dispositions'][0].update(resolution='deferred',deferred_to='T25')
        with self.assertRaisesRegex(Refusal,'DEFERRED_OWNER'):f.evaluate()


    def test_t00_contribution_does_not_require_or_close_full_ac13(self):
        f=self.f
        ac=next(o for o in f.inventory.occurrences if o['document_id']=='acceptance'
                and o['selector']['heading']=='AC13')
        scope=[o['id'] for o in f.inventory.occurrences if o['document_id']=='completion:T00'
               and o['role']=='criterion' and o['selector']['heading']=='Done criteria and acceptance evidence']
        entry=next(e for e in f.policies if e['occurrence_id']==ac['id'])
        contribution=next(d for d in entry['dispositions'] if d['task_id']=='T00')
        contribution.update(resolution='contribution',scope_occurrence_ids=scope)
        f.evidence();out=f.evaluate().projection
        self.assertEqual(out['tasks']['T00']['status'],'ELIGIBLE')
        self.assertEqual(out['acceptance']['AC13']['status'],'PENDING')
        own=next(c for c in out['criteria'] if c['occurrence_id']==ac['id'] and c['task_id']=='T00')
        self.assertEqual(own['contribution_scope'],scope)
        self.assertEqual(own['status'],'PASS')

    def test_required_stage_terminal_pairs_are_conjunctive(self):
        f=self.f
        for e in f.policies:
            for d in e['dispositions']:
                if d['task_id']=='T00' and d['resolution']=='required':
                    d.update(allowed_stages=['inert-contract','human-observation'],
                        terminal_kinds=['process','human-observation'],requires_timing=False,
                        required_proofs=[{'stage':'inert-contract','terminal_kind':'process'},
                            {'stage':'human-observation','terminal_kind':'human-observation'}])
        f.evidence()
        partial=f.evaluate().projection
        self.assertEqual(partial['tasks']['T00']['status'],'INELIGIBLE')
        self.assertTrue(any(c['status']=='PARTIAL' for c in partial['criteria'] if c['task_id']=='T00'))
        f.evidence(kind='human-observation',stage='human-observation')
        complete=f.evaluate().projection
        self.assertEqual(complete['tasks']['T00']['status'],'ELIGIBLE')
        self.assertFalse(complete['effect_permission_conferred'])

    def test_human_receipt_does_not_invent_process_exit(self):
        f=self.f
        for e in f.policies:
            for d in e['dispositions']:
                if d['task_id']=='T00' and d['resolution']=='required':
                    d.update(allowed_stages=['human-observation'],terminal_kinds=['human-observation'],
                        requires_timing=False,required_proofs=[{'stage':'human-observation',
                                                              'terminal_kind':'human-observation'}])
        f.evidence(kind='human-observation',stage='human-observation')
        self.assertEqual(f.evaluate().projection['tasks']['T00']['status'],'ELIGIBLE')
        f.records=[];f.enrollments=[]
        f.evidence(kind='human-observation',stage='human-observation',terminal_change={'actual_exit':0})
        out=f.evaluate().projection
        self.assertEqual(out['tasks']['T00']['status'],'INELIGIBLE')
        self.assertEqual(out['evidence'][0]['reason'],'EVIDENCE_REFUSED')

    def test_authenticated_negative_disposition_is_observation_not_permission(self):
        f=self.f
        for e in f.policies:
            for d in e['dispositions']:
                if d['task_id']=='T26' and d['resolution']=='required':
                    d.update(allowed_stages=['authorized-effect'],terminal_kinds=['native-effect'],
                        requires_timing=False,allowed_dispositions=['approve','reject','defer','stop'],
                        required_proofs=[{'stage':'authorized-effect','terminal_kind':'native-effect'}])
        f.evidence(task='T26',kind='native-effect',stage='authorized-effect',disposition='reject')
        out=f.evaluate().projection
        observed=out['evidence'][0]
        self.assertTrue(observed['eligible']);self.assertEqual(observed['observation_disposition'],'reject')
        self.assertFalse(out['effect_permission_conferred'])
        self.assertEqual(out['tasks']['T27']['status'],'INELIGIBLE')
        self.assertEqual(out['acceptance']['AC13']['status'],'PENDING')

    def test_policy_size_bound_refuses_before_any_body_read(self):
        f=self.f
        selected={**f.subject,'size_bytes':32*1024*1024+1}
        f.bindings.append(selected)
        with self.assertRaisesRegex(Refusal,'READ_LIMIT'):
            policy(f.reader(),selected,f.inventory)



    def test_candidate_readiness_before_later_disposition_and_effects(self):
        f=self.f
        for e in f.policies:
            o=next((o for o in f.inventory.occurrences if o['id']==e['occurrence_id']),None)
            if o['document_id']!='acceptance':continue
            for d in e['dispositions']:
                if d['task_id'] in {'T26','T27','T28','T29','T30'}:
                    scope=[x['id'] for x in f.inventory.occurrences if
                        x['document_id']=='completion:'+d['task_id'] and x['role']=='criterion' and
                        x['selector']['heading']=='Done criteria and acceptance evidence']
                    d.update(resolution='contribution',scope_occurrence_ids=scope)
        for task in f.inventory.summary['tasks']:
            if task not in {'T26','T27','T28','T29','T30'}:f.evidence(task=task)
        out=f.evaluate().projection
        self.assertEqual(out['tasks']['T25']['status'],'ELIGIBLE')
        self.assertTrue(all(a['candidate_status']=='PASS' for a in out['acceptance'].values()))
        self.assertEqual(out['acceptance']['AC13']['later_operational_status'],'PENDING')
        self.assertEqual(out['acceptance']['AC01']['later_operational_status'],'NOT_APPLICABLE')
        self.assertFalse(out['effect_permission_conferred'])

    def test_rejected_owner_route_cannot_close_later_effect_tasks(self):
        f=self.f
        for task in f.inventory.summary['tasks']:
            f.evidence(task=task,disposition='reject' if task=='T26' else 'not-applicable')
        out=f.evaluate().projection
        self.assertEqual(out['tasks']['T26']['status'],'ELIGIBLE')
        for task in ['T27','T28','T29','T30']:
            self.assertEqual(out['tasks'][task]['status'],'INELIGIBLE')
        self.assertEqual(out['acceptance']['AC13']['later_operational_status'],'PENDING')



    def test_current_target_and_review_lineage_are_separately_selected(self):
        f=self.f
        initial=f.put({'schema_version':'fixture-initial-bundle/v1','revision':1})
        current=f.put({'schema_version':'fixture-later-target/v1','revision':2})
        review=f.put({'schema_version':'fixture-current-authority-review/v1','initial':initial,'target':current})
        for role,b in [('exact-final-bundle',initial),('current-effect-scope',current),
                       ('current-authority-review',review)]:f.subjects.append({'role':role,'binding':b})
        for e in f.policies:
            for d in e['dispositions']:
                if d['task_id']=='T00' and d['resolution']=='required':
                    d['required_roles']=['code','exact-final-bundle','current-effect-scope','current-authority-review']
        f.evidence();out=f.evaluate().projection
        self.assertNotEqual(initial,current)
        self.assertEqual(out['tasks']['T00']['status'],'ELIGIBLE')
        self.assertFalse(out['effect_permission_conferred'])
        f.records=[];f.enrollments=[]
        wrong=copy.deepcopy(f.subjects)
        next(x for x in wrong if x['role']=='current-effect-scope')['binding']=initial
        f.evidence(change={'subject_bindings':wrong})
        bad=f.evaluate().projection
        self.assertEqual(bad['evidence'][0]['reason'],'EVIDENCE_REFUSED')
        self.assertEqual(bad['tasks']['T00']['status'],'INELIGIBLE')

    def test_valid_negative_propagates_through_contribution_and_ac_phase(self):
        f=self.f
        ac=next(o for o in f.inventory.occurrences if o['document_id']=='acceptance'
                and o['selector']['heading']=='AC13')
        scope=[o['id'] for o in f.inventory.occurrences if o['document_id']=='completion:T00'
               and o['role']=='criterion' and o['selector']['heading']=='Done criteria and acceptance evidence']
        entry=next(e for e in f.policies if e['occurrence_id']==ac['id'])
        next(d for d in entry['dispositions'] if d['task_id']=='T00').update(
            resolution='contribution',scope_occurrence_ids=scope)
        f.evidence(outcome='FAIL');out=f.evaluate().projection
        contribution=next(c for c in out['criteria'] if c['occurrence_id']==ac['id'] and c['task_id']=='T00')
        self.assertEqual(contribution['status'],'CONFLICTED')
        self.assertTrue(contribution['counterevidence'])
        self.assertEqual(out['acceptance']['AC13']['candidate_status'],'FAIL')
        self.assertEqual(out['acceptance']['AC13']['status'],'FAIL')
        self.assertTrue(out['tasks']['T01']['failure_observed'])



    def test_constructed_and_mutated_projection_cannot_export(self):
        f=self.f;result=f.evaluate();p=f.path/'forged-projection';p.mkdir()
        anchor=RootAnchor('owned',str(p),identity(p.stat()))
        forged=Evaluation({'unselected_private_payload':'inert sentinel secret'},())
        with self.assertRaisesRegex(Refusal,'RETENTION_PROJECTION_MISMATCH'):
            persist(forged,anchor,reader=f.reader(),expected_disclosure=f.last_context,
                    expected_inventory=f.inventory_binding,expected_policy=f.last_policy)
        self.assertEqual(list(p.iterdir()),[])
        result.projection['tasks']['T00']['unselected_private_payload']='nested inert sentinel'
        with self.assertRaisesRegex(Refusal,'RETENTION_PROJECTION_MISMATCH'):
            persist(result,anchor,reader=f.reader(),expected_disclosure=f.last_context,
                    expected_inventory=f.inventory_binding,expected_policy=f.last_policy)
        self.assertEqual(list(p.iterdir()),[])

    def test_later_task_pairs_preserve_earlier_record_without_authority_transfer(self):
        f=self.f;initial=f.put({'fixture':'initial ancestry'})
        f.subjects.append({'role':'exact-final-bundle','binding':initial})
        def pair(task):
            target=f.put({'fixture':'current target','task':task})
            reviewed=f.put({'fixture':'independently selected review','target':target,'ancestry':initial})
            return {'task_id':task,'subject_bindings':[{'role':'current-effect-scope','binding':target},
                {'role':'current-authority-review','binding':reviewed}]}
        first=pair('T27');f.task_subjects=[first]
        for e in f.policies:
            for d in e['dispositions']:
                if d['task_id'] in {'T27','T30'} and d['resolution']=='required':
                    d['required_roles']=['code','exact-final-bundle','current-effect-scope','current-authority-review']
        f.evidence(task='T27');first_binding=f.records[0];first_bytes=f.reader().read(first_binding)
        self.assertTrue(f.evaluate().projection['evidence'][0]['eligible'])
        later=pair('T30');f.task_subjects.append(later);f.evidence(task='T30')
        original_records=list(f.records);original_enrollments=list(f.enrollments)
        out=f.evaluate().projection
        self.assertTrue(all(e['eligible'] for e in out['evidence']))
        self.assertEqual(first_bytes,f.reader().read(first_binding))
        self.assertFalse(out['effect_permission_conferred'])
        for role in ['current-effect-scope','current-authority-review']:
            f.records=list(original_records[:1]);f.enrollments=list(original_enrollments[:1])
            wrong=copy.deepcopy(f.subjects)+copy.deepcopy(later['subject_bindings'])
            next(x for x in wrong if x['role']==role)['binding']=next(x['binding'] for x in first['subject_bindings'] if x['role']==role)
            f.evidence(task='T30',change={'subject_bindings':wrong})
            out=f.evaluate().projection
            self.assertTrue(out['evidence'][0]['eligible']);self.assertFalse(out['evidence'][1]['eligible'])
            self.assertEqual(first_bytes,f.reader().read(first_binding))

    def test_task_subject_map_is_closed_and_cannot_override_shared_roles(self):
        f=self.f
        good={'task_id':'T27','subject_bindings':[{'role':'current-effect-scope','binding':f.subject},
              {'role':'current-authority-review','binding':f.selection}]}
        for rows,reason in [([good,good],'TASK_SUBJECT_ID'),
            ([{**good,'task_id':'T26'}],'TASK_SUBJECT_ID'),
            ([{**good,'subject_bindings':[{'role':'source-family','binding':f.subject}]}],'TASK_SUBJECT_OVERRIDE'),
            ([{**good,'subject_bindings':good['subject_bindings'][:1]}],'TASK_SUBJECT_COVERAGE'),
            ([{**good,'unselected_payload':'no export'}],'CLOSED_FIELDS')]:
            f.task_subjects=rows
            with self.assertRaisesRegex(Refusal,reason):f.evaluate()



    def test_not_run_is_incomplete_and_candidate_pending(self):
        f=self.f;f.evidence(outcome='NOT_RUN');out=f.evaluate().projection
        self.assertEqual(out['evidence'][0]['reason'],'INCOMPLETE')
        self.assertIn('INCOMPLETE',{c['status'] for c in out['criteria'] if c['task_id']=='T00'})
        self.assertEqual(out['acceptance']['AC13']['candidate_status'],'PENDING')
        self.assertFalse(out['tasks']['T00']['failure_observed'])

    def test_unknown_same_scope_blocks_pass_without_fabricated_failure(self):
        f=self.f;f.evidence(outcome='UNKNOWN');f.evidence();out=f.evaluate().projection
        self.assertEqual(out['tasks']['T00']['status'],'INELIGIBLE')
        self.assertFalse(out['tasks']['T00']['failure_observed'])
        self.assertEqual(out['acceptance']['AC13']['candidate_status'],'PENDING')
        self.assertIn('INCOMPLETE',{c['status'] for c in out['criteria'] if c['task_id']=='T00'})

    def test_unknown_inert_effect_blocks_same_scope_pass(self):
        f=self.f;f.evidence(terminal_change={'effect_state':'unknown'});f.evidence()
        out=f.evaluate().projection
        self.assertEqual([e['reason'] for e in out['evidence']],['INCOMPLETE','ELIGIBLE'])
        self.assertEqual(out['tasks']['T00']['status'],'INELIGIBLE')
        self.assertFalse(out['tasks']['T00']['failure_observed'])
        self.assertEqual(out['acceptance']['AC13']['candidate_status'],'PENDING')

    def test_known_failure_dominates_same_scope_unknown(self):
        f=self.f;f.evidence(outcome='UNKNOWN');f.evidence(outcome='FAIL');out=f.evaluate().projection
        self.assertEqual([e['reason'] for e in out['evidence']],['INCOMPLETE','KNOWN_FAILURE'])
        self.assertTrue(out['tasks']['T00']['failure_observed'])
        self.assertEqual(out['acceptance']['AC13']['candidate_status'],'FAIL')
        self.assertIn('CONFLICTED',{c['status'] for c in out['criteria'] if c['task_id']=='T00'})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--temp-root',required=True);parser.add_argument('--only',action='append',default=[])
    args=parser.parse_args();TEMP=Path(args.temp_root)
    suite=unittest.TestSuite(IndexTests(name) for name in args.only) if args.only else unittest.defaultTestLoader.loadTestsFromTestCase(IndexTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'schema_version':'lab-case-command-result/v1',
        'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,
        'effect_state':'owned-inert','cleanup':'clean'}))
    sys.exit(0 if result.wasSuccessful() else 1)
