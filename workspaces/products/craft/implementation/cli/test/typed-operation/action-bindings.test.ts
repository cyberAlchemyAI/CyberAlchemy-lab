import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings,decodeOperationActionBindings,assertCheckedOperationAction,OPERATION_ACTION_BINDINGS_VERSION,OperationActionError} from '../../src/typed-operation/action-bindings.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
const read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const contract=fs.readFileSync(path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation/operation-action-contract.json'),'utf8');
const boundaryContract=fs.readFileSync(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'),'utf8');
const fieldContract=fs.readFileSync(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'),'utf8');
const scalar=(name='String')=>({kind:'scalar',name});
const named=(selector:string)=>({kind:'named',selector});
const at=(root:string,...properties:string[])=>({op:'path',root,properties});
const lit=(type:string,value:any)=>({op:'literal',type,value});
const arg=(parameter:string,value:any)=>({parameter,value});
const ref=(selector:string,...args:any[])=>({selector,arguments:args});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-action-bindings-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
  const write=(p:string,v:any)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
  const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
  const edge=(id:string,relationship:string,from:string,to:string)=>{if(!edges.includes(id))edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',edge_id:id,feature_id:'commerce',relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
  const property=(id:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+id.toUpperCase()+'#'+name,name,type,cardinality:'one',identity,meaning:name});
  for(const id of ['account','receipt'])node(id,'Entity',{fields:['id','balance'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),properties:[property(id,'id',scalar(),true),property(id,'balance',scalar('UInt64'))]}});
  node('can-post','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-CAN-POST',parameters:[{name:'account',type:named('commerce:account')},{name:'amount',type:scalar('UInt64')}],expression:{op:'lt',left:at('amount'),right:at('account','FIXTURE-ACCOUNT#balance')}}});
  node('audit','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-AUDIT',parameters:[{name:'allowed',type:scalar('Bool')}],expression:{op:'eq',left:at('allowed'),right:lit('Bool',true)}}});
  node('posted','Event',{event_type:'posted',version:'1',occurrence_id:{field_id:'occurrence-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[{field_id:'account-id',type_ref:{kind:'reference',selector:'commerce:account'},required:true}]});
  node('post','Operation',{reads:['account-snapshot'],writes:['account-state','new-receipt'],effects:['posted-fact'],guard:'can-post',failure_continuation:'return-post-error'});
  edge('post-reads-account','reads','post','account');edge('post-creates-receipt','creates','post','receipt');edge('post-produces-posted','produces','post','posted');edge('can-post-enforces-post','enforces','can-post','post');edge('audit-enforces-post','enforces','audit','post');
  const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'operation-actions',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
  const bindings:any={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'commerce:post',inputs:[{name:'account_id',type:scalar()},{name:'amount',type:scalar('UInt64')},{name:'replacement',type:named('commerce:account')},{name:'receipt',type:named('commerce:receipt')},{name:'response',type:scalar()}],
    reads:[{slot:'account-snapshot',target:'commerce:account',parameter:'current',key:at('account_id')}],guards:[ref('commerce:can-post',arg('account',at('current')),arg('amount',at('amount'))),ref('commerce:audit',arg('allowed',lit('Bool',true)))],
    writes:[{slot:'account-state',target:'commerce:account',mode:'replace',value:at('replacement')},{slot:'new-receipt',target:'commerce:receipt',mode:'create',value:at('receipt')}],events:[{slot:'posted-fact',target:'commerce:posted',parameter:'posted_input'}],result:{type:scalar(),value:at('response')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
  const compile=()=>{
    const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundaryContract);
    const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:account','commerce:receipt'],bindings:[]},fieldContract);
    return {graph,boundary,fields,check:(b:any=bindings,c=contract)=>compileOperationActionBindings(graph,boundary,fields,b,c)};
  };
  return {temp,source,nodes,edges,write,node,edge,save,property,bindings,compile,...compile()};
}
const rejects=(fn:()=>unknown,code:string)=>assert.throws(fn,(e:any)=>e instanceof OperationActionError&&e.code==='OPERATION_ACTION_'+code);

test('Action binding closes exact authored slots, typed live reads, declared Rules and produced Events',t=>{
  const f=fixture(t),before=JSON.stringify(f.bindings),a=f.check();assertCheckedOperationAction(a);assert.deepEqual(f.check(),a);
  assert.equal(JSON.stringify(f.bindings),before);assert.equal(Object.isFrozen(f.bindings),false);
  assert.equal(a.reads[0]!.identity.property,'FIXTURE-ACCOUNT#id');assert.equal(a.guards[0]!.arguments[0]!.value.op,'path');
  assert.equal(a.writes[1]!.mode,'create');assert.equal(a.events[0]!.contract.event_type,'posted');assert.equal(a.events[0]!.parameter,'posted_input');
  assert.equal(a.failure_continuation,'return-post-error');assert.equal(a.execution,'not-performed');assert.equal(a.authority_effect,'none');
  const {action_sha256,...body}=a;assert.equal(action_sha256,sha256(canonicalJson(body)));assert.equal(a.bindings_sha256,sha256(canonicalJson(a.bindings)));
  const frozen=(v:any)=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));Object.values(v).forEach(frozen);}};frozen(a);
  assert.equal(a.events[0]!.source.kind,'Event');assert.equal(a.writes[0]!.source.kind,'Entity');
  assert.deepEqual(f.graph.relationships.map(r=>r.relationship).sort(),['creates','enforces','enforces','produces','reads']);
  const clone=structuredClone(a);rejects(()=>assertCheckedOperationAction(clone),'UNVALIDATED');
  fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(f.check(),a);
});

