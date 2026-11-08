/** Faithful candidate pure producer data; no computation engine is executed.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createCoreCommerceComputationContract,checkCoreCommerceComputationProposal} from '../../src/commerce/commerce-core-pure-contract.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const limits={max_input_bytes:1048576,max_output_bytes:1048576,max_value_bytes:1048576,max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:64,max_call_depth:32,fuel:100000};
const text=`module Demo version 1
value-object Label:
  carrier String
  utf8-bytes 2..8
  unicode-scalars 2..8
  pattern "^[a-z]{2,8}$"
value-object Receipt:
  kind literal "accepted"
  label Label
entity Store:
  id UInt64
  version UInt64
  identity id
  immutable all
  invariant version > 0
event Happened:
  version 1
  id UInt64
enum Status:
  value Ready wire "ready"
  value Done wire "done"
enum Signal:
  value Go
calculation RefineLabel:
  pure
  input raw literal "abc"
  result Label
  expression Label(raw)
calculation Difference:
  pure
  input first UInt64
  input second UInt64
  result UInt64
  expression first - second
  on-evaluation-error reject invalid-difference
calculation Divide:
  pure
  result UInt64
  rounding floor
  expression 4 / 3
  on-evaluation-error fail InvalidDivision
calculation Ceil:
  pure
  result UInt64
  rounding ceil
  expression 4 / 3
policy Select:
  input yes Bool
  result UInt64
  ordered-cases:
    primary when yes -> Difference(second=4 / 0,first=0 - 1)
    otherwise -> Divide()
state-machine Lifecycle:
  state Status
  input Signal
  initial Ready
  terminal Done
  transition Ready Go -> Done
  otherwise reject invalid-transition
mapping MakeReceipt:
  target Receipt
  total true
  field kind <- "accepted"
  field label <- Label("abc")
mapping Positive:
  input value UInt64
  target UInt64
  total true
  requires value > 0
  expression value
interface Application:
  kind application-composition
  formal-claims optional
`;
const sources=(value=text)=>[{path:'application.alch',text:value}];
const contract=(node='Demo.Select',value=text)=>createCoreCommerceComputationContract(sources(value),node,limits);
const definition=(name:string,node='Demo.Select')=>contract(node).functions.find(f=>f.name==='Demo.'+name)!;
const schema=JSON.parse(readFileSync(new URL('../../contracts/iteration-expression-v2.schema.json',import.meta.url),'utf8'));
const validate=Object.assign((instance:unknown)=>{const r=spawnSync('python3',['-c','import json,sys,jsonschema; d=json.load(sys.stdin); errors=list(jsonschema.Draft202012Validator(d["schema"]).iter_errors(d["instance"])); print(json.dumps([e.message for e in errors[:10]]))'],{input:JSON.stringify({schema,instance}),encoding:'utf8',maxBuffer:1048576});assert.equal(r.status,0,r.stderr);validate.errors=JSON.parse(r.stdout);return validate.errors.length===0;},{errors:[] as string[]});
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
test('fresh source projection conforms to the current closed computation schema',()=>{const c=contract();assert.equal(validate(c),true,JSON.stringify(validate.errors));assert.equal(c.source_node,'Demo.Select');assert.equal(c.expression.op,'call');assert.equal(Object.hasOwn(c,'accepted'),false);});
test('literal field constraints remain exact in both the schema and constructed AST',()=>{const c=contract(),r=c.values.records.find(r=>r.name==='Demo.Receipt')!,body=c.functions.find(f=>f.name==='Demo.MakeReceipt')!.body;assert.deepEqual(r.fields.kind,{kind:'literal',value:'accepted'});assert.equal(body.op,'record');if(body.op==='record'){const kind=body.fields.kind!;assert.equal(kind.op,'literal');if(kind.op==='literal')assert.deepEqual(kind.type,{kind:'literal',value:'accepted'});}});
test('refinement byte/scalar minima, maxima and pattern all cross the producer boundary',()=>{const r=contract().values.refinements[0]!;assert.equal(r.min_utf8_bytes,2);assert.equal(r.max_utf8_bytes,8);assert.equal(r.min_unicode_scalars,2);assert.equal(r.max_unicode_scalars,8);assert.equal(r.pattern,'^[a-z]{2,8}$');assert.equal(r.normalization,'none');});
test('dynamic constructor emits validation with a declared failure instead of an unchecked cast',()=>{const b=definition('RefineLabel').body;assert.equal(b.op,'validate_refinement');if(b.op==='validate_refinement'){assert.equal(b.refinement,'Demo.Label');assert.equal(b.on_invalid,'InputType');assert.deepEqual(b.value,{op:'var',name:'raw'});}});
test('named Policy action evaluates the second parameter expression first because it is first in source',()=>{const b=definition('Select').body;assert.equal(b.op,'policy');if(b.op!=='policy')return;const action=b.cases[0]!.action;assert.equal(action.calculation,'Demo.Difference');const first=action.expression;assert.equal(first.op,'let');if(first.op!=='let')return;assert.equal(first.value.op,'binary');if(first.value.op==='binary')assert.equal(first.value.operator,'divide');const second=first.body;assert.equal(second.op,'let');if(second.op!=='let')return;assert.equal(second.value.op,'binary');if(second.value.op==='binary')assert.equal(second.value.operator,'subtract');assert.equal(second.body.op,'call');if(second.body.op==='call')assert.deepEqual(second.body.arguments,[{op:'var',name:second.binding.name},{op:'var',name:first.binding.name}]);});
test('Policy actions stay inside their source branch and otherwise remains a separate call',()=>{const b=definition('Select').body;assert.equal(b.op,'policy');if(b.op==='policy'){assert.equal(b.cases[0]!.action.expression.op,'let');assert.equal(b.otherwise.calculation,'Demo.Divide');assert.equal(b.otherwise.expression.op,'call');}});
test('each function retains its own rounding and error channel independently of root rounding',()=>{const c=contract(),divide=c.functions.find(f=>f.name==='Demo.Divide')!,ceil=c.functions.find(f=>f.name==='Demo.Ceil')!;assert.equal(c.rounding,'reject');assert.equal(divide.rounding,'floor');assert.deepEqual(divide.on_evaluation_error,{kind:'fail',code:'InvalidDivision'});assert.equal(ceil.rounding,'ceil');assert.equal(ceil.on_evaluation_error,null);assert.equal(contract('Demo.Divide').rounding,'floor');});
test('Mapping preconditions remain annotations of checks embedded once in the body',()=>{const f=definition('Positive');assert.equal(f.preconditions.length,1);assert.equal(f.precondition_mode,'embedded-once-in-body');assert.equal(f.body.op,'require_some');});
test('enum wire values remain distinct from source variant names',()=>{const status=contract().values.enums.find(e=>e.name==='Demo.Status')!;assert.deepEqual(status.variants.map(v=>({name:v.name,wire:v.wire})),[{name:'Ready',wire:'ready'},{name:'Done',wire:'done'}]);});
test('StateMachine initial, terminal and rejection reason are retained in its own AST',()=>{const b=definition('Lifecycle').body;assert.equal(b.op,'state_machine');if(b.op==='state_machine'){assert.equal(b.initial.op,'enum_value');if(b.initial.op==='enum_value')assert.equal(b.initial.variant,'Ready');assert.equal(b.terminal.length,1);assert.equal(b.otherwise_reason,'invalid-transition');assert.equal(b.otherwise,'reject');}});
test('Event schema version, Entity invariants and immutable-all fields are explicit',()=>{const c=contract(),event=c.values.records.find(r=>r.name==='Demo.Happened')!,entity=c.values.records.find(r=>r.name==='Demo.Store')!;assert.equal(event.event_version,1);assert.equal(entity.event_version,null);assert.equal(entity.invariants.length,1);assert.deepEqual(entity.entity!.immutable,['id','version']);assert.equal(entity.entity!.version,'version');});
test('a zero-byte refinement domain remains zero rather than being widened to one byte',()=>{const value=text.replace('utf8-bytes 2..8','utf8-bytes 0..0').replace('unicode-scalars 2..8','unicode-scalars 0..0').replace('^[a-z]{2,8}$','^$').replaceAll('literal "abc"','literal ""').replaceAll('Label("abc")','Label("")');const c=contract('Demo.RefineLabel',value),r=c.values.refinements[0]!;assert.equal(r.min_utf8_bytes,0);assert.equal(r.max_utf8_bytes,0);assert.deepEqual(r.carrier,{kind:'string',max_bytes:0,max_scalars:0});assert.equal(validate(c),true,JSON.stringify(validate.errors));});
test('source/limit inputs and returned data are not mutated by projection',()=>{const before=JSON.stringify(limits),c=contract();assert.equal(JSON.stringify(limits),before);assert.notEqual(c.limits,limits);assert.equal(Object.isFrozen(c),true);assert.equal(Object.isFrozen(c.functions),true);});
test('unknown or merely unqualified selected declaration rejects',()=>{failure(()=>contract('Select'),'UnknownReference');failure(()=>contract('Demo.Absent'),'UnknownReference');});
test('unknown, missing or nonpositive limit fields reject',()=>{for(const bad of [{...limits,extra:1},{...limits,fuel:0},{...limits,max_items:1.2}])failure(()=>createCoreCommerceComputationContract(sources(),'Demo.Select',bad as any),'InvalidContract');const bad:any={...limits};delete bad.fuel;failure(()=>createCoreCommerceComputationContract(sources(),'Demo.Select',bad),'InvalidContract');});
test('limit accessors are rejected without executing them',()=>{let called=false;const bad={...limits};Object.defineProperty(bad,'fuel',{enumerable:true,get(){called=true;return 1;}});failure(()=>createCoreCommerceComputationContract(sources(),'Demo.Select',bad),'InvalidContract');assert.equal(called,false);});
test('whole matching data is freshly rebuilt and supplies no original semantic or native owner',()=>{const proposal=JSON.parse(JSON.stringify(contract())),actual=checkCoreCommerceComputationProposal(sources(),'Demo.Select',limits,proposal);assert.notEqual(actual,proposal);assert.equal(Object.hasOwn(actual,'authorized'),false);assert.equal(Object.hasOwn(actual,'original_owner'),false);});
for(const field of ['values','functions','rounding','inputs','expression','limits','source_node','result'])test('rejects producer proposal forgery '+field,()=>{const p=JSON.parse(JSON.stringify(contract()));p[field]='forged';failure(()=>checkCoreCommerceComputationProposal(sources(),'Demo.Select',limits,p),'InvalidContract');});
test('changing a function rounding/error or bound cannot hide under matching contract identity labels',()=>{for(const edit of [(p:any)=>p.functions.find((f:any)=>f.name==='Demo.Divide').rounding='ceil',(p:any)=>p.functions.find((f:any)=>f.name==='Demo.Divide').on_evaluation_error=null,(p:any)=>p.values.refinements[0].min_utf8_bytes=0,(p:any)=>p.values.enums.find((e:any)=>e.name==='Demo.Status').variants[0].wire='Ready']){const p=JSON.parse(JSON.stringify(contract()));edit(p);failure(()=>checkCoreCommerceComputationProposal(sources(),'Demo.Select',limits,p),'InvalidContract');}});
test('the closed shape rejects erased metadata, unknown AST keys and an invented successful validation outcome',()=>{for(const edit of [(p:any)=>delete p.functions[0].rounding,(p:any)=>delete p.values.refinements[0].min_utf8_bytes,(p:any)=>p.functions.find((f:any)=>f.name==='Demo.RefineLabel').body.on_invalid='continue',(p:any)=>p.functions[0].body.callback='arbitrary']){const p=JSON.parse(JSON.stringify(contract()));edit(p);assert.equal(validate(p),false);}});
test('proposal getters do not execute during a comparison',()=>{let called=false;failure(()=>checkCoreCommerceComputationProposal(sources(),'Demo.Select',limits,{get values(){called=true;return {};}}),'InvalidContract');assert.equal(called,false);});
