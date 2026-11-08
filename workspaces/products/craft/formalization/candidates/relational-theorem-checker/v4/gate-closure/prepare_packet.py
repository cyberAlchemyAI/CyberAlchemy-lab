"""Create new immutable review artifacts inside the original task boundaries."""
from pathlib import Path
import json
from closure_api import HERE,ROOT,SCOPE,ROLES,check,read,binding,encoded,durable,implementation_bindings


def link(label,path):
    return '['+label+']('+str(path)+')'


def prepare():
    base=HERE.parents[1];r06=ROOT/SCOPE['r06_output_root'];g4=ROOT/SCOPE['g4_output_root']
    r06.mkdir(parents=True,exist_ok=False);g4.mkdir(parents=True,exist_ok=False)
    audit_path=HERE/'execution/h01/predecessor-current-audit.json';audit=read(audit_path)
    original=read(HERE/'execution/h01/original-plan-audit.json')
    pilot=read(base/'v1/pilot/shadow-pilot-report.json')
    matrix=read(HERE/'execution/h01/supported-use-matrix.json')
    durable(r06/'shadow-pilot-report.json',encoded(pilot))
    durable(r06/'supported-use-matrix.json',encoded(matrix))
    durable(r06/'reviewer-feedback.md',b'# Original R06 reviewer feedback\n\nPending actual direct human meaning and diagnostic assessment of this exact packet.\n\nNo historical P11 answer is transferred. Gate acceptance has not occurred.\n')
    # Exact actual examples; retain their complete raw input and outcome bindings.
    rows=[]
    for name in ['f0-instance','f0-semantic-failure','extension-semantic-failure','replay-fresh-kind']:
        case=next(c for c in pilot['accepted_predecessor_cases'] if c['name']==name)
        rows.append(case)
    examples=[]
    for case in rows+pilot['fresh_cases']:
        outcome=read(check(case['outcome']));argv=case['argv']
        inputs=[binding(Path(v)) for v in argv if v.startswith(str(ROOT)) and Path(v).is_file()]
        examples.append({'name':case['name'],'argv':argv,'inputs':inputs,'outcome':case['outcome'],
                         'exit_code':case['exit_code'],'readiness':outcome['readiness'],
                         'results':outcome['results'],'diagnostics':outcome.get('diagnostics',[]),
                         'execution_observation':'Existing bound execution; current re-audit, not a new kernel run.'})
    durable(r06/'worked-examples.json',encoded({'schema':'relational.original-pilot-worked-examples/v4','examples':examples,'authority_effect':'none'}))
    layers={}
    descriptions={
      'L0':'Independent F0 relation meanings; checker/addition soundness; inhabited/coexistence models.',
      'L1':'Captured registry structure and source identity; selected meanings distinguished from inherited unresolved meanings.',
      'L2':'Computed change classes and complete hard inventory; selected-data compatibility, invariant preservation and old-model expansion remain separate.',
      'L3':'Typed finite positive Horn derivation, exact bounded closure/absence, complete protected lineage, exact checked countermodels and fresh-head conservativity.',
      'L4':'Exact proof/dependency replay, complete required obligations, CLI failure distinctions, recaptured shadow application and measured pilot; actual review still pending.'}
    for layer,description in descriptions.items():
        tasks=[t for t in original['requirements'] if t['layer']==layer]
        layers[layer]={'guarantees':description,'task_ids':[t['task'] for t in tasks],
                       'accepted_receipts':[t['receipt'] for t in tasks if t['status']=='accepted'],
                       'pending':[t['task'] for t in tasks if t['status']!='accepted']}
    criteria=[]
    for task in original['requirements']:
        for i,criterion in enumerate(task['criteria']):
            criteria.append({'task':task['task'],'criterion':criterion,
                             'status':'accepted-current' if task['status']=='accepted' else 'pending-original-gate',
                             'source':task.get('receipt',binding(base/'v1/pilot/shadow-pilot-report.json') if task['task']=='R06' else binding(HERE/'execution/h01/original-plan-audit.json')),
                             'finding':task.get('evidence_findings',[{}]*len(task['criteria']))[i].get('finding','Original scoped evidence reference or pending actual gate assessment; see full original audit.')})
    alignment={'schema':'relational.original-layer-alignment/v4','result':'prepared-current-machine-evidence; human gates pending',
               'base_plan':SCOPE['base_plan'],'original_counts':audit['original_counts'],
               'original_plan_audit':binding(HERE/'execution/h01/original-plan-audit.json'),
               'source_audit':binding(audit_path),'layers':layers,'criteria_coverage':criteria,
               'r06_machine_pilot':binding(r06/'shadow-pilot-report.json'),
               'r06_human_assessment':'pending','g4_human_use_recommendation':'pending',
               'owner_decisions':{'implementation':'Codex local candidate implementation and author evidence audit',
                                  'semantic_and_use':'Actual human assessment of frozen original packet required',
                                  'fact_truth':'Supplied assessment/receipt/root truth remains with its external owners'},
               'authority_effect':'none','application_authorized':False}
    durable(g4/'alignment-and-layering-audit.json',encoded(alignment))
    recommendation='''# Proposed bounded-use recommendation

Use the original relational checker as a local review aid for the exact supported-use matrix in this packet, with current source/toolchain bindings and every independently required obligation checked. Its candidate shadow adapter is suitable only for an owned cooperating local store. This recommendation is prepared for the actual human use reviewer; it is not yet an accepted G4 decision.

Supported original use includes F0's three exact evidence-bound relation meanings, the captured registry's structure, unchanged/instance-only proposals, append-only pure-annotation fresh kinds, the captured empty-old-rule/fresh-unary-head profile, exact proof replay, and bounded search that stays unresolved until its required witness is checked. Selected-data compatibility, universal preservation and model conservativity remain separate claims. Unsupported changes or unresolved hard obligations prevent readiness.

The captured integration uses an existential unary conformance projection and epoch 0. It does not preserve arbitrary target/scope distinctions or establish live time/authority. The structural 41-kind registry does not establish 263 unresolved inherited semantic obligations. Supplied assessment, action, receipt and root truth; parser/emitter/hash/host behavior; the pinned kernel; and cooperative local filesystem behavior remain assumptions.

Measurements describe captured examples on this host only. No throughput guarantee or hard aggregate memory cap is inferred. Timeouts and incomplete evidence remain unknown/refused, not approved. Reusing recorded evidence does not issue a fresh qualification event. Exact later shadow application still requires its existing fresh checking and baseline recapture.

The seven extension profiles remain separately scoped and their integration gaps are explained in the annex. The E06 independent checker covers one theorem sample. G4 completion does not approve a composed extension service, deployment, authority publication or organizational admission. Any broader capability requires its own implementation, evidence and actual use assessment.
'''
    durable(g4/'bounded-use-recommendation.md',recommendation.encode())
    review_source=base/'v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/REVIEW.md'
    annex='# Separately scoped seven-extension annex\n\nThis annex explains accepted v3 units and their remaining limits. It does not transfer their semantics or prior P11 feedback to original R06/G4. Original gate acceptance is about the original pilot and bounded use named in the main packet.\n\n'+review_source.read_text()
    durable(r06/'extensions-annex.md',annex.encode())
    diagnostic=next(e for e in examples if e['name']=='extension-semantic-failure')['diagnostics'][0]
    rule=next(c for c in pilot['fresh_cases'] if c['name']=='complete-rule-change')
    search=next(c for c in pilot['fresh_cases'] if c['name']=='search-without-checked-witness')
    case_table=['| Actual case | Exit | Interpretation |','|---|---:|---|']
    explanations={'f0-instance':'Exact supported graph/addition accepted.','f0-semantic-failure':'Wrong literal target-version qualifier refused.','extension-semantic-failure':'Selected-data compatibility failure names the assertion and correction.',
                  'replay-fresh-kind':'Complete supported fresh-kind evidence replayed.','endpoint-extension-unsupported':'Existing endpoint widening is outside the preservation profile.',
                  'complete-rule-change':'All 15 independently required obligations satisfied.','protected-head-unsupported':'A new old/protected head is outside this integration profile.',
                  'search-without-checked-witness':'14 obligations satisfied; exactly one required witness remains unknown.'}
    for e in examples:
        case_table.append('| '+link(e['name'],ROOT/e['outcome']['path'])+' | '+str(e['exit_code'])+' | '+explanations[e['name']]+' |')
    packet=f'''# Exact original R06/G4 review packet

This packet asks whether the original relational checker gives the intended meanings and useful diagnostics, and whether its measured limits support bounded local shadow use. It is a versioned review of original R06/G4. Your earlier v3 P11 answer remains valid for that earlier packet; it is not copied as acceptance here.

Machine preparation is complete. R06 and G4 remain pending actual human assessment. The current source audit verified **{len(audit['source_bindings']):,} files**. The original plan has 35 tasks, 40 working units and 56 dependencies: 33 historical acceptances remain current. The successor has 19 accepted units, 19 complete final-source extension witnesses and 277 extension control records. These are scoped checks, not 277 distinct theorems. Existing proof executions were re-audited; the nine new gate theorems were actually compiled and replayed.

## 1. What the relations mean

The model is a typed versioned graph. A relation assertion has exact endpoint revisions, an allowed ordered kind pair, explicit qualifiers and source-bound evidence. A reversed pair or evidence about another revision cannot silently establish the same claim.

**Conforms-to** means an accepted supplied assessment concerns this exact subject, target revision and scope. The captured example is `capability:reviewer@v1 → contract:review@v1`, scope `static`, with one opaque evidence token. Changing the target-version qualifier to another revision breaks that meaning. Acceptance proves consistency with the supplied assessment; it does not authenticate the assessor or grant permission.

**Declares-effect-on** records a decision's declared effect on an exact target revision. It describes the intended effect. It does not execute the effect or make a successor eligible.

**Materializes-consequence** requires a supplied accepted receipt matching the exact transaction, output, consequence role and output digest; the digest must equal the output node's supplied content identity. It proves consistency of those supplied records, not actual execution, cryptographic computation or transaction authorization.

The additional semantic stress profile distinguishes a recorded `acts-for` edge from effective representation at an exact snapshot: scope, action, interval, revocation and required assessments must hold. The logic stress profile propagates inherited contract norms with their origin. Potential obligation, active obligation, fulfilled obligation and authorization are separate meanings.

The seven later extensions add expressions, evidence collections, bounded chains, criterion fulfillment, lifecycle transitions, canonical IR and one independent-checker sample. Their complete explanation and remaining gaps are in the {link('separate extension annex',r06/'extensions-annex.md')}. Original gate completion does not automatically approve their composition.

## 2. What the theorems establish

For the typed supported graph, `checkGraph(G) = true ↔ Inv(G)`: successful checking matches the independently defined graph invariant. `checkAddition(G,e) = true → Inv(applyAddition(G,e))`: the whole resulting graph satisfies it. Adding a conformance edge cannot manufacture an admission root.

For positive Horn logic, derivations preserve the required premises/origins and the checked finite least closure is exact. A cycle `Review → Ready → Review` propagates a seed fact if one exists. With no seed, the least closure contains neither fact. This conclusion is about derivability from the captured facts/rules; it is not a claim that the predicates are false in all conceivable models.

The original rule-change integration is narrower than the generic engine: unchanged graph/registry, empty prior rule set, fresh ordinary unary heads and old-predicate positive bodies. An exact submitted proof, checked model and independently complete obligation inventory are needed. A valid proof of a weaker statement cannot satisfy the intended obligation. Selected-data compatibility, universal invariant preservation and expansion of every old model are distinct checks.

The new gate model proves exact review binding checks, scope separation, rejection of revisions/undecided feedback, G4's accepted-R06 prerequisite and preservation of predecessor evidence. It does not prove that a JSON quote came from a human; the operator must capture the observed direct response faithfully.

## 3. Actual worked inputs and diagnostics

The {link('worked-example inventory',r06/'worked-examples.json')} links complete raw inputs, command arguments, exact outcomes, obligations and diagnostics. The examples below are actual bound executions, not hypothetical success labels.

{chr(10).join(case_table)}

The semantic diagnostic says:

```text
Code: {diagnostic['code']}
Message: {diagnostic['message']}
Location: {diagnostic['location']}
Required obligation: {diagnostic['obligation_id']}
Next action: {diagnostic['next_action']}
```

This tells you which assertion is inconsistent and what to correct. Correcting a qualifier only helps when the assessment actually supports that exact target/scope. A rejected submitted proof means invalid evidence; it does not automatically refute the theorem. A resource refusal supplies no completed semantic conclusion. A completed bounded-search request without its checked witness stays unresolved even when 14 other obligations passed.

## 4. Supported use and measured limits

The exact {link('supported-use matrix',r06/'supported-use-matrix.json')} names seven original profiles. Their meanings are bounded to their versioned sources. The 41-kind registry has structural coverage across 550 ordered pairs and 109 node kinds; **263 inherited source-semantic obligations remain outside the supported meanings**. Seven extension receipts do not automatically discharge those obligations.

The original captured unary `Conforms(subject)` projection is existential: it loses target/scope detail, and the original integration epoch is 0. Do not use its unary fact to infer conformance to another contract/scope, current real-world authority or fulfillment. Existing endpoint widening, changed qualifiers/meanings, old/protected heads and unsupported mixed changes cannot borrow a preservation guarantee from this profile.

Actual original pilot costs:

| Execution | Elapsed time | Observed peak process RSS |
|---|---:|---:|
| Complete 15-obligation rule change | {rule['process_measurements']['elapsed_seconds']:.2f} s | {rule['process_measurements']['peak_rss_kib']/1048576:.2f} GiB |
| 14 satisfied plus one unresolved search witness | {search['process_measurements']['elapsed_seconds']:.2f} s | {search['process_measurements']['peak_rss_kib']/1048576:.2f} GiB |

These are measured captured runs, not throughput promises or hard memory caps. The successor has different operator policies and measured examples; its IR batch completed in 125.951 s with 991.5 MiB observed aggregate RSS, while earlier representations timed out. Static input ceilings do not guarantee completion. Default RSS observation is advisory; hard enforcement requires an actual delegated host backend. A timeout stays unknown/refused.

Remaining trust includes supplied evidence/root/action truth; selected source meaning; JSON/parser/emitter/hash behavior; the pinned Lean kernel; Python/host/filesystem behavior; and cooperating local application callers. E06 independently checks one 18-declaration theorem sample and cannot establish whole-core independent validation. Its valid-proof-under-substituted-definition control shows why exact meanings must be anchored too.

## 5. Layer alignment and closure behavior

The {link('layer alignment audit',g4/'alignment-and-layering-audit.json')} maps all original tasks and criteria to evidence or the pending actual gate assessment. L0 keeps independent meanings/checker soundness; L1 keeps structure/source guarantees; L2 distinguishes compatibility/preservation/model expansion; L3 keeps exact inference/absence/protected lineage; L4 keeps exact proof identities, complete obligations, diagnostic distinctions and recaptured candidate application.

The closure implementation has 32 passing evidence/feedback controls and 43 passing controls including actual concurrent writers and crashes immediately before/after authoritative log publication. Fixtures are marked synthetic and cannot supply actual human approval. Recovery recognizes committed state and never creates a fresh event.

Later gate acceptance is recorded in a checked append-only overlay. The original captured plan stays at its historical 33/35 state so its bound provenance remains valid. The status reader validates original criteria, outputs, current source identities and actual review before counting R06 or G4. A new `accepted` label without checked receipts is insufficient. The {link('API explanation',HERE/'API.md')} describes capture, acceptance and recovery.

## 6. Exactly what you need to review

For **R06**, assess whether the relation meanings above match your intent, and whether the actual diagnostics give clear causes and useful corrections. Machine proof validity is a separate completed check. State accepted, revisions needed or undecided; describe any meaning or diagnostic you want changed.

For **G4**, read the layer audit and {link('proposed bounded-use recommendation',g4/'bounded-use-recommendation.md')}. Assess whether the retained guarantees and exclusions support using this as a bounded local shadow review aid. G4 acceptance additionally requires accepted R06 and a fresh check of the same bound artifacts. It does not authorize deployment, organizational admission or authority publication.

The extension annex is explanatory context with its own scope. Its owned-definition, criterion-universe, eligibility-composition, transport and independent-checking gaps remain explicit successor work. You can recommend the original bounded use while requesting those broader improvements separately.

The exact review identities are in `review-manifest.json` next to this packet and the G4 directory. Feedback is bound to those hashes, the actual direct question/answer and the named scope. No historical approval is relabeled and no gate is accepted by merely preparing this packet.
'''
    durable(r06/'review-packet.md',packet.encode())
    for gate,folder in [('R06',r06),('G4',g4)]:
        artifacts=({'packet':binding(r06/'review-packet.md'),'matrix':binding(r06/'supported-use-matrix.json'),
                    'pilot':binding(r06/'shadow-pilot-report.json'),'audit':binding(audit_path)} if gate=='R06' else
                   {'packet':binding(r06/'review-packet.md'),'matrix':binding(r06/'supported-use-matrix.json'),
                    'alignment':binding(g4/'alignment-and-layering-audit.json'),'recommendation':binding(g4/'bounded-use-recommendation.md')})
        manifest={'schema':'relational.gate-review-manifest/v4','gate':gate,'scope':SCOPE['scope_ids'][gate],
                  'base_plan':SCOPE['base_plan'],'artifacts':artifacts,'source_audit':binding(audit_path),
                  'implementation_bindings':implementation_bindings(),'authority_effect':'none','application_authorized':False}
        durable(folder/'review-manifest.json',encoded(manifest))
    challenges={'R06':binding(r06/'review-manifest.json'),'G4':binding(g4/'review-manifest.json')}
    durable(HERE/'review-challenges.json',encoded(challenges))
    return r06,g4,challenges

if __name__=='__main__':
    r06,g4,challenge=prepare()
    print(json.dumps({'r06_packet':str(r06/'review-packet.md'),'g4_audit':str(g4/'alignment-and-layering-audit.json'),'challenges':challenge},indent=2))
