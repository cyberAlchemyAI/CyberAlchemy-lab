#!/usr/bin/env python3
"""Freeze complete candidate evidence and exact refreshed postimages.

Prepared material is not an owner admission or an adopted policy. Decisions and
application receipts are absent, not predicted SHA values or invented IDs.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import importlib.metadata

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
BASE=STEP.parent.parent
OLD=BASE/'steps/08-exact-postimages-review'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def save(n,d):
    with (STEP/n).open('x') as f:json.dump(d,f,indent=2,ensure_ascii=False,sort_keys=True);f.write('\n')
def text(n,s):
    with (STEP/n).open('x') as f:f.write(s.rstrip()+'\n')
def link(p,label):return f'[{label}]({os.path.relpath(p,STEP)})'
def esc(s):return str(s).replace('|','\\|').replace('\n',' ')

def main():
    for f in load(STEP/'source-selection.json')['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    for f in load(OLD/'package-manifest.json')['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    targets=load(STEP/'targets.json')['targets'];assurance=load(STEP/'assurance-results.json');evidence=load(STEP/'evidence-results.json')
    accepted=load(STEP/'accepted-review-selections.json');scope=load(STEP/'comparison-coverage.json');impact=load(STEP/'consumer-impact-evidence.json')
    assert len(accepted['selections'])==16 and assurance['directed_non_equivalence_witnesses']==84
    save('review-selection.json',{'authority_effect':'none','subjects':targets,'prior_frozen_selection':bind(OLD/'selection.json'),
        'meaning_bytes_changed':False,'excluded_specimen':load(OLD/'selection.json')['excluded_specimen'],
        'new_fidelity_subjects':[bind(STEP/'interpretations.json'),bind(STEP/'clause-correspondence.json'),bind(STEP/'formal-core.json'),bind(STEP/'consumer-impact-evidence.json')],
        'final_fidelity':'Required for fresh interpretation and final postimage/evidence cohort; not inferred from earlier scoped selections.'})
    formula_rows=[]
    mappings={
        'Pack':{'FiniteNonempty(C)':'typed nonempty RequiredConcept relation','delta in Functions(C,D)':'typed exactly-one handling among four closed tags, plus no undeclared handling',
            'dom(H)=C':'PayloadDomainExactlyConcepts and matching payload/disposition relations','PayloadMatches(H(c),delta(c))':'typed payload matching axiom and bounded route cases',
            'ResolvedWithStandingAtCapture':'41 real source bindings and declared-reference/gap case population; not truth or permission',
            'NoNewAuthorityFromPack(A)':'explicit NoNewAuthorityFromPreparation iff preparation did not create authority; negative control and independent permission model'},
        'Define':{'WellFormedPack(P)':'ConformingDefineResult requires the typed Pack frame including exact payload domain and no preparation-origin authority',
            'PreservesIntentAndGoalLineage':'LineagePreserved requirement; altered/missing lineage cannot qualify as result',
            'AccountsForDeclaredConcepts':'DeclaredConceptCoverage requirement and bounded conditional outcome cases; full discovery is not asserted',
            'RecordsSourceStandingAndGaps':'real captured source provenance plus explicit requirement/gap flags; no always-current or execution guarantee'},
        'Definition':{'DefinitionComplete(d)':'Preserved governing completeness expression encoded with separate normative owner/consumer obligations',
            'Admitted(d)':'CanonicalAuthority requires separate selected owner effect, exact binding and confirmed application; completeness does not force it'},
        'EvaluationProfile':{'ConformingEvaluation':'Necessary exact binding/outcome/blocker requirements; no converse shortcut or execution from declaration',
            'A(P,g,O_e)':'fixed exact phase rule evidence retained from step 7 and exact selected check contract'},
        'LifecycleProfile':{'PermittedBy':'exact binding plus declared directed pair and PASS gate is separated from actual transition and confirmed effect',
            'ConsistentAdmittedState':'selected exact owner admission and confirmed application support rule; no actual state inferred from declaration'},
    }
    for t in targets:
        d=load(ROOT/t['path']);formal=d['voices']['scientific_formal']['formal_expression']
        for fragment,interpretation in mappings[t['model_role']].items():
            assert fragment in formal,(t['model_role'],fragment)
            formula_rows.append({'subject':t['definition_ref'],'selector':'/voices/scientific_formal/formal_expression','source':{'path':t['path'],'sha256':t['sha256']},
                'fragment':fragment,'interpretation':interpretation,'fidelity_status':'AUTHOR_CORRESPONDENCE; FINAL_REVIEW_REQUIRED'})
    save('formal-expression-correspondence.json',{'authority_effect':'none','rows':formula_rows,
        'deferred':['Full population/candidate membership semantics beyond the supplied finite frames','Complete natural-language equivalence and imported source/classification axioms','Actual owner authenticity, runtime execution and infinite temporal/storage recovery properties'],
        'ceiling':'Clauses are grounded in exact canonical fields; this correspondence does not invent admitted axioms or assert complete source equivalence.'})
    voice_rows=[]
    judgements={
        'Pack':'All voices retain a bounded required-concept handling bundle with frozen standing and visible gaps. Formal payload-domain/authority-origin obligations are now explicit in the model.',
        'Define':'Enabled outcome, Product instance, Method, realization, actor and saved Pack remain separate. Initial Intent and explicit concept-set lineage survive; follow-up Intent proposals remain outside the selected responsibility.',
        'Definition':'One owner-scoped normative meaning; nonnormative explanations preserve account/filter/snapshot/output limits. Changed exact-carrier/profile verification is explicit; old normative/formal/scope fields remain unchanged.',
        'EvaluationProfile':'Declared checking contract, actual Evaluation, semantic fidelity, selected owner Decision and confirmed application remain separate; absent evidence is not FAIL and phase scopes are explicit.',
        'LifecycleProfile':'Declared initial/states/pairs/gates/effects do not record transitions. Revised input evidence reopens affected assessments while past states and receipts are preserved.'}
    for t in targets:
        d=load(ROOT/t['path'])
        voice_rows.append({'subject':t['definition_ref'],'canonical_source':{'path':t['path'],'sha256':t['sha256']},
            'author_finding':judgements[t['model_role']],'scientific_formal':d['voices']['scientific_formal'],
            'plain_language':d['voices']['plain_language'],'domain_context':d['voices']['domain_context'],
            'conversational_meaning_selection':next(s['record'] for s in accepted['selections'] if s['item']==['Pack','Define','Definition','EvaluationProfile','LifecycleProfile'].index(t['model_role']) and False) if False else accepted['selections'][['Pack','Define','Definition','EvaluationProfile','LifecycleProfile'].index(t['model_role'])]['record'],
            'fresh_formal_fidelity':'PENDING final exact owner review; no new normative text or automatic transfer of earlier acceptance'})
    save('voice-fidelity-review.json',{'authority_effect':'none','subjects':voice_rows,'author_finding':'No scoped explanatory contradiction identified in the reviewed voices; this is attributable author analysis, not full source/owner conformance proof.'})
    # Update proposed views; preserve every original Definition and history row.
    registry=copy.deepcopy(load(OLD/'registry-postimage.json'))
    registry.update({'record_id':'CAL-DEFINE-M1-REGISTRY-POSTIMAGE-09','candidate_source':str((STEP/'review-selection.json').relative_to(ROOT)),
        'source_direction':{'canonical':'registry-postimage.json','human_projection':'DEFINITIONS-INDEX.md','projection_policy':'generated-only',
            'generator_ref':str(Path(__file__).resolve().relative_to(ROOT)),'generator_sha256':sha(Path(__file__))},
        'claim_ceiling':'Exact mixed candidate projection. Five additions remain unadmitted; all 189 inherited rows remain exact. New review metadata/evidence must receive final scoped confirmation before any applied mirror policy or selection.'})
    save('registry-postimage.json',registry)
    live=load(ROOT/registry['predecessor']['path'])
    rows=['<!-- GENERATED from exact candidate registry and bound Definition records. -->','# Complete proposed Definition index','',
        '**189 inherited admitted versions + 5 unadmitted candidates = 194 versions. Live current identities: 183. Proposed: 187.**','',
        'Representation is read from the exact source record; it is not inferred from the term, ownership or authority status. “Proposed” is not effective current authority.','',
        '| Term | Exact version | Representation | Standing | Live current | Proposed selection | Record | SHA-256 |','| --- | --- | --- | --- | --- | --- | --- | --- |']
    for e in registry['entries']:
        exact=e['definition_id']+'@'+e['version'];p=ROOT/e['path'];assert sha(p)==e['sha256'];d=load(p)
        actual=live['current_lookup'].get(e['definition_id'])==exact;proposed=registry['proposed_current_lookup'].get(e['definition_id'])==exact
        rows.append('| '+' | '.join([esc(e['term']),'`'+exact+'`','`'+d['schema_version']+'`',e['lifecycle_state'],'yes' if actual else 'no','retained' if proposed and actual else 'pending' if proposed else 'no',link(p,'JSON'),'`'+e['sha256']+'`'])+' |')
    text('DEFINITIONS-INDEX.md','\n'.join(rows))
    (STEP/'artifact-type-registry-postimage.json').write_bytes((OLD/'artifact-type-registry-postimage.json').read_bytes())
    (STEP/'registration-delta.json').write_bytes((OLD/'registration-delta.json').read_bytes())
    resolution=copy.deepcopy(load(OLD/'representation-bindings.json'))
    for t in resolution['subjects']:
        t['resolved_candidate_index']=bind(STEP/'DEFINITIONS-INDEX.md');t['resolved_registry']=bind(STEP/'registry-postimage.json')
        t['aggregate_audit_path']=str((STEP/'drift-audit-postimage.json').relative_to(ROOT));t['resolution_scope']='Exact step-9 candidate review only; no global alias/current authority registration'
    resolution['virtual_ref_resolution']['candidate:define-m1:DEFINITIONS-INDEX']=bind(STEP/'DEFINITIONS-INDEX.md')
    save('representation-bindings.json',resolution)
    residue=[
        {'id':'E01','material_status':'BOUNDED_AUTHOR_EVIDENCE_EXECUTED','evidence':[bind(STEP/'assurance-results.json'),bind(STEP/'formal-expression-correspondence.json')],
            'closure':'Pack/Define interpreted witnesses, relational total handling/payload-domain checks, specialization/reference/outcome cases and source correspondence are prepared and executed.',
            'remaining':'Fresh exact formal interpretation/fidelity and required semantic scope confirmation are final review subjects; no unrestricted natural-language theorem.'},
        {'id':'E02','material_status':'BOUNDED_COMPATIBILITY_EVIDENCED','evidence':[bind(STEP/'bounded-cases.json'),bind(STEP/'consumer-impact-evidence.json')],
            'closure':'Changed exact-carrier criterion tested under declared binding/standing conditions; original norm/formula/scope and historical source bytes preserved; C03/C04 dispositions are grounded in exact endpoint contracts.',
            'remaining':'Conditional v1 slice is not universal compatibility; actual successor admission and descriptor application remain absent.'},
        {'id':'E03','material_status':'SCOPED_PRESERVATION_ACCOUNTED','evidence':[bind(STEP/'comparison-coverage.json'),bind(STEP/'consumer-impact-evidence.json')],
            'closure':'915 reference-screen records account for all 5x183 current-target combinations; 42 selected pairs have native interpreted witnesses. Exact capture set is 34 source users + 2 evidence users + 1 predecessor, with type/operational witnesses.',
            'remaining':'Whole-repository consistency and unknown/private/external consumers remain excluded, as in C02. Fresh review must acknowledge corrected source/evidence/self classification.'},
        {'id':'E04','material_status':'NOT_CLOSED_BY_AUTHOR_OR_BEFORE_ADOPTION','evidence':[bind(STEP/'evaluation-preview.json'),bind(STEP/'voice-fidelity-review.json')],
            'closure':'Exact final subjects, dispositions, source/owner routes, model evidence, preconditions and honest phase blockers are assembled.',
            'remaining':'Fresh owner fidelity/final cohort confirmation and compatible/adopted contract standing cannot be invented. All five current pre-decision previews remain NOT_EVALUABLE. Dependency-ordered admission/adoption effects need separate exact owner decisions and confirmed application.'},
        {'id':'E05','material_status':'DEFERRED_OUTSIDE_THIS_ASSURANCE_STEP','evidence':[],
            'closure':'No product runtime or private/live state changed. Legacy CLI scope and bounded review interface remain preserved.',
            'remaining':'Strict M1 provider/exporter, immutable integration, runtime enforcement and operational qualification remain implementation work; no complete M1 capability claim.'}]
    save('residue-disposition.json',{'authority_effect':'none','items':residue,'admission_ready':False,'all_gaps_closed':False})
    findings=[]
    for r in residue:
        findings.append({'finding_id':r['id'],'severity':'blocker' if r['id']=='E04' else 'scope-limit' if r['id']=='E05' else 'prepared-evidence',
            'status':r['material_status'],'condition':r['closure'],'remaining':r['remaining'],'evidence':r['evidence']})
    drift={'schema_version':'cal.define-definition-drift-postimage/v1','authority_effect':'none','status':'candidate-evidence','owner_ref':'role:evidence-conformance-owner',
        'registry_ref':str((STEP/'registry-postimage.json').relative_to(ROOT)),'registry_sha256':sha(STEP/'registry-postimage.json'),
        'baseline_audit':bind(ROOT/'authority/definitions/drift-audit.json'),'inherited_findings':load(ROOT/'authority/definitions/drift-audit.json')['findings'],
        'accepted_proposals':accepted['selections'],'fresh_findings':findings,'summary':{'versions':194,'live_current_identities':183,'proposed_current_identities':187,
            'conversational_selections':16,'unselected_conversational_items':0,'actual_admission_adoption_effects':0,'source_reference_gaps':0,
            'whole_repository_consistency':'NOT_ESTABLISHED','fresh_final_fidelity':'PENDING','admission_ready':False},
        'claim_ceiling':'Earlier zero-drift/history findings keep their original scope. This candidate audit does not relabel pending fresh review or adopted standing as completed.'}
    save('drift-audit-postimage.json',drift)
    text('DEFINITION-DRIFT-AUDIT.md','# Candidate assurance and drift audit\n\n16 conversational proposals selected; fresh final fidelity and adopted standing remain explicit.\n\n'+
        '\n'.join(f"## {r['id']} — {r['material_status']}\n\n{r['closure']}\n\nRemaining: {r['remaining']}\n" for r in residue))
    activation=copy.deepcopy(load(OLD/'activation-order.json'))
    activation['fresh_evidence_binding']=bind(STEP/'review-selection.json');activation['status']='prospective closed dependency ordering; no effective nodes'
    save('activation-order.json',activation)
    envelope=copy.deepcopy(load(OLD/'review-envelope.json'))
    for b in envelope['exact_currentness_preconditions']:assert sha(ROOT/b['path'])==b['sha256']
    envelope.update({'exact_semantic_selection':bind(STEP/'review-selection.json'),'review_items':bind(STEP/'accepted-review-selections.json'),
        'fresh_fidelity_inputs':[bind(STEP/'formal-core.json'),bind(STEP/'formal-expression-correspondence.json'),bind(STEP/'voice-fidelity-review.json'),bind(STEP/'consumer-impact-evidence.json')],
        'status':'all explained proposals selected; fresh final cohort/fidelity/effect review pending','actual_admission_decisions':None,'confirmed_application_receipt':None})
    envelope['required_concurrence']['C05']['status']='prospective direction accepted; final exact independent owner/effect scopes remain to be confirmed'
    save('review-envelope.json',envelope)
    save('materialization-recipe.json',{'authority_effect':'none','status':'deterministic prospective recipe; not applied outputs','preconditions':envelope['exact_currentness_preconditions'],
        'stable_review_inputs':[bind(STEP/'review-selection.json'),bind(STEP/'registry-postimage.json'),bind(STEP/'registration-delta.json'),bind(STEP/'activation-order.json')],
        'actual_owner_decisions':None,'application_receipt':None,
        'ordering':['Fresh exact interpretation/cohort/role-scope confirmation','Two profile meanings reviewed/admitted through existing v1 bootstrap','Exact profile mechanics and carrier type effects','Independent evaluation/lifecycle profile adoption','Foundational successor under applicable exact contracts','Binding-only Definition/v2 descriptor revision','Pack and Define exact semantic admission','One confirmed coherent final epoch selection; derivative compatibility mirrors thereafter'],
        'no_self_hash':'Reviewed recipe/inputs and actual Decisions are distinct from generated outputs/receipts. No receipt or owner-admitted registry is its own input.',
        'exactness':'Candidate bytes are frozen now. Applied bytes depend on actual qualified Decisions/effect evidence and must be instantiated and verified before any permitted publication. No future Decision IDs/digests are invented.'})
    # Final owner requests identify new material rather than silently refreshing
    # already selected conversational records.
    save('final-review-request.json',{'authority_effect':'none','status':'prepared for fresh review; no selected admission',
        'requests':[{'id':'FINAL-FIDELITY','owner_ref':'role:definition-owner','subjects':targets,'material':[bind(STEP/'formal-core.json'),bind(STEP/'formal-expression-correspondence.json'),bind(STEP/'voice-fidelity-review.json')],
            'question':'Confirm the exact fresh interpreted requirements, source/voice correspondence, scoped countermodels and explicit coverage ceilings without transferring earlier acceptance to unseen material.'},
           {'id':'FINAL-REPRESENTATION-IMPACT','owner_refs':['role:artifact-mechanics-owner','role:definition-owner','role:evidence-conformance-owner','role:artifact-type-owner'],
            'material':[bind(STEP/'registry-postimage.json'),bind(STEP/'consumer-impact-evidence.json'),bind(STEP/'drift-audit-postimage.json')],
            'question':'Confirm refreshed exact postimages/generator, corrected 34-source/2-evidence/1-subject classification, preserved records and independent scope/effect prerequisites.'}],
        'selection_options':['confirm exact bounded preparation','revise specified material','defer dependent route','reject specified proposed effect'],
        'ceiling':'No semantic admission, profile/type adoption or epoch/application authorization is requested by this author-only preparation file.'})
    exec_info={'schema_version':'cal.define-assurance-execution-bindings/v1','authority_effect':'none','python':sys.version,
        'python_executable':{'path':str(Path(sys.executable).resolve()),'sha256':sha(Path(sys.executable).resolve())},'jsonschema_version':importlib.metadata.version('jsonschema'),
        'executions':[{'script':bind(STEP/n),'argv':['python3',str((STEP/n).relative_to(ROOT))],
            'outputs':[bind(STEP/f) for f in outputs]} for n,outputs in [('check_assurance.py',['assurance-results.json','formal-core.json','witnesses.json','controls.json','bounded-cases.json']),('check_evidence.py',['evidence-results.json','source-closure.json','consumer-impact-evidence.json','evaluation-preview.json']),('verify_outputs.py',['independent-verification.json'])]],
        'earlier_profile_rules':{'evidence':bind(BASE/'steps/07-profile-formal-source-evidence/rule-results.json'),'status':'existing executed exact fixed rule evidence; original scope/date preserved, not rerun or relabeled'},
        'attempts_preserved':[str(p.relative_to(ROOT)) for p in sorted((STEP/'attempts').glob('*/attempt.json'))]}
    save('execution-bindings.json',exec_info)
    out=['# Define M1 — assurance evidence and complete review package','',
        '**All 16 explained proposals are accepted in conversation. No admission, profile/type adoption or current lookup change has occurred.**','',
        '## What is complete now','',
        '- Exact five-subject meanings remain byte-identical to those reviewed.',
        '- Pack/Define/Foundation assurance now has typed executed finite witnesses and concrete handling/compatibility cases.',
        '- Exact source and impact evidence, corrected reference classification, old/new dependency ordering and refreshed registry/index/drift postimages are assembled.',
        '- Previous runs and narrower/failed attempts are preserved with their original scope.','',
        '## Executed evidence','',
        '| Evidence | Result |','| --- | --- |',
        '| Joint interpreted core | Checked finite satisfiability witness; no inconsistent selected axiom found |',
        f"| Non-collapse | {assurance['comparison_pairs']} interpreted pairs / {assurance['directed_non_equivalence_witnesses']} directed countermodels |",
        f"| Boundary checks | {assurance['non_entailment_boundaries']} non-entailment countermodels |",
        f"| Controls | {assurance['controls_passed']} model/meaning controls, including same requirements under different labels and preparation-origin authority |",
        '| Pack handling | 1,048,576 assignments over four concepts, handling subsets and payload bits |',
        '| Additional bounded cases | 256 reference/gap, 24 source-posture, 48 specialization, 64 result/attempt and 96 carrier/standing cases |',
        '| Source closure | 41 exact source/selector/admission bindings; no technical reference gaps |',
        '| Independent verification | Stored typed witnesses rechecked without importing construction functions; 21 hostile schema changes rejected |',
        '| Existing profile rules | Earlier 3^14 aggregation, 72 eligibility guards and 576 state/gate/support cases remain exact referenced evidence |','',
        '[Assurance results](assurance-results.json) · [Stored witnesses](witnesses.json) · [Independent verification](independent-verification.json) · [Execution bindings](execution-bindings.json)','',
        'These are interpreted finite-model and bounded-case results. They are not a Lean theorem, full native provider/service qualification, natural-language equivalence certificate or whole-repository consistency proof.','',
        '## The two tightened Pack obligations','',
        'The model now explicitly requires the payload domain to equal the declared concept set and rejects undeclared/nonselected payloads. It also distinguishes authority claimed to originate in preparation from independently established action permission: a Pack can coexist with separate permission while granting none itself.','',
        '[Exact formal-expression correspondence](formal-expression-correspondence.json) · [All voices and author fidelity review](voice-fidelity-review.json)','',
        '## Consumer inventory correction','',
        'The earlier 37-record search mixed different reference kinds. Exact audit finds **34 direct source users, two evidence-reference users and the foundational predecessor itself**. Thus there are **36 actual Definition consumers among 37 impacted records**. All 37 exact records are preserved. This correction does not invent normative dependencies from text matches.','',
        'Three current type contracts, three selected operational/narrative consumers and the declared Define integration/contract documents are also assessed within their captured scope. Source-code witnesses are not runtime regression tests.','',
        '[Per-record impact evidence](consumer-impact-evidence.json)','',
        'All 183 current meanings are accounted for in 915 target/current-source screen rows, split into batches of 512 and 403. Only the selected interpreted pairs have formal witnesses; remaining rows say explicitly that they are not formalized.','',
        '[Coverage and excluded claims](comparison-coverage.json)','',
        '## Exact refreshed postimages','',
        '- [Registry postimage](registry-postimage.json) and [full generated index](DEFINITIONS-INDEX.md): **194 versions / 187 proposed identities**, including all 189 admitted versions. Live lookup remains 183 identities.',
        '- [Drift audit](drift-audit-postimage.json) and [human view](DEFINITION-DRIFT-AUDIT.md): conversational acceptance, fresh fidelity and missing adoption effects remain distinct.',
        '- [Type registry postimage](artifact-type-registry-postimage.json) and [registration delta](registration-delta.json): exact accepted candidate descriptor material preserved; no admitted rows fabricated.',
        '- [Representation bindings](representation-bindings.json), [source closure](source-closure.json), [owner routes](owner-route-evidence.json) and [accepted selections](accepted-review-selections.json).','',
        'The completeness specimen is still outside the five-subject selection. New metadata/generation/evidence bytes require final scoped confirmation; earlier postimage acceptance is not automatically transferred.','',
        '## What remains before admission','',
        '**E04 cannot be closed by author checks alone under the no-admission constraint.** Fresh interpretation/fidelity and final cohort/representation confirmation remain owner review subjects. Actual compatible profile/type standing still depends on the declared admission/adoption effects.','',
        'The honest [evaluation preview](evaluation-preview.json) therefore reports **NOT_EVALUABLE for all five current pre-decision assessments**. Shape/source/preservation checks passed where supported; missing full fidelity or adopted standing was not changed to PASS.','',
        '[Remaining obligations and scope](residue-disposition.json) · [Exact final review request](final-review-request.json)','',
        '**E05 remains separate implementation work:** strict M1 provider/exporter and runtime enforcement were not implemented or qualified by this evidence step. Existing CLI output and private/live state remain unchanged.','',
        '## Complete source and effect boundaries','',
        'The [review envelope](review-envelope.json) binds current Project State/registry/type/profile preconditions. The [activation order](activation-order.json) is acyclic and prospective. The [materialization recipe](materialization-recipe.json) separates exact reviewed inputs, future actual qualified Decisions and generated application outputs; no self-hash cycle or invented admission receipt is used.','',
        '[Frozen package manifest](package-manifest.json). Source currentness or interpretation changes reopen the affected review; historical receipts retain their original scope.','',
        '**Admission-ready: no. Admissions: 0. Runtime changes: 0. All authorable bounded evidence above is prepared for final review; absent owner/adoption facts remain explicit.**','']
    text('REVIEW.md','\n'.join(out))
    text('README.md','# Assurance evidence closure\n\nStart with the [complete review](REVIEW.md).\n\nAll 16 explained proposals are accepted within their scoped conditions. Bounded assurance/source/impact evidence is executed and independently checked. Fresh final fidelity and actual contract standing remain unresolved; no admission or runtime effect occurred.\n')
    # Self-independent manifest: local files and exact external sources form the
    # reviewed inputs; subsequent verification results are consequences.
    external={ROOT/f['path'] for f in load(STEP/'source-selection.json')['files'] if not (ROOT/f['path']).is_relative_to(STEP)}
    external.update(ROOT/f['path'] for f in load(OLD/'integrity-validation.json')['additional_frozen_source_files'])
    external.update(ROOT/b['path'] for b in envelope['exact_currentness_preconditions'])
    external.update(p for p in (BASE/'reviews').glob('*.json'))
    local=sorted(p for p in STEP.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='package-manifest.json')
    total=sum(p.stat().st_size for p in local)+sum(p.stat().st_size for p in external)
    assert total<=16_777_216,('selected output/review cohort exceeds 16 MiB',total)
    save('package-manifest.json',{'schema_version':'cal.define-final-assurance-review-manifest/v1','authority_effect':'none','status':'frozen candidate final review; not admission-ready','review_date':'2026-10-14',
        'files':[bind(p) for p in local],'external_inputs':[bind(p) for p in sorted(external)],'selected_review_bytes':total,
        'selected_meanings':targets,'prior_package':bind(OLD/'package-manifest.json'),'actual_admission_decisions':None,'confirmed_application':None,
        'exclusions':['self manifest','later final-verification output','mutable M1 progress/index/README','unselected/private/live state'],
        'scope':'Exact bounded interpreted evidence and explicit owner/effect prerequisites; no universal consistency or actual semantic/type/profile adoption claim.'})
    print(json.dumps({'local_files':len(local),'external_inputs':len(external),'review_bytes':total,'manifest':bind(STEP/'package-manifest.json'),'admission_ready':False}))

if __name__=='__main__':main()
