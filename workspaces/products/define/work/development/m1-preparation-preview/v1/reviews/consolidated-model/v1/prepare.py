#!/usr/bin/env python3
"""Create one descriptive review package; never select or apply authority effects."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[7]
BASE = ROOT / 'define/development/m1-preparation-preview/v1'
OUT = Path(__file__).resolve().parent


def load(path):
    return json.loads((ROOT / path).read_text())


def ref(path):
    path = Path(path)
    absolute = path if path.is_absolute() else ROOT / path
    data = absolute.read_bytes()
    return {'path': str(absolute.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def write(name, data):
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n' if not isinstance(data, str) else data
    with (OUT / name).open('x') as target:
        target.write(text)


def relative(path):
    import os
    return os.path.relpath(ROOT / path, OUT)


def link(path, label):
    return f'[{label}]({relative(path)})'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


checks = []


def check(name, predicate, detail=''):
    checks.append({'check_id': name, 'outcome': 'PASS' if predicate else 'FAIL', 'detail': detail})
    if not predicate:
        raise ValueError(f'{name}: {detail}')


prefix = str(BASE.relative_to(ROOT))
step9 = prefix + '/steps/09-assurance-evidence-closure'
step10 = prefix + '/steps/10-profile-meanings-v1-owner-package'
step4 = prefix + '/steps/04-definition-v2-profiles'
mapping = step10 + '/mapping-determination-v1'
selection = load(step9 + '/package-manifest.json')['selected_meanings']
profiles = {k: load(step4 + '/' + k + '.json') for k in ['evaluation', 'lifecycle']}
contract = load(step4 + '/check-contracts.json')
activation = load(step9 + '/activation-order.json')
work = load('define/proposals/0005-amended-integration-plan/work-items.json')
limits = load(prefix + '/reviews/e04-final-review/v1/assurance-limits.json')
registry = load('authority/definitions/registry.json')
current = registry['current_lookup']
protected_paths = [
    'authority/definitions/registry.json', 'authority/definitions/DEFINITIONS-INDEX.md',
    'authority/definitions/drift-audit.json',
    'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json',
    'authority/project-state-transitions/current.json',
    'authority/owners/foundation-01/v1/owners.json',
    'authority/profiles/definition/v1/evaluation.json', 'authority/profiles/definition/v1/lifecycle.json',
]
protected = [ref(p) for p in protected_paths]
check('baseline-version-count', len(registry['entries']) == 189)
check('baseline-current-count', len(current) == 183)
check('live-types', len(load(protected_paths[3])['admitted_contracts']) == 143)
check('five-selected-meanings', len(selection) == 5)
check('all-selected-candidate3', all(x['definition_ref'].endswith('@1.0.0-candidate.3') for x in selection))

# Recheck each frozen input in the existing packages. This is a fresh integrity
# check; old formal/runtime/evaluation conclusions are not rerun or upgraded.
seals = [step9 + '/package-manifest.json', step10 + '/package-manifest.json',
         step10 + '/supplement-01-authored-postimage/package-manifest.json',
         step10 + '/owner-package-manifest.json', mapping + '/package-manifest.json']
bound = {}
for path in seals:
    d = load(path)
    for item in d.get('files', []) + d.get('external_inputs', []) + d.get('component_seals', []):
        observed = ref(item['path'])
        check('sealed:' + item['path'], observed['sha256'] == item['sha256'], 'Exact selected bytes; historical conclusions retain their original scope.')
        if 'bytes' in item:
            check('size:' + item['path'], observed['bytes'] == item['bytes'])
        bound[item['path']] = observed
    bound[path] = ref(path)

for item in selection:
    d = load(item['path'])
    check('subject-hash:' + d['definition_id'], ref(item['path'])['sha256'] == item['sha256'])
    jsonschema.Draft202012Validator(load(item['schema']['path'])).validate(d)
    check('schema:' + d['definition_id'], True)
    renderer = module(item['generator']['path'], 'definition_' + d['definition_id'].replace('.', '_'))
    first, second = renderer.render(d), renderer.render(d)
    check('projection:' + d['definition_id'], first == second == (ROOT / item['human_projection']['path']).read_text())

profile_schema = load(step4 + '/profile-carriers.schema.json')
profile_renderer = module(step4 + '/generator.py', 'profile_renderer')
for kind, d in profiles.items():
    wrapped = dict(profile_schema, **{'$ref': '#/$defs/' + kind + 'Profile'})
    jsonschema.Draft202012Validator(wrapped).validate(d)
    check('profile-schema:' + kind, True)
    check('profile-projection:' + kind, profile_renderer.render(d) == (ROOT / step4 / (kind.upper() + '.md')).read_text())
    check('profile-check-binding:' + kind, d['binding_contract_sha256'] == ref(step4 + '/check-contracts.json')['sha256'])
check('fourteen-checks', len(contract['checks']) == len(profiles['evaluation']['checks']) == 14)
check('check-order-and-identities', [x['check_id'] for x in contract['checks']] == [x['check_id'] for x in profiles['evaluation']['checks']])
check('six-states', len(profiles['lifecycle']['states']) == 6)
check('nine-transition-pairs', len(profiles['lifecycle']['transitions']) == 9)
check('nonempty-predecision', len(contract['phases']['pre_decision']) == 12)
check('decision-excluded-from-predecision', not set(contract['phases']['decision']) & set(contract['phases']['pre_decision']))
check('application-excluded-from-predecision', not set(contract['phases']['application']) & set(contract['phases']['pre_decision']))


def acyclic(rows, key):
    graph = {x[key]: x['depends_on'] for x in rows}
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            return False
        if node in visited:
            return True
        if node not in graph:
            return False
        visiting.add(node)
        if not all(visit(parent) for parent in graph[node]):
            return False
        visiting.remove(node)
        visited.add(node)
        return True
    return all(visit(node) for node in graph)


check('activation-dag', acyclic(activation['nodes'], 'id'))
check('work-map-dag', acyclic(work['work_items'], 'work_id'))
check('complete-work-map', len(work['work_items']) == work['work_item_count'] == 79)
check('registered-limits', len(limits['items']) == 17)
new_reg = load(step9 + '/registry-postimage.json')
check('full-cohort-versions', len(new_reg['entries']) == 194)
check('full-cohort-identities', len(new_reg['proposed_current_lookup']) == 187)
new_by_identity = {(x['definition_id'], x['version']): x for x in new_reg['entries']}
check('historical-rows-preserved', all(new_by_identity.get((x['definition_id'], x['version'])) == x for x in registry['entries']))
meaning_eval = load(mapping + '/evaluation-refresh.json')
check('actual-readiness-still-pending', all(not x['eligible_for_admission'] for x in meaning_eval['actual_evaluations']))
check('conditional-results-nonactual', all(x['actual'] is False for x in meaning_eval['conditional_after_exact_review']))
request = load(mapping + '/review-request.json')
check('mapping-unselected', request['selected'] is False and request['actual_decision_ref'] is None)

direct = [
    'define/INTEGRATION.md', 'define/runtime.json', 'implementation/define-cli/v1/CONTRACT.md',
    'define/proposals/0005-amended-integration-plan/WORK-MAP.md',
    'define/proposals/0005-amended-integration-plan/DESIGN.md',
    'define/proposals/0005-amended-integration-plan/work-items.json',
    prefix + '/reviews/e04-final-review/v1/assurance-limits.json',
    prefix + '/steps/03-foundational-definition/example-definition.json',
    prefix + '/steps/02-cyberalchemy-define/example.json',
    step9 + '/registration-delta.json', step9 + '/activation-order.json',
    step9 + '/assurance-results.json', step9 + '/consumer-impact-evidence.json',
    step9 + '/registry-postimage.json', step9 + '/artifact-type-registry-postimage.json',
    mapping + '/review-request.json', mapping + '/evaluation-refresh.json',
    step10 + '/supplement-01-authored-postimage/registry-representation-mapping.json',
]
for path in direct + protected_paths:
    bound[path] = ref(path)

review_findings = [
    {'id': 'R01', 'finding': 'One user review was confused with one subject Evaluation.',
     'disposition': 'This package is one consolidated proposal covering five meanings. Each later Evaluation still binds one exact Definition version. Package review is not a production Evaluation receipt.'},
    {'id': 'R02', 'finding': 'Meaning, profile contract, executed evidence and authority effect could collapse.',
     'disposition': 'Model separates the five meanings, two concrete profiles, Evaluation records, owner decisions, application receipts and visible Project State.'},
    {'id': 'R03', 'finding': 'Pending owner reviews could appear closed by the instruction to prepare everything.',
     'disposition': 'All three mapping scopes remain unselected; actual v1 checks 06/07 retain NOT_EVALUABLE. Preparation authorization records no owner concurrence.'},
    {'id': 'R04', 'finding': 'v1 lifecycle full-PASS wording can be mistaken for the pre-decision eligibility rule.',
     'disposition': 'No lifecycle transition is inferred from checks 01-05 or a conditional 01-06 PASS. Current v1 admission rule remains exact; its lifecycle gate interpretation needs applicable owner disposition at execution. Proposed v2 explicitly names phase gates without modifying v1.'},
    {'id': 'R05', 'finding': 'The two-meaning and full-cohort postimages have different counts and authority representations.',
     'disposition': '191/185 is conditional two-meaning bootstrap; 194/187 is prospective full five-meaning cohort. Current 189/183 remains unchanged. v1 authoring labels are conditional values, with metadata required to recover actual standing.'},
    {'id': 'R06', 'finding': 'Older carrier/activation drafts refer to candidate.1 meanings.',
     'disposition': 'The consolidated model selects the frozen step-09 candidate.3 activation and registration material, preserving older drafts as history.'},
    {'id': 'R07', 'finding': 'An incident predicate can fail even when a Definition is structurally valid.',
     'disposition': 'Illustration separates coverage assessment from Definition evaluation; retains account, filters, snapshot, output and noncoverage exclusions. The specimen is excluded from the five-meaning admission cohort.'},
    {'id': 'R08', 'finding': 'Schema checks and finite semantic evidence could be overstated as full conformance.',
     'disposition': 'Fresh checks cover integrity, structure, projection and selected dependency consistency. Prior formal conclusions remain bounded; runtime qualification and all 17 assurance follow-ups remain open.'},
    {'id': 'R09', 'finding': 'Existing runnable CLI could be confused with completion of strict M1 integration.',
     'disposition': 'Existing legacy Lab CLI and its context/graph/review/compiler bindings are retained. Strict pack adapter, provider/exporter and application qualification remain explicit implementation work.'},
    {'id': 'R10', 'finding': 'A single review could imply one principal has every authority scope.',
     'disposition': 'One presentation collects independent scope outcomes. Existing assignments are evidence of their declared scope; future v2 and Product effect applicability still requires explicit verification.'},
]

model = {
    'schema_version': 'cal.define-consolidated-review-model/v1',
    'representation_status': 'local descriptive review format; not an admitted Lab Evaluation carrier',
    'status': 'prepared-for-one-consolidated-user-review', 'authority_effect': 'none',
    'purpose': 'Complete Define integration model for one user evaluation of the proposal.',
    'user_review_count': 1, 'definition_subject_count': 5,
    'selected_meanings': selection,
    'concrete_profiles': {k: ref(step4 + '/' + k + '.json') for k in profiles},
    'check_contract': ref(step4 + '/check-contracts.json'),
    'activation': activation,
    'incident': {'posture': 'synthetic illustration; outside admission cohort',
                 'definition': ref(prefix + '/steps/03-foundational-definition/example-definition.json'),
                 'account': 'Northstar', 'filters': {'status': 'active'},
                 'snapshot': 'S-1042', 'output': 'E-1042', 'required_unique_ids': 12000,
                 'exported_required_unique_ids': 11800, 'missing_unique_ids': 200,
                 'criterion_outcome': 'FAIL under the proposed coverage predicate',
                 'definition_admission': False, 'incident_closure': False},
    'baseline': {'versions': 189, 'current_identities': 183, 'type_contracts': 143, 'protected': protected},
    'postimage_options': {'two_meaning_bootstrap': {'versions': 191, 'conditional_current_identities': 185},
                         'full_five_meaning_cohort': {'versions': 194, 'conditional_current_identities': 187}},
    'owner_mapping_review': request,
    'actual_bootstrap_evaluations': meaning_eval['actual_evaluations'],
    'remaining_implementation_map': ref('define/proposals/0005-amended-integration-plan/work-items.json'),
    'assurance_limits': {'reference': ref(prefix + '/reviews/e04-final-review/v1/assurance-limits.json'), 'open_count': 17},
    'review_outcome': {'selected': False, 'semantic_admission_selected': False,
                       'application_selected': False, 'actual_decision_ref': None,
                       'scope': 'One model review; later execution records preserve independent roles and dependency gates.'},
    'completion': {'review_package_prepared': True, 'strict_m1_runtime_complete': False,
                   'admission_ready': False, 'applied': False},
}
write('model.json', model)
write('source-bindings.json', {'authority_effect': 'none', 'scope': 'Exact source material used for this consolidated descriptive model.', 'inputs': sorted(bound.values(), key=lambda x: x['path'])})

main = '''# Define in CyberAlchemy Lab — one complete model to review

Status: proposed integration model. This is one consolidated user review of the proposal. Its five Definition subjects retain their exact reviewed bytes; their admission and the new profile adoption remain pending.

## 1. The outcome

A person or agent asks what a task depends on. Define identifies the meanings already available, the meanings that need a proposal and the questions still unanswered. It produces a reviewable bundle. Proposed meanings can then pass the applicable checks, receive an exact owner decision and become available to later work through governed Project State and its views.

The practical deliverable is a complete preparation workflow using the Lab's existing context, ontology and review interfaces. Success requires a usable CLI demonstration, complete exported Definition records, exact evidence and an owner review package with visible blockers. Building the definitions prepares those interfaces and gates; it does not complete the implementation.

```mermaid
flowchart LR
  A[Intent and Goal] --> B[Selected Project State and views]
  B --> C[Define]
  C --> D[Definition Pack]
  D --> E[Complete proposed Definitions]
  E --> F[Scoped Evaluation evidence]
  F --> G[Owner review and exact Decision]
  G --> H[Confirmed application]
  H --> I[Governed Project State]
  I --> J[Context and Ontology Views for later work]
```

These arrows explain data and review flow. They do not declare new global Typed Relations.

## 2. The five meanings

| Meaning | Question it answers | Incident example |
| --- | --- | --- |
| Definition | What does one term mean, within whose scope, with which boundaries? | What does identifier completeness mean for this export? |
| Definition Pack | Which concepts does this task require, and how is each handled? | Incident reused; Work specialized; completeness proposed; exclusivity open. |
| CyberAlchemy Define | What transformation prepares those meanings for the task? | Clarify the investigation's meaning and unresolved criteria using saved evidence. |
| Definition Evaluation Profile | Which checks, evidence, outcomes and phase gates assess an exact Definition? | Check the completeness Definition and its package independently of the export data. |
| Definition Lifecycle Profile | Which states and directed changes are allowed, with what evidence and authority? | The proposed completeness meaning starts authored; later validation, review and admission are separately evidenced. |

All five selected meanings are `1.0.0-candidate.3`. The two profile meanings use Definition/v1 as their explicit bootstrap carrier. Definition, Pack and Define use the existing Definition/v2 carrier. A profile meaning is a Definition; the concrete reusable profile is a different artifact. These are the five semantic subjects; the incident specimen is outside their admission cohort.

The full original normative statements, formulas, notation, explanations, boundaries and sources are collected in [Contracts and definitions](CONTRACTS.md). This explanatory model introduces no replacement canonical meanings.

## 3. What Define receives and returns

### Input

- One explicit Goal with its Project link and originating Intent.
- Declared context, named consumer and intended use.
- A finite, nonempty set of required concept identities.
- Exact selected source records and evidence, with standing at capture.
- Applicable owner routes, or explicit gaps where those routes are unresolved.

Goal, Intent and required-concept revisions retain attributable reasons and prior lineage. A consumer solution cannot silently replace the request.

### Four handling choices

| Disposition | Required payload | Example |
| --- | --- | --- |
| reuse | Exact admitted Definition version, captured standing and applicability. | Existing Incident meaning. |
| specialize | Exact parent plus application parameters, or an explicit proposed semantic change. | Existing Work applied to investigating this incident. |
| propose | A proposed meaning exported as a complete Lab Definition, with lineage and visible unresolved obligations. | Export identifier completeness. |
| open | Question, reason, affected use, owner route or gap, and continuation. | Whether extra records are permitted. |

Each declared concept receives exactly one current choice and matching payload. Duplicate, omitted and undeclared handling rows are rejected. An open question can be part of a conforming Pack and still block a particular later use.

Define can yield zero, one or many proposed Definitions. It records the missing meaning or a continuation; creation and selection of a follow-up Intent belongs to its own route. Define does not select the consumer's solution, achieve its Goal, appoint an owner or authorize execution.

### Output artifacts

1. A version-exact candidate Pack with scope, concept handling, evidence, ownership gaps and use-specific readiness.
2. Complete Definition JSON for each proposed semantic identity/version, plus deterministic generated Markdown.
3. Field lineage identifying reused, supplied, generated and unresolved fields.
4. Evaluation evidence with exact subject/profile/input bindings, check outcomes, causal blockers and claim limits.
5. A frozen review package: selected candidates, consumer dispositions, registry/index/drift postimages, independent owner scopes and the output recipe.

The Pack is a candidate input bundle in this release. A new independently admitted Pack Artifact Type or Pack instance is outside the selected first release. The strict preparation wire contracts and exporter remain implementation work; this model does not invent an already adopted protocol schema.

## 4. The incident, end to end

### The request

**INC-1042: Northstar's active-account export may omit rows after pagination.** The intended investigation uses a saved source snapshot and saved output. The agent needs an explicit criterion for identifying missing records.

| Bound input | Selected value |
| --- | --- |
| Account A | Northstar |
| Filters F | status=active |
| Source snapshot S | S-1042 |
| Saved output E | E-1042 |
| Required unique IDs | 12,000 |
| Required unique IDs present | 11,800 |
| Missing required IDs | 200 |

This is a synthetic realistic illustration. The fixture assumes globally unique identifiers; account-local identifiers would need an explicit composite identity contract.

### The proposed Definition

**Export identifier completeness:** for a fixed source snapshot S, declared account A, declared filters F and saved output E, every identifier required by S, A and F appears in E.

```text
CompleteIds(S,A,F,E) iff RequiredIds(S,A,F) subseteq ExportedIds(E)
```

S is one identified source snapshot; A selects the account; F selects records within that account; E is the saved export. The required identifier population must be established. An unknown population is NOT_EVALUABLE; a genuinely established empty population satisfies inclusion.

### Two different assessments

| Assessment | Subject | Result in this example |
| --- | --- | --- |
| Coverage assessment | Saved export compared with the required population. | FAIL: 200 required IDs are missing. |
| Definition evaluation | Meaning, representation and governance package for the proposed criterion. | Requires the 14 checks below; this illustration supplies no completed evaluation or admission. |

A valid criterion can expose a failing export. A missing-ID count does not establish the cause of the incident. Pagination is a hypothesis requiring independent evidence.

An export containing all required IDs can satisfy this inclusion criterion while still containing inaccurate values, duplicates or unauthorized extra records. Accuracy, exclusivity and incident closure therefore remain separate questions. The proposed Definition grants no production access, extraction, repair or closure permission.

### How the agent uses the result

An ephemeral machine-agent instance receives context from Project State through Context and Ontology Views. It can prepare the proposed criterion and evidence within its authorized Session. Short-term memory belongs to that Session. Later agents obtain durable knowledge from governed project records and views; a saved chat or work-session file does not become accepted Project State automatically.

## 5. The complete evaluation model

An Evaluation binds one exact Definition version, the exact applicable profile, selected input/evidence epoch, scope and phase. One user review may consider the whole model; each actual Evaluation still preserves its own subject and evidence.

- **PASS:** applicable evidence establishes the required predicate in the selected scope.
- **FAIL:** applicable evidence establishes a violation.
- **NOT_EVALUABLE:** required evidence, standing, input, execution or review is absent, unsupported or stale.

Independent checks continue after another check fails. A blocked dependent check records NOT_EVALUABLE and its causal reason. Every declared check is reported, while only the selected phase's required checks contribute to its aggregate.

### All fourteen proposed v2 checks

__CHECK_TABLE__

### Phase aggregation

__PHASE_TABLE__

For each selected phase, an established required FAIL takes precedence; otherwise any required NOT_EVALUABLE yields NOT_EVALUABLE; otherwise the phase is PASS. The pinned pre-decision set is nonempty. There is no global average that can hide a required failure.

Before admission, checks 01–12 must PASS on current exact inputs. Check 13 may be NOT_EVALUABLE solely because the admission decision has not occurred; check 14 is excluded before application. An existing Decision is assessed as an existing exact record, rather than relabeled pending.

### What an evidence record must retain

The record retains subject identity/version/digest, profile identity/digest/standing, phase and scope, exact inputs and source standing, all fourteen check outcomes, evidence references, causal blockers, phase aggregate, pre-decision eligibility, producer/Session attribution and explicit claim limits. Exact Decision and application references remain absent until the corresponding facts exist. This is a description of required information; implementing its closed carrier and evaluator remains separate work.

Changing the subject, source selection, profile, consumer/effect set or evidence epoch reopens affected checks. Old receipts remain bound to their original inputs and cannot be silently refreshed.

## 6. Lifecycle and actual changes

```mermaid
flowchart LR
  A[candidate-authored] --> B[validated-candidate]
  B --> C[owner-reviewed]
  C --> D[admitted]
  D --> E[superseded]
```

Withdrawal is also permitted from each non-withdrawn state through its declared owner gate. All directed pairs and gates follow.

__TRANSITION_TABLE__

Passing a gate establishes a condition. A separately attributable transition record and any required selected/confirmed effect establish an actual change. Revise, defer and reject are review outcomes; they do not automatically create withdrawal. Pre-decision eligibility is an assessment and does not add a seventh state.

The existing v1 lifecycle's full-PASS wording is preserved. A v1 pre-decision eligibility assessment cannot silently be renamed a full-PASS lifecycle transition; applicable owner interpretation must be resolved for an execution that relies on it. The proposed v2 phase gates express that distinction explicitly. No transition is claimed here.

## 7. Authority, provenance and lifecycle in this workflow

| Lens | What it records | Incident example |
| --- | --- | --- |
| Authority | Applicable admitted meanings/contracts, independent owners, permitted effects and scope. | The completeness Definition can govern a bounded criterion after exact admission; the agent still needs applicable action authority. |
| Provenance | Where exact selected information came from, its source epoch, evidence and attributable reviews. | S-1042, E-1042, account/filter selection, identifier comparison and its producer. |
| Lifecycle | Current posture, allowed directed changes and evidence of actual transitions/effects. | Candidate criterion, later review, exact admission and confirmed visibility. |

An exact digest establishes integrity of selected bytes. It does not establish source truth, owner identity, currentness for every later use or permission. A passed check and a directory location supply no owner authority.

### Independent responsibilities in one review package

| Role | Responsibility | Required separation |
| --- | --- | --- |
| artifact-mechanics-owner | Exact representation, schema, generator and field/projection mapping. | Excludes semantic admission. |
| definition-owner | Meaning, scope, exact version, preservation and semantic admission/Definition lifecycle effects. | A reviewed draft is distinct from selected admission. |
| evidence-conformance-owner | Evaluation contracts and sufficiency of scoped evidence. | Excludes semantic truth and admission. |
| artifact-type-owner | Applicable type registrations and exact contract bindings. | Existing v1 scope does not silently confer every v2 effect. |
| source-admission-owner | Applicable external source selection/admission. | Capture alone does not promote a source. |
| Applicable Product/capability owner | Product outcome, scope and realization/adoption decision. | Product approval does not select semantic or source admission. |

The current owner map and its admitted decision are exact inputs. A single person can hold several recorded roles, but each determination retains its own scope. One consolidated presentation can collect those outcomes without transferring roles.

Ontology Views can explain relationships already supported by admitted typed endpoint contracts. Embedded owner/source references, Pack relationship suggestions and presentation arrows do not manufacture global graph edges. Historical predecessor links are preserved; unsupported Definition→Role or Definition→SourceAdmission interpretations are not copied into new Typed Relations.

## 8. Bootstrap, type changes and effective visibility

The new profile meanings are reviewed through existing admitted v1 authority, then the new profile mechanics, carriers and concrete adoption receive their own applicable determinations. The following selected final activation recipe remains prospective.

__ACTIVATION_TABLE__

The registration proposal has two new profile/v2 type registrations and one Definition/v2 semantic-binding descriptor revision. The Definition/v2 instance schema, discriminator and relation roles remain unchanged. Existing historical contracts and Definition source records remain intact.

| State or scenario | Definition versions | Current identities | What it means |
| --- | --- | --- | --- |
| Current live baseline | 189 | 183 | Existing actual standing and lookup. |
| Two-meaning v1 bootstrap | 191 | 185, conditional | Two profile meanings only; foundational predecessor remains selected. |
| Full five-meaning cohort | 194 | 187, conditional | Four new semantic identities and one foundational successor version. |

The 143 existing admitted type-contract rows are preserved. Two pending type registrations are additional proposals, rather than already admitted rows. The index and drift material are generated from their exact selected inputs. The 12 inherited drift findings are preserved, and the 17 registered assurance limits remain open.

### Registry compatibility

The original closed v1 authoring registry and later admitted-output registry have different representation roles. The prepared v1 authoring postimage uses conditional future admitted entry labels under a candidate root. Those labels are not evidence of current standing. Actual candidate posture, admission metadata and current selection remain separately recorded.

The mapping preserves all 189 inherited rows and metadata. Recovering actual standing is lossless only with that metadata; the reduced authored view alone cannot restore it. The exact mechanics, semantic-preservation and evidence-conformance mapping scopes remain unselected. Actual v1 checks 06 and 07 therefore remain NOT_EVALUABLE.

The full five-meaning mixed-registry/Project State visibility recipe is a further exact representation/consumer effect. Reviewing the limited two-meaning v1 mapping does not adopt that global recipe. Publication uses a selected immutable cohort and one coherent effective-epoch lookup; it remains implementation and application work. No intermediate draft lookup is exposed here.

## 9. How this fits the existing Lab implementation

The existing Lab-owned CLI is a runnable candidate successor using Lab operational runtime v2 context, bounded ontology queries and Store.review. Its current output retains the legacy candidate Pack shape. That Pack does not already provide the complete Definition export required here.

| Interface | Selected reuse | Work still required for this model |
| --- | --- | --- |
| Source/provider | Existing source capture and freshness interfaces. | Strict bounded read/hash/parse of the same exact bytes, current selected-epoch support and original-byte transport. |
| Context | Existing Project State and Session views. | Complete strict preparation input binding and scoped freshness/readiness. |
| Ontology | Existing bounded graph query with diagnostics. | Lawful selected links and explicit boundary/impact handling. |
| Review | Existing Store.review on an explicitly selected local branch. | Exact full-Definition owner package, independent scoped outcomes and guarded recipes. |
| Exporter | Candidate-file behavior and deterministic generators. | Closed Lab preparation adapter, full per-disposition export, field lineage and safe early freeze. |
| Agent | Ephemeral native app-server session. | Qualify the strict preparation realization without attributing authority to model output. |
| Craft compilation | Existing public API; pure semantic functions lower to Calculation. | Preserve supported legacy compilation; v2 Pack compilation remains unsupported in this release. |
| Application/views | Existing governance surfaces. | Exact authorized epoch publication, recovery/idempotency and read-back, with explicit consumer compatibility. |

Inspection and early preparation create no private key, store or admission. Local work-session persistence is retained as work data and does not establish persistent machine-agent memory or accepted Project State.

## 10. The bounded completion plan

__AREA_TABLE__

The existing amended work map has 79 items. Its complete IDs, actions, dependencies, outputs and completion criteria are retained in [Contracts and definitions](CONTRACTS.md). Its historic planned labels are not a fresh claim that completed semantic preparation never happened. Current frozen preparation and accepted scope reviews are later evidence; implementation and owner effects need their own closure records.

### Delivery gates

1. **M1 — preparation preview:** strict provider and exporter produce a complete bounded candidate preview or exact blockers, with generated records and field lineage. Preserve legacy APIs and candidate-only effects.
2. **M2 — guarded review:** one user-facing package exposes exact subjects, independent roles, outcomes, consumer preservation/update choices and registry/index/drift/visibility recipes.
3. **M3 — application and visibility:** exact verified implementation, checked documentation, applicable Product approval and independently authorized effects produce coherent state plus verified read-back.

Implementation completion is demonstrated with the incident and another bounded consumer: useful generated records, repeatable evidence, visible gaps and successful governed retrieval by a subsequent agent. The incident criterion needs its own domain/assurance/review closure if selected for actual admission; it is not silently included in the five-meaning cohort.

## 11. Review conclusions and one requested evaluation

This proposal brings the whole selected integration model into one review. The review examined meaning separation, representation, profile phases, lifecycle gates, source/owner scope, dependency ordering, registry preservation, incident boundaries, runtime status and registered assurance limits.

The structural and source-integrity results are in [Review report](REVIEW.md). They establish consistency of the selected preparation material within that scope. They do not establish whole-repository semantic consistency, runtime conformance, owner concurrence, admission or applied visibility.

The remaining conditions are visible together:

- Exact qualified concurrence for the existing three-scope v1 registry mapping; actual checks 06/07 remain pending.
- Applicable v1 lifecycle gate interpretation for any relying bootstrap execution, without changing the v1 source.
- Independent meanings/mechanics/type/profile/compatibility owner effects under the selected final dependency order.
- Full-cohort representation and consumer visibility compatibility before global state changes.
- Strict M1 provider/exporter and later application qualification, including preservation of legacy behavior.
- All 17 registered assurance follow-ups, with their bounded claim ceilings retained.

**Review requested:** evaluate this complete model, its boundaries, dependency order and completion plan in one pass. You may accept it, identify changes or defer it. Any acceptance is recorded with the scope you state; semantic admission and application are not inferred from accepting the proposal. If you explicitly select those effects later, their exact role/effect records remain separate even when presented together.

No new owner outcome or admission has been recorded by preparing this document.
'''


def cell(x):
    return str(x).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in rows])


main = main.replace('__CHECK_TABLE__', table(['Check', 'Required evidence / established condition', 'Dependencies'],
    [[x['check_id'], x['pass_when'], ', '.join(x['depends_on']) or 'None'] for x in contract['checks']]))
main = main.replace('__PHASE_TABLE__', table(['Phase', 'Required checks'],
    [[k, ', '.join(x.split('-')[1] for x in v)] for k, v in contract['phases'].items()]))
main = main.replace('__TRANSITION_TABLE__', table(['From', 'To', 'Gate', 'Effect'],
    [[x[k] for k in ['from', 'to', 'gate', 'effect']] for x in profiles['lifecycle']['transitions']]))
main = main.replace('__ACTIVATION_TABLE__', table(['Stage', 'Depends on', 'Review scope'],
    [[x['id'], ', '.join(x['depends_on']) or 'Existing authority', x['route']] for x in activation['nodes']]))
main = main.replace('__AREA_TABLE__', table(['Area', 'Outcome', 'Items'],
    [[x['gap_id'] + ' — ' + x['title'], x['outcome'], len(x['work_ids'])] for x in work['gaps']]))
write('MODEL.md', main)

appendix = ['# Full definitions, contracts and work map', '',
            'Source excerpts retain their exact wording. This generated review collection is explanatory and grants no normative authority. Exact canonical input hashes are in [source bindings](source-bindings.json).', '']
for item in selection:
    d = load(item['path'])
    appendix += ['## ' + d['term'], '', link(item['path'], 'Canonical JSON') + ' · SHA256 `' + item['sha256'] + '`', '',
                 (ROOT / item['human_projection']['path']).read_text(), '']
for label, path in [('Evaluation/v2 profile', step4 + '/evaluation.json'),
                    ('Lifecycle/v2 profile', step4 + '/lifecycle.json'),
                    ('Fourteen-check contract, phases and evidence requirements', step4 + '/check-contracts.json'),
                    ('Final type-registration changes', step9 + '/registration-delta.json')]:
    appendix += ['## ' + label, '', link(path, 'Canonical candidate'), '', '```json', (ROOT / path).read_text().rstrip(), '```', '']
appendix += ['## Schemas and generators', '']
for path in ['authority/artifact-types/definition/v1/schema.json', 'authority/artifact-types/definition/v2/schema.json',
             'authority/artifact-types/definition/v1/generator.py', 'authority/artifact-types/definition/v2/generator.py',
             step4 + '/profile-carriers.schema.json', step4 + '/generator.py', 'authority/foundation/v1/schema.json',
             'authority/foundation/v1/render.py']:
    appendix += ['- ' + link(path, path) + ' · SHA256 `' + ref(path)['sha256'] + '`']
appendix += ['', '## Registered assurance limits', '',
             table(['ID', 'Title', 'Claim ceiling', 'Future work'],
                   [[x['id'], x['title'], x['claim_ceiling'], x['proposed_future_work']] for x in limits['items']]), '',
             'These 17 limits remain open. Their original register is preserved; later preparation acceptances do not retroactively rewrite its historic wording.', '',
             '## All 79 amended work items', '', link('define/proposals/0005-amended-integration-plan/work-items.json', 'Original exact planning source'), '',
             'The complete planning item declarations follow. They retain historic status labels. Current semantic preparation is separately evidenced; this collection does not automatically mark tasks executed.', '',
             '```json', json.dumps(work['work_items'], ensure_ascii=False, indent=2), '```', '']
write('CONTRACTS.md', '\n'.join(appendix))

# Validate newly presented links and preservation after read-only review.
for name in ['MODEL.md', 'CONTRACTS.md']:
    text = (OUT / name).read_text()
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if target.startswith(('https:', 'http:', '#')):
            continue
        path = target.split('#')[0]
        # Quoted historical generated projections are copied verbatim; their
        # original relative links retain the original base, if any.
        resolved = OUT / path
        if path == 'REVIEW.md':
            continue  # Forward link is checked immediately after its creation.
        check('link:' + name + ':' + path, resolved.exists(), 'Local document target exists.')
check('no-unexpanded-template-tokens', not re.search(r'__[A-Z_]+__', (OUT / 'MODEL.md').read_text()))
for original in protected:
    check('live-preserved:' + original['path'], ref(original['path']) == original)

report = {'schema_version': 'cal.define-consolidated-model-self-review/v1', 'authority_effect': 'none',
          'reviewer': 'authoring assistant; self-review, not independent owner review',
          'review_date': '2026-10-14', 'scope': 'Exact selected files, schemas/projections, dependency structure and explanation alignment.',
          'findings': review_findings, 'checks': checks,
          'result': 'PASS executed scoped structural/source checks; model corrections incorporated; owner/effect and implementation conditions remain open',
          'check_count': len(checks), 'failed_checks': 0,
          'runtime_tests_executed': False, 'prior_formal_evidence_rerun': False,
          'independent_owner_review': False, 'admission_ready': False,
          'new_concurrence': False, 'new_admissions': 0, 'application': False,
          'prior_formal_evidence': ref(step9 + '/assurance-results.json'),
          'current_owner_gate': ref(mapping + '/evaluation-refresh.json'),
          'protected_live_material': protected}
write('review-report.json', report)
review_md = f'''# Review completed before presentation

Result: **{len(checks):,} scoped checks PASS; zero failures.** This is the authoring assistant's self-review of the consolidated proposal. Applicable independent owner review remains unselected.

## What was checked

- Frozen prior package bindings and every selected source digest and recorded size.
- Five exact Definition schemas and deterministic generated projection parity.
- Both concrete v2 profile schemas, generated views and exact check-contract bindings.
- Fourteen complete check identities, nonempty pre-decision set and excluded Decision/application phases.
- Six states, nine transition pairs and acyclic activation/work-map dependencies.
- Full-cohort counts, preservation of all 189 historical rows, unchanged live material and retained actual pending owner gates.
- Complete 79-item plan, 17 registered limits and local document links.

## Corrections and qualifications incorporated

{table(['Finding', 'Disposition'], [[x['id'] + ' — ' + x['finding'], x['disposition']] for x in review_findings])}

## Evidence limits

No runtime/regression suite or formal assurance rerun was performed. Historical finite-model evidence retains its exact interpretation and ceilings. No natural-language equivalence theorem, whole-repository consistency, external owner authentication, admitted profile standing, transition, admission or application is established by these checks.

Read [the complete model](MODEL.md), [all exact meanings/contracts](CONTRACTS.md), [the machine-readable model](model.json) or [the executed review observations](review-report.json).
'''
write('REVIEW.md', review_md)
assert (OUT / 'REVIEW.md').is_file(), 'The model forward link must resolve before sealing.'
files = [ref(OUT / name) for name in ['prepare.py', 'MODEL.md', 'CONTRACTS.md', 'model.json', 'source-bindings.json', 'review-report.json', 'REVIEW.md']]
manifest = {'schema_version': 'cal.define-consolidated-review-manifest/v1', 'authority_effect': 'none',
            'status': 'frozen descriptive model prepared for one user review; no effect selected',
            'files': files, 'source_bindings': ref(OUT / 'source-bindings.json'),
            'exclusions': ['This manifest itself', 'later routing and verification receipts', 'mutable navigation/progress', 'private/live operator state'],
            'requested_effects': [], 'actual_decision_ref': None, 'application': False}
write('package-manifest.json', manifest)
print(json.dumps({'review': str(OUT / 'MODEL.md'), 'checks_passed': len(checks), 'sealed_files': len(files),
                  'bound_sources': len(bound), 'manifest': ref(OUT / 'package-manifest.json'), 'admission_ready': False}, indent=2))