test('Action decoder is closed and inert with bounded resources and no getter/coercion calls',t=>{
  const f=fixture(t);let calls=0;
  for(const mutation of [(b:any)=>b.extra=true,(b:any)=>b.atomicity='best-effort',(b:any)=>b.continuation='background',(b:any)=>b.guards=[],(b:any)=>b.inputs.push(b.inputs[0]),(b:any)=>b.events[0].parameter='current',(b:any)=>b.writes[1].slot=b.writes[0].slot,(b:any)=>b.guards.push(b.guards[0]),(b:any)=>b.guards[0].arguments.push(b.guards[0].arguments[0]),(b:any)=>b.writes[0].mode='evaluate']){
    const b=structuredClone(f.bindings);mutation(b);assert.throws(()=>decodeOperationActionBindings(b));
  }
  const getter={...f.bindings,get inputs(){calls++;return f.bindings.inputs;}};rejects(()=>decodeOperationActionBindings(getter),'DATA');
  const b=structuredClone(f.bindings);Object.defineProperty(b.guards[0].arguments[0],'value',{get(){calls++;return at('current');},enumerable:true});rejects(()=>decodeOperationActionBindings(b),'DATA');
  rejects(()=>decodeOperationActionBindings({...f.bindings,inputs:Object.assign(new Array(4294967295),{})}),'DATA');
  rejects(()=>decodeOperationActionBindings({...f.bindings,inputs:[{name:'bad',type:{valueOf(){calls++;return scalar();}}}]}),'DATA');
  const hidden=structuredClone(f.bindings);Object.defineProperty(hidden,'selector',{value:hidden.selector,enumerable:false});rejects(()=>decodeOperationActionBindings(hidden),'DATA');
  for(const mutate of [(b:any)=>b.selector+='\n',(b:any)=>b.inputs[0].name+='\n',(b:any)=>b.events[0].target+='\n']){
    const malformed=structuredClone(f.bindings);mutate(malformed);rejects(()=>decodeOperationActionBindings(malformed),'IDENTIFIER');
  }
  rejects(()=>decodeOperationActionBindings({...f.bindings,[Symbol()]:1}),'DATA');
  const cyclic=structuredClone(f.bindings);cyclic.result.value=cyclic;rejects(()=>decodeOperationActionBindings(cyclic),'LIMIT');assert.equal(calls,0);
});

test('Source slot and canonical relationship coverage cannot be forged or silently dropped',t=>{
  const f=fixture(t);
  const cases:[(b:any)=>void,string][]=[
    [b=>b.reads[0].slot='invented','COVERAGE'],[b=>b.writes.pop(),'COVERAGE'],[b=>b.events=[],'COVERAGE'],[b=>b.reads[0].target='commerce:receipt','COVERAGE'],
    [b=>b.writes[1].mode='replace','COVERAGE'],[b=>b.events[0].target='commerce:account','COVERAGE'],[b=>b.guards.pop(),'COVERAGE'],[b=>b.guards[0].selector='commerce:missing','COVERAGE'],
  ];
  for(const [mutate,code] of cases){const b=structuredClone(f.bindings);mutate(b);rejects(()=>f.check(b),code);}
  const node=read(path.join(f.source,'specs/commerce/nodes/post.json'));node.body.guard='other-rule';f.write('specs/commerce/nodes/post.json',node);rejects(()=>f.compile().check(),'PRIMARY_GUARD');
  const invalid=fixture(t);invalid.edge('forged-write-edge','mutates','account','post');invalid.save();assert.throws(()=>invalid.compile(),/endpoint|Binding|mutates/);
});

