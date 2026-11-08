"""Bind the captured rule proposal to typed profiles and complete obligations."""
from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'evolution/impact'))
import readiness as r
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'protected'))
import lineage_checker as lineage
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'independence'))
# Avoid importing the unrelated evolution/models witness_checker under the same name.
import importlib.util
spec=importlib.util.spec_from_file_location('inference_model_checker',Path(__file__).resolve().parents[1]/'independence/witness_checker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
c=lineage.c;f=c.f;s=c.s;d=c.d;g=r.g
BASE=Path(__file__).resolve().parent
RULE_TARGETS={'typed-rule-profile':'Inference.Captured.theory_valid',
    'derivation-soundness':'Inference.RequiredDerivationSoundness','closure-adequacy':'Inference.RequiredClosureAdequacy',
    'protected-lineage':'Inference.RequiredProtectedLineage','independence-witnesses':'Inference.RequiredCountermodelSoundness',
    'rule-extension-compatibility':'Inference.Extension.RequiredRuleConservativity'}
KINDS={'baseline-current':'current-baseline','computed-classification':'computed-diff','source-profile-projection':'source-projection',
    'carrier-projection':'carrier-projection','selected-data-compatibility':'checked-selected-data',
    'invariant-preservation':'general-theorem','conservative-expansion':'general-theorem','inhabited-model':'checked-model-witness',
    'protected-root-independence':'general-semantic-theorem','typed-rule-profile':'kernel-checked-typed-profile',
    'derivation-soundness':'general-theorem','closure-adequacy':'general-theorem','protected-lineage':'general-theorem',
    'independence-witnesses':'checked-model-witness','rule-extension-compatibility':'general-theorem'}


def capture(proposal):
    required=g.generate(proposal);classification=required['classification']
    s.require(classification['profile']=='rule-only-extension','unsupported mixed/change profile for this rule integration')
    s.require(proposal['before']==g.c.baseline(),'proposal is not bound to the current captured registry/graph/rule baseline')
    s.require(proposal['after']['registry']==proposal['before']['registry'] and proposal['after']['graph']==proposal['before']['graph'],'rule-only profile changes registry/graph meaning')
    s.require(not proposal['before']['rules'],'selected old-body fresh-head profile requires the captured empty-rule baseline')
    g.source_projection(proposal)
    resolved=g.c.r.resolve(proposal['before']['graph'],proposal['before']['registry'])
    s.require(resolved['status']=='supported' and not resolved['errors'],'unresolved graph reference semantics')
    graph=proposal['before']['graph'];s.require(not graph['admission_roots'],'mapping existing graph roots requires separately supplied exact root receipts; do not fabricate them')
    domain=[{'kind':'reference',**n['ref']} for n in graph['nodes']]
    domain += [{'kind':'effect','value':'admission'},{'kind':'scope','value':'static'},{'kind':'epoch','value':0}]
    facts=[];projection=[]
    for edge in graph['assertions']:
        if edge['kind']!='relation.conforms-to':continue
        fact={'predicate':'Conforms','version':'v1','terms':[{'kind':'reference',**edge['source']}]}
        if fact not in facts:facts.append(fact)
        projection.append({'assertion_id':edge['id'],'kind_version':edge['kind_version'],'source':edge['source'],
                           'target':edge['target'],'qualifiers':edge['qualifiers'],'projected_fact':fact})
    before={'schema':'relational.inference-input/v1','snapshot_epoch':0,'domain':domain,'predicates':deepcopy(f.CORE),
        'rules':deepcopy(proposal['before']['rules']),'facts':facts,'roots':[],'root_assessments':[]}
    after=deepcopy(before);after['predicates'].append({'id':'ReviewSignal','version':'v1','sorts':['reference'],'role':'ordinary'})
    after['rules']=deepcopy(proposal['after']['rules'])
    old=f.normalize(before);new=f.normalize(after)
    # These profile conditions support the generic conservativity construction.
    old_keys=[{k:p[k] for k in ['id','version','hash']} for p in old['predicates']]
    for rule in new['rules']:
        s.require(rule['head']['predicate'] not in old_keys,'an old-predicate head requires separate preservation/conservativity evidence')
        s.require(all(p['predicate'] in old_keys for p in rule['body']),'fresh recursive body requires another model expansion profile')
    s.require(facts,'named selected use case has no conformance facts')
    return {'proposal_identity':required['proposal_identity'],'before_input':before,'after_input':after,
        'before_normal':old,'after_normal':new,'conformance_projection':projection,'reference_validation':resolved,
        'claim_ceiling':'Conforms(subjectVersion) is a unary existential projection of captured, validated F0 conformance assertions, not the full relation meaning.',
        'epoch_interpretation':'0 is the frozen candidate inference context epoch; no live authority epoch or admission is claimed.'}


def validate_submission(proposal,submission,normal_identity):
    required=g.validate_submission(proposal,submission);entries={o['name']:o for o in submission['obligations']};missing=[]
    for obligation in required['obligations']:
        entry=entries[obligation['name']]
        s.require(entry.get('proposal_identity')==required['proposal_identity'] and entry.get('normal_form_identity')==normal_identity,'obligation evidence belongs to another proposal or inference snapshot')
        if entry.get('status')!='discharged' or not entry.get('evidence'):missing.append(obligation);continue
        s.require(entry.get('evidence_kind')==KINDS[obligation['name']],'evidence method does not discharge this obligation')
        target={**r.TARGETS,**RULE_TARGETS}.get(obligation['name'])
        if target:s.require(entry.get('required_statement')==target,'required statement weakened or substituted')
        for binding in entry['evidence']:s.check_binding(binding)
    return {'status':'pending' if missing else 'inference-obligations-discharged-pending-G3',
        'proposal_identity':required['proposal_identity'],'normal_form_identity':normal_identity,
        'missing_hard_obligations':missing,'required':required,'authority_effect':'none',
        'public_submission_policy':'Aggregation of freshly checked author-pipeline evidence; independent untrusted proof/bundle verification remains R02/R03.'}


def conservativity_source(captured):
    old=captured['before_normal'];new=captured['after_normal']
    fresh=new['predicates'][len(old['predicates']):]
    def pred(p):return '{ key := '+c.c.key_lean(p)+', sorts := '+d.rows(p['sorts'],lambda sort:'.'+sort)+', role := .ordinary }'
    source='import InferenceFixture\nimport RuleConservativity\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Inference.Extension.Captured\n'
    source+='def before : Theory := '+c.c.theory_lean(old)+'\ndef after : Theory := Inference.Captured.theory\n'
    source+='theorem before_valid : TheoryValid before := by decide\n'
    source+='def actual : FreshHeadExtension before after := { fresh := '+d.rows(fresh,pred)+', added := groundInstances after, domain_same := by decide, predicates_append := by decide, roots_same := by decide, fresh_keys := by decide, cover := by decide, old_bodies := by decide, added_bodies := by decide, fresh_heads := by decide, head_typed := by decide, head_roots := by decide }\n'
    source+='theorem actual_every_base_model_expands : ∀ M, SemanticModel before Inference.Captured.facts M → ∃ expandedModel, SemanticModel after Inference.Captured.facts expandedModel ∧ ∀ a, Old before a → (expandedModel a ↔ M a) := audited_rule_conservativity before after actual Inference.Captured.facts\n'
    source+='#print axioms before_valid\n#print axioms actual_every_base_model_expands\nend Inference.Extension.Captured\n'
    return source


def registry_identity_source():
    return '''import RegistrySnapshot
import Preservation
import ConservativeExpansion
namespace Registry.RuleIdentity
def actual : Evolution.FreshExtension Snapshot.captured Snapshot.captured :=
  { added := [], nodes_equal := rfl, kinds_append := by simp, fresh_ids := by simp,
    base_valid := Snapshot.valid_snapshot, expanded_valid := Snapshot.valid_snapshot }
theorem actual_registry_preservation : ∀ g, Evolution.OldLanguage Snapshot.captured g →
    (Inv Snapshot.captured g ↔ Inv Snapshot.captured g) := Evolution.preserves_old_language actual
theorem actual_registry_conservativity : ∀ model, Inv Snapshot.captured model →
    ∃ expansion, Inv Snapshot.captured expansion ∧ Models.oldReduct Snapshot.captured expansion = model :=
  Models.expands_every_base_model Snapshot.captured [] (by simpa [Models.expandedTheory] using Snapshot.valid_snapshot)
theorem required_preservation : Evolution.RequiredPreservation := Evolution.audited_preservation
theorem required_conservativity : Models.RequiredConservativity := Models.audited_conservativity
#print axioms actual_registry_preservation
#print axioms actual_registry_conservativity
#print axioms required_preservation
#print axioms required_conservativity
end Registry.RuleIdentity
'''


def dependency_manifest(proposal):
    captured=capture(proposal);paths=set()
    # Bind stable accepted exports, not the mutable plan status or historical
    # context-pack hashes. The frozen C06 manifest supplies its full baseline.
    pending=[]
    for task_id in ['C03','C06','E02','E05','I01','I02','I03','I04','I05']:
        task=s.task(task_id);s.require(task['status']=='accepted','unaccepted inference dependency: '+task_id)
        binding=task['validation']['acceptance_ref'];s.check_binding(binding);pending.append(s.ROOT/binding['path'])
    while pending:
        path=Path(pending.pop()).resolve()
        if path in paths:continue
        paths.add(path)
        if path.suffix=='.json':
            document=s.read(path)
            if document.get('schema')=='relational.task-acceptance/v1':
                for b in document['artifacts']+document['dependency_bindings']:s.check_binding(b);pending.append(s.ROOT/b['path'])
    for name in ['integration.py','RuleConservativity.lean','StatementAudit.lean','run_integration.py',
                 'CapturedRuleConservativity.lean','RegistryIdentity.lean','InferenceFixture.lean',
                 'ActualClosure.lean','ActualLineage.lean','ActualCountermodel.lean']:
        paths.add(BASE/name)
    paths.add(s.BASE/'evolution/proposals/rule-change-proposal.json')
    sys.path.insert(0,str(s.BASE/'replay'));import replay_engine as replay
    legacy=s.read(s.BASE/'replay/dependency-manifest.json');replay.verify(legacy)
    manifest={'schema':'relational.rule-replay-dependencies/v1','proposal_identity':captured['proposal_identity'],
        'before_normal_identity':captured['before_normal']['normal_form_identity'],
        'after_normal_identity':captured['after_normal']['normal_form_identity'],
        'baseline_dependency_identity':legacy['dependency_identity'],
        'bindings':[s.binding(path) for path in sorted(paths)],'authority_effect':'none',
        'policy':'Full identity recheck; timestamps cannot repair changed rule/theory/proof/source dependencies.'}
    manifest['dependency_identity']=g.c.identity(manifest)
    return manifest


def verify_dependencies(proposal,bound,executed_at=None):
    s.require(bound==dependency_manifest(proposal),'rule/theory/proof dependency manifest stale, omitted or scope-mismatched')
    return True
