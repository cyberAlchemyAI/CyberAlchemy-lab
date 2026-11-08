#!/usr/bin/env python3
"""Create exact candidate projections. Never write admitted authority or apply effects.

Create-only outputs; prior evidence is referenced by digest, never relabeled.
This local preparation generator is not an admitted registry generator.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import sys
import jsonschema

STEP = Path(__file__).resolve().parent
BASE = STEP.parent.parent
ROOT = STEP.parents[5]

def load(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return str(Path(p).relative_to(ROOT))
def binding(p):
    p = Path(p)
    return {"path": rel(p), "sha256": sha(p), "bytes": p.stat().st_size}
def write(name, value):
    p = STEP / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f: f.write(value)
def dump(name, value): write(name, json.dumps(value, indent=2, sort_keys=True) + '\n')
def module(p, name):
    s = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m
def link(p, title): return f'[{title}]({os.path.relpath(p, STEP)})'
def esc(s): return str(s).replace('|', '\\|').replace('\n', ' ')

TARGETS = [
    ('01-definition-pack/definition.json', '83bb643b14b48980d85db9bd381c1d4b2ccd27b7bb890c9e24fd2848809dfe76'),
    ('02-cyberalchemy-define/definition.json', 'd4ba6c882cea56e3bc9cc425c356d9fbc34f5de83727f3426cadad1c4326f286'),
    ('03-foundational-definition/definition.json', '37a81341252f331236ff0a260edcc48d57ecae117559f50ebe11876a732abbe8'),
    ('07-profile-formal-source-evidence/definitions/definition-evaluation-profile/definition.json', '5cb480685961c24223e16796eeee0852a22bdf6f31249b379a11ec681d8727b1'),
    ('07-profile-formal-source-evidence/definitions/definition-lifecycle-profile/definition.json', '876835497765f255b3de998cf1786d3d5b2196d25a44ba66159e8185520944ac'),
]

def render_index(r):
    out = ['<!-- GENERATED from registry-postimage.json by build.py; candidate only. -->',
           '# Complete proposed Definition index', '',
           '189 inherited admitted versions + 5 unadmitted candidate versions. Proposed lookup: 187 identities. Live lookup: 183 identities.', '',
           '“Proposed current” describes a requested selection, not effective authority. Historical admission and lifecycle facts are preserved.', '',
           '| Term | Exact identity/version | Standing | Live current | Proposed current | JSON | SHA-256 |',
           '| --- | --- | --- | --- | --- | --- | --- |']
    baseline = load(ROOT / r['predecessor']['path'])
    for e in r['entries']:
        exact = e['definition_id'] + '@' + e['version']
        live = baseline['current_lookup'].get(e['definition_id']) == exact
        proposed = r['proposed_current_lookup'].get(e['definition_id']) == exact
        out.append('| ' + ' | '.join([esc(e['term']), '`'+exact+'`', e['lifecycle_state'], 'yes' if live else 'no',
                   'pending' if proposed and not live else ('retained' if proposed else 'no'),
                   link(ROOT / e['path'], 'record'), '`'+e['sha256']+'`']) + ' |')
    return '\n'.join(out) + '\n'

def main():
    registry_path = ROOT / 'authority/definitions/registry.json'
    live = load(registry_path)
    assert sha(registry_path) == '5f5472203c0cc90eb657422c77d935a5ee00a3559a0245c9a1063744e6babaf1'
    assert len(live['entries']) == 189 and len(live['current_lookup']) == 183
    prior = BASE / 'steps/07-profile-formal-source-evidence'
    assert sha(prior / 'package-manifest.json') == '89fceca8a9eb21e4efdc2b9e17a741f331f08c09c94a212e169e04d062834cc1'
    for f in load(prior / 'package-manifest.json')['files']:
        assert sha(ROOT / f['path']) == f['sha256'], f['path']
    baseline_paths = [registry_path, ROOT/'authority/definitions/DEFINITIONS-INDEX.md', ROOT/'authority/definitions/drift-audit.json',
        ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json',
        ROOT/'authority/profiles/definition/v1/evaluation.json', ROOT/'authority/profiles/definition/v1/lifecycle.json']
    baselines = [binding(p) for p in baseline_paths]
    for e in live['entries']: assert sha(ROOT/e['path']) == e['sha256'], e['path']
    targets = []
    checks = []
    for relative, expected in TARGETS:
        p = BASE / 'steps' / relative
        assert sha(p) == expected
        d = load(p)
        v = d['schema_version'].rsplit('/', 1)[-1]
        schema = ROOT / f'authority/artifact-types/definition/{v}/schema.json'
        gen = ROOT / f'authority/artifact-types/definition/{v}/generator.py'
        jsonschema.Draft202012Validator(load(schema)).validate(d)
        assert module(gen, 'def_'+v).render(d).rstrip() == (p.parent/'DEFINITION.md').read_text().rstrip()
        targets.append({**binding(p), 'definition_ref':d['definition_id']+'@'+d['version'],
                        'carrier_ref':d['classification']['artifact_type_ref'], 'schema':binding(schema), 'generator':binding(gen),
                        'human_projection':binding(p.parent/'DEFINITION.md'), 'admission_posture':'candidate-unadmitted'})
        checks.append({'check':'selected Definition schema and projection', 'subject':targets[-1]['definition_ref'], 'result':'PASS'})
    dump('selection.json', {'schema_version':'cal.define-exact-review-selection/v1', 'authority_effect':'none', 'targets':targets,
        'excluded_specimen':{**binding(BASE/'steps/03-foundational-definition/example-definition.json'),
                             'reason':'Illustrative incident completeness candidate, outside this five-subject admission proposal'},
        'status':'candidate-review-selection; no owner decision'})
    entries = copy.deepcopy(live['entries'])
    lookup = dict(live['current_lookup'])
    for t in targets:
        d = load(ROOT / t['path'])
        entries.append({'definition_id':d['definition_id'], 'version':d['version'], 'term':d['term'],
                        'path':t['path'], 'sha256':t['sha256'], 'lifecycle_state':'candidate-unadmitted'})
        lookup[d['definition_id']] = t['definition_ref']
    entries.sort(key=lambda e:(e['definition_id'], e['version']))
    registry = {'schema_version':'cyberalchemy-lab-definition-registry-postimage/v1',
        'record_id':'CAL-DEFINE-M1-REGISTRY-POSTIMAGE-08', 'status':'candidate-postimage', 'authority_effect':'none',
        'owner_ref':'role:definition-owner', 'predecessor':binding(registry_path), 'candidate_source':rel(STEP/'selection.json'),
        'entries':entries, 'proposed_current_lookup':dict(sorted(lookup.items())),
        'source_direction':{'canonical':'registry-postimage.json', 'human_projection':'DEFINITIONS-INDEX.md',
                            'projection_policy':'generated-only', 'generator_ref':rel(STEP/'build.py'), 'generator_sha256':sha(STEP/'build.py')},
        'claim_ceiling':'Exact candidate union and proposed lookup, not an applied owner-admitted mirror. Decision-specific admission metadata requires later reviewed materialization. Mixed v1/v2 representation compatibility is pending C05.'}
    dump('registry-postimage.json', registry)
    write('DEFINITIONS-INDEX.md', render_index(registry))
    # Preserve the old plan; stage a new delta using the latest exact semantic bindings.
    delta = load(BASE/'steps/05-carrier-foundational-compatibility/registration-delta.json')
    for idx, row in enumerate(delta['proposed_new_registrations']):
        row['semantic_definition_refs'] = [targets[idx+3]['definition_ref']]
    descriptor_paths = [prior/'staged-carriers/definition-evaluation-profile/artifact.json',
        prior/'staged-carriers/definition-lifecycle-profile/artifact.json',
        BASE/'steps/05-carrier-foundational-compatibility/carriers/definition-binding-successor/artifact.json']
    delta['proposed_descriptor_revisions'] = [{**binding(p),'artifact_type_ref':load(p)['artifact_type_ref']} for p in descriptor_paths]
    delta['promotion_dependencies'] = [targets[3],targets[4],targets[2]]
    delta['supersedes_for_this_review_only'] = binding(BASE/'steps/05-carrier-foundational-compatibility/registration-delta.json')
    dump('registration-delta.json', delta)
    type_live = load(baseline_paths[3])
    dump('artifact-type-registry-postimage.json', {'schema_version':'cal.define-artifact-type-registry-postimage/v1',
        'authority_effect':'none','status':'candidate-postimage','predecessor':binding(baseline_paths[3]),
        'inherited_admitted_contracts':type_live['admitted_contracts'], 'inherited_current_by_identity':type_live['current_by_identity'],
        'proposed_new_registrations':delta['proposed_new_registrations'], 'proposed_descriptor_revisions':delta['proposed_descriptor_revisions'],
        'proposed_selection_policy':'Select evaluation-profile/v2 and lifecycle-profile/v2 for new Definition/v2 use only after exact type/profile adoption; preserve existing exact v1 uses. Definition/v2 gets a binding-only descriptor revision, not a second ambiguous instance discriminator.',
        'claim_ceiling':'Exact inherited contracts plus pending deltas. No fabricated admitted rows, no implicit withdrawal or current type selection.'})
    impacts = load(BASE/'steps/05-carrier-foundational-compatibility/consumer-impact.json')
    current_consumers = impacts['current_definition_consumers']
    for c in current_consumers: assert sha(ROOT/c['path']) == c['sha256']
    active_consumers = []
    for c in impacts['selected_operational_consumers']:
        active_consumers.append({**binding(ROOT/c['path']), 'previous_captured_sha256':c['sha256'],
             'changed_since_step5':sha(ROOT/c['path']) != c['sha256'], 'recommended_disposition':c['disposition'], 'owner_acceptance':'pending'})
    dump('consumer-compatibility.json', {'schema_version':'cal.define-exact-consumer-compatibility/v1','authority_effect':'none',
        'current_definition_consumers':current_consumers, 'current_type_consumers':impacts['current_type_consumers'],
        'selected_operational_consumers':active_consumers,'disposition_status':'author recommendations; no owner acceptance',
        'historical_discovery':binding(BASE/'steps/05-carrier-foundational-compatibility/consumer-impact.json'),
        'scope_limit':impacts['scope_limit'], 'source_change_policy':'Changed narrative recaptured; step5 receipt retains its original scope and may be stale. No prior receipt is made current by this capture.'})
    meanings = [load(ROOT/t['path']) for t in targets]
    examples = [
        'INC-1042: reuse Incident, specialize the application of Work, propose identifier completeness, and keep account exclusivity open. A complete four-way disposition table can still be unready for the intended use.',
        'The incident-investigation consumer invokes Define to clarify the evidence it needs. The result is a Pack covering the declared concepts. It does not resolve the incident, authorize extraction, or propose a follow-up Intent as Define output.',
        'For snapshot S-1042, account A and filters F, RequiredIds(S,A,F) must be a subset of ExportedIds(E). With 12,000 required IDs and 11,800 matched IDs, 200 are missing: completeness is false. The specimen is a scoped draft, outside this admission cohort.',
        'Evaluation rules select the exact completeness draft, evidence and phase. Schema/projection checks may pass while owner fidelity is pending. Pre-decision eligibility requires checks 1–12 PASS and check 13 NOT_EVALUABLE solely because selection is pending; it is not a completed admission.',
        'The completeness draft remains authored until evidence supports a permitted transition. A review record supports owner-reviewed; an owner Decision and confirmed application support admitted. Finding 200 missing IDs does not itself change the Definition lifecycle or close the incident.',
    ]
    questions = [
        'Does exactly one disposition per declared concept preserve specialization as application versus proposed meaning, explicit gaps and use-relative readiness without implying complete discovery?',
        'Does this define a capability outcome, preserving the originating Intent and the separation from Method, CLI, actor, solution selection and subsequent Intent proposals?',
        'Are unchanged normative meaning/formal expression/scope and the exact-carrier/profile criterion compatible with the predecessor and all required consumers?',
        'Does the finite frame retain the normative requirements and conditional implication (not biconditional), including causal blockers, named phases and the non-entailment of execution/admission?',
        'Does the finite frame retain subject, directed transitions, invalidation/history and separation of gates, state record, Decision and applied effect without inventing temporal proof?',
    ]
    decisions = []
    for idx, t in enumerate(targets):
        decisions.append({'decision_id':f'F{idx+1:02}', 'kind':'meaning-source-voice-interpretation-fidelity',
            'owner_ref':'role:definition-owner','subjects':[t], 'question':questions[idx],
            'recommendation':'Keep the revised meaning within its declared scope; require attributable exact owner fidelity review and stated evidence limits.',
            'evidence': 'Bounded two-profile source/model correspondence' if idx>=3 else 'Author distinction/compatibility analysis only; remaining semantic assurance is not replaced by this package',
            'example':examples[idx], 'status':'pending','selected_outcome':None,
            'permitted_outcomes':['accept-with-exact-scope','revise','defer','reject'],
            'acceptance_is_admission':False})
    compat = [
        ('C01','role:definition-owner',[targets[2]],'Foundational criterion and mixed version use',
         'Accept the exact applicable carrier/profile criterion prospectively; retain the unchanged normative statement, formula and authority scope. Do not retroactively invalidate v1 meanings.'),
        ('C02','role:definition-owner',[binding(STEP/'consumer-compatibility.json')],'Current consumer dispositions',
         'Review each of the 37 exact current Definition premises, three type contracts and selected runtime/narrative consumers; preserve exact pinned historical contracts. Acceptance must cover all declared affected consumers, not infer compatibility from search matches.'),
        ('C03','role:definition-owner',[binding(BASE/'steps/03-foundational-definition/compatibility-review.json')],'Historical governed-by reference',
         'Preserve the old Definition→Role reference in exact admitted history; omit automatic transfer to the successor. Keep semantic_owner_ref. A new governed-by edge requires an exact Constitution endpoint and its own route.'),
        ('C04','role:definition-owner',[binding(BASE/'steps/03-foundational-definition/compatibility-review.json')],'Historical originates-from reference',
         'Preserve source-admission lineage and omit automatic Source Admission→Source conversion. No Source node or typed relation is created. Any later origin edge requires the exact Source endpoint and qualifier.'),
        ('C05','role:artifact-mechanics-owner',[binding(STEP/'registry-postimage.json'),binding(STEP/'artifact-type-registry-postimage.json')],'Registry, generated index and drift representation compatibility',
         'Approve a mixed v1/v2 candidate projection and later explicit owner-mirror representation amendment. Historical registry definition_artifact_type_ref=v1 and its old closed schema cannot silently authorize or describe v2 additions. Use exact per-subject representation bindings; do not install this candidate schema as admitted policy.'),
        ('C06','role:artifact-mechanics-owner',[binding(BASE/'steps/04-definition-v2-profiles/profile-carriers.schema.json'),binding(BASE/'steps/04-definition-v2-profiles/generator.py'),binding(BASE/'steps/05-carrier-foundational-compatibility/schema-amendment.json')],'Profile schema/generator evolution',
         'Review the closed v2 schema, selectors, generator and structural witnesses. Runtime enforcement remains declared residue; mechanics acceptance does not admit types or semantics.'),
        ('C07','role:artifact-type-owner',[binding(descriptor_paths[0]),binding(STEP/'registration-delta.json')],'Evaluation-profile/v2 type registration',
         'Register only after the exact Evaluation Profile semantic Definition is independently admitted using the existing v1 bootstrap route. Candidate bindings cannot count as admitted-current meanings.'),
        ('C08','role:artifact-type-owner',[binding(descriptor_paths[1]),binding(STEP/'registration-delta.json')],'Lifecycle-profile/v2 type registration',
         'Register only after the exact Lifecycle Profile semantic Definition is independently admitted using the existing v1 bootstrap route; preserve v1 contracts and their exact subjects.'),
        ('C09','role:evidence-conformance-owner',[binding(BASE/'steps/04-definition-v2-profiles/evaluation.json'),binding(BASE/'steps/04-definition-v2-profiles/check-contracts.json')],'Definition/v2 evaluation profile adoption',
         'Adopt the exact phase and eligibility rules only for the declared Definition/v2 use after mechanics/type effects. Model/rule evidence is not an Evaluation PASS for every proposed subject.'),
        ('C10','role:definition-owner',[binding(BASE/'steps/04-definition-v2-profiles/lifecycle.json'),binding(BASE/'steps/04-definition-v2-profiles/check-contracts.json')],'Definition/v2 lifecycle profile adoption',
         'Adopt the exact six-state gates, invalidation and history-preservation contract independently; a declaration performs no lifecycle transition.'),
        ('C11','role:artifact-type-owner',[binding(descriptor_paths[2])],'Definition/v2 binding-only successor descriptor',
         'Rebind to the admitted foundational successor after exact admission; preserve instance schema/discriminator and relation roles. Do not create a parallel competing current type or automatically rebind historical instances.'),
    ]
    for id_, owner, subjects, title, recommendation in compat:
        decisions.append({'decision_id':id_,'kind':'compatibility-or-independent-contract-adoption','owner_ref':owner,
           'subjects':subjects,'question':title,'recommendation':recommendation,'status':'pending','selected_outcome':None,
           'permitted_outcomes':['accept-with-exact-scope','revise','defer','reject'],'acceptance_is_admission':False})
    dump('remaining-decisions.json', {'schema_version':'cal.define-exact-pending-review-decisions/v1','authority_effect':'none',
        'decisions':decisions,'decision_ids_are':'Local pending review item labels, not Lab Decision records',
        'authorization_route':'Existing admitted role assignments; attributable human owner review must identify the exact role/scope/subject and effect. Local keys, ARE receipts and agent authorship cannot supply owner acceptance.',
        'separation':'One principal may hold several roles; determinations remain independently scoped. Acceptance of fidelity/compatibility does not select admission or confirm application.'})
    # Explicit evidence work remains separate from the pending owner decisions.
    residue = [
        {'id':'E01','status':'open','blocks':'pre-decision semantic readiness of Pack and Define',
         'required':'Complete the declared formal non-collapse/consistency evidence and clause correspondence for Pack and Define; existing nine author comparisons are not executed formal evidence.', 'subjects':[targets[0],targets[1]]},
        {'id':'E02','status':'open','blocks':'pre-decision readiness of foundational successor',
         'required':'Provide scoped successor semantic/compatibility evidence covering its changed criterion and old embedded-reference dispositions; unchanged normative fields alone do not prove full compatibility.', 'subjects':[targets[2]]},
        {'id':'E03','status':'open','blocks':'any wider consistency or universal compatibility claim',
         'required':'183 current meanings are reference-captured, not all formalized. Close the required comparison/impact scope or explicitly narrow it under attributable review; do not interpret the 13 tested profile pairs as whole-repository consistency.', 'subjects':[binding(prior/'comparison-selection.json'),binding(STEP/'consumer-compatibility.json')]},
        {'id':'E04','status':'open','blocks':'admission-ready actual evidence package',
         'required':'Evaluate the exact final selected subjects/package against applicable adopted contracts, then obtain attributable fidelity/compatibility reviews. Current structural checks do not stand in for all 12 pre-decision checks.', 'subjects':targets},
        {'id':'E05','status':'open','blocks':'M1 operational preview completion, not semantic admission by itself',
         'required':'Implement the strict candidate provider/exporter and immutable context/ontology/review integration under the approved later M1 work. No working implementation or live agent run is claimed here.', 'subjects':[]},
    ]
    dump('evidence-residue.json', {'schema_version':'cal.define-review-evidence-residue/v1','authority_effect':'none','items':residue})
    bindings = []
    for d,t in zip(meanings,targets):
        bindings.append({'definition_ref':t['definition_ref'],'declared_index_entry':d['index_entry'],
            'resolved_candidate_index':binding(STEP/'DEFINITIONS-INDEX.md'),'resolved_registry':binding(STEP/'registry-postimage.json'),
            'declared_drift_route':d['drift_route'],'aggregate_audit_path':rel(STEP/'drift-audit-postimage.json'),
            'resolution_scope':'This exact candidate package only; no global alias or authority registration',
            'original_audit_evidence':binding(ROOT/d['drift_route']['audit_ref']) if not d['drift_route']['audit_ref'].startswith('candidate:') else binding(BASE/'steps/01-definition-pack/distinction-review.json')})
    dump('representation-bindings.json', {'schema_version':'cal.define-postimage-representation-bindings/v1','authority_effect':'none',
        'subjects':bindings,'virtual_ref_resolution':{'candidate:define-m1:DEFINITIONS-INDEX':binding(STEP/'DEFINITIONS-INDEX.md'),
            'candidate:define-m1:definition-pack:distinction-review':binding(BASE/'steps/01-definition-pack/distinction-review.json')},
        'note':'Draft source bytes stay unchanged. Companion bindings resolve review surfaces; they do not appoint owners or replace admitted registry contracts.'})
    findings = []
    for d in decisions:
        findings.append({'finding_id':d['decision_id'],'severity':'blocker','status':'pending-owner-review',
            'target':d['subjects'][0]['path'],'condition':d['question'],'remediation':d['recommendation'],
            'blocking_for':'exact selected effect and required subject admission scope; independent owners remain separate'})
    for e in residue:
        findings.append({'finding_id':e['id'],'severity':'warning' if e['id'] in ['E03','E05'] else 'blocker',
            'status':'open-evidence-obligation','target':e['subjects'][0]['path'] if e['subjects'] else rel(BASE),
            'condition':e['required'],'remediation':'Prepare evidence within the declared scope before assigning PASS or requesting its effect.', 'blocking_for':e['blocks']})
    audit = {'schema_version':'cal.define-definition-drift-postimage/v1','title':'M1 exact candidate drift and decision audit',
        'authority_effect':'none','status':'candidate-evidence','owner_ref':'role:evidence-conformance-owner',
        'registry_ref':rel(STEP/'registry-postimage.json'),'registry_sha256':sha(STEP/'registry-postimage.json'),
        'baseline_audit':binding(baseline_paths[2]),'inherited_findings':load(baseline_paths[2])['findings'],
        'summary':{'inherited_admitted_versions':189,'candidate_versions':5,'proposed_total_versions':194,
                   'live_current_identities':183,'proposed_current_identities':187,'pending_owner_determinations':len(decisions),
                   'open_evidence_obligations':len(residue),'new_source_admissions':0,'admission_ready':False},
        'findings':findings,'source_direction':{'canonical':'drift-audit-postimage.json','human_projection':'DEFINITION-DRIFT-AUDIT.md','generator_ref':rel(STEP/'build.py'),'generator_sha256':sha(STEP/'build.py')},
        'claim_ceiling':'Historical findings retain historical scope. This audit is not a new zero-drift or universal consistency result; all pending determinations and evidence obligations remain open.'}
    dump('drift-audit-postimage.json',audit)
    write('DEFINITION-DRIFT-AUDIT.md', '# Candidate drift audit\n\nGenerated from `drift-audit-postimage.json`. No authority effect.\n\n'+'\n'.join(f"## {f['finding_id']} — {f['status']}\n\n{f['condition']}\n\nRequired: {f['remediation']}\n\nBlocks: {f['blocking_for']}\n" for f in findings))
    nodes = [
        {'id':'PROFILE-MEANINGS','depends_on':[],'subjects':[targets[3],targets[4]],'route':'existing admitted Definition/v1 and v1 review profiles'},
        {'id':'PROFILE-MECHANICS','depends_on':[],'subjects':decisions[10]['subjects'],'route':'independent mechanics owner'},
        {'id':'PROFILE-TYPES','depends_on':['PROFILE-MEANINGS','PROFILE-MECHANICS'],'subjects':[binding(p) for p in descriptor_paths[:2]],'route':'artifact-type owner; admitted semantic bindings required'},
        {'id':'PROFILE-ADOPTION','depends_on':['PROFILE-TYPES'],'subjects':[binding(BASE/'steps/04-definition-v2-profiles/evaluation.json'),binding(BASE/'steps/04-definition-v2-profiles/lifecycle.json')],'route':'separate evidence and Definition lifecycle owners'},
        {'id':'FOUNDATIONAL-SUCCESSOR','depends_on':['PROFILE-ADOPTION'],'subjects':[targets[2]],'route':'exact v2 subject review, evidence and compatibility decisions'},
        {'id':'DEFINITION-BINDING','depends_on':['FOUNDATIONAL-SUCCESSOR'],'subjects':[binding(descriptor_paths[2])],'route':'binding-only artifact-type owner effect'},
        {'id':'PACK-AND-DEFINE','depends_on':['PROFILE-ADOPTION','FOUNDATIONAL-SUCCESSOR','DEFINITION-BINDING'],'subjects':targets[:2],'route':'separate exact v2 Definition review; formal/fidelity obligations open'},
        {'id':'COHERENT-VISIBILITY','depends_on':['PACK-AND-DEFINE','PROFILE-MEANINGS','PROFILE-MECHANICS','PROFILE-TYPES','PROFILE-ADOPTION','FOUNDATIONAL-SUCCESSOR','DEFINITION-BINDING'],'subjects':[],'route':'single frozen Project State epoch and explicit derivative mirror compatibility recipe; no application here'},
    ]
    # Choose by label rather than a positional review-target dependency.
    nodes[1]['subjects'] = next(d['subjects'] for d in decisions if d['decision_id']=='C06')
    dump('activation-order.json', {'schema_version':'cal.define-exact-activation-recipe/v1','authority_effect':'none','nodes':nodes,
        'status':'prospective dependency ordering; no selected or applied nodes','visibility':'Logical effects may be prepared in dependency order inside one reviewed immutable cohort; expose no intermediate current lookup. One actual final epoch commit remains separate from these candidates.'})
    dump('materialization-recipe.json', {'schema_version':'cal.define-decision-dependent-materialization/v1','authority_effect':'none',
        'review_inputs':[binding(STEP/'selection.json'),binding(STEP/'registry-postimage.json'),binding(STEP/'registration-delta.json'),binding(STEP/'drift-audit-postimage.json')],
        'preconditions':baselines,'actual_owner_decisions':None,'application_receipt':None,
        'future_recipe':['Recheck all frozen source digests and required evidence/review outcomes; changed bytes invalidate affected reviews.',
            'Bind actual scoped owner Decision records to exact semantic subjects, mechanics/types and profile effects separately; never generate acceptance from this proposal.',
            'After approved representation amendment, generate applied registry/mirrors from the candidate selection plus actual Decision metadata. Their admission_decision_ref, status and bytes cannot be finalized before those inputs exist.',
            'Digest the resulting immutable outputs; prepare the effect envelope with explicit before/after selections and rollback/history preservation.',
            'Confirm one authorized Project State epoch visibility effect; generated application evidence refers to the selected inputs/outputs without being its own input. No circular receipt/registry/Decision hashes.'],
        'exactness_boundary':'Candidate postimages are complete exact bytes now. Applied owner-admitted postimages are decision-dependent outputs, not fabricated exact futures. A later manifest/review binds those exact generated bytes before application.'})
    # Native preparation checks only: no old mutating validators, admission builders or runtime tests.
    assert len(entries)==194 and len(lookup)==187
    assert len({(e['definition_id'],e['version']) for e in entries})==194
    assert all(e in entries for e in live['entries'])
    selected_new = [e for e in entries if e['lifecycle_state']=='candidate-unadmitted']
    assert len(selected_new)==5 and all('admission_decision_ref' not in e for e in selected_new)
    assert all(v in {e['definition_id']+'@'+e['version'] for e in entries} for v in lookup.values())
    assert len([k for k in live['current_lookup'] if lookup[k]!=live['current_lookup'][k]])==1
    assert len(current_consumers)==37
    assert not any(load(ROOT/t['path'])['definition_id']=='cal.definition.export-identifier-completeness' for t in targets)
    assert (STEP/'DEFINITIONS-INDEX.md').read_text()==render_index(registry)
    todo=set();done=set()
    while len(done)<len(nodes):
        ready=[n['id'] for n in nodes if n['id'] not in done and set(n['depends_on'])<=done]
        assert ready,'dependency cycle';done.update(ready)
    for b in baselines: assert sha(ROOT/b['path'])==b['sha256']
    checks += [{'check':name,'result':'PASS'} for name in ['189 inherited rows and digests preserved','194 unique versions / 187 proposed identities',
        'five pending entries have no fabricated admission decision','one current identity successor and four added identities',
        '37 exact current Definition consumer records preserved','generated index parity','acyclic prospective activation order','live registry/index/drift/type/profile bytes unchanged']]
    dump('review-checks.json',{'schema_version':'cal.define-exact-postimage-checks/v1','authority_effect':'none','checks':checks,
        'admission_ready':False,'admissions':0,'runtime_tests_executed':False,'claim_ceiling':'Structural and integrity preparation only; no semantic/effect or full profile PASS.'})
    dump('baselines.json',{'schema_version':'cal.define-postimage-baselines/v1','authority_effect':'none','files':baselines,
        'registered_definitions':live['entries'],'preserve_all_history':True})
    # External reviewed references are frozen alongside the exact local candidate files.
    external = set()
    for p in (BASE/'steps').rglob('*'):
        if p.is_file() and STEP not in p.parents and '__pycache__' not in p.parts: external.add(p)
    for p in baseline_paths: external.add(p)
    for e in live['entries']: external.add(ROOT/e['path'])
    for c in active_consumers: external.add(ROOT/c['path'])
    for t in targets:
        external.update([ROOT/t['schema']['path'],ROOT/t['generator']['path']])
    for f in load(prior/'source-selection.json')['files']: external.add(ROOT/f['path'])
    dump('review-inputs.json',{'schema_version':'cal.define-frozen-exact-review-inputs/v1','authority_effect':'none',
        'files':[binding(p) for p in sorted(external)], 'historical_receipts':'Historical receipts preserve their captured scope. This current hash selection does not rerun or refresh their results.'})
    out=['# Define M1 — complete exact review package', '',
        '**Prepared candidate bytes. Not admission-ready. No owner acceptance, current lookup change or runtime effect.**', '',
        '## What would change', '',
        '- Definition versions: **189 → 194**. Current identities: **183 → 187**.',
        '- Four new meanings and one foundational Definition successor. Every historical admitted row and source byte is retained.',
        '- The completeness specimen remains an illustration outside the cohort. All examples below are synthetic incident fixtures.', '',
        '## Exact proposed surfaces', '',
        '- [Registry postimage](registry-postimage.json) and [complete generated index](DEFINITIONS-INDEX.md).',
        '- [Drift postimage](drift-audit-postimage.json) and [human drift audit](DEFINITION-DRIFT-AUDIT.md).',
        '- [Type registry postimage](artifact-type-registry-postimage.json) and [latest registration delta](registration-delta.json).',
        '- [Per-subject representation/index/drift bindings](representation-bindings.json).',
        '- [Exact selection](selection.json), [frozen review inputs](review-inputs.json) and [integrity checks](review-checks.json).', '',
        'The candidate registry follows the existing candidate-postimage convention. Its pending rows have no invented admission Decision. The old live registry and foundation schema are not silently amended. C05 explicitly requests the mixed-representation/mirror compatibility decision.', '',
        '## The five revised meanings and examples', '']
    for idx,(d,t) in enumerate(zip(meanings,targets)):
        out += [f"### {idx+1}. {d['term']}", '', f"Exact: `{t['definition_ref']}` · SHA-256: `{t['sha256']}`", '',
                link(ROOT/t['human_projection']['path'],'Complete Definition, all voices, notation, boundaries and sources'), '',
                d['voices']['scientific_formal']['normative_statement'], '',
                '**Incident example**', '', examples[idx], '', '**Fidelity decision**', '', questions[idx], '']
    out += ['## Remaining owner decisions', '',
        'These are pending local review items, not admitted Lab Decisions. Recommended dispositions have not been selected. Each acceptance must name exact subject, role, scope and evidence; semantic fidelity acceptance, profile/type adoption and admission are separate effects.', '',
        '| Item | Owner role | Question / recommendation |', '| --- | --- | --- |']
    for d in decisions: out.append(f"| {d['decision_id']} | `{d['owner_ref']}` | {esc(d['question'])}. {esc(d['recommendation'])} |")
    out += ['', '[Exact subjects and permitted review outcomes](remaining-decisions.json).', '',
        '## Evidence that still needs work', '',
        'Owner approval alone does not close missing evidence. [Evidence residue](evidence-residue.json) records separate readiness blockers.', '']
    out += [f"- **{e['id']}** — {e['required']} Blocks: {e['blocks']}." for e in residue]
    out += ['', '## What the executed profile evidence establishes', '',
        'Two profile meanings have exact source closure (24 bindings), checked finite joint satisfiability, 13 pair comparisons in 26 directions, 11 non-entailment boundaries and exhaustive fixed-profile aggregation/state checks. This supports the stated interpreted frames; it is not a mechanized theorem, complete natural-language fidelity review or whole-repository consistency proof.', '',
        link(prior/'REVIEW.md','Executed evidence, coverage and preserved attempts'), '',
        'The 37 current Definition consumers and three type contracts have explicit proposed preservation dispositions. The practical guide changed after the older step-5 capture and is recaptured here; its old receipt is not relabeled current. Unknown/external/private consumers remain outside the compatibility claim.', '',
        '## Activation and exact future outputs', '',
        '[Dependency ordering](activation-order.json): v1 bootstrap for the two profile meanings → mechanics/types → profile adoption → foundational successor → Definition/v2 binding → Pack and Define → one coherent epoch visibility effect.', '',
        'This is an acyclic prospective recipe, not staged effective admission. Local signing material cannot appoint a semantic owner. The final Project State commit and any derivative mirror update require explicit compatible effects.', '',
        '[Materialization recipe](materialization-recipe.json) separates exact reviewed candidate inputs, actual selected owner Decisions and generated applied outputs. Applied postimages require actual Decision metadata and will have different bytes. No self-referential hash or fake future Decision closes that gap.', '',
        '## Review order', '',
        '1. Finish E01–E04 in their required scopes; inspect the five meanings and source/formal correspondence.',
        '2. Record independently attributable F01–F05 fidelity determinations and C01–C11 compatibility/mechanics/type/profile determinations for the exact subjects.',
        '3. Re-freeze any changed candidate/evidence cohort and evaluate the applicable pre-decision checks before preparing an admission request.',
        '4. Prepare Decision-specific exact outputs and permitted application only after required decisions are selected. E05 remains the subsequent M1 implementation task.', '',
        '**Current admissions: 0. Runtime changes: 0. M1 remains in progress.**', '']
    write('REVIEW.md','\n'.join(out))
    print(json.dumps({'versions':194,'proposed_current':187,'pending_owner_items':len(decisions),'open_evidence_items':len(residue),'checks':len(checks),'admissions':0}))

if __name__=='__main__': main()
