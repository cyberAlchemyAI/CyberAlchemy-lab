"""Elaborate all inherited conclusion arguments into explicit typed anchor plans.

Plans describe participants and independent existential selections. They do not
assert the selected conclusion, authenticate a catalog, or prove a countermodel.
The consolidated meaning packet stays immutable; this is a proposed supplement.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
N01=HERE.parents[1]
SUCCESSOR=N01.parents[1]
ROOT=SUCCESSOR.parents[5]
BATCH=N01/'batch-review'
REVISION='v5-conclusion-anchor-contracts-2026-10-11-1'
SORTS={'RevisionRef':'ref','Frame':'frame','Epoch':'epoch','EffectCode':'effect','OwnedActionSubjectUniverse':'universe','TypedValue':'value','ResultCode':'result','SemanticWorld':'world'}

def read(path):return json.loads(path.read_text())
def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def lean_string(value):return json.dumps(value,ensure_ascii=False)

def source():return {'tag':'source','sort':'ref'}
def target():return {'tag':'target','sort':'ref'}
def field(name,sort='ref'):return {'tag':'witness','name':name,'sort':sort}
def frame(name,sort='ref'):return {'tag':'frame','name':name,'sort':sort}
def variable(name,sort):return {'tag':'variable','name':name,'sort':sort}


class Context:
    def __init__(self,definition,pair):
        self.definition=definition;self.unit=definition['unit'];self.pair=pair
        self.binders=[];self.constraints=[]
    def extra(self,name,sort,domain,selection,joins):
        assert name not in {b['name'] for b in self.binders}
        # Domain is a typed independent catalog; this selection has no asserted
        # truth bit and does not imply its conclusion is admissible or true.
        self.binders.append({'name':name,'sort':sort,'domain':domain,'selection_role':selection,'joins':joins,'domain_authenticity_proved':False})
        return variable(name,sort)
    def focus(self):
        return target() if self.unit in {'K03','K05','K09','K12','K17','K18','K19','K22','K25','K29','K30','K34','K35'} else source()
    def actor(self,name):
        if self.unit in {'K00','K06','K29'} or (self.unit=='K22' and self.pair['source_kind']=='agent-instance'):
            return source()
        basis=field('sessionOrAction') if self.unit=='K04' else field('control') if self.unit=='K13' else source()
        return self.extra(name,'ref','accountable-participants','Independently declared accountable actor for this subject/envelope; not an inferred grant',{'subject':basis,'scope':frame('scope')})
    def operation(self,name):
        if self.unit in {'K30','K34'}:return source()
        if self.unit=='K29':return target()
        basis=field('delegation') if self.unit=='K00' else field('sessionOrAction') if self.unit=='K04' else field('control') if self.unit=='K13' else source()
        return self.extra(name,'ref','operation-targets','Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution',{'subject':basis,'scope':frame('scope')})
    def proposition(self,name):
        if self.unit=='K18':return field('proposition')
        if self.unit=='K37':
            return self.extra(name,'ref','proposition-selectors','Exact interpreted proposition carried by the targeted Hypothesis revision',{'carrier':target(),'scope':frame('scope')})
        if self.unit=='K16' and self.pair['source_kind']=='finding':
            return self.extra(name,'ref','proposition-selectors','Exact proposed-answer statement carried by this Finding for this Inquiry',{'carrier':source(),'inquiry':target(),'scope':frame('scope')})
        carrier=target() if self.unit in {'K09','K17','K19','K32'} else source()
        return self.extra(name,'ref','proposition-selectors','Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector',{'carrier':carrier,'scope':frame('scope')})
    def included_source(self,name):
        if self.unit in {'K11','K20'}:
            view=target() if self.unit=='K11' else source()
            return self.extra(name,'ref','view-lineage','Exact included source revision of this immutable view, excluding omitted material',{'view':view,'scope':frame('scope')})
        if self.unit=='K33':
            return self.extra(name,'ref','context-source-boundary','Exact source revision selected by the requested Context boundary',{'context':target(),'scope':frame('scope')})
        return target() if self.unit=='K19' else source()


def fixed_parameters(c,label):
    """No generic fallback: every inherited conclusion label has a case."""
    k=c.unit;s=source();t=target();scope=frame('scope');f=frame('frame','frame')
    if label in {'identity-equivalence','identity','identity-equality','endpoint-identity-collapse','identity-merge'}:
        return {'source':s,'target':t}
    if label in {'authority-transfer','source-authority-transfer'}:
        if label=='source-authority-transfer':return {'source':t,'derived':s,'boundary':c.extra('boundary','ref','authority-boundaries','Exact boundary relevant to the source/derived authority transfer',{'source':t,'derived':s,'scope':scope})}
        # Ownership and authority do not follow correspondence/lineage direction
        # automatically. This exact directional transfer is the proposed target.
        return {'from':t if k in {'K08','K28','K36'} else s,'to':s if k in {'K08','K28','K36'} else t,'scope':scope,'frame':f}
    if label=='ownership-transfer':
        artifact=c.extra('artifact','ref','owned-artifacts','An exact governed artifact in the represented Principal envelope',{'principal':t,'scope':scope}) if k=='K00' else s
        return {'artifact':artifact}
    if label=='unrestricted-authority':return {'actor':s,'universe':frame('ownedUniverse','universe'),'frame':f}
    if label in {'resolution','improvement','priority'}:return {'target':t}
    if label in {'authority','permission','authorization','permission-grant'}:
        holder_key='actor' if label in {'permission','permission-grant'} else 'holder'
        operation_key='action' if label=='authority' else 'operation'
        return {holder_key:c.actor(holder_key),operation_key:c.operation(operation_key),'scope':scope,**({'frame':f} if label!='permission-grant' else {})}
    if label=='satisfaction':return {'intent':t}
    if label=='completion':return {'work':s,'frame':f}
    if label=='membership':return {'member':s,'container':t if k=='K12' and c.pair['target_kind']=='product' else c.extra('container','ref','membership-targets','Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container',{'member':s,'scope':scope})}
    if label=='cause':
        outcome=t if k in {'K03','K34'} else s
        cause=s if k=='K03' else c.extra('cause','ref','causal-participants','Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention',{'outcome':outcome,'scope':scope})
        return {'cause':cause,'outcome':outcome}
    if label in {'severity','blame'}:return {'occurrence':t if k=='K34' else s}
    if label=='ownership':
        artifact=t
        owner=s if k=='K29' else c.extra('owner','ref','ownership-participants','Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred',{'artifact':artifact,'scope':scope})
        return {'owner':owner,'artifact':artifact}
    if label in {'compliance','benefit'}:return {'application':s,'frame':f}
    if label=='method-use':return {'subject':field('sessionOrAction')}
    if label=='private-attribute-inference':return {'subject':t}
    if label=='team-membership':return {'assignee':s}
    if label=='conformance':return {'subject':s,'target':t,'scope':scope,'frame':f}
    if label=='runtime-effectiveness':return {'implementation':s}
    if label=='admission':return {'endpoint':t if k in {'K18','K29','K30'} else s}
    if label=='suspension':return {'subject':t}
    if label=='reversal':
        decision=t if c.pair['target_kind']=='decision' else c.extra('decision','ref','selected-decisions','Exact independently selected earlier decision about the challenged target',{'target':t,'scope':scope})
        return {'decision':decision}
    if label=='contradiction-proof':return {'theory':frame('theory'),'claim':c.proposition('claim')}
    if label=='runtime-conformance':return {'subject':s,'contract':t if c.pair['target_kind']=='contract' else c.extra('contract','ref','runtime-contracts','Exact independently owned live-runtime contract associated with the conformance subject/target',{'subject':s,'target':t,'scope':scope}),'frame':f}
    if label=='effectiveness':return {'subject':field('control') if k=='K13' else s,'frame':f}
    if label=='currentness':return {'source':c.included_source('source'),'now':frame('epoch','epoch'),'timeDomain':frame('timeDomain')}
    if label=='source-authority':return {'source':c.included_source('source')}
    if label=='memory-ownership':return {'holder':s,'memory':t}
    if label=='request-fulfillment':return {'view':t,'frame':f}
    if label=='realization':return {'subject':s,'target':t}
    if label=='evaluation-result':return {'evaluation':c.extra('evaluation','ref','evaluation-targets','Independent evaluation associated with this intended contribution',{'activity':s,'objective':t,'scope':scope})}
    if label=='product-value':
        product=t if c.pair['target_kind']=='product' else s if c.pair['source_kind']=='product' else c.extra('product','ref','product-associations','Exact independently associated Product; capability, thesis and goal are not relabeled as a Product',{'subject':c.focus(),'scope':scope})
        return {'product':product}
    if label in {'installation','execution'}:return {'control':field('control')}
    if label in {'effect-execution','cross-effect-inference'}:
        if k=='K14':return {'decision':s,'target':t,('declared' if label=='cross-effect-inference' else 'effect'):field('effect','effect')}
        decision=c.extra('decision','ref','selected-decisions','Exact independently selected effect decision about this declared authority subject',{'declarer':s,'target':t,'scope':scope})
        return {'decision':decision,'target':t}
    if label=='runtime-success':return {'operation':c.extra('operation','ref','operation-targets','Independently specified runtime operation implementing this declaration; declaration is not execution',{'decision':s,'target':t,'scope':scope})}
    if label=='finding-acceptance':
        finding=s if c.pair['source_kind']=='finding' else c.extra('finding','ref','research-outputs','Exact Finding independently recorded as an output of this inquiry activity',{'activity':s,'inquiry':t,'scope':scope})
        return {'finding':finding,'frame':f}
    if label in {'support','contradiction','evidence-support'}:
        if k=='K16' and c.pair['source_kind']=='finding':evidence=s
        else:evidence=c.extra('evidence','ref','evidence-carriers','Exact evidence independently associated with this evaluated/tested/realized/answer subject',{'subject':s,'target':t,'scope':scope})
        return {'evidence':evidence,'claim':c.proposition('claim'),'policy':frame('evidencePolicy')}
    if label=='inquiry-completion':return {'inquiry':t,'frame':f}
    if label=='adoption':return {'endpoint':s}
    if label=='claim-acceptance':return {'claim':field('proposition'),'frame':f}
    if label=='decision':return {'decision':c.extra('decision','ref','selected-decisions','Exact independent decision concerning this target proposition',{'claim':field('proposition'),'scope':scope})}
    if label=='truth':return {'claim':c.proposition('claim')}
    if label=='context-mutation':
        context=t if k=='K33' else c.extra('context','ref','view-contexts','Exact Context revision referenced by this fulfilled Context View and Request',{'view':s,'request':t,'scope':scope})
        return {'context':context}
    if label=='successful-performance':
        agent=s if c.pair['source_kind']=='agent-instance' else c.extra('agent','ref','profile-instances','Exact Agent Instance independently configured by this Agent Profile; a profile is not relabeled as its performing instance',{'profile':s,'capability':t,'scope':scope})
        return {'agent':agent,'capability':t}
    if label=='new-authorization':
        return {'before':c.extra('before','ref','captured-state-snapshots','Exact captured prior state of this authorized transaction',{'transaction':s,'scope':scope}), 'after':c.extra('after','ref','captured-state-snapshots','Exact captured final applied state of this same transaction',{'transaction':s,'output':t,'scope':scope})}
    if label=='semantic-correctness':return {'output':t}
    if label=='runtime-activation':return {'implementation':c.extra('implementation','ref','runtime-targets','Exact runtime implementation independently associated with this applied bundle; a generated output/state/history is not itself an Implementation',{'transaction':s,'output':t,'scope':scope})}
    if label=='external-effect':return {'operation':s}
    if label=='contribution':
        objective=t if c.pair['target_kind']=='product' else c.extra('objective','ref','contribution-targets','Exact Product or Goal independently associated with this membership record',{'member':s,'container':t,'scope':scope})
        return {'activity':s,'objective':objective,'scope':scope}
    if label=='assignment':
        responsibility=t if c.pair['target_kind']=='role' else c.extra('responsibility','ref','assignment-targets','Exact Responsibility independently associated with this member/container',{'assignee':s,'container':t,'scope':scope})
        if c.pair['target_kind']=='role':
            responsibility=c.extra('responsibility','ref','role-responsibilities','Exact Responsibility within this Role; a Role is not substituted for a Responsibility',{'role':t,'scope':scope})
        assignee=s if c.pair['source_kind'] in {'agent-instance','person-reference','team'} else c.extra('assignee','ref','accountable-participants','Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor',{'member':s,'container':t,'scope':scope})
        return {'assignee':assignee,'responsibility':responsibility}
    if label=='recovery':return {'occurrence':s,'envelope':t}
    if label=='derivation':return {'derived':s,'source':t}
    if label=='successor':return {'successor':s,'predecessor':t}
    if label=='approval':return {'operation':t,'frame':f}
    if label=='successful-effect':return {'action':t}
    if label=='acceptance':return {'subject':t,'frame':f}
    if label=='correctness':return {'output':t}
    if label=='authority-effect':return {'target':t}
    if label=='capability':return {'agent':s}
    if label=='identity-continuity':return {'instance':s}
    if label in {'recovery-success','closure'}:
        incident=t if c.pair['target_kind']=='incident' else c.extra('incident','ref','incident-occurrence-membership','Exact Incident independently containing this Failure Occurrence; the occurrence is not relabeled as an Incident',{'occurrence':t,'action':s,'scope':scope})
        return {'action':s,'incident':incident} if label=='recovery-success' else {'incident':incident,'frame':f}
    if label=='claim-authentication':
        claim=s if c.pair['source_kind']=='authority-claim' else c.extra('claim','ref','boundary-claims','Exact Authority Claim independently associated with this Authority Boundary',{'boundary':s,'subject':t,'scope':scope})
        return {'claim':claim}
    if label=='automatic-supersession':return {'successor':s,'predecessor':t}
    if label=='successful-execution':return {'design':s}
    if label=='validation':return {'subject':s,'specification':t}
    if label=='achievement':return {'subject':s,'frame':f}
    if label=='automatic-failure-confirmation':return {'occurrence':s}
    raise AssertionError(('missing explicit conclusion case',k,label))


# Every remaining typed parameter names a particular independent catalog role.
# No generic "extra witness" or conclusion-validity Boolean is used.
EXTRAS={
 'owner':('review-owners','Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner'),
 'identityModel':('identity-models','Independent governed identity interpretation for these exact endpoint participants'),
 'transition':('state-transitions','Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application'),
 'beforeOwner':('ownership-participants','Exact prior owner associated with this artifact and prior captured state'),
 'afterOwner':('ownership-participants','Exact proposed/final owner associated with this artifact and transition context'),
 'resolution':('resolution-records','Completed resolution candidate for this exact target under its owned criteria'),
 'criteria':('criterion-sets','Exact complete independently owned criterion-set revision for these target/operation participants'),
 'before':('measurement-snapshots','Exact baseline observation/state revision for this target under the selected metric policy'),
 'after':('measurement-snapshots','Exact comparison observation/state revision for this same target under that metric policy'),
 'metric':('metric-definitions','Exact independently owned outcome/benefit/improvement metric for these participants'),
 'queue':('work-queues','Exact owned work queue containing this target'),
 'orderingPolicy':('ordering-policies','Exact owned ordering policy for the selected queue/target'),
 'tests':('criterion-sets','Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test'),
 'assessment':('assessment-candidates','Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates'),
 'requirements':('criterion-sets','Exact complete owned work requirements for this selected work subject'),
 'record':('relation-records','Separate independently supplied record for this named conclusion relationship'),
 'causalModel':('causal-models','Exact independently owned causal interpretation joining the candidate cause and outcome'),
 'severityPolicy':('severity-policies','Exact independently owned severity grading policy for this occurrence/incident'),
 'actor':('accountable-participants','Exact independently assessed actor associated with this occurrence; timing does not identify blame'),
 'instruction':('instruction-origins','Exact applicable instruction origin for this lesson application, retaining precedence and conflicts'),
 'baseline':('measurement-snapshots','Exact independently owned comparison baseline for this lesson application and metric'),
 'method':('method-targets','Exact Method specification independently employed by this session/action; the lesson is not substituted for it'),
 'useRecord':('method-use-records','Separate exact method-employment record joining subject and method'),
 'attribute':('private-attribute-definitions','Exact private attribute definition concerning this correspondence target'),
 'value':('typed-attribute-values','Independently supplied typed value for that subject and attribute; assertion content alone does not establish it'),
 'provenance':('provenance-records','Exact independent provenance candidate for the selected subject/attribute/value'),
 'team':('team-membership-targets','Exact Team independently associated with this assignee; assignment does not add membership'),
 'objective':('objective-definitions','Exact independently owned outcome/objective of the named subject/operation'),
 'decision':('decision-candidates','Separate independently captured decision candidate about the named governed subject'),
 'state':('captured-state-snapshots','Exact state revision relevant to this admission candidate'),
 'reversal':('reversal-records','Separate reversal candidate of the exact earlier selected decision'),
 'proof':('proof-artifacts','Exact proof artifact of the independently specified statement; selection does not establish validity'),
 'execution':('execution-observations','Exact actual-execution candidate trace for the named operation/design/subject'),
 'observedHead':('live-source-observations','Exact independently observed source-head revision at the requested live epoch and time domain'),
 'boundary':('authority-boundaries','Exact independent governance boundary recognizing the named source/holder'),
 'admissionOrGrant':('admission-or-grant-records','Separate actual admission/grant candidate for that source and authority boundary'),
 'ownershipRecord':('ownership-records','Separate exact ownership record joining holder and memory/artifact'),
 'request':('view-requests','Exact Context Request independently referenced by this view; consumption alone does not fulfill it'),
 'witness':('realization-witnesses','Independent exact instantiation/execution witness for these realization participants'),
 'result':('evaluation-results','Independent typed result associated with this exact evaluation; targeting alone supplies no result'),
 'valuationPolicy':('valuation-policies','Exact owned Product valuation metric/baseline policy'),
 'environment':('execution-environments','Exact independently specified environment of the installation/activation/external operation'),
 'installationReceipt':('installation-observations','Exact independent installation receipt candidate for control and environment'),
 'occurrence':('failure-occurrences','Exact independent occurrence targeted by execution of this control'),
 'trace':('execution-observations','Exact actual execution candidate trace joining this control and occurrence'),
 'receipt':('execution-receipts','Exact independently captured applied/executed/validated receipt candidate for these participants'),
 'other':('effect-codes','A different declared governance effect from the exact selected declared effect'),
 'adopter':('accountable-participants','Exact independently governed adopter for this endpoint'),
 'policy':('assessment-policies','Exact owned policy for acceptance/adoption or evidential interpretation of this subject'),
 'outcome':('decision-outcomes','Exact independently selected outcome for this decision about the named proposition'),
 'review':('actual-review-records','Exact actual review candidate concerning this decision and outcome'),
 'interpretation':('proposition-interpretations','Exact independent interpretation of this selected claim/proposition'),
 'world':('truth-interpretations','Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth'),
 'capability':('capability-declarations','Exact independently declared Agent Capability for this configured instance'),
 'basis':('capability-declaration-bases','Exact separate owned declaration basis joining agent and capability'),
 'predecessor':('identity-continuity-participants','Exact prior instance identity under an independently governed continuity interpretation'),
 'continuityRecord':('identity-continuity-records','Separate exact identity-continuity record; configuring a profile does not supply it'),
 'closure':('incident-closure-records','Separate owned closure candidate for this incident or independently aggregated occurrence envelope'),
 'issuer':('claim-issuers','Exact issuer independently associated with this authority claim'),
 'verification':('authentication-records','Exact issuer/content authentication candidate for the claim'),
 'effect':('effect-codes','Exact independently declared effect of this decision, separate from the primary relation declaration'),
 'grant':('permission-grants','Separate authorized grant candidate for this actor, operation and scope'),
 'succession':('succession-records','Separate exact directional succession record; origin does not supply it'),
 'transform':('transformation-records','Separate exact transformation/compilation/projection record joining this derived artifact to this source'),
 'specification':('correctness-specifications','Exact independent correctness specification of this output'),
 'meaning':('semantic-specifications','Exact independent intended semantic specification for the generated output'),
 'root':('authorization-roots','An exact root in the final state absent from the prior approved envelope; its existence must be independently established'),
 'activationReceipt':('runtime-activation-observations','Exact actual permitted activation candidate joining implementation and environment'),
 'observation':('outcome-observations','Exact independent outcome/external observation for this operation and its environment/objective'),
 'mode':('failure-mode-targets','Exact independently assessed Failure Mode of this occurrence; boundary failure does not confirm it'),
}


def make_plan(definition,conclusion,pair,index):
    c=Context(definition,pair)
    typed_params=[tuple(part.strip().split(':')) for part in conclusion['parameter_types'].split(',')]
    anchors=fixed_parameters(c,conclusion['label'])
    expected={name for name,_ in typed_params}
    assert set(anchors)<=expected,(definition['unit'],conclusion['label'],set(anchors)-expected)
    for name,typ in typed_params:
        if name not in anchors:
            assert name in EXTRAS,(definition['unit'],conclusion['label'],name)
            domain,selection=EXTRAS[name]
            joins={'primarySource':source(),'primaryTarget':target(),'scope':frame('scope')}
            joins.update({k:v for k,v in anchors.items() if v['sort']=='ref' and k!=name})
            if name in {'tests','requirements'} and definition['unit']=='K02':joins['intentResolution']=field('resolution')
            if name=='observedHead':joins.update({'source':anchors['source'],'now':anchors['now'],'timeDomain':anchors['timeDomain']})
            anchors[name]=c.extra(name,SORTS[typ],domain,selection,joins)
        assert anchors[name]['sort']==SORTS[typ],(conclusion['id'],name)
    if conclusion['label']=='cross-effect-inference':
        c.constraints.append({'tag':'notEqual','left':anchors['declared'],'right':anchors['other'],'sort':'effect'})
    arguments=[{'name':name,'declared_type':typ,'sort':SORTS[typ],'term':anchors[name]} for name,typ in typed_params]
    return {'id':conclusion['id']+f':branch:{index:03}','obligation_id':conclusion['id'],'unit':definition['unit'],
      'relation_kind':definition['kind'],'conclusion_label':conclusion['label'],'conclusion_predicate':conclusion['predicate'],
      'source_kind':pair['source_kind'],'target_kind':pair['target_kind'],'signature_branch_index':index,
      'arguments':arguments,'independent_existential_binders':c.binders,'constraints':c.constraints,
      'conclusion_definition':conclusion['definition'],
      'quantifier_contract':'Conclusion_k,b(W,e,f) := ∃ bound variables selected from their independent typed catalogs, all specified joins and constraints hold ∧ the independent conclusion predicate holds on these arguments. Catalog selection is not evidence of the final predicate.',
      'world_validity_required':'WF(W) and every primary meaning/source restriction in the complete pinned theory; these plans are not source-theory countermodels.',
      'non_entailment_proved':False,'raw_source_role_projection_proved':False,'actual_owner_assessment':None}


def term_text(term):
    if term['tag']=='source':return 'e.source'
    if term['tag']=='target':return 'e.target'
    if term['tag']=='frame':return 'f.'+term['name']
    if term['tag']=='witness':return 'exactRole(w,'+term['name']+')'
    return term['name']


def lean_term(term):
    tag=term['tag'];sort=term['sort']
    if tag in {'source','target'}:return '.'+tag
    if tag=='variable':return f'.variable {lean_string(term["name"])}'
    if tag=='frame':return f'.frameField {lean_string(term["name"])} (by decide)'
    if tag=='witness':return f'.witnessField {lean_string(term["name"])} (by decide)'
    raise AssertionError(tag)


def lean_terms(terms):
    text='.nil'
    for term in reversed(terms):text=f'.cons ({lean_term(term)}) ({text})'
    return text


def lean_dynamic(term):return f'⟨.{term["sort"]}, {lean_term(term)}⟩'


def emit_sources(definitions,plans):
    slot_map={d['unit']:{} for d in definitions}
    for plan in plans:
        terms=[a['term'] for a in plan['arguments']]+[t for b in plan['independent_existential_binders'] for t in b['joins'].values()]
        for term in terms:
            if term['tag']=='witness':
                old=slot_map[plan['unit']].get(term['name'])
                assert old in {None,term['sort']}
                assert term['name'] in next(d for d in definitions if d['unit']==plan['unit'])['notation']['witness_fields']
                slot_map[plan['unit']][term['name']]=term['sort']
    frame_slots={'scope':'ref','epoch':'epoch','timeDomain':'ref','evidencePolicy':'ref','theory':'ref','frame':'frame','ownedUniverse':'universe'}
    schema_lines=['import Lean','', 'namespace CandidateConclusionAnchors', '',
      'inductive Sort where','  | ref | frame | epoch | effect | universe | value | result | world','  deriving DecidableEq, Repr','',
      'def witnessSlots : Nat → List (String × Sort)']
    for d in definitions:
        fields=slot_map[d['unit']]
        pairs=', '.join('('+lean_string(k)+', .'+v+')' for k,v in fields.items())
        schema_lines.append(f'  | {int(d["unit"][1:])} => [{pairs}]')
    schema_lines += ['  | _ => []','','def frameSlots : List (String × Sort) := [', '  '+', '.join('('+lean_string(k)+', .'+v+')' for k,v in frame_slots.items()), ']','',
      'inductive Term (unit : Nat) : Sort → Type where',
      '  | source : Term unit .ref','  | target : Term unit .ref',
      '  | witnessField {sort : Sort} (name : String) (declared : (name, sort) ∈ witnessSlots unit) : Term unit sort',
      '  | frameField {sort : Sort} (name : String) (declared : (name, sort) ∈ frameSlots) : Term unit sort',
      '  | variable {sort : Sort} (name : String) : Term unit sort','',
      'inductive Args (unit : Nat) : List Sort → Type where',
      '  | nil : Args unit []','  | cons {sort : Sort} {tail : List Sort} : Term unit sort → Args unit tail → Args unit (sort :: tail)','',
      'structure Binder (unit : Nat) where','  name : String','  sort : Sort','  domain : String','  selectionRole : String','  joins : List (String × Sigma (Term unit))','',
      'inductive Constraint (unit : Nat) where',
      '  | notEqual {sort : Sort} : Term unit sort → Term unit sort → Constraint unit','',
      'def termVariables {unit : Nat} {sort : Sort} : Term unit sort → List (String × Sort)',
      '  | .variable name => [(name, sort)]','  | _ => []','',
      'def termParticipant {unit : Nat} {sort : Sort} : Term unit sort → Bool',
      '  | .source => true','  | .target => true','  | .witnessField _ _ => true','  | _ => false','',
      'def argsVariables {unit : Nat} {sorts : List Sort} : Args unit sorts → List (String × Sort)',
      '  | .nil => []','  | .cons head tail => termVariables head ++ argsVariables tail','',
      'def constraintVariables {unit : Nat} : Constraint unit → List (String × Sort)',
      '  | .notEqual left right => termVariables left ++ termVariables right','',
      'def knownVariables (available needed : List (String × Sort)) : Bool :=',
      '  needed.all fun key => available.contains key','',
      'def validBinderPrefix {unit : Nat} : List (String × Sort) → List (Binder unit) → Bool',
      '  | _, [] => true',
      '  | available, binder :: tail =>',
      '      !binder.name.isEmpty && !binder.domain.isEmpty && !binder.selectionRole.isEmpty &&',
      '      !(available.map Prod.fst).contains binder.name && !binder.joins.isEmpty &&',
      '      (binder.joins.any fun join => termParticipant join.2.2) &&',
      '      (binder.joins.all fun join => !join.1.isEmpty && knownVariables available (termVariables join.2.2)) &&',
      '      validBinderPrefix ((binder.name, binder.sort) :: available) tail','',
      'def planValid {unit : Nat} {sorts : List Sort} (args : Args unit sorts)',
      '    (binders : List (Binder unit)) (constraints : List (Constraint unit)) : Bool :=',
      '  validBinderPrefix [] binders &&',
      '  knownVariables (binders.map fun b => (b.name, b.sort)) (argsVariables args) &&',
      '  (constraints.all fun c => knownVariables (binders.map fun b => (b.name, b.sort)) (constraintVariables c)) &&',
      '  (binders.all fun b => (argsVariables args).contains (b.name,b.sort) ||',
      '    binders.any fun later => later.joins.any fun join => (termVariables join.2.2).contains (b.name,b.sort))','',
      'structure Plan (unit : Nat) (sorts : List Sort) where',
      '  obligationId : String','  sourceKind : String','  targetKind : String','  branchIndex : Nat',
      '  arguments : Args unit sorts','  binders : List (Binder unit)','  constraints : List (Constraint unit)',
      '  structurallyValid : planValid arguments binders constraints = true','',
      '-- This proof field certifies anchor syntax/typing only. No World, Meaning,',
      '-- conclusion truth, source authenticity or countermodel is asserted here.',
      'end CandidateConclusionAnchors','']
    # Lean reserves Sort for universe syntax; the explicit argument-sort type is
    # named ArgSort to avoid colliding with that language keyword.
    (HERE/'AnchorContracts.lean').write_text(re.sub(r'\bSort\b','ArgSort','\n'.join(schema_lines)))
    modules=[]
    for d in definitions:
        unit=d['unit'];number=int(unit[1:]);selected=[p for p in plans if p['unit']==unit]
        declarations=[];lines=['import AnchorContracts','','set_option maxRecDepth 8192','set_option maxHeartbeats 20000000','',f'namespace CandidateConclusionAnchors.{unit}','']
        for p in selected:
            short=p['obligation_id'].split(':')[-1];name=f'plan_{short}_{p["signature_branch_index"]:03}'
            declarations.append(name)
            sorts=', '.join('.'+a['sort'] for a in p['arguments'])
            lines += [f'def {name} : Plan {number} [{sorts}] :=', '  { obligationId := '+lean_string(p['obligation_id']),
              '    sourceKind := '+lean_string(p['source_kind']), '    targetKind := '+lean_string(p['target_kind']),
              f'    branchIndex := {p["signature_branch_index"]}',
              '    arguments := '+lean_terms([a['term'] for a in p['arguments']]), '    binders := [']
            for i,b in enumerate(p['independent_existential_binders']):
                joins=', '.join('('+lean_string(key)+', '+lean_dynamic(t)+')' for key,t in b['joins'].items())
                lines += ['      { name := '+lean_string(b['name'])+', sort := .'+b['sort']+', domain := '+lean_string(b['domain'])+', selectionRole := '+lean_string(b['selection_role'])+', joins := ['+joins+'] }'+(',' if i+1<len(p['independent_existential_binders']) else '')]
            constraints=', '.join('.notEqual ('+lean_term(c['left'])+') ('+lean_term(c['right'])+')' for c in p['constraints'])
            lines += ['    ]','    constraints := ['+constraints+']','    structurallyValid := by decide }','']
        for name in declarations:lines.append('#print axioms '+name)
        lines += [f'end CandidateConclusionAnchors.{unit}','']
        path=HERE/f'Anchors{unit}.lean';path.write_text('\n'.join(lines))
        modules.append({'unit':unit,'source':binding(path),'anchor_plan_definitions':len(selected),'declarations':[f'CandidateConclusionAnchors.{unit}.{name}' for name in declarations]})
    return modules,slot_map


def build():
    ds=[read(p) for p in sorted((BATCH/'definitions').glob('*.json'))]
    original=read(BATCH/'obligation-targets.json')
    pending_ids={r['id'] for r in original['rows'] if r['category']=='forbidden'}
    plans=[];obligations=[]
    for d in ds:
        for conclusion in d['forbidden_conclusions']:
            selected=[make_plan(d,conclusion,pair,i) for i,pair in enumerate(d['ordered_pairs'])]
            plans.extend(selected)
            obligations.append({'id':conclusion['id'],'unit':d['unit'],'label':conclusion['label'],
              'independent_predicate':conclusion['predicate'],'parameter_types':conclusion['parameter_types'],
              'definition':conclusion['definition'],'prior_definition':binding(ROOT/next(r for r in read(BATCH/'index.json')['units'] if r['unit']==d['unit'])['definition']['path']),
              'anchor_plan_ids':[p['id'] for p in selected], 'semantic_branch_count':len(selected),'full_theory_non_entailment_proved':False,'inherited_discharge':False})
    assert len(obligations)==148 and {r['id'] for r in obligations}==pending_ids
    assert len(plans)==len({p['id'] for p in plans})==1982
    modules,slots=emit_sources(ds,plans)
    write(HERE/'anchor-contracts.json',{'schema':'relational.typed-conclusion-anchor-contracts/v1','revision':REVISION,
      'source_definition_manifest':binding(BATCH/'review-manifest.json'),'source_obligation_inventory':binding(BATCH/'obligation-targets.json'),
      'obligation_count':148,'branch_plan_count':1982,'units':41,'sorts':SORTS,
      'witness_reference_projection_slots':slots,'projection_status':'Typed projection contracts only; source-to-role implementation/proof remains open.',
      'obligations':obligations,'plans':plans,'actual_owner_assessment':None,'inherited_discharges':0,'authority_effect':'none'})
    write(HERE/'generation-manifest.json',{'revision':REVISION,'generator':binding(Path(__file__)),'source_definition_index':binding(BATCH/'index.json'),
      'anchor_contracts':binding(HERE/'anchor-contracts.json'),'core_source':binding(HERE/'AnchorContracts.lean'),
      'modules':modules,'anchor_plan_definitions':1982,'named_theorem_declarations':0,'full_source_refinement_proved':False,'non_entailment_proved':False,'inherited_discharges':0})
    rows=[]
    for obligation in obligations:
        unit=obligation['unit'];selected=[p for p in plans if p['obligation_id']==obligation['id']]
        rows += [f'## {unit} — {obligation["label"]}', '',obligation['definition'],'',f'Original ID: `{obligation["id"]}`. Exact signature branches: {len(selected)}.','']
        for p in selected:
            rows += [f'**{p["source_kind"]} → {p["target_kind"]}**', '',
              '| Parameter | Type | Exact anchor |','|---|---|---|']
            rows += [f'| `{a["name"]}` | `{a["declared_type"]}` | `{term_text(a["term"])}` |' for a in p['arguments']]
            for b in p['independent_existential_binders']:
                joins=', '.join(key+'='+term_text(term) for key,term in b['joins'].items())
                rows += ['',f'`{b["name"]}` ranges over `{b["domain"]}`: {b["selection_role"]}. Exact selection joins: {joins}.']
            if p['constraints']: rows += ['', '**Additional constraint:** other effect differs from the declared effect.']
            rows += ['']
    (HERE/'ALL-ANCHORS.md').write_text('# Exact conclusion participants for all 148 inherited IDs\n\nProposed supplement. Structural type checking is not proof of conclusion truth, catalog authenticity or a full-theory countermodel.\n\n'+'\n'.join(rows))
    print(json.dumps({'obligations':148,'signature_branches':1982,'units':41,'new_theorem_declarations':0}))


if __name__=='__main__':build()
