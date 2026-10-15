"""Explain Actor full delivery while retaining frozen typed review and all scope ceilings."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.actor')
load=lambda n:json.loads((u/n).read_bytes())
fresh=load('fresh-command-results.json');assert len(fresh)==6 and all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
inventory=load('current-inventory.json');graph=load('current-dependency-graph.json');local=load('dependency-graph.json');profile=load('authority-profile-checks.json');consumer=load('carrier-consumer-inspection.json');source=load('source-checks.json');prep=load('next-unit-preparation/source-inspection.json');typed=load('types-logic-receipt.json');assert inventory['partial_drafts']==99 and len(inventory['missing_current_drafts'])==84
s=(u/'REVIEW.md').read_text().replace('# Actor: definitions,types and logic review','# Actor: complete candidate delivery review')
s=s.replace('The last completed full inventory remains98partialdrafts85missing until Actor\'s full delivery.','The current full inventory now records99partialdrafts84missing;the preserved prior Withdrawal Record inventory remains98/85.')
s=s.replace('Three fresh type-stage checks passed with actual exit zero. Sixteen typed inputs are then frozen and separately audited before current carrier/consumer mapping,qualified profiles,reachable dependencies,the whole99draftinventory,sixfreshdeliverychecks,full delivery review,seal and separate audit. Identity Lineage native creation follows that full audit. Last full inventory98/85 and current working99/84 remain separate until the full refresh.','Three fresh type-stage checks passed with actual exit zero,and the sixteen-input typed freeze and separate actual audit passed. Current carrier/consumer inspection,qualified profiles,reachable dependencies and the whole99draftinventory now have actual results. Six fresh delivery checks also passed. The full review is prepared for seal and separate audit,which require their own terminal evidence. Identity Lineage native creation follows the full Actor audit. Prior Withdrawal Record inventory98/85 and current Actor inventory99/84 remain separately preserved.')
s+='\n'+(u/'CONSUMER-REVIEW.md').read_text().replace('# Actor carrier and consumer review','Detailed carrier and consumer review observations')
s+='''\nCurrent whole-inventory and semantic dependency evidence

The native whole-inventory producer and fresh replay both recomputed exact source/core/IR/correspondence accounting for all99partialdrafts. Each packet has a freshly independently evaluated supplied T/I witness;none is treated as a source-owner accepted translation. Combined count is2324sourceunits2904mappedclauses974encoded814explanatory1116deferred1219requiredpopulations5671unresolvedpopulations. These denominators include Actor's27/27/19/6/2and18/136contribution without changing the original183identityscope. Per-packet consistency is separate from a common-carrier or shared-meaning model.

The joint graph has144nodes2491edges45missingcounterpartpackets and one unresolved cycle. Actor adds24authored direct semantic uses;all prior graph sources and edges are retained. The reachable Actor graph has142nodes2436edges97selectedexistingpackets45missingcounterparts and the same unresolved cycle. Reachability does not assemble every prior theory into Actor T. No missing interpretation is treated as a satisfiable accepted map,no cycle is arbitrarily classified recursive,and the edge denominator remains requires-independent-review. Source owners must still review semantic dependencies and common denotations.

Qualified mapping has32profiles31rejections and118finiteframes117rejections across37pendingmapobligations. The one passing profile/frame is a complete unaccepted hypothesis with empty owner-review and accepted-map references. It does not admit a carrier or classify a subject. Rejected cases expose missing/empty/invented acceptance,identity collapse,universal-carrier invention,authority transfer,shape-to-truth promotion,historical-review-to-runtime promotion and silent sibling merging. Eight consumer findings remain unresolved alongside all22sourcefindings.

Fifteen independently run static-reuse differential and adversarial checks passed. Only identical canonical static snapshot bytes may reuse prior static verification;live repository currentness still delegates the original checker. Model evaluation,source correspondence,IR compilation and graph compilation are not bypassed. The current inventory still evaluates every supplied witness. Shared sealed verifier modules remain unchanged. Checker limits remain one million bytes,fifty thousand nodes,one hundred thousand steps and thirty seconds;successful performance is not a reason to enlarge a semantic claim.

Identity Lineage is prepared only as the next exact source. C29currentIdentityLineage@1.0.0-candidate.1SHA32c15860fb0621edaf172efea9f1f5ab467763a5ca4454d0d2424e7783c499bf passed37source-onlychecks,26sourceunits and two identical4506-byte projections. Three embedded upstream source hashes are exact local Definition_v1,Product_v1 and chain0001bytes. The symbolic chain0002consumer is resolved through exact C29 selection;it is not a filename or an executed continuity instance. The Craft lineage candidate body and separate type-schema path are observed without accepted mapping or current runtime claims. No next-native interpretation or model exists before the full Actor audit.

Full delivery requires its own successful seal and separate exact-fileset audit after this review. Both must preserve8999priorsealedfiles201originalsourcebytes,all16frozenty pedinputs and actual terminal captures. No original task,edge,SWU,frontier,Definition ID,source digest or unrelated tracked edit is rewritten. Owner acceptance,whole translation,mechanized whole-definition proof and semantic readiness remain pending. Goal status stays active until the complete original scope and the final episode-wide review have supporting evidence. Completing Actor's reversible candidate package does not complete the183identityepisode.
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
dag={'schema_version':'definition-assurance-work-delivery-dag/v1-candidate','authority_effect':'none','source':load('context.json')['source_selection'],'nodes':[{'node_id':k,'label':z} for k,z in labels.items()],'edges':edges,'is_semantic_dependency_graph':False,'next_native_requires_full_separate_audit':True,'next_definition_priority':'F05-T.cal.definition.identity-lineage'}
with (u/'work-delivery-dag.json').open('x') as f:json.dump(dag,f,indent=2,sort_keys=True);f.write('\n')
text='''# Actor full delivery context

Exact C65 Actor candidate types/logic packet was frozen and separately audited with actual exit0. Sixteen frozen inputs remain unchanged. Native14sorts1constant32functions136signatures183declarations;account27units27mapped19encoded6explanatory2deferred18required136unresolved24directuses45queries.244controls98Ttrue138Tfalse8malformed;101sourcechecks72sourcequeryobligations. Root,use and attribution queries are separately scoped;actual outcomes remain outside necessary theory.

Current registry143contracts121current has no directly bound Actor carrier. Eight separate classification/concrete-kind contracts bind their own meanings;25meaningprojections121checks54Definitionprobes14accept412carrierprobes86accept16independentT/Icomparisons passed. Exact separately valid Assignment/Value/AgentInstance fixtures are not a joined classification instance;historical missing-Actor review text is not current runtime truth.32profiles31reject118frames117reject37pendingmaps8consumerfindings. Accepted maps remain0.

Whole inventory99partialdrafts84missing with all99suppliedwitnesses freshly independently evaluated. Counts2324source2904mapped974encoded814explanatory1116deferred1219required5671unresolved. Joint144nodes2491edges45missing1unresolvedcycle;reachable142nodes2436edges97selectedpackets45missing1cycle.15staticreusechecks preserve livecurrentness,allmodel/source/IR/graph checks and unchanged shared validators.

Six actual fresh checks passed with exit0. IdentityLineage next-source37checks26units4506projectionbytes3exactlocalupstreams passed;nextnative absent until full Actor audit. Full review and17node17edgeacyclicworkDAG prepared. Full seal and separate audit need their own actual terminal outcomes. Preserve8999priorsealedfiles201sourcebytes,original183/189/201and121/511/797/36scope,all16typedinputs and unrelated30trackedfiles4833insertions518deletions. No failed prepared/native/type/full consumer/fresh/next-source producer occurred.

Source fidelity,shared meaning maps,whole translation and whole-definition proofs pending;semantic readinessfalse;goalactive. No actual Actor classification,attribution,agency,owner/lifecycle/authority transfer,successful action or canonical/private/live/publication/deployment/external effect. Complete183identityepisode and final review remain required.
'''
with (p/'FULL-DELIVERY-CONTEXT.md').open('x') as f:f.write(text)
print(json.dumps({'result':'written-complete-Actor-candidate-review','words':len(s.split()),'aspects':13,'source_findings':22,'consumer_findings':8,'dag_nodes':17,'dag_edges':17,'fresh_checks':6},indent=2))

