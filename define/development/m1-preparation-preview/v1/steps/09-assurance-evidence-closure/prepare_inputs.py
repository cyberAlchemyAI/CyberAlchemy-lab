#!/usr/bin/env python3
"""Freeze exact sources and bounded interpreted requirements; candidate-only.

No admission, role assignment, runtime/store or previous evidence writes.
"""
from pathlib import Path
import hashlib
import json
import re

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
BASE=STEP.parent.parent
OLD=BASE/'steps/08-exact-postimages-review'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def save(name,d):
    with (STEP/name).open('x') as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')

# Shared Entity carrier, with requirements grounded in source text. No role-label
# disjointness or entity-sort trick supplies a distinction witness.
FRAMES={
 'Pack':['VersionExact','Scoped','BoundedGoalDeclared','OriginatingIntentDeclared','NamedConsumerUse','CapturedStandingOrGaps','OwnerRoutesOrGaps','RelationshipsScoped','ValidationScopeDeclared','ClaimLimitsDeclared','ConceptSetNonempty','EveryConceptSingleDisposition','EveryDispositionPayloadMatches','PayloadDomainExactlyConcepts','NoUndeclaredConceptHandling','NoNewAuthorityFromPreparation'],
 'Define':['EnabledOutcomeDeclared','MeaningPreparationOutcome','BoundedGoalDeclared','OriginatingIntentDeclared','NamedConsumerUse','DeclaredConceptCoverageOutcome','ReviewablePackOutcome','LineagePreservingOutcome','SourceStandingGapsOutcome','NoSolutionOrFollowupSelectionOutcome'],
 'Definition':['StableSemanticIdentity','VersionExact','OwnerQualified','Scoped','SingleNormativeMeaning','TermMeaningAssignment'],
 'EvaluationProfile':['VersionExact','OwnerQualified','Scoped','DefinitionSubjectDeclared','InputSelectionDeclared','ChecksDeclared','OutcomeRulesDeclared','CausalBlockersDeclared','PhasesDeclared','ClaimLimitsDeclared'],
 'LifecycleProfile':['VersionExact','OwnerQualified','Scoped','DefinitionSubjectDeclared','InitialPostureDeclared','StatesDeclared','DirectedPairsDeclared','GateRulesDeclared','EffectRulesDeclared','InvalidationRulesDeclared','HistoryRulesDeclared'],
 'ContextView':['ImmutableSourceEpoch','ContextRequestResolution','IncludedExcludedSelection','ViewLineage','RefreshExpiryConditions'],
 'Review':['AssessmentOccurred','ExactSubjectBindings','CriteriaDeclared','EvidenceDeclared','ClaimLimitsDeclared'],
 'DecisionBundle':['ClosedOrderedRequestSet','CheckpointBinding','IndependentMemberBoundaries','MemberEffectsDeclared','MemberInvalidationDeclared'],
 'EvidenceSet':['QuestionClaimBounded','SupportingCounterEvidenceAggregate','ProvenanceDeclared','EvidenceFreshnessLimits'],
 'UbiquitousLanguage':['BoundedContextLanguage','ExpressionsRelationsRules','UsageSurfaces','AmbiguitiesRevisionRoutes','LoadBearingDispositionResolution'],
 'GovernedModel':['VersionExact','Scoped','OwnerQualified','ExplicitRepresentation','SourcesAssumptionsDeclared','ValidationLifecycleChallengeDeclared'],
 'Ledger':['OrderedEntries','EntryIdentitySchema','IntegrityCorrectionRule','ReconciliationRule','RetentionChallengeContract','OwnerQualified'],
 'GeneratedOutput':['CanonicalInputBinding','ExactGovernedGenerator','ReproducibleProduction','LineageParityChecks'],
 'ProductCapability':['StableOutcomeIdentity','EnabledOutcomeDeclared','OwnerQualified','Scoped','ExactlyOneProductAnchor','ConsumerContractsContextEvidenceLimits'],
 'Method':['RepeatableTransformation','InputsActionsRolesGatesOutputs','EvidenceResidueRules','ValidationRecompositionBoundary'],
 'Implementation':['StableTechnicalIdentity','VersionExact','OwnerQualified','SourceBuildDeploymentBinding','InterfacesEvidenceBindings'],
 'AgentCapability':['BoundedTechnicalAttemptClass','InputOutputEvidenceFailureContracts'],
 'AgentInstance':['ConcreteTimeBoundedActor','ProfileImplementationCapabilityBinding','AccountablePrincipalBinding','ActorOwnerLifecycle','MachineSessionBound'],
 'IntentResolution':['SelectionActOccurred','ExactIntentBinding','SelectedGovernedResolution','SatisfactionTestDeclared','AttributionPresent','ApplicableAuthority'],
 'ResearchInquiry':['BoundedQuestion','SourcePolicyMethod','ProjectGoalLinks','OwnerRouteStoppingConditions'],
 'WorkContinuity':['WorkReconstructionOutcome','PeopleSessionsInterruptions','DeclaredLedgerState','DecisionsBlockersEvidenceResidueRoutes'],
 'ArtifactType':['VersionExact','OwnerQualified','Scoped','SemanticMeaningBinding','ClosedSchemaBinding','CanonicalSourceDirection','ProjectionRuleDeclared','ValidationRuleDeclared'],
 'Policy':['VersionExact','Scoped','IssuedRuleSet','BehaviorConstraintsDeclared'],
 'OntologyNode':['IndependentGraphIdentity','ExactRepresentedSubject','OntologyBinding','ProvenanceDeclared','ContestabilityDeclared'],
 'Source':['ExactProvenanceOrigin','ResolvableReference','IntegrityBoundary'],
 'Decision':['SelectionActOccurred','ExactSubjectEffectSelected','AttributionPresent','ApplicableAuthority'],
 'CanonicalRepresentationInvariant':['OneCanonicalRepresentationRule','DerivedHumanViewRule','AllowedProcessOriginRule','HonestAssuranceRule'],
 'Evaluation':['ExecutionOccurred','ExactInputBindings','CompleteOutcomeMap','CausalBlockersPreserved','DeclaredCoverage'],
}
ROLE_REFS={
 'ContextView':'cal.definition.context-view','Review':'cal.definition.review','DecisionBundle':'cal.definition.decision-bundle',
 'EvidenceSet':'cal.definition.evidence-set','UbiquitousLanguage':'cal.definition.ubiquitous-language','GovernedModel':'cal.definition.governed-model',
 'Ledger':'cal.definition.ledger','GeneratedOutput':'cal.definition.generated-output','ProductCapability':'cal.definition.product-capability',
 'Method':'CAV2-D32','Implementation':'cal.definition.implementation','AgentCapability':'cal.definition.agent-capability',
 'AgentInstance':'cal.definition.agent-instance','IntentResolution':'cal.definition.intent-resolution','ResearchInquiry':'cal.definition.research-inquiry',
 'WorkContinuity':'cal.definition.work-state-continuity-capability','ArtifactType':'cal.definition.artifact-type','Policy':'cal.definition.policy',
 'OntologyNode':'cal.definition.ontology-node','Source':'cal.definition.source','Decision':'cal.definition.decision',
 'CanonicalRepresentationInvariant':'cal.definition.canonical-representation-invariant','Evaluation':'cal.definition.evaluation',
}

