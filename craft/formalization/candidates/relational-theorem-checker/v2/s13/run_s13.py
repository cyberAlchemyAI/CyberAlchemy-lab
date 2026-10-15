from pathlib import Path
import sys,copy,json,time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import rich_case as rich
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s07'));import fixtures as f
import audit_successor as audit
s=rich.s;HERE=Path(__file__).resolve().parent
s.context('S13',[(s.BASE/'s11/stage-measurements.json','qualified measured reference'),(s.BASE/'s01/requirements.json','independent requirements and deferred meanings'),(s.BASE/'s10/qualification-audit.json','exact full trust/regression audit'),(s.BASE/'s09/application-qualification.json','actual two-step shadow pilot'),(s.BASE/'s07/mapping-audit.json','actual unknown/false/conflicting/expired/override cases'),(s.BASE/'s08/explanation-fixtures.json','worked original explanations'),(s.BASE/'s12/optimization-audit.json','reference fallback selected; conditional edge inactive')],[{'decision':'Pilot uses qualified reference and bounded same-statement witness stages; no optimized evaluator','basis':'S11/S12 selection'},{'decision':'Exercise a rich rule reading exact contract/scope/kind rather than relying only on lossy unary conformance','basis':'S01 semantic load-bearing requirement'}])
outputs=[];measures=[]
for name,wrong in [('exact-contract-scope-kind',False),('wrong-scope-unseeded-fresh-cycle',True)]:
 p=rich.proposal(wrong)
 if '--resume-after-audit-fix' in sys.argv:
  s.require(s.read(HERE/(name+'-proposal.json'))==p,'saved proposal changed');result=s.read(HERE/(name+'-result.json'));explanation=rich.explain(p,result);s.require(s.read(HERE/(name+'-explanation.json'))==explanation,'saved explanation changed');elapsed=None
 else:
  s.write(HERE/(name+'-proposal.json'),p);start=time.monotonic();result=rich.bounded.qualify(p,HERE/'build');explanation=rich.explain(p,result);elapsed=time.monotonic()-start
 s.require(explanation['present'] is (not wrong),'semantic pilot scope leak');path=HERE/(name+'-result.json');s.write(path,result);s.write(HERE/(name+'-explanation.json'),explanation);outputs.append({'name':name,'proposal':s.binding(HERE/(name+'-proposal.json')),'result':s.binding(path),'explanation':s.binding(HERE/(name+'-explanation.json')),'seconds':elapsed,'query_present':explanation['present']});measures.append(elapsed);print(name+' checked',flush=True)
# Fresh critical mapped pilot checks; previous full case inventory remains exact/current.
mapped=[]
for name,q in [('unknown-potential',f.example('inheritance')),('active-origin',f.holds(f.example('inheritance'))),('expired-delegation',f.example('delegation'))]:
 if name=='expired-delegation':q['typed']['snapshot']['epoch']=10;q['baseline']['context']['epoch']=10;q['baseline']['inference']['snapshot_epoch']=10;f.refresh(q)
 if '--resume-after-audit-fix' in sys.argv:
  prior=s.read(HERE/(name+'.json'));s.require(prior['request']==q,'saved mapped request changed');out=prior['result']
 else:
  out=f.a.evaluate(q,HERE/'stress-build');s.write(HERE/(name+'.json'),{'request':q,'result':out})
 mapped.append(s.binding(HERE/(name+'.json')))
 if name=='unknown-potential':s.require(len(out['potential_norms'])==1 and out['active_norms']==[],'unknown activated')
 if name=='active-origin':s.require(len(out['active_norms'])==1 and out['fulfilled']=='not-established','active meaning upgraded')
 if name=='expired-delegation':s.require(out['status']=='no','expiry ignored')
shadow=s.read(s.BASE/'s09/application-qualification.json');s.require(len(shadow['applications'])==2,'missing actual shadow pilot');closure=audit.binding_closure([s.BASE/'s09/application-qualification.json',s.BASE/'s07/mapping-audit.json',s.BASE/'s10/qualification-audit.json']+[s.ROOT/x['result']['path'] for x in outputs]+[s.ROOT/x['path'] for x in mapped]);s.write(HERE/'pilot-currentness.json',closure)
for app in shadow['applications']:rich.saved_guard.validate(app['qualification'])
truncated=copy.deepcopy(s.read(s.ROOT/outputs[0]['result']['path']));truncated['evidence']['actual'].pop()
try:
 rich.saved_guard.validate(truncated);raise ValueError('truncated evidence accepted')