test('Read keys, post-read guards, write values and success results retain exact types',t=>{
  const f=fixture(t);
  const cases:[(b:any)=>void,string][]=[
    [b=>b.reads[0].key=at('amount'),'READ_KEY_TYPE'],[b=>b.reads[0].key=at('current','FIXTURE-ACCOUNT#id'),'TYPE'],
    [b=>b.guards[0].arguments[0].value=at('receipt'),'GUARD_ARGUMENT_TYPE'],[b=>b.guards[0].arguments.pop(),'GUARD_ARGUMENTS'],
    [b=>b.guards[0].arguments[1].value=at('current','FIXTURE-ACCOUNT#id'),'GUARD_ARGUMENT_TYPE'],[b=>b.guards[0].arguments[0].value=at('posted_input'),'TYPE'],
    [b=>b.writes[0].value=at('receipt'),'WRITE_VALUE_TYPE'],[b=>b.result.value=at('amount'),'RESULT_TYPE'],[b=>b.result.value=at('unknown'),'TYPE'],
  ];
  for(const [mutate,code] of cases){const b=structuredClone(f.bindings);mutate(b);rejects(()=>f.check(b),code);}
  const readValue=structuredClone(f.bindings);readValue.writes[0].value=at('current');readValue.result={type:scalar('UInt64'),value:at('current','FIXTURE-ACCOUNT#balance')};assert.equal(f.check(readValue).bindings.result.type.kind,'scalar');
  const deletion=structuredClone(f.bindings);deletion.writes[0].mode='delete';assert.equal(f.check(deletion).writes[0]!.mode,'delete');
  const literal=structuredClone(f.bindings);literal.result={type:scalar('UInt64'),value:lit('UInt64','18446744073709551615')};assert.equal((f.check(literal).bindings.result.value as any).value,'18446744073709551615');
  literal.result.value.value='18446744073709551616';assert.throws(()=>f.check(literal));
});

test('Field/source brands, cross-graph selections and exact contract bytes are enforced',t=>{
  const f=fixture(t);rejects(()=>f.check(f.bindings,contract+' '),'CONTRACT_DRIFT');
  assert.throws(()=>compileOperationActionBindings(structuredClone(f.graph),f.boundary,f.fields,f.bindings,contract));
  assert.throws(()=>compileOperationActionBindings(f.graph,structuredClone(f.boundary),f.fields,f.bindings,contract));
  assert.throws(()=>compileOperationActionBindings(f.graph,f.boundary,structuredClone(f.fields),f.bindings,contract));
  rejects(()=>f.check({...f.bindings,selector:'commerce:account'}),'ROOT');
  const changed=read(path.join(f.source,'specs/commerce/nodes/audit.json'));changed.body.description='changed rule evidence';f.write('specs/commerce/nodes/audit.json',changed);
  const other=f.compile();rejects(()=>compileOperationActionBindings(other.graph,f.boundary,f.fields,f.bindings,contract),'CROSS_GRAPH');
  rejects(()=>compileOperationActionBindings(other.graph,other.boundary,f.fields,f.bindings,contract),'CROSS_GRAPH');
});

test('Input/source changes are causal while slot order and repeated concept occurrences stay distinct',t=>{
  const f=fixture(t),first=f.check(),b=structuredClone(f.bindings);b.guards.reverse();const reordered=f.check(b);assert.notEqual(first.action_sha256,reordered.action_sha256);assert.equal(reordered.guards[0]!.selector,'commerce:audit');
  const literal=structuredClone(f.bindings);literal.guards[1].arguments[0].value=lit('Bool',false);assert.notEqual(first.action_sha256,f.check(literal).action_sha256);
  const event=read(path.join(f.source,'specs/commerce/nodes/posted.json'));event.body.version='2';f.write('specs/commerce/nodes/posted.json',event);
  const second=f.compile().check();assert.notEqual(first.action_sha256,second.action_sha256);assert.equal(first.bindings_sha256,second.bindings_sha256);assert.equal(second.events[0]!.contract.version,'2');
  const op=read(path.join(f.source,'specs/commerce/nodes/post.json'));op.body.effects.push('second-posted-fact');f.write('specs/commerce/nodes/post.json',op);
  const repeated=structuredClone(f.bindings);repeated.events.push({slot:'second-posted-fact',target:'commerce:posted',parameter:'second_posted_input'});
  const result=f.compile().check(repeated);assert.equal(result.events.length,2);assert.equal(result.events[0]!.target,result.events[1]!.target);assert.notEqual(result.events[0]!.parameter,result.events[1]!.parameter);
});