def main():
    old_manifest=load(OLD/'package-manifest.json')
    for f in old_manifest['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    targets=load(OLD/'selection.json')['targets'];roles=['Pack','Define','Definition','EvaluationProfile','LifecycleProfile']
    targets=[{**t,'model_role':role} for t,role in zip(targets,roles)]
    registry=load(ROOT/'authority/definitions/registry.json')
    current={e['definition_id']:e for e in registry['entries'] if registry['current_lookup'][e['definition_id']]==e['definition_id']+'@'+e['version']}
    corpus=[];neighbors=[]
    for identity,e in current.items():
        assert sha(ROOT/e['path'])==e['sha256']
        d=load(ROOT/e['path']);formal=d['voices']['scientific_formal']
        corpus.append({**e,'normative_statement':formal['normative_statement'],'formal_expression':formal.get('formal_expression'),
                       'scope':d['scope'],'source_refs':d['source_refs'],'selection_policy':'exact current lookup; original candidate labels do not override admitted standing'})
    for role,identity in ROLE_REFS.items():
        e=current[identity];d=load(ROOT/e['path'])
        neighbors.append({'model_role':role,**e,'source_text':d['voices']['scientific_formal']['normative_statement'],
            'selector':'/voices/scientific_formal/normative_statement','encoded_frame_fields':FRAMES[role],
            'coverage':'Source-grounded selected role/behavior requirements, not a complete formalization of every source clause',
            'deferred':'Unencoded imported classification/source axioms, temporal/state authenticity, full population and whole-domain correctness remain outside this interpreted frame.'})
    save('targets.json',{'schema_version':'cal.define-closure-targets/v1','authority_effect':'none','targets':targets})
    save('corpus-selection.json',{'schema_version':'cal.define-current-corpus-scope/v1','authority_effect':'none','registry':bind(ROOT/'authority/definitions/registry.json'),
        'current_count':183,'current_records':sorted(corpus,key=lambda r:r['definition_id']),
        'claim_ceiling':'Exact source capture and relevance accounting; no all-183 formalization or universal compatibility claim.'})
    save('neighbor-correspondence.json',{'authority_effect':'none','neighbors':neighbors,
        'owner_fidelity':'Fresh interpreted fields are authored review material; prior conversational acceptance does not certify unseen correspondence.'})
    pairs=set()
    ref_to_role={t['definition_ref']:t['model_role'] for t in targets}
    ref_to_role.update({n['definition_id']+'@'+n['version']:n['model_role'] for n in neighbors})
    ref_to_role[registry['current_lookup']['cal.definition.definition']]='Definition'
    for step,role in [('01-definition-pack','Pack'),('02-cyberalchemy-define','Define'),('03-foundational-definition','Definition')]:
        for c in load(BASE/'steps'/step/'distinction-review.json')['comparisons']:
            other=ref_to_role[c['against']['exact_ref']]
            if other!=role:pairs.add(tuple(sorted([role,other])))
    previous_pairs=[('EvaluationProfile','Evaluation'),('EvaluationProfile','ArtifactType'),('EvaluationProfile','Policy'),('EvaluationProfile','Review'),('EvaluationProfile','Definition'),('EvaluationProfile','OntologyNode'),('EvaluationProfile','LifecycleProfile'),('LifecycleProfile','Decision'),('LifecycleProfile','Policy'),('LifecycleProfile','Review'),('LifecycleProfile','Definition'),('LifecycleProfile','OntologyNode'),('LifecycleProfile','ArtifactType')]
    for p in previous_pairs:pairs.add(tuple(sorted(p)))
    for i,a in enumerate(roles):
        for b in roles[i+1:]:pairs.add(tuple(sorted([a,b])))
    clauses=[]
    anchor_maps={
        'Pack':[['VersionExact','BoundedGoalDeclared','OriginatingIntentDeclared','NamedConsumerUse'],['ConceptSetNonempty','EveryConceptSingleDisposition'],['EveryDispositionPayloadMatches'],['CapturedStandingOrGaps','OwnerRoutesOrGaps','RelationshipsScoped','ValidationScopeDeclared','ClaimLimitsDeclared'],['AuthorityNonEntailment'],['SpecializationRouteCases'],['AuthorityNonEntailment']],
        'Define':[['EnabledOutcomeDeclared','MeaningPreparationOutcome','BoundedGoalDeclared','OriginatingIntentDeclared','NamedConsumerUse'],['DeclaredConceptCoverageOutcome','SourceStandingGapsOutcome','ReviewablePackOutcome'],['LineagePreservingOutcome'],['CoverageCases'],['FailedAttemptCases'],['AuthorityNonEntailment'],['ProductInstanceSeparation']],
        'Definition':[['StableSemanticIdentity','VersionExact','OwnerQualified','Scoped','SingleNormativeMeaning','TermMeaningAssignment'],['CompleteDefinitionRequirements'],['OwnerAdmissionSupport']],
    }
    for t in targets:
        d=load(ROOT/t['path']);text=d['voices']['scientific_formal']['normative_statement']
        # Exact spans, not an altered substitute normative Definition.
        matches=list(re.finditer(r'[^.!?]+(?:[.!?]|$)',text))
        for i,m in enumerate(matches):
            stripped=m.group().strip();start=m.start()+len(m.group())-len(m.group().lstrip())
            mapped=anchor_maps.get(t['model_role'],[])
            clauses.append({'subject':t['definition_ref'],'clause_id':t['model_role']+'-N'+str(i+1),
                'selector':'/voices/scientific_formal/normative_statement','span':[start,start+len(stripped)],'text':stripped,
                'interpreted_obligations':mapped[i] if i<len(mapped) else FRAMES[t['model_role']],
                'source_binding':{'path':t['path'],'sha256':t['sha256']},
                'fidelity':'Authored correspondence; full fresh interpretation remains a final review subject'})
    interpretations={'schema_version':'cal.define-closure-interpreted-requirements/v1','authority_effect':'none','frames':FRAMES,'comparison_pairs':[list(p) for p in sorted(pairs)],
        'selection':'All 24 initial Pack/Define/Foundation comparisons, all 13 earlier profile comparisons, plus all five-target pairs; duplicates coalesce explicitly',
        'assumptions':['Frame primitives are interpreted requirements grounded in exact source text; they do not prove actual role authority or source truth.',
            'One shared Entity carrier; no disjoint role sorts, inequality-by-label or exclusive kind tags manufacture non-collapse.',
            'Specialization/overlap is permitted; witnesses disprove forced equivalence, not all overlap.',
            'Conforming result and complete Definition are distinct from runtime execution, consumer readiness, admission and effect application.'],
        'limits':['Finite models and declared bounded case populations only; no Lean theorem or full provider/service conformance.',
            'Full natural-language/source-population equivalence and actual/infinite temporal trace correctness are not established.',
            'Remaining current meanings are source-screened, not given synthetic role definitions to manufacture universal proofs.']}
    save('interpretations.json',interpretations)
    save('clause-correspondence.json',{'authority_effect':'none','clauses':clauses,'per_voice_sources':[{'subject':t['definition_ref'],'voice':voice,'content':load(ROOT/t['path'])['voices'][voice]} for t in targets for voice in ['scientific_formal','plain_language','domain_context']],
        'current_owner_acceptances':[bind(p) for p in sorted((BASE/'reviews').glob('*-accepted-*.json'))],
        'new_material_acceptance':'No prior acceptance is relabeled as approval of this fresh formal interpretation or final cohort.'})
    frozen={ROOT/f['path'] for f in old_manifest['files']}
    frozen.update(p for p in (BASE/'reviews').glob('*.json'))
    frozen.update(ROOT/e['path'] for e in registry['entries'])
    frozen.update(ROOT/f['path'] for f in load(OLD/'integrity-validation.json')['additional_frozen_source_files'])
    frozen.update(ROOT/'craft/formalization/candidates/definition-assurance-v1'/f for f in ['verifier.py','ir.py','contracts.py','resolver.py','obligations.py','bundles.py','providers/finite.py'])
    frozen.add(ROOT/'authority/owners/foundation-01/v1/owners.json')
    frozen.add(ROOT/'define/proposals/0005-amended-integration-plan/limits.json')
    frozen.add(ROOT/'define/proposals/0005-amended-integration-plan/DESIGN.md')
    frozen.add(ROOT/'define/INTEGRATION.md');frozen.add(ROOT/'implementation/define-cli/v1/CONTRACT.md')
    frozen.update(p for p in STEP.glob('*.json'))
    frozen.update(p for p in STEP.glob('*.py'))
    total=sum(p.stat().st_size for p in frozen)
    assert total<=67_108_864
    save('source-selection.json',{'schema_version':'cal.define-closure-source-selection/v1','authority_effect':'none','files':[bind(p) for p in sorted(frozen)],'total_bytes':total,'capture_date':'2026-10-14',
        'ceiling':'64 MiB selected source bytes; no unselected/private/live state or runtime/store reset'})
    print(json.dumps({'targets':5,'neighbor_frames':len(neighbors),'comparison_pairs':len(pairs),'source_bytes':total,'admissions':0}))

if __name__=='__main__':main()
