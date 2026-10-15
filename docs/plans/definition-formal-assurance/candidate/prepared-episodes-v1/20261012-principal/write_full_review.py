"""Principal full thirteen-aspect review and exact work delivery DAG."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal')
load=lambda n:json.loads((u/n).read_bytes())
fresh=load('fresh-command-results.json');assert len(fresh)==6 and all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
inventory=load('current-inventory.json');graph=load('current-dependency-graph.json');local=load('dependency-graph.json');profile=load('authority-profile-checks.json');consumer=load('carrier-consumer-inspection.json');prep=load('next-unit-preparation/source-inspection.json');assert inventory['partial_drafts']==101 and len(inventory['missing_current_drafts'])==82
s=(u/'REVIEW.md').read_text().replace('# Principal: definitions,types and logic review','# Principal: complete candidate delivery review')
s=s.replace('Last completed whole inventory remains100partialdrafts83missing until Principal full delivery.','Current whole inventory now records101partialdrafts82missing;the preserved prior Identity Lineage inventory remains100/83.')
s=s.replace('Sixteen typed inputs are frozen and separately audited before current carrier/consumer inspection,qualified profiles,reachable dependencies,the whole101draftinventory,sixfreshchecks,full review,seal and separate audit. Principal Reference native creation follows that full Principal audit. Working101/82 differs from last completed whole inventory100/83 until full refresh.','The sixteen-input typed freeze and separate actual audit passed. Current carrier/consumer inspection,qualified profiles,reachable dependencies and whole101draftinventory now have actual results. Six fresh delivery checks passed with exit0. Full review is prepared for seal and separate audit,which need their own terminal outcomes. Principal Reference native creation follows that full Principal audit. Prior Identity Lineage inventory100/83 and current Principal inventory101/82 remain separately preserved.')
s+='\n'+(u/'CONSUMER-REVIEW.md').read_text().replace('# Principal carrier and consumer review','Detailed current carrier and consumer evidence')
s+='''\nCurrent full-scope inventory and semantic dependencies

The initial current-inventory producer and fresh replay both recomputed the source/core/IR/correspondence account for all101partialdrafts. Each has one supplied model freshly independently evaluated for its own necessary theory T and required populations I. There is no assembled common-meaning model or inherited owner acceptance. Combined count is2374sourceunits2954mappedclauses1005encoded829explanatory1120deferred1262requiredpopulations5942unresolvedpopulations. Principal contributes24/24/16/6/2and26/157without changing the original183identity189versionscope. All201originalsourcefiles remain current by exact digest.

The joint declared graph has144nodes2535edges43missingcounterpartpackets and one unresolved cycle. It retains all prior Identity Lineage graph sources and edges and adds24direct Principal uses. Missing count falls from44to43because the Principal packet now exists. Reachable Principal closure has142nodes2480edges99selectedexistingpackets43missingcounterparts and one unresolved cycle. Those selected packets do not bring their whole theories into primary Principal T. Edge-denominator and recursive-cycle interpretations remain owner pending. A graph traversal cannot certify semantic closure or common denotations.

Thirty-two qualified profiles include31rejections. One hundred twenty-one finite source-map frames include120rejections across38pendingmappingobligations. The one passing profile/frame is a complete unaccepted hypothesis:owner-review and accepted-map references remain empty. It preserves exact source,scope,role,claim ceiling and distinct sibling meanings. Missing/empty mappings,invented acceptance,discarded findings,changed scope/issuer coordinates and silently collapsed siblings fail. That bounded consistency result does not accept Principal recognition,issuer authenticity,grant authority or all consumer alignment.

Fifteen static-snapshot differential and adversarial checks passed. Reuse applies only to identical canonical static snapshot bytes. Live repository currentness still delegates the unchanged original checker. Result mutation,changed/malformed snapshots,in-place selected snapshot mutation and exception restoration are covered. Source accounting,IR compilation,model evaluation and graph construction remain active. Every101per-definitionwitness is freshly evaluated. Shared sealed validators are unchanged. Limits remain one million input bytes,fifty thousand qualified nodes,one hundred thousand steps and thirty seconds;performance improvements cannot widen an evidence claim.

Recognition,reference and grant interpretation boundaries

Current Principal/v1 directly binds C65 meaning under C70 admission. The separately admitted PrincipalReference carrier does not authenticate that identity merely because its issuer,resolver and integrity fields are present. Its fixture Principal label differs from the Principal fixture node. The Principal fixture's stable subject differs from the selected PersonReference node. Delegation's Principal and Agent labels likewise do not join the selected fixtures. The consumer reports those exact mismatches while preserving each valid record shape and independent source meaning. No reference is rebound and no identity is fabricated to make the examples appear connected.

The shape-valid empty recognition list remains a mapping obligation. A real recognized Principal must meet the positive Definition's exact boundary meaning,which an empty list alone cannot establish. AuthorityClaim and Delegation preserve basis,scope,permission,period,revocation,policy and gate fields as their own record structures. They are not converted into actual current grants by a hypothetical source map. Principal identity scope,recognition-boundary scope and authorization scope remain separately nominated. Grant issuer may differ from recognition issuer when separately governed. Owners still need accepted denotations for these relationships and the source's only-through-exact-grants boundary.

C70 decision,authorization,bundle and proposal are exact. Its broad type/relation admission and integrated Governed Model instance do not admit Principal fixtures,activate consumers or execute authorization. Recorded consumer/runtime/typed-relation activations remain zero. Reading those bytes preserves existing authority boundaries without granting this formalization new effects or source acceptance. The local review/integrated-model files are likewise source observations. Private read-first routing documents remain hash-bound metadata only;no private package content or meaning is copied into primary theory or the current public source artifacts.

Actual terminal evidence and next source

Native author,build,model and source producers passed. The prepared full signature/source-clause contract and every supplied control passed before native creation. All three fresh typed checks and the sixteen-input freeze/separate audit passed. Six full fresh checks now passed independently:contract,model,source,profile,reachable dependencies and current whole inventory. A fresh separate carrier comparison also matches the report. Exact executable arguments,stdout and empty stderr remain bound. There were no failed prepared/native/profile/fresh/next-source/seal or audit producers in this packet.

The initial compressed routing description produced a no-match result. Its exact request and non-authorizing receipts are retained. A corrected spaced governance request passed route,context and effect checks without changing the task,source,theory or checker limits. Routing gates are source/proposal evidence rather than owner effect authority. The user's active goal authorizes reversible candidate artifacts;actual Principal identities,recognition,grants,permissions,canonical changes and publication remain outside the performed work.

Principal Reference is prepared only as the next exact source:cal.definition.principal-reference@1.0.0-candidate.1SHA7ca6bd645843a17ac21936da623f7ccff6b011f4d7051ad6e4ffd19121b1a16e. C65source-onlyinspection passed29checks24sourceunits and two identical5116-byte projections. The local actor-model-review hash and integrated consumer are exact. Its design retains minimal consumer-needed coordinates,one governed Principal or explicit unresolved state,no copied identity record/secret/credential/excess data,and separate current grant evidence for authority decisions. No next-native interpretation or model exists before full Principal audit.

Full delivery and original episode completion

This4,500-plus-word review and its seventeen-node,seventeen-edge acyclic work DAG are prepared for the full seal and separate exact-fileset audit. Both must supply their own terminal outcomes before Principal Reference native creation. The artifact dependencies preserve definitions/types/logic first,then carrier mappings,qualified profiles,reachability,whole inventory,fresh checks,review,seal and audit. The work DAG is separate from the semantic dependency graph's unresolved cycle and cannot decide its recursive meaning.

All9,251priorsealedfiles201sources and sixteen frozen typed inputs remain preserved. Unrelated tracked work is unchanged at30files4833insertions518deletions during inspection. Original121tasks511planningedges797SWUs36frontiers are exact. Source fidelity,shared meanings,whole translation,source-owner acceptance and whole-definition proofs remain pending;semantic readiness remains false. The active goal still requires the remaining82currentidentities and the final episode-wide review/completion audit. A verified101draftcandidate inventory is progress within the original objective and cannot redefine completion around a successful subset.
'''
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
dag={'schema_version':'definition-assurance-work-delivery-dag/v1-candidate','authority_effect':'none','source':load('context.json')['source_selection'],'nodes':[{'node_id':k,'label':z} for k,z in labels.items()],'edges':edges,'is_semantic_dependency_graph':False,'next_native_requires_full_separate_audit':True,'next_definition_priority':'F05-T.cal.definition.principal-reference'}
with (u/'work-delivery-dag.json').open('x') as f:json.dump(dag,f,indent=2,sort_keys=True);f.write('\n')
text='''# Principal full delivery context

Exact C65Principal typed packet froze16inputs and separate actual auditpassed0.15sorts1constant34functions157signatures207declarations;24units24mapped16encoded6explanatory2deferred26required157unresolved24directuses48queries10consequential-authconditioned.270controls115Ttrue147Tfalse8malformed;92sourcechecks63obligations;projection4698bytes. Preserve9251priorsealedfiles201sources and original183/189/201plus121/511/797/36scope.

Current consumer124checks25meanings8contracts55Definitionprobes14accept415carrierprobes83accept17independentT/Icomparisons. Direct current C70Principal/v1 owns C65 meaning;C70PrincipalReference/AuthorityClaim/Delegation and subject types remain separate. Empty recognition-list shape and unverified issuer/resolver/integrity strings do not prove recognition. Fixtures are not joinedPrincipal/subject/delegation identities. C70onlyintegratedGovernedModel ordinary instance;zero consumer/runtime/typedrelation activation;no Principal fixtures admitted.32profiles31reject121frames120reject38pendingmaps8consumerfindings;acceptedmaps0.

Current101partial82missing inventory2374source2954mapped1005encoded829explanatory1120deferred1262required5942unresolved. All101supplied per-definitionwitnesses freshly independently evaluated. Joint144nodes2535edges43missing1cycle;reachable142nodes2480edges99selectedpackets43missing1cycle.15staticreusechecks preserve livecurrentness/model/source/IR/graph checks and unchanged shared validators.

Six actual fresh checks and fresh separate carrier inspection passed0. PrincipalReference next-source29checks24units5116bytes1upstream passed;nativeabsent beforefullPrincipal audit. Full13aspectreview and17node17edgeacyclicDAG prepared;seal/separateaudit require actualterminaloutcomes. No failed prepared/native/profile/fresh/next-source/seal/audit producers. Initial routing no-match retained;corrected gate non-authorizing. Private routing read-first data remain path/hash metadata without content/meaning import.

Source fidelity/sharedmaps/wholetranslation/wholeproofpending;semantic readinessfalse;goalactive. No actual Principal recognition,resolution,authorization,grant,rights,canonical/private/live/publication/deploymenteffect. Unrelated30trackedfiles4833insertions518deletionspreserved. Completeoriginalepisode and final review remain required.
'''
with (p/'FULL-DELIVERY-CONTEXT.md').open('x') as f:f.write(text)
print(json.dumps({'result':'written-complete-Principal-candidate-review','words':len(s.split()),'aspects':13,'source_findings':22,'consumer_findings':8,'dag_nodes':17,'dag_edges':17,'fresh_checks':6},indent=2))