test('Composite Entity identity keys use their declared Value Object, not a String shortcut',t=>{
  const f=fixture(t);
  f.node('valid-identity','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-VALID-IDENTITY',parameters:[{name:'code',type:scalar()}],expression:{op:'eq',left:at('code'),right:at('code')}}});
  f.node('identity','Value Object',{fields:['code'],invariant_refs:['commerce:valid-identity'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-IDENTITY',properties:[f.property('identity','code',scalar())]}});
  const account=read(path.join(f.source,'specs/commerce/nodes/account.json'));account.body.typed_contract.properties[0].type=named('commerce:identity');f.write('specs/commerce/nodes/account.json',account);f.save();
  const c=f.compile();rejects(()=>c.check(),'READ_KEY_TYPE');
  const b=structuredClone(f.bindings);b.inputs[0].type=named('commerce:identity');const checked=c.check(b);assert.deepEqual(checked.reads[0]!.identity.type,named('commerce:identity'));
});

test('Optional, list, set and sum inputs remain distinct and cannot be implicitly traversed',t=>{
  const f=fixture(t),hashes=new Set<string>();
  const types=[{kind:'optional',element:named('commerce:account')},{kind:'list',element:named('commerce:account')},{kind:'set',element:named('commerce:account')},
    {kind:'sum',variants:[{ontology_variant:'FIXTURE-RESULT#Empty',name:'Empty',payload:null},{ontology_variant:'FIXTURE-RESULT#Found',name:'Found',payload:named('commerce:account')}]}];
  for(const type of types){
    const b=structuredClone(f.bindings);b.inputs.push({name:'structured',type});b.result={type,value:at('structured')};
    const checked=f.check(b);assert.deepEqual(checked.bindings.result.type,type);hashes.add(checked.action_sha256);
    b.result.type=named('commerce:account');rejects(()=>f.check(b),'RESULT_TYPE');
    if(type.kind==='optional'||type.kind==='sum'){b.result={type:scalar(),value:at('structured','FIXTURE-ACCOUNT#id')};rejects(()=>f.check(b),'TYPE');}
  }
  assert.equal(hashes.size,4);
  const b=structuredClone(f.bindings);b.inputs.push({name:'accounts',type:types[1]});b.result={type:types[2],value:{op:'to_set',value:at('accounts')}};
  assert.deepEqual(f.check(b).bindings.result.type,types[2]);
  b.result.type=types[1];rejects(()=>f.check(b),'RESULT_TYPE');
  const swap=structuredClone(f.bindings);swap.inputs.push({name:'other_id',type:scalar()});const first=f.check(swap);swap.reads[0].key=at('other_id');
  assert.notEqual(first.action_sha256,f.check(swap).action_sha256);
  assert.ok(first.execution_obligations.includes('owned-value-validation-before-writes'));
});

test('Legacy typed Operation v1 is not reinterpreted as explicit action bindings',t=>{
  const f=fixture(t),op=read(path.join(f.source,'specs/commerce/nodes/post.json'));
  op.body.typed_contract={schema_version:'domainspec.typed-operation/v1',ontology_operation:'FIXTURE-LEGACY-POST',inputs:[{name:'account',type:named('commerce:account')}],
    output:named('commerce:receipt'),guard:'commerce:can-post',reads:['commerce:account'],writes:['commerce:receipt'],effects:[],failure_continuation:'return-post-error',
    success_result:{variant:'Allow',payload_variant:null},failure_result:{variant:'Deny',payload_variant:null}};
  f.write('specs/commerce/nodes/post.json',op);
  rejects(()=>f.compile().check(),'LEGACY_TYPED_SOURCE');
});

test('Source-declared Event-only and guard-only Operations do not acquire fabricated writes',t=>{
  const f=fixture(t),op=read(path.join(f.source,'specs/commerce/nodes/post.json')),b=structuredClone(f.bindings);
  op.body.writes=[];b.writes=[];f.edges.splice(f.edges.indexOf('post-creates-receipt'),1);
  f.write('specs/commerce/nodes/post.json',op);f.save();
  const eventOnly=f.compile().check(b);assert.equal(eventOnly.writes.length,0);assert.equal(eventOnly.events.length,1);
  op.body.effects=[];b.events=[];f.edges.splice(f.edges.indexOf('post-produces-posted'),1);
  f.write('specs/commerce/nodes/post.json',op);f.save();
  const guardedRead=f.compile().check(b);assert.equal(guardedRead.writes.length,0);assert.equal(guardedRead.events.length,0);assert.equal(guardedRead.reads.length,1);
  assert.notEqual(eventOnly.action_sha256,guardedRead.action_sha256);
  assert.equal(guardedRead.execution,'not-performed');
});
