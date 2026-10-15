"""W06 actual lesson application, independent observation and unapplied effect proposal."""
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from lessons import *

BEFORE = "hypothesis['evidence_refs']=[];hypothesis['relation_refs']=[{'relation_kind_ref':'relation.tests-hypothesis','direction':'target','counterpart_kind':'experiment-design','counterpart_ref':'experiment-design:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison'}]"
AFTER = "hypothesis['evidence_refs']=[];hypothesis['relation_refs']=[{'relation_kind_ref':'relation.evidence-bears-on','direction':'target','counterpart_kind':'evidence-set','counterpart_ref':'evidence-set:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison'}]"


def repaired_source(original):
    require(type(original) is bytes and original.decode().count(BEFORE) == 1, 'selected inline-only repair no longer exact')
    require(AFTER in CORRECTED.read_text(), 'independent corrected source no longer confirms inline role')
    output = original.decode().replace(BEFORE,AFTER).encode()
    require(output != original and output.decode().count(AFTER) == 1, 'repair did not produce one exact changed inline declaration')
    return output


class LessonApplicationService:
    def __init__(self, lessons):
        require(isinstance(lessons,LessonService),'trusted lesson service required')
        self.lessons, self.e = lessons, lessons.e
        self.application_ref = None; self.observation_ref = None; self.outcome_ref = None
        self.manifest_ref = None; self.journal_ref = None; self.observed = None

    def apply(self, selection, lesson_ref, *, current_context_reader=None):
        e = self.e
        lesson = self.lessons.selected_for_application(selection,lesson_ref)
        require(self.application_ref is None and self.journal_ref is None and not (e.output/'application-pending.json').exists(),'pending or completed application prohibits redispatch')
        require(selection.context.family == FAMILY and selection.context.source_sha256 == e.sources[OLD], 'application source family/version differs')
        require(self.lessons.rules[lesson_ref].effect == 'inline-only-repair'
            and lesson['payload']['predicted_benefit'] == PREDICTION,
            'selected lesson influence/prediction differs from this closed application implementation')
        if current_context_reader:
            pack = current_context_reader()
            require(pack['head'] == selection.context.source_head and pack['session_id'] == selection.context.session_ref,'current Project/context differs before application')
        original = OLD.read_bytes();require(byte_sha(original) == e.sources[OLD],'selected original source drift')
        self.journal_ref = e.blob('application-pending.json',encoded({'posture':'pending','retry_allowed':False,
            'lesson_ref':lesson_ref,'lesson_sha256':e.records[lesson_ref][1],'selection_ref':selection.original_ref,
            'session_ref':selection.context.session_ref,'source_head':selection.context.source_head,
            'input_source_sha256':byte_sha(original),'predicted_outcome':PREDICTION,'actual_owner_outcome':None}))
        repaired = repaired_source(original)
        source_ref = e.blob('repaired_builder.py',repaired)
        e.check()
        try:
            p = subprocess.run([sys.executable,str(PACKAGE/'learning/probe_child.py'),str(e.output/'repaired_builder.py'),
                str(e.output/'later-prepared-inputs'),byte_sha(repaired)],capture_output=True,timeout=25)
        except subprocess.TimeoutExpired as exc:
            e.blob('application-timeout-stdout.log',exc.stdout or b'')
            e.blob('application-timeout-stderr.log',exc.stderr or b'')
            e.blob('application-timeout.json',encoded({'posture':'inconclusive-timeout','retry_allowed':False,'controlled':True}))
            raise
        require(len(p.stdout)+len(p.stderr) <= e.host.grant.max_output_bytes,'application process output budget exceeded')
        stdout = e.blob('application-stdout.json',p.stdout);stderr = e.blob('application-stderr.log',p.stderr)
        require(p.returncode == 0,'incomplete application probe; preserve pending and inspect, never redispatch')
        result = parse(p.stdout)
        require(result['controlled'] is True and result['source_sha256'] == byte_sha(repaired),'application observation source differs')
        e.check()
        require(byte_sha(OLD.read_bytes()) == e.sources[OLD] and e.original(source_ref) == repaired,'original or repaired source drift')
        self.observed = {'controlled':True,'lesson_ref':lesson_ref,'selection_ref':selection.original_ref,
            'source_head':selection.context.source_head,'session_ref':selection.context.session_ref,'stdout_ref':stdout,'stderr_ref':stderr,
            'result':result,'original_source_unchanged':True,'inline_only_change':True,'returncode':p.returncode,
            'repaired_source_ref':source_ref,'observed_at':utc(e.host.now[0]),'actual_owner_outcome':None}
        self.manifest_ref = e.blob('application-manifest.json',encoded(self.observed))
        action = e.put(e.make('agent-action','later-lesson-application',{
            'action_kind':'apply-exact-controlled-inline-repair','agent_instance_ref':e.host.ref('agent-instance'),
            'assignment_ref':e.host.ref('agent-assignment'),'session_ref':e.host.ref('agent-session'),
            'authority_evidence_refs':[e.host.grant.evidence_ref],'tool_refs':[e.host.ref('tool')],
            'implementation_refs':['implementation:lab-W09:bc3c50170a404b4ba8d8:learning:application-adapter@'+VERSION],
            'input_refs':[lesson_ref,selection.original_ref],'output_refs':[self.manifest_ref,source_ref],
            'posture':'completed','receipt_refs':[self.manifest_ref],'residue_refs':['protocol:W06-no-general-efficacy']},
            ('produces','source','lesson-application','lesson-application:lab-W09:bc3c50170a404b4ba8d8:learning:later-inline-repair@'+VERSION)))
        self.application_ref = e.put(e.make('lesson-application','later-inline-repair',{
            'lesson_revision_ref':lesson_ref,'session_ref':selection.context.session_ref,
            'application_posture':'applied-in-controlled-later-case','applicability_assessment_ref':selection.original_ref,
            'intended_influence':lesson['payload']['predicted_benefit'],'conflict_refs':[],'override_refs':[]},
            ('applies-lesson','source','operational-lesson',lesson_ref)))
        self.observation_ref = e.put(e.make('operational-observation','later-preparation-outcome',{
            'action_ref':action,'datum':'Original later preparation manifest '+self.manifest_ref,'evidence_refs':[self.manifest_ref],
            'interpretation_posture':'uninterpreted-original-process-results','method_ref':'protocol:W06-inline-only-source-repair@1',
            'observed_at':self.observed['observed_at'],'project_ref':SCOPE},
            ('evidence-bears-on','source','lesson-outcome-assessment','lesson-outcome-assessment:lab-W09:bc3c50170a404b4ba8d8:learning:later-outcome@'+VERSION)))
        e.edge('application-lesson','applies-lesson',self.application_ref,lesson_ref,{
            'lesson_revision_ref':lesson_ref,'application_posture':'applied-in-controlled-later-case',
            'applicability_assessment_ref':selection.original_ref,'instruction_precedence':'current-explicit-instruction-and-host-permission'})
        e.edge('action-application','produces',action,self.application_ref,{'action_receipt_ref':self.manifest_ref,
            'production_role':'observed-actual-application','output_posture':'candidate-unadmitted'})
        e.blob('application-completed.json',encoded({'posture':'completed','manifest_ref':self.manifest_ref,'retry_allowed':False,
            'application_ref':self.application_ref,'outcome_assessed':False,'actual_owner_outcome':None}))
        return self.application_ref

    def assess(self, *, requested_disposition=None, claimed_benefit=None):
        e = self.e;e.check()
        require(self.application_ref is not None and self.observed is not None and self.outcome_ref is None,'actual unassessed application required')
        application = e.get(self.application_ref,'lesson-application')['payload']
        manifest = parse(e.original(self.manifest_ref))
        require(manifest == self.observed and application['lesson_revision_ref'] == manifest['lesson_ref'],'assessment original application evidence differs')
        result = manifest['result']
        disposition = ('supported-for-this-controlled-case' if result['preparation_posture']=='completed' and result['validated_records']==13
            and manifest['original_source_unchanged'] and manifest['inline_only_change'] else
            'not-supported-for-this-controlled-case' if result['preparation_posture']=='rejected' else 'inconclusive')
        require(requested_disposition is None or requested_disposition == disposition,'outcome disposition cannot be supplied independently of observations')
        require(claimed_benefit is None,'one application cannot establish general or causal benefit')
        source_counterevidence = self.e.manifest_ref
        self.outcome_ref = e.put(e.make('lesson-outcome-assessment','later-outcome',{
            'lesson_application_ref':self.application_ref,'predicted_outcome':PREDICTION,
            'observed_outcome':result['preparation_posture']+'; validated records='+str(result['validated_records'])+'; original unchanged; inline-only repair.',
            'evidence_refs':[self.observation_ref,self.manifest_ref],'counterevidence_refs':[source_counterevidence],
            'disposition':disposition,'causal_claim_ceiling':CAUSAL_CEILING},
            ('evaluates','source','lesson-application',self.application_ref)))
        e.edge('outcome-application','evaluates',self.outcome_ref,self.application_ref,{
            'evaluation_role':'prediction-versus-original-later-observation','evaluation_purpose':'bounded-application-outcome'})
        e.edge('observation-outcome','evidence-bears-on',self.observation_ref,self.outcome_ref,{'polarity':disposition})
        return self.outcome_ref

    def propose_improvement(self):
        e = self.e;e.check();require(self.outcome_ref is not None,'assessed actual application required before proposal')
        lesson = e.get(self.application_ref)['payload']['lesson_revision_ref']
        signal = e.put(e.make('improvement-signal','preparation-preflight-signal',{
            'source_refs':[self.observation_ref,self.outcome_ref],'signal_statement':'Consider an explicit preflight for carrier inline roles; one later repair succeeded and broader effectiveness remains unproven.',
            'deduplication_key':'W06/hypothesis-inline-role-preflight','observed_window':self.observed['observed_at'],
            'evidence_posture':'candidate-one-controlled-case','routing_owner_ref':'protocol:R08-final-owner-route',
            'improvement_target_ref':'improvement-target:lab-W09:bc3c50170a404b4ba8d8:learning:preflight-target@'+VERSION},
            ('derives-from','source','operational-observation',self.observation_ref)))
        target = e.put(e.make('improvement-target','preflight-target',{
            'target_statement':'Review a shared carrier-inline preflight before broadening lesson applicability or treating it as effective.',
            'basis_refs':[lesson,self.outcome_ref,signal],'affected_scope_refs':[SCOPE],
            'success_measure_refs':['protocol:W06-later-comparable-preparation-outcomes'],'research_route_ref':'protocol:W04-future-bounded-comparisons',
            'priority_posture':'candidate-owner-review-required'},('derives-from','source','lesson-outcome-assessment',self.outcome_ref)))
        effect = e.put(e.make('effect','proposed-preflight-work',{
            'effect_kind':'proposed-improvement-work','subject_ref':target,'intended_state':'review-for-future-bounded-implementation',
            'effective_when':'only a future exact owner-authorized Decision and declared scope','verification_refs':[self.outcome_ref,self.manifest_ref]},
            ('declares-effect-on','target','decision','protocol:R08-future-unresolved-owner-decision')))
        e.edge('signal-observation','derives-from',signal,self.observation_ref,{'derivation_role':'actual-later-observation'})
        e.edge('target-outcome','derives-from',target,self.outcome_ref,{'derivation_role':'explicit-unapplied-improvement-proposal'})
        e.blob('unapplied-effect.json',encoded({'effect_ref':effect,'target_ref':target,'applied':False,'actual_owner_outcome':None,
            'unresolved_decision_ref':'protocol:R08-future-unresolved-owner-decision','lesson_promoted':False,'general_benefit_established':False}))
        return signal,target,effect
