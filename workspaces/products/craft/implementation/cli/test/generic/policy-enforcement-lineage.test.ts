/** Static source lineage from actual original checked declarations, not a
 * synthetic graph standing in for behavior. Open Questions: docs/POLICY-ENFORCEMENT.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createGenericSourceComputation,checkGenericSource} from '../../src/generic/pure-source-stage.js';
import {projectPolicyEnforcementLineage} from '../../src/generic/policy-enforcement-lineage.js';
import {genericTransactionSourceSite} from '../../src/generic/identity.js';
import {secondDomain,secondDomainInline,secondDomainLibrary} from './policy-enforcement-fixtures.js';

const limits={max_input_bytes:65536,max_output_bytes:65536,max_value_bytes:32768,max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:64,max_call_depth:32,fuel:200000};
function checked(text=secondDomain){
 const source=text+'\ninterface Application:\n  kind application-composition\n  computation-bounds contracts/bounds.json\n';
 const sources=[{path:'publication.alch',text:source},{path:'admission.alch',text:secondDomainLibrary}],roles=checkGenericSource(sources),contract=createGenericSourceComputation(sources,'ResearchDesk.Publish',limits).contract;
 const operation=roles.effects.find(x=>x.operation.module+'.'+x.operation.name==='ResearchDesk.Publish')!;
 return {contract,operation};
}
test('EN07 actual checked enforcement links Operation, physical site, Policy, branches, Calculations, Rule and enum types',()=>{
 const f=checked();const graph=projectPolicyEnforcementLineage({artifactNode:'generated:ResearchDesk.Publish',functions:f.contract.functions,operations:[{operation:'ResearchDesk.Publish',body:f.operation.body}]});
 const operation=graph.nodes.find(x=>x.kind==='checked-operation')!,site=graph.nodes.find(x=>x.kind==='policy-enforcement-site')!,policy=graph.nodes.find(x=>x.declaration==='ResearchDesk.PublicationEligibility'&&x.kind==='checked-pure-declaration')!;
 assert.equal(operation.declaration,'ResearchDesk.Publish');assert.equal(site.source_span?.path,'publication.alch');assert.ok(site.source_span!.end>site.source_span!.start);assert.equal(site.source_site,undefined);
 assert.ok(graph.edges.some(e=>e.from===operation.id&&e.to===site.id&&e.kind==='enforces-policy-at'));
 assert.ok(graph.edges.some(e=>e.from===site.id&&e.to===policy.id&&e.kind==='evaluates-policy'));
 assert.equal(graph.nodes.filter(x=>x.kind==='policy-case').length,3);
 for(const name of ['ResearchDesk.Permit','ResearchDesk.Deny','ResearchDesk.PositiveRatio'])assert.ok(graph.nodes.some(x=>x.declaration===name&&x.kind==='checked-pure-declaration'));
 assert.ok(graph.nodes.some(x=>x.declaration==='ResearchAdmission.Verdict'&&x.kind==='checked-enforcement-type'));assert.ok(graph.nodes.some(x=>x.declaration==='ResearchAdmission.Cause'&&x.kind==='checked-enforcement-type'));
 const known=new Set(['generated:ResearchDesk.Publish',...graph.nodes.map(x=>x.id)]);for(const e of graph.edges){assert.ok(known.has(e.from));assert.ok(known.has(e.to));assert.equal(e.static_only,true);}
 assert.ok(graph.links.some(x=>x.business==='ResearchDesk.Publish'&&x.system===site.id&&x.source_span?.path==='publication.alch'));
 assert.doesNotMatch(JSON.stringify(graph),/"expression"|"condition"|"approved"|"divisor"|selected_branch|runtime-selected/);
 assert.ok(graph.nodes.every(x=>x.static_only));
});
test('EN07 nested original conditional enforcement remains visible and graph ordering is deterministic',()=>{
 const f=checked(secondDomain.replace('  enforce PublicationEligibility(approved=approved,divisor=divisor)','  when approved:\n    enforce PublicationEligibility(approved=approved,divisor=divisor)'));
 const input={artifactNode:'generated:ResearchDesk.Publish',functions:f.contract.functions,operations:[{operation:'ResearchDesk.Publish',body:f.operation.body}]};
 const graph=projectPolicyEnforcementLineage(input);assert.equal(graph.nodes.filter(x=>x.kind==='policy-enforcement-site').length,1);
 assert.deepEqual(projectPolicyEnforcementLineage({...input,functions:[...f.contract.functions].reverse(),operations:[...input.operations,...input.operations]}),graph);
});
test('EN07 physical source span and original generic source-site identities remain distinct',()=>{
 const f=checked(),s=f.operation.body[0]!;assert.equal(s.kind,'enforce-policy');if(s.kind!=='enforce-policy')return;
 const source_site=genericTransactionSourceSite('ResearchDesk.Publish',[['enforce',0]]);
 // The source descriptor is genuinely checked above; this adapter exercises
 // the stateful projector's separate provenance fields, not stateful execution.
 const adapted={...s,source_span:s.source_site,source_site,value:{...s.value,local_records:[] as const}};
 const graph=projectPolicyEnforcementLineage({artifactNode:'generated:ResearchDesk.Publish',functions:f.contract.functions,operations:[{operation:'ResearchDesk.Publish',body:[adapted]}]});
 const site=graph.nodes.find(x=>x.kind==='policy-enforcement-site')!;assert.equal(site.source_site,source_site);assert.deepEqual(site.source_span,s.source_site);
 assert.ok(graph.links.some(x=>x.source_site===source_site&&x.source_span?.path==='publication.alch'));
});
test('EN07 existing inline-only Operation adds no enforcement lineage',()=>{
 const f=checked(secondDomainInline);assert.deepEqual(projectPolicyEnforcementLineage({artifactNode:'generated:ResearchDesk.Publish',functions:f.contract.functions,operations:[{operation:'ResearchDesk.Publish',body:f.operation.body}]}),{nodes:[],edges:[],links:[]});
});
