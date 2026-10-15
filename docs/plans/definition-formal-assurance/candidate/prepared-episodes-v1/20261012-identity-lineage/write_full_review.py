"""Complete Identity Lineage candidate review,work DAG and exact full-delivery context."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.identity-lineage')
load=lambda n:json.loads((u/n).read_bytes())
fresh=load('fresh-command-results.json');assert len(fresh)==6 and all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
inventory=load('current-inventory.json');graph=load('current-dependency-graph.json');local=load('dependency-graph.json');profile=load('authority-profile-checks.json');consumer=load('carrier-consumer-inspection.json');prep=load('next-unit-preparation/source-inspection.json');typed=load('types-logic-receipt.json');assert inventory['partial_drafts']==100 and len(inventory['missing_current_drafts'])==83
s=(u/'REVIEW.md').read_text().replace('# Identity Lineage: definitions,types and logic review','# Identity Lineage: complete candidate delivery review')
s=s.replace('The last completed whole inventory remains99partialdrafts84missing until this packet\'s full delivery.','The current whole inventory now records100partialdrafts83missing;the preserved prior Actor inventory remains99/84.')
s=s.replace('Sixteen typed inputs are then frozen and separately audited before current carrier/consumer mapping,qualified profiles,reachable dependencies,the whole100draftinventory,sixfreshchecks,full review,seal and separate audit. Principal native work follows the full Identity Lineage audit. Working100/83 and last completed whole inventory99/84 remain distinct until full refresh.','The sixteen-input typed freeze and separate audit passed. Current carrier/consumer comparisons,qualified profiles,reachable dependencies and whole100draftinventory now have actual results. Six fresh delivery checks passed with exit0. Full review is prepared for seal and separate audit,which require their own terminal evidence. Principal native work follows that full Identity Lineage audit. Prior Actor inventory99/84 and current IdentityLineage inventory100/83 remain separately preserved.')
s+='\n'+(u/'CONSUMER-REVIEW.md').read_text().replace('# Identity Lineage carrier and consumer review','Detailed current carrier and consumer evidence')
s+='''\nCurrent full-scope inventory and dependency evidence

The original inventory remains183identities189versions201sourcefiles. Both the initial current-inventory producer and its fresh replay recomputed exact source/core/IR/correspondence accounting for100partialdrafts. Each definition has one supplied model freshly and independently evaluated for its own T and I. There is no assembled shared-carrier meaning model or inherited owner acceptance. Combined count is2350sourceunits2930mappedclauses989encoded823explanatory1118deferred1236requiredpopulations5785unresolvedpopulations. Identity Lineage contributes26/26/15/9/2and17/114without changing the denominator or silently removing missing source identities.

The joint declared graph has144nodes2511edges44missingcounterpartpackets and one unresolved cycle. It retains all sources and edges from Actor's144node2491edgegraph and adds20direct Identity Lineage uses. The missing count drops from45to44because the exact Identity Lineage packet now exists. No other absent source is treated as translated or consistent. Its reachable graph has142nodes2456edges98selectedexistingpackets44missingcounterparts and one unresolved cycle. Root reachability is separate from the whole inventory. Cycle classification and edge-denominator acceptance remain unresolved;neither a traversal nor a larger draft count establishes semantic closure.

Thirty-two qualified profiles include31rejections. One hundred six finite source-map frames include105rejections across33pendingmapobligations. The one passing profile/frame is an explicit complete hypothesis with empty accepted-map and owner-review references. It does not turn C30,C31orC57admission into formalization-owner source correspondence. Rejected cases retain identity/reference distinctions,recorded versus actual immutable/evidence/owner posture,subject-kind/generalization scope,existing assessment ceilings and Method/CraftMethod independence. Eight consumer findings remain unresolved alongside all22sourcefindings.

Fifteen static-snapshot differential/adversarial checks passed. Only identical canonical static snapshot bytes may reuse static verification;live repository currentness still delegates the unchanged original checker. Changed snapshots,malformed inputs,result mutation,in-place snapshot mutation and exception restoration are tested. Source accounting,model evaluation,IR compilation and graph construction remain active. Each of the100currentT/Iwitnesses is actually evaluated. Shared sealed verifiers are unchanged. The unchanged limits are one million bytes,fifty thousand qualified nodes,one hundred thousand steps and thirty seconds. Performance improvements do not widen a proof claim or replace required source review.

Exact admission and semantic correspondence

C29Definition admission,C30specialized carrier admission,C31exact Craft lineage instance admission and C57Producttype succession have separate subjects,digests and effect scopes. C31recognizes schema and identity-contract conformance at its recorded boundary while leaving implementation/runtime not_evaluable and migration completion not_proven. Current formalization does not revoke or rewrite that evidence. It also does not promote it to whole-source translation acceptance,immutable runtime storage,all-kind generalized lineage or owner-approved common denotations. The source tuple and current carrier fields need explicit mappings even though a narrower instance has a legitimate existing admission.

CAV2-D32Method and CAV2-D20CraftMethod are separately current meanings. The initial successful consumer comparison omitted generic Method while including Craft Method;its exact producer,report and terminal captures are retained. The current comparison adds generic Method without changing primary theory,scope,source bytes,required populations or the16frozenty pedinputs. Current consumer checks number123with25meaningobservations. This distinction matters because a MethodBinding that refers to Craft Method does not silently define every Method's identity semantics. Project and Goal likewise keep their exact CAV2IDs. No new cal.definition.project/method/goal aliases are fabricated.

Retained failures and next-source readiness

One actual preparation-script escaping failure remains retained from before native creation. One successful native builder stage before correcting copied opaque interpretation/profile labels also remains retained. Neither changed the semantic formulas or checker limits. Full consumer work retained one successful earlier meaning-selection stage. The Principal source inspector initially checked whether Actor native output was absent;the copied target was wrong because Actor was already completed. Its failed producer and terminal captures are preserved. The corrected check targets Principal and adds its explicit normative nonimplication check. There was no failed native definition producer,no failed qualified profile,and no failed fresh delivery check.

Principal is source-only preparation:exact current C65Principal@1.0.0-candidate.1SHA60180d24ef3e83c517ea8f51f5ab863801c248ac80d19864353b58f70aaad794 passed29checks24sourceunits and two identical4698-byte projections. Its embedded actor-model-review hash and local integrated consumer are exact. Recognition boundaries,independent represented-subject identity/lifecycle and consequential authorization through exact current grant/scope are retained in the next types/logic design. No Principal native interpretation,identity recognition,grant or actual authorization is created before the full IdentityLineage audit.

Full delivery and final episode obligations

Six actual fresh checks passed:contract,model,source,qualified profile,reachable dependencies and current whole inventory. Their exact executable arguments,stdout and empty stderr captures remain bound. A fresh separate carrier inspection also matches the current report. This review and its seventeen-node,seventeen-edge acyclic work DAG are prepared for the full seal and separate exact-fileset audit. Those two operations must supply their own terminal outcomes before Principal native creation. Source fidelity,whole translation,common meaning alignment,whole proofs and semantic readiness remain pending.

Every9,112priorsealedfile and all201originalsourcefiles stay preserved. The full candidate package leaves unrelated tracked work untouched:30files4833insertions518deletions at inspection. Original121tasks511planningedges797SWUs36frontiers remain exact. The goal remains active across the remaining83missingcurrentdrafts and the final episode-wide aspect-by-aspect review and completion audit. A verified100draftcandidate inventory is concrete progress toward that full objective;it cannot redefine the original episode around a successful subset or provide evidence for absent owner acceptance and whole-definition proof.
'''
s=s.replace('frozenty pedinputs','frozen typed inputs')
assert len(s.split())>4500 and len(re.findall(r'^## [0-9]+\.',s,re.M))==13
with (u/'DELIVERY-REVIEW.md').open('x') as f:f.write(s)
fence=chr(96)*3;diagram=s.split(fence+'mermaid\n')[1].split(fence)[0];edges=[];labels={}
for line in diagram.splitlines():
 m=re.match(r' ([A-Z]+)(?:\[(.*?)\])? --> ([A-Z]+)(?:\[(.*?)\])?',line)
 if m:
  a,al,z,zl=m.groups();edges.append({'from':a,'to':z})
  if al:labels[a]=al
  if zl:labels[z]=zl
assert len(labels)==17 and len(edges)==17
dag={'schema_version':'definition-assurance-work-delivery-dag/v1-candidate','authority_effect':'none','source':load('context.json')['source_selection'],'nodes':[{'node_id':k,'label':z} for k,z in labels.items()],'edges':edges,'is_semantic_dependency_graph':False,'next_native_requires_full_separate_audit':True,'next_definition_priority':'F05-T.cal.definition.principal'}
with (u/'work-delivery-dag.json').open('x') as f:json.dump(dag,f,indent=2,sort_keys=True);f.write('\n')
text='''# Identity Lineage full delivery context

Exact current C29 IdentityLineage typed packet froze16inputs and separate actual auditpassed0.14sorts1constant28functions114signatures157declarations;26units26mapped15encoded9explanatory2deferred17required114unresolved20directuses34queries10source-conditioned.205controls79Ttrue118Tfalse8malformed;89sourcechecks52obligations;source-only projection4506bytes. Preserve9112priorsealedfiles201sources and original183/189/201plus121/511/797/36scope.

Current consumer123checks25meaningobservations7contracts50Definitionprobes14accept281carrierprobes43accept16independentT/Icomparisons. Direct current C30IdentityLineage/v1 specializes Product/same-product-renamed;C31exactunchangedinstance and boundedrecognizedconformance preserved;C57Product/v2type transition didnot admit/rebind instance or activate consumer. Legacy ProjectCAV2-D60,MethodD32,CraftMethodD20,GoalD59 remain separately qualified.32profiles31reject106frames105reject33pendingmaps8unresolvedconsumerfindings;acceptedmaps0.

Current100draft83missing inventory2350source2930mapped989encoded823explanatory1118deferred1236required5785unresolved. All100per-definitionwitnesses freshly independently evaluated. Joint144nodes2511edges44missing1cycle;reachable142nodes2456edges98selectedpackets44missing1cycle.15staticreusechecks preserve livecurrentness/model/source/IR/graph checks and unchangedsharedvalidators. Sixfreshchecksactualexit0 plusfreshseparateconsumerinspection0.

Retain actualpreparationescapingfailure1,successfulpre-label-native-stage1,successfulpriorconsumerMeaning-stage1 andactualnext-sourcewrong-absence-targetfailure1. Source/frozenT/limitsunchanged;failednativeDefinition/profile/freshchecks0. Principalnextsource29checks24units4698bytes1upstreampassed;nativeabsent beforefullIdentityLineageaudit. Full13aspectreview and17node17edgeacyclicDAG prepared;seal and separateaudit require actualterminalresults.

Source fidelity/sharedmaps/wholetranslation/wholeproofpending;semantic readinessfalse;goalactive. No newactualcontinuity,immutable storage,owner authority,identity transfer,endpoint admission,deletion,supersession orcanonical/private/live/publication/deploymenteffect. Unrelated30trackedfiles4833insertions518deletionspreserved. Completeoriginalepisode and final review remain required.
'''
with (p/'FULL-DELIVERY-CONTEXT.md').open('x') as f:f.write(text)
print(json.dumps({'result':'written-complete-IdentityLineage-candidate-review','words':len(s.split()),'aspects':13,'source_findings':22,'consumer_findings':8,'dag_nodes':17,'dag_edges':17,'fresh_checks':6},indent=2))

