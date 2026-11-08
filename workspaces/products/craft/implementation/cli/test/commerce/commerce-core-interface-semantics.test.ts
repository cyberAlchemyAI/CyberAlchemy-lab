/** Eager unused Interface rejection; native qualification stays separate.
 * Open Questions: docs/COMMERCE-OBLIGATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {checkCoreCommerceInterfaceSources,CORE_INTERFACE_IMPLEMENTATION_TASKS} from '../../src/commerce/commerce-core-interface-semantics.js';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const base=`module Test version 1
value-object Item:
  count UInt64
rule Positive:
  input value UInt64
  expression value > 0
operation Run:
  input item Item
  output Item
  return item
interface Api:
  kind internal
  exposes Run
  visibility service-private owner test
interface Application:
  kind application-composition
  service test module Test
  formal-claims optional
`;
const native=`interface Native:
  kind native-producer
  abi craft.test/v1-candidate
  custody private-registered-source-profile-callsite
  signatures context.json#/methods
`;
const value={source_module:'Test@1',abi:'craft.test/v1-candidate',methods:{unused:{parameters:['UInt64'],result:'Bool'}}};
const check=(extra='',doc:unknown=value,source=base)=>checkCoreCommerceInterfaceSources([{path:'application.alch',text:source+extra}],[{path:'context.json',text:JSON.stringify(doc)}]);
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
test('eager check captures unused native parameters/results without original native custody',()=>{const rows=check(native),n=rows.find(r=>r.name==='Test.Native')!;assert.equal(n.static_types.length,2);assert.deepEqual(n.dependencies,['context.json']);assert.equal(n.runtime_qualified,false);assert.deepEqual(n.implementation_tasks,['EC09','EC12']);assert.ok(Object.isFrozen(CORE_INTERFACE_IMPLEMENTATION_TASKS['native-producer']));});
for(const [name,edit]of [
 ['unknown parameter',(d:any)=>d.methods.unused.parameters=['Missing']],
 ['unknown result',(d:any)=>d.methods.unused.result='Missing'],
 ['foreign schema version',(d:any)=>d.methods.unused.result='schema:Test.Item@2'],
 ['unknown source module',(d:any)=>d.source_module='Other@1'],
 ['missing finite domain',(d:any)=>d.methods.unused.parameters=['ServiceId']],
 ['public ABI signature',(d:any)=>d.methods.unused.abi='foreign/v1'],
 ['invalid method name',(d:any)=>{d.methods['bad-name']=d.methods.unused;delete d.methods.unused;}],
 ['invalid parameter name',(d:any)=>d.methods.unused.parameters=[{name:'bad-name',type:'UInt64'}]],
]as const)test('unused Interface rejects '+name,()=>{const d=JSON.parse(JSON.stringify(value));edit(d);failure(()=>check(native,d));});
test('service-private visibility must match actual service module owner',()=>failure(()=>check('',value,base.replace('owner test','owner other')),'InvalidContract'));
test('a clause from a different Interface kind is rejected eagerly',()=>failure(()=>check('',value,base.replace('  exposes Run','  exposes Run\n  protocol TestProtocol')),'InvalidContract'));
test('duplicate singleton metadata cannot silently choose one value',()=>failure(()=>check(native.replace('  abi craft.test/v1-candidate','  abi craft.test/v1-candidate\n  abi craft.test/v1-candidate')),'DuplicateSymbol'));
const domain=`interface Values:
  kind bounded-schema
  scalar UInt64 wire canonical-decimal-string native bigint range 0..18446744073709551615
  validates UInt64 using Positive
`;
test('full unsigned scalar domain and exact unary Bool rule are checked',()=>{assert.equal(check(domain).find(r=>r.name==='Test.Values')!.static_types.length,1);});
test('narrow primitive range must be expressed as a business refinement',()=>failure(()=>check(domain.replace('0..18446744073709551615','1..18446744073709551615')),'UnsupportedCapability'));
test('closed enum validation mode cannot bless a UInt64',()=>failure(()=>check(domain.replace('using Positive','using closed-enum')),'TypeMismatch'));
test('a validation rule needs the exact bounded argument type',()=>failure(()=>check(domain, value,base.replace('input value UInt64','input value Bool').replace('expression value > 0','expression value')),'TypeMismatch'));
test('an unresolved configuration pointer is not an implementation binding',()=>failure(()=>check(native.replace('#/methods','#/missing')),'UnknownReference'));
test('the original semantic owner rejects an unused invalid signature',()=>{const root=mkdtempSync(path.join(tmpdir(),'commerce-interface-eager-'));try{writeFileSync(path.join(root,'application.alch'),base+native);const invalid=JSON.parse(JSON.stringify(value));invalid.methods.unused.result='Missing';writeFileSync(path.join(root,'context.json'),JSON.stringify(invalid));const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root),semantics=createCoreCommerceSemanticOwner(sources);failure(()=>semantics.check(capture),'UnknownReference');}finally{rmSync(root,{recursive:true,force:true});}});