except ValueError as e:s.require('incomplete split proof inventory' in str(e),'truncated evidence control failed')
s.write(HERE/'saved-evidence-controls.json',{'result':'pass','controls':['all four actual split modules required','saved proof evidence equals exact bound evidence file','truncated actual proof inventory rejected','both shadow application result inventories verified'],'authority_effect':'none'})
report={'result':'pass','reference_evaluator':True,'fresh_rich_recursive_cases':outputs,'fresh_mapped_cases':mapped,'full_boundary_case_inventory':s.binding(s.BASE/'s07/mapping-audit.json'),'actual_two_step_shadow':s.binding(s.BASE/'s09/application-qualification.json'),'pilot_resume':'Previously completed actual qualifications in this execution revalidated after documentary audit-reader correction; no fresh reexecution or missing elapsed-time claim' if '--resume-after-audit-fix' in sys.argv else 'fresh actual qualification', 'shadow_reexecution':'Actual runs performed in S09 in this execution; revalidated exact bindings here, not relabeled as a new execution','hard_obligation_ids':[o['id'] for o in rich.r.ext.c.obligations('rule-only')],'early_resource_unknown':s.binding(s.BASE/'s11/exhausted-result.json'),'source_currentness':s.binding(HERE/'pilot-currentness.json'),'human_feedback':None,'original_R06_G4':'pending','authority_effect':'none'}
s.write(HERE/'pilot-report.json',report)
pos=s.read(HERE/'exact-contract-scope-kind-explanation.json');neg=s.read(HERE/'wrong-scope-unseeded-fresh-cycle-explanation.json');edge=next(e for e in rich.proposal()['before']['graph']['assertions'] if e['kind']=='relation.conforms-to');subject=edge['source'];target=edge['target'];scope=edge['qualifiers']['conformance_scope']
perf=s.read(s.BASE/'s11/stage-measurements.json')['full_qualification'];perf_text='; '.join(m['mode']+': '+str(round(m['seconds'],2))+' seconds, '+str(round(m['child_max_rss_kib']/1048576,2))+' GiB observed child peak RSS' for m in perf)
packet=f'''# Relational theorem checker: worked review

The implemented candidate checks a finite, explicitly selected relational/logic profile. It now supports exact contextual observations, sealed source producers, positive recursive fresh definitions, nonempty old-rule baselines, explicit delegation/inheritance mappings, condition activation, and two-step local shadow application. Machine qualification and human meaning/use review are separate.

## The concrete relations

The source says `{subject['id']}@{subject['version']}` conforms to `{target['id']}@{target['version']}` in scope `{scope}`. That produces `ConformsTo(subject,target,scope)` only when the assertion belongs to the graph and its assessment has matching endpoints, target revision, scope and supplied accepted status. `TargetKind(target,contract)` independently records the target type. Every observation retains its member assertion/assessment or node support. Multiple supports remain visible even when the fact is deduplicated.

The pilot rule reads **both** exact observations and derives `ContractReview(subject)`. `ContractReady(subject)` follows from it; a positive cycle feeds back to `ContractReview`. These are informational conclusions. Source observations cannot be supplied as caller facts or written by ordinary rules, and derived information cannot become an independent admission root.

The positive case returns `{pos['query']}`. Its trace is [shown here](exact-contract-scope-kind-explanation.json), ending at the exact conformance assertion/assessment and target-kind node. The second case requests declared scope `other-scope` with the same target and kind. That scope is present in the fixed before/after domain but has no conformance observation. It produces no ContractReady fact: {neg['reason']} See the [wrong-scope explanation](wrong-scope-unseeded-fresh-cycle-explanation.json). The old unary `Conforms(subject)` still exists, but it cannot satisfy that exact target/scope premise.

## What the theorem actually says

For every old semantic model M, if the independently checked extension hypotheses hold, there is an expanded model N satisfying the extended rules, and every old atom has the same truth in N and M:

`∀ M, SemanticModel(before,F,M) → ∃ N, SemanticModel(after,F,N) ∧ ∀ old a, (N(a) ↔ M(a))`.

The checked hypotheses preserve the old graph, domain, roots, facts, context, interpretation, predicates and rules; new heads are fresh ordinary derived predicates with positive bodies. Recursion is allowed. The proof constructs a least fresh closure relative to **arbitrary M**, rather than assuming that M equals one sampled closure. A separate finite theorem proves that reference saturation terminates with an exact closure when its pending head inventory is complete. A checked query derivation and a complete closure remain different claims.

A generic Horn model may contain extra observation truths. The stronger **source-faithful** class fixes sealed observations exactly to source meanings and is separately named/proved. Richer graph/domain migrations use a distinct initial-view embedding theorem; they do not reuse fixed-domain model conservativity.

## The semantic stress relation

`inherits-contract` first resolves the exact binding and contract revision. That gives a **potential norm** with binding/contract origin. Even a condition named `always` is not executed or assumed true. Only a matching positive, consistent evaluation for the exact condition revision, context, subject, target, scope and epoch makes the norm **active**. Unknown, missing, false or conflicting selected statuses do not activate it. Active require/forbid conflicts retain both origins and do not enable arbitrary conclusions. Neither inheritance nor activation establishes fulfillment, conformance or admission.

`acts-for` maps exact agent/principal/delegation, scope, half-open period, revocation and supplied policy/gate data. The expiry boundary and revocation controls deny effectiveness; missing policy/gate interpretation and permitted-but-unimplemented redelegation chains remain unknown. Its source endpoint kinds lie outside F0, so the registry source selection is a separately tested boundary.

## Evidence and limits

[The pilot report](pilot-report.json) binds actual rich positive/negative proofs, fresh mapped checks, the complete hard inventory and the prior actual two-step shadow run. [Full qualification](../s10/qualification-audit.json) audits source/definition/proof closure and retained v1 guarantees. [Performance measurements](../s11/performance-baseline.md) distinguish complete cold/warm qualification from evaluator-only probes. The measured benchmark was {perf_text}. These are local observations; larger workloads have no general time or memory guarantee. Work and per-stage time ceilings do not impose an OS memory cap. The unchanged 60-second compiler-stage limit stopped the first second-successor registration before publication; splitting the same concrete declarations/proofs into independent modules completed that bounded case. This is not a weaker theorem or a broader completion-time guarantee.

The following limits remain explicit:

1. All 41 source relations were reviewed, but only selected fragments are implemented. The [source map](../s18/source-map.json) retains deferred meanings and inherited unsupported obligations.
2. Assessment, root-receipt, policy/gate and condition truth are supplied inputs. Hash binding and logic do not authenticate those external claims.
3. The language is finite positive Horn logic with fresh ordinary heads. Old-head changes, mixed edits, negation, functions, entity generation, overrides and redelegation chains need other profiles/proofs.
4. JSON/normalization/source selection are tested boundaries. Pure values, exact independent types and proof declarations are checked/replayed by the same pinned Lean kernel, not a second kernel.
5. Work ceilings can return unknown. Partial closure cannot prove absence or readiness. Local shadow locking coordinates cooperative writers; an external writer can race the final check/rename, with postcheck/reconciliation limits stated in the [application report](../s09/application-qualification.json).
6. Machine and author checks do not supply human semantic, diagnostic or bounded-use approval. Original v1 R06/G4 remain pending. There is no live authority, publication or deployment effect.

## API and review request

[CLI/Python API contracts](../s08/API.md) cover projection, recursive qualification, stress mapping and explanations. [The shadow adapter](../s09/shadow-adapter.py) additionally initializes/reviews/applies candidate snapshots inside its local runs directory, with bounded split witness stages. [Execution status](../execution/status.json) records task acceptance and the optional optimization decision; the qualified reference remains selected.

Please assess whether these meanings match the intended model, whether the worked diagnostics explain the failures, and whether bounded local shadow use is appropriate under the stated limits. Use [the feedback template](feedback-template.md). Actual feedback is required to finish S14; no response is inferred from machine passes or the request to implement the plan.
'''
(HERE/'review-packet.md').write_text(packet)
s.accept('S13',['Fresh rich target/scope/kind recursive positive and wrong-scope empty-cycle cases pass exact full obligations; mapped potential/active/expiry and retained hostile/shadow cases have current evidence.','No human feedback has been inferred or fabricated; a concrete worked packet and feedback template are ready.','Original R06/G4 remain pending; source/trust/budget/writer/unsupported limits are explicit.'],controls=[{'name':x['name'],'result':'pass'} for x in outputs]+[{'name':'fresh-potential-active-expiry','result':'pass'},{'name':'actual-two-step-shadow-current','result':'pass'},{'name':'truncated-split-evidence-rejected','result':'pass'}],extra_dependencies=[HERE/'rich_case.py',HERE/'audit_successor.py',HERE/'saved_result_guard.py',HERE/'saved-evidence-controls.json',HERE/'pilot-currentness.json']+[s.ROOT/x['result']['path'] for x in outputs]+[s.ROOT/x['explanation']['path'] for x in outputs]+[s.ROOT/x['path'] for x in mapped])
print('S13 accepted: actual rich semantic/recursive pilot; concrete human review packet ready.')
