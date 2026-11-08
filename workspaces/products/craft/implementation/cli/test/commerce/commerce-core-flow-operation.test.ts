/** Typed operation/control/native obligations, never runtime commit evidence.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {checkCoreCommerceOperationSources,auditCoreCommerceOperationSources,checkCoreCommerceOperationProposal,type CoreOperationStep,type CoreOperationSource} from '../../src/commerce/commerce-core-flow-operation.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const base=`module Demo version 1
entity Counter:
  id UInt64
  amount UInt64
  version UInt64
  identity id
  immutable id
enum Flag:
  value Yes
  value No
enum Status:
  value Open
  value Closed
enum Signal:
  value Go
event Changed:
  version 1
  id UInt64
  amount UInt64
interface Application:
  kind application-composition
  service demo module Demo
  formal-claims optional
`;
const operation=`
operation Apply:
  input id UInt64
  input increment UInt64
  output UInt64
  read counter Counter by id=id
    on-missing reject missing
    on-unavailable fail outcome-unknown
  requires increment > 0
  transaction Change:
    atomic-participants Counter
    update changed Counter by id=id expected-version counter.version:
      amount <- counter.amount + increment
      version <- counter.version + 1
    on-version-conflict reject contention
    on-unknown-commit fail outcome-unknown
  return changed.amount
`;
const source=(extra=operation,model=base)=>[{path:'application.alch',text:model+extra}];
const check=(extra=operation,model=base)=>checkCoreCommerceOperationSources(source(extra,model));
const op=(extra=operation,name='Demo.Apply')=>check(extra).operations.find(o=>o.name===name)!;
const transaction=(o:CoreOperationSource)=>{const t=o.body.find(s=>s.kind==='transaction');assert.equal(t?.kind,'transaction');if(t?.kind!=='transaction')assert.fail();return t.transaction;};
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(error:unknown)=>error instanceof CoreCommerceSourceError&&(!code||error.diagnostics[0]!.code===code));
function historicalSource(){const root=fileURLToPath(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/binding-repair-before/',import.meta.url)).replace(/\/$/,''),owner=createCoreCommerceSourceOwner(),handle=owner.prepare(root),inspection=owner.inspect(handle),paths=new Set(inspection.reconstruction.modules.map(m=>m.path));return {owner,handle,sources:inspection.files.filter(f=>paths.has(f.path)),assets:inspection.files.filter(f=>f.path.endsWith('.json')).map(f=>({path:f.path,text:f.text}))};}
test('preserved pre-repair commerce source reconstructs 17 Operations and reports the exact two unresolved native type bindings',()=>{const f=historicalSource(),result=auditCoreCommerceOperationSources(f.sources,f.assets);assert.equal(result.operations.length,17);assert.equal(result.complete,false);assert.deepEqual(result.diagnostics.map(d=>d.operation).sort(),['Orders.CancelOrder','Orders.ConfirmOrder']);assert.ok(result.diagnostics.every(d=>d.diagnostics[0]!.code==='UnknownReference'&&d.diagnostics[0]!.message.includes('CancellationReason')));f.owner.assertCurrent(f.handle);failure(()=>checkCoreCommerceOperationSources(f.sources,f.assets),'UnknownReference');f.owner.dispose(f.handle);});
test('all 19 operation bodies typecheck under an isolated explicit ABI binding repair, without changing original source assets',()=>{const f=historicalSource(),original=f.assets.find(a=>a.path==='contracts/context.json')!.text,assets=f.assets.map(a=>{if(a.path!=='contracts/context.json')return a;const doc=JSON.parse(a.text);doc.identity_producers.methods.orderActionFingerprint.parameters[2].type='optional<Shop.Events.CancellationReason>';return {...a,text:JSON.stringify(doc)};});const result=checkCoreCommerceOperationSources(f.sources,assets);assert.equal(result.operations.length,19);assert.equal(result.complete,true);assert.ok(result.operations.every(o=>o.qualification==='typed-operation-source-only'));assert.equal(f.assets.find(a=>a.path==='contracts/context.json')!.text,original);f.owner.assertCurrent(f.handle);f.owner.dispose(f.handle);});
test('structured reads, guards, ordered writes and typed results preserve their source order',()=>{const r=op();assert.deepEqual(r.body.map(s=>s.kind),['read','guard','transaction','action']);assert.equal(r.result.kind,'UInt64');assert.equal(r.qualification,'typed-operation-source-only');});
test('transaction version values remain guarded native requirements rather than fake CAS receipts',()=>{const t=transaction(op()),m=t.body[0]!;assert.equal(m.kind,'mutation');if(m.kind==='mutation'){assert.equal(m.original_row,'required-for-exact-key-and-store');assert.equal(m.version_validation,'original-row+expected-version+exact-one-increment-before-write');assert.equal(m.expected_version!.type.kind,'UInt64');}assert.ok(t.native_requirements.includes('original-commit-or-rollback-or-indeterminate-evidence'));});
test('rollback and unknown commit channels remain distinct original evidence requirements',()=>{const t=transaction(op());assert.equal(t.handlers.find(h=>h.channel==='on-version-conflict')!.requires,'original-proven-rollback');assert.equal(t.handlers.find(h=>h.channel==='on-unknown-commit')!.requires,'original-unresolved-commit');assert.equal(t.handlers.find(h=>h.channel==='on-unknown-commit')!.retain_original,true);});
test('missing transaction handlers retain exact fixed defaults and explicit rollback fallback order',()=>{const t=transaction(op(operation.replace('    on-version-conflict reject contention\n','')));assert.deepEqual(t.defaults.find(d=>d.channel==='on-version-conflict')!.action,{kind:'reject',code:'transaction-contention'});assert.equal(t.defaults.find(d=>d.channel==='on-arithmetic-error')!.fallback,'explicit-proven-rollback-handler-then-fixed-default');assert.equal(t.defaults.find(d=>d.channel==='on-unknown-commit')!.fallback,'fixed-default');});
test('a continuing successful read is unwrapped only when its missing action terminates',()=>{const r=op(),read=r.body[0]!;assert.equal(read.kind,'read');if(read.kind==='read')assert.deepEqual(read.type,{kind:'record',name:'Demo.Counter'});failure(()=>check(operation.replace('    on-missing reject missing\n','')),'TypeMismatch');});
test('on-present paths narrow optional records only inside their true branch',()=>{const extra='\noperation Apply:\n  input id UInt64\n  output UInt64\n  read prior Counter by id=id\n  on-present require prior.amount > 0 else reject invalid\n  on-present return prior.amount\n  return 0\n';assert.equal(op(extra).body[1]!.kind,'present');failure(()=>check(extra.replace('  return 0','  return prior.amount')),'TypeMismatch');});
test('a terminating absence test narrows the continuing path',()=>{const extra='\noperation Apply:\n  input id UInt64\n  output UInt64\n  read prior Counter by id=id\n  on absent(prior) reject missing\n  return prior.amount\n';assert.equal(op(extra).body.at(-1)!.kind,'action');});
test('complete enum branch coverage proves the result path without a fake trailing return',()=>{const extra='\noperation Apply:\n  input flag Flag\n  output UInt64\n  on flag Yes return 1\n  on flag No return 0\n';assert.deepEqual(op(extra).body.map(s=>s.kind),['case','case']);failure(()=>check(extra.replace('  on flag No return 0\n','')),'MissingMapping');});
test('guarded enum cases cannot manufacture exhaustive result coverage',()=>{const extra='\noperation Apply:\n  input flag Flag\n  output UInt64\n  on flag Yes when false return 1\n  on flag No return 0\n';failure(()=>check(extra),'MissingMapping');});
test('when/otherwise paths with typed returns are complete',()=>{const extra='\noperation Apply:\n  input yes Bool\n  output UInt64\n  when yes:\n    return 1\n  otherwise:\n    return 0\n';assert.equal(op(extra).body[0]!.kind,'conditional');});
test('new transaction aliases escape only on the successful commit path',()=>{const extra='\noperation Apply:\n  input id UInt64\n  output UInt64\n  transaction Create:\n    atomic-participants Counter\n    create counter Counter:\n      id <- id\n      amount <- 0\n      version <- 1\n    on-unknown-commit fail outcome-unknown\n  return counter.amount\n';assert.equal(op(extra).body.at(-1)!.kind,'action');failure(()=>check(extra.replace('on-unknown-commit fail outcome-unknown','on-unknown-commit return counter.amount')),'UnknownReference');});
test('a create alias may reuse the same optional outer read without manufacturing an unwrapped outer binding',()=>{const extra='\noperation Apply:\n  input id UInt64\n  output UInt64\n  read counter Counter by id=id\n  on-present return counter.amount\n  transaction Create:\n    atomic-participants Counter\n    create counter Counter:\n      id <- id\n      amount <- 0\n      version <- 1\n  return 0\n';assert.equal(transaction(op(extra)).body[0]!.kind,'mutation');});
test('branch-local mutation aliases may repeat without leaking across branches',()=>{const extra='\noperation Apply:\n  input id UInt64\n  input yes Bool\n  output UInt64\n  transaction Create:\n    atomic-participants Counter\n    when yes:\n      create row Counter:\n        id <- id\n        amount <- 1\n        version <- 1\n    otherwise:\n      create row Counter:\n        id <- id\n        amount <- 0\n        version <- 1\n  return 0\n';assert.equal(transaction(op(extra)).body[0]!.kind,'conditional');failure(()=>check(extra.replace('  return 0','  return row.amount')),'UnknownReference');});
test('typed record-event materializes data inside a transaction but sends nothing',()=>{const extra=operation.replace('    on-version-conflict','    record-event changedEvent Changed:\n      id <- id\n      amount <- changed.amount\n    on-version-conflict');const t=transaction(op(extra));assert.equal(t.body[1]!.kind,'mutation');if(t.body[1]!.kind==='mutation')assert.equal(t.body[1]!.operation,'record-event');});
test('transaction guard and local-expression failures require actual proven rollback before their actions',()=>{const extra=operation.replace('    update changed','    requires increment > 0\n    let next = counter.amount + increment\n    update changed'),t=transaction(op(extra));assert.equal(t.body[0]!.kind,'guard');if(t.body[0]!.kind==='guard')assert.equal(t.body[0]!.failure_execution,'after-original-proven-rollback');assert.equal(t.body[1]!.kind,'let');if(t.body[1]!.kind==='let')assert.equal(t.body[1]!.on_error,null);});
test('read failure acknowledgement suppression remains in the checked source facet',()=>{const r=op(operation.replace('on-unavailable fail outcome-unknown','on-unavailable fail outcome-unknown; do-not-ack')),read=r.body[0]!;assert.equal(read.kind,'read');if(read.kind==='read')assert.deepEqual(read.do_not_ack,['unavailable']);});
test('local Operation calls retain source argument order and actual result types',()=>{const extra='\noperation Helper:\n  input second UInt64\n  input first UInt64\n  output UInt64\n  return first\n\noperation Apply:\n  input id UInt64\n  output UInt64\n  call value Helper(first=id,second=0)\n  return value\n';const step=op(extra).body[0]!;assert.equal(step.kind,'call');if(step.kind==='call')assert.deepEqual(step.call.arguments.map(a=>a.parameter),['first','second']);});
test('invoke-return retains its callee role instead of becoming a pure call',()=>{const extra='\noperation Helper:\n  output UInt64\n  return 1\n\noperation Apply:\n  output UInt64\n  return Helper()\n';const a=op(extra).body[0]!;assert.equal(a.kind,'action');if(a.kind==='action')assert.equal(a.action.kind,'invoke-return');});
const set=`
operation Reject:
  output UInt64
  transaction RejectWork:
    atomic-participants Counter
    create receipt Counter:
      id <- 0
      amount <- 0
      version <- 1
  return 0
operation Apply:
  input ids List<UInt64,10>
  output UInt64
  read-set rows:
    for id in ids:
      read row Counter by id=id
        on-missing return Reject()
      bind row, expectedVersion = row.version
    validate-all-before-writes
  transaction ChangeAll:
    atomic-participants Counter
    for value in rows:
      update changed Counter by id=value.row.id expected-version value.expectedVersion:
        amount <- value.row.amount + 1
        version <- value.row.version + 1
  return 1
`;
test('read-set collection retains closed row/version data and bounded transaction iteration',()=>{const r=op(set),readset=r.body[0]!;assert.equal(readset.kind,'read-set');if(readset.kind==='read-set'){assert.equal(readset.before_writes,true);assert.equal(readset.type.kind,'List');assert.deepEqual(readset.collected.map(f=>f.name),['row','expectedVersion']);const read=readset.body[0]!;assert.equal(read.kind,'read');if(read.kind==='read'){assert.equal(read.on_missing!.kind,'invoke-return');if(read.on_missing!.kind==='invoke-return')assert.equal(read.on_missing!.read_set_unwind_required,true);}}assert.equal(transaction(r).body[0]!.kind,'for');});
test('effectful validation calls must terminate and unwind rather than continue inside read-set',()=>failure(()=>check(set.replace('      read row Counter','      call ignored Reject()\n      read row Counter')),'InvalidContract'));
test('read-set and transaction loop binders cannot escape their source scopes',()=>failure(()=>check(set.replace('  return 1','  return value.row.amount')),'UnknownReference'));
test('StateMachine proposed state requires the source transition guard before mutation use',()=>{const machine='\nstate-machine Flow:\n  state Status\n  input Signal\n  initial Open\n  transition Open Go -> Closed\n  otherwise reject invalid-transition\n',extra=machine+'\noperation Apply:\n  input current Status\n  input event Signal\n  output Status\n  let proposal = Flow.propose(current,event)\n  requires proposal.tag == "transition"\n  return proposal.state\n';assert.equal(op(extra).body.at(-1)!.kind,'action');failure(()=>check(extra.replace('  requires proposal.tag == "transition"\n','')),'InvalidContract');assert.equal(op(extra.replace('  requires proposal.tag == "transition"','  on proposal.tag != "transition" reject invalid-transition')).body.at(-1)!.kind,'action');});
for(const [name,extra,code]of [
 ['Bool guard type',operation.replace('requires increment > 0','requires increment'),'TypeMismatch'],
 ['wrong return type',operation.replace('return changed.amount','return true'),'TypeMismatch'],
 ['missing result path',operation.replace('  return changed.amount\n',''),'MissingMapping'],
 ['unreachable statement',operation+'  return 0\n','InvalidContract'],
 ['unknown data variable',operation.replace('amount <- counter.amount + increment','amount <- missing'),'UnknownReference'],
 ['duplicate local binding',operation.replace('  requires increment > 0','  let id = 1\n  requires increment > 0'),'DuplicateSymbol'],
 ['partial compound key',operation.replace('by id=id','by amount=id'),'InvalidContract'],
 ['duplicate key field',operation.replace('by id=id','by id=id,id=id'),'DuplicateSymbol'],
 ['wrong key type',operation.replace('by id=id','by id=true'),'TypeMismatch'],
 ['wrong expected version type',operation.replace('expected-version counter.version','expected-version true'),'TypeMismatch'],
 ['missing next version assignment',operation.replace('      version <- counter.version + 1\n',''),'MissingMapping'],
 ['immutable identity update',operation.replace('      amount <-','      id <- 1\n      amount <-'),'InvalidContract'],
 ['unknown mutation field',operation.replace('      amount <-','      unknown <-'),'UnknownReference'],
 ['duplicate mutation field',operation.replace('      amount <- counter.amount + increment','      amount <- 1\n      amount <- counter.amount + increment'),'DuplicateSymbol'],
 ['mutation outside atomic participants',operation.replace('atomic-participants Counter','atomic-participants Other'),'UnknownReference'],
 ['duplicate atomic participant',operation.replace('atomic-participants Counter','atomic-participants Counter, Counter'),'DuplicateSymbol'],
 ['provisional binding used by rollback handler',operation.replace('on-version-conflict reject contention','on-version-conflict return changed.amount'),'UnknownReference'],
 ['unknown commit cannot infer rollback',operation.replace('on-unknown-commit fail outcome-unknown','on-unknown-commit rollback-all then fail outcome-unknown'),'InvalidContract'],
 ['duplicate transaction handler',operation.replace('    on-version-conflict reject contention','    on-version-conflict reject contention\n    on-version-conflict reject other'),'DuplicateSymbol'],
 ['partial create fields','\noperation Apply:\n  output UInt64\n  transaction Create:\n    atomic-participants Counter\n    create row Counter:\n      id <- 1\n      amount <- 0\n  return 0\n','MissingMapping'],
 ['non-list readset',set.replace('input ids List<UInt64,10>','input ids UInt64'),'TypeMismatch'],
 ['readset writes before validation',set.replace('      read row Counter','      transaction TooEarly:\n        atomic-participants Counter\n        create early Counter:\n          id <- id\n          amount <- 0\n          version <- 1\n      read row Counter'),'InvalidContract'],
 ['missing local callee argument','\noperation Helper:\n  input id UInt64\n  output UInt64\n  return id\n\noperation Apply:\n  output UInt64\n  return Helper()\n','MissingMapping'],
 ['wrong invoke-return output','\noperation Helper:\n  output Bool\n  return true\n\noperation Apply:\n  output UInt64\n  return Helper()\n','TypeMismatch'],
]as const)test('rejects '+name,()=>failure(()=>check(extra),code));
test('unknown commit cannot dispatch a new mutating helper',()=>{const extra='\noperation Helper:\n  output UInt64\n  return 1\n'+operation.replace('on-unknown-commit fail outcome-unknown','on-unknown-commit return Helper()');failure(()=>check(extra),'InvalidContract');});
test('recursive local Operation calls cannot become an admitted graph',()=>failure(()=>check('\noperation First:\n  output UInt64\n  return Second()\n\noperation Second:\n  output UInt64\n  return First()\n'),'InvalidContract'));
test('a Query may be used by a typed read but an Operation cannot masquerade as a read',()=>{const helper='\nquery ReadCounter:\n  input id UInt64\n  source row Counter\n  output optional<Counter>\n  where row.id == id\n  project row\n  on-missing return none\n',extra=helper+operation.replace('read counter Counter by id=id','read counter from ReadCounter(id)');assert.equal(op(extra).body[0]!.kind,'read');failure(()=>check('\noperation ReadCounter:\n  input id UInt64\n  output UInt64\n  return id\n'+operation.replace('read counter Counter by id=id','read counter from ReadCounter(id)')),'TypeMismatch');});
test('unavailable handlers cannot read a nonexistent row',()=>failure(()=>check(operation.replace('on-unavailable fail outcome-unknown','on-unavailable return counter.amount')),'UnknownReference'));
test('record-event cannot masquerade as a storage Entity',()=>failure(()=>check(operation.replace('    on-version-conflict','    record-event e Counter:\n      id <- id\n      amount <- 0\n      version <- 1\n    on-version-conflict')),'TypeMismatch'));
test('unknown pattern payload cannot be used as a Bool predicate',()=>failure(()=>check('\noperation Apply:\n  input flag Flag\n  output UInt64\n  on flag Unknown return 1\n  return 0\n'),'UnknownReference'));
test('Operation proposals are independently reconstructed and matching JSON carries no custody',()=>{const s=source(),proposal=JSON.parse(JSON.stringify(checkCoreCommerceOperationSources(s))),r=checkCoreCommerceOperationProposal(s,[],proposal);assert.notEqual(r,proposal);assert.equal(r.complete,true);assert.equal(Object.hasOwn(r,'accepted'),false);});
for(const field of ['parameters','contexts','result','body','protocol','qualification'])test('Operation proposal forgery rejects '+field,()=>{const s=source(),proposal=JSON.parse(JSON.stringify(checkCoreCommerceOperationSources(s)));proposal.operations[0][field]='forged';failure(()=>checkCoreCommerceOperationProposal(s,[],proposal),'InvalidContract');});
test('native obligations and rollback requirements cannot be deleted from a proposal',()=>{const s=source(),proposal=JSON.parse(JSON.stringify(checkCoreCommerceOperationSources(s)));proposal.operations[0].body.find((s:CoreOperationStep)=>s.kind==='transaction').transaction.native_requirements=[];failure(()=>checkCoreCommerceOperationProposal(s,[],proposal),'InvalidContract');});
test('Operation proposal accessors reject without running them',()=>{let invoked=false;failure(()=>checkCoreCommerceOperationProposal(source(),[],{get operations(){invoked=true;return [];}}),'InvalidContract');assert.equal(invoked,false);});
// These exercise the native scalar ABI boundary added for event occurrence IDs.
// Bounds may imply compatibility here; ordinary named data remains nominal.
const scalarBoundary=(actual:string,expected:string)=>{
 const declaration=(name:string,bounds:string)=>`value-object ${name}:\n  carrier String\n  representation transparent-scalar\n${bounds}\n`;
 const text='module Boundary version 1\n'+declaration('Narrow',actual)+declaration('Wide',expected)+`interface Native:
  kind native-producer
  abi craft.scalar-boundary/v1-candidate
  custody private-registered-source-profile-callsite
  signatures context.json#/identity_producers/methods
interface Application:
  kind application-composition
  formal-claims optional
operation Probe:
  input value Narrow
  context native Native
  output Bool
  return native.approve(value)
`;
 const doc={source_module:'Boundary@1',identity_producers:{abi:'craft.scalar-boundary/v1-candidate',methods:{approve:{parameters:['Wide'],result:'Bool'}}}};
 return ()=>checkCoreCommerceOperationSources([{path:'application.alch',text}],[{path:'context.json',text:JSON.stringify(doc)}]);
};
test('a bounded event-like scalar refinement may enter a provably wider native scalar parameter',()=>{
 const r=scalarBoundary('  pattern "^evt_[a-f0-9]{64}$"\n  utf8-bytes 68..68','  utf8-bytes 1..128\n  unicode-scalars 1..128')();
 assert.equal(r.operations[0]!.body[0]!.kind,'action');
});
for(const [name,actual,expected]of [
 ['UTF-8 upper bound','  utf8-bytes 1..129','  utf8-bytes 1..128'],
 ['UTF-8 lower bound','  utf8-bytes 0..128','  utf8-bytes 1..128'],
 ['Unicode scalar lower bound','  utf8-bytes 4..4\n  unicode-scalars 1..4','  utf8-bytes 1..8\n  unicode-scalars 2..8'],
 ['Unicode scalar upper bound','  utf8-bytes 4..4\n  unicode-scalars 1..4','  utf8-bytes 1..8\n  unicode-scalars 1..3'],
 ['expected pattern needs proof','  utf8-bytes 1..8','  pattern "^[a-z]{1,8}$"\n  utf8-bytes 1..8'],
]as const)test('native scalar widening rejects unproved '+name,()=>failure(scalarBoundary(actual,expected),'TypeMismatch'));
