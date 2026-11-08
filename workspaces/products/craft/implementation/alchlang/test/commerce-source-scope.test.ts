// Open Questions: private EC06/CONTEXT.md. Namespace/syntax proofs only;Core checks meaning.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseCommerceModuleSource} from '../src/commerce-source-parser.js';
import {linkCommerceSourceModules} from '../src/commerce-source-link.js';
import {CommerceSourceError,commerceSyntaxDescendants,commerceSyntaxChildren,commerceSyntaxTokens} from '../src/commerce-source-model.js';
const parse=(body:string,module='Scope')=>parseCommerceModuleSource('module '+module+' version 1\n'+body,module+'.alch');
const link=(body:string)=>linkCommerceSourceModules([parse(body)]);
const fails=(fn:()=>unknown,code:string)=>assert.throws(fn,(e:unknown)=>e instanceof CommerceSourceError&&e.diagnostics[0]?.code===code);
const enums='enum Choice:\n  variant Item value UInt64\n  variant Empty\nenum Other:\n  variant Unrelated value UInt64\n';
test('bare variant patterns resolve only against the actual subject enum',()=>{
 const good=link(enums+'rule Check:\n  input value Choice\n  expression match value:\n    Item(amount) => amount > 0\n    Empty => false\n');assert.ok(good.references.some(r=>r.kind==='enum-pattern'&&r.target==='Scope.Choice.Item'));
 fails(()=>link(enums+'rule Check:\n  input value Choice\n  expression match value:\n    Unrelated(amount) => amount > 0\n    otherwise => false\n'),'UnknownReference');
});
test('qualified variant patterns cannot cross nominal enum identity',()=>fails(()=>link(enums+'rule Check:\n  input value Choice\n  expression match value:\n    Other.Unrelated(amount) => amount > 0\n    otherwise => false\n'),'TypeMismatch'));
test('a pattern payload binder cannot escape its branch',()=>fails(()=>link(enums+'calculation Get:\n  pure\n  input value Choice\n  result UInt64\n  expression checked-add(match value Item(amount) => amount else 0, amount)\n'),'UnknownReference'));
test('unknown fields fail with their original source location',()=>fails(()=>link('value-object Value:\n  amount UInt64\nrule Check:\n  input value Value\n  expression value.missing > 0\n'),'UnknownReference'));
test('a single-argument Bool Rule is a condition rather than a payload pattern',()=>{
 const linked=link('rule IsVerified:\n  input verified Bool\n  expression verified\noperation Select:\n  input verified Bool\n  output UInt64\n  on IsVerified(verified) return 1\n  return 0\n');assert.ok(linked.references.some(r=>r.kind==='call'&&r.target==='Scope.IsVerified'));
});
test('a Bool variable condition needs no implicit enum subject',()=>{link('operation Select:\n  input verified Bool\n  output UInt64\n  on verified return 1\n  return 0\n');});
test('a numeric condition cannot become an implicit enum pattern',()=>fails(()=>link('operation Select:\n  input count UInt64\n  output UInt64\n  on count return 1\n  return 0\n'),'TypeMismatch'));
test('operation implicit result patterns retain the actual local call result type',()=>{
 const linked=link(enums+'operation Read:\n  output Choice\n  return Choice.Item(1)\noperation Select:\n  output UInt64\n  call result Read()\n  on Item(amount) return amount\n  return 0\n');assert.ok(linked.references.some(r=>r.kind==='enum-pattern'&&r.target==='Scope.Choice.Item'));
 fails(()=>link(enums+'operation Read:\n  output Choice\n  return Choice.Item(1)\noperation Select:\n  output UInt64\n  call result Read()\n  on Unrelated(amount) return amount\n  return 0\n'),'UnknownReference');
});
test('a missing implicit result is ambiguous rather than a globally unique-tag fallback',()=>fails(()=>link(enums+'operation Select:\n  output UInt64\n  on Item(amount) return amount\n  return 0\n'),'AmbiguousReference'));
test('lambda binders cannot shadow caller parameters',()=>fails(()=>link('calculation Sum:\n  pure\n  input item UInt64\n  input values List<UInt64,100>\n  result UInt64\n  expression length(map(values, item:UInt64 => item))\n'),'DuplicateSymbol'));
test('grouped patterns check the shared body separately for every typed payload',()=>{
 const body='value-object Receipt:\n  amount UInt64\nenum Result:\n  variant Recorded receipt Receipt\n  variant Unknown id UInt64\nrule Check:\n  input result Result\n  expression match result Recorded(value), Unknown(value) => value.amount > 0 else false\n';fails(()=>link(body),'TypeMismatch');
});
test('match else consumes property access and arithmetic before outer operators',()=>{
 const module=parse('value-object Value:\n  amount UInt64\ncalculation Get:\n  pure\n  input value optional<Value>\n  input fallback Value\n  result UInt64\n  expression match value some(found) => found.amount else fallback.amount + 2 * 3\n');
 linkCommerceSourceModules([module]);const match=commerceSyntaxDescendants(module.syntax,'optional-match')[0]!,otherwise=commerceSyntaxChildren(match,'expression').at(-1)!;assert.ok(commerceSyntaxDescendants(otherwise,'sum').length);assert.ok(commerceSyntaxDescendants(otherwise,'product').length);assert.ok(commerceSyntaxTokens(otherwise).some(t=>t.text==='fallback'));
});
test('parenthesized match supports member access on the whole selected record',()=>{link('value-object Value:\n  amount UInt64\ncalculation Get:\n  pure\n  input value optional<Value>\n  input fallback Value\n  result UInt64\n  expression (match value some(found) => found else fallback).amount\n');});
test('unknown formal claim targets reject even though claims are optional',()=>{
 link('rule Check:\n  expression true\nformal-claim Evidence:\n  language smtlib2\n  source claims/model.smt2\n  targets Check\n');fails(()=>link('rule Check:\n  expression true\nformal-claim Evidence:\n  language smtlib2\n  source claims/model.smt2\n  targets Missing\n'),'UnknownReference');
});
test('private callable imports and interface reexports cannot strengthen visibility',()=>{
 const a=parse('operation Hidden:\n  output UInt64\n  return 1\n','A');fails(()=>linkCommerceSourceModules([a,parse('use A.Hidden\noperation Get:\n  output UInt64\n  return Hidden()\n','B')]),'UnknownReference');fails(()=>linkCommerceSourceModules([a,parse('interface Reexport:\n  kind internal\n  exposes A.Hidden\n','B')]),'UnknownReference');
});
test('direct cross-module calls require an entry even when the target is exposed',()=>{
 const a=parse('operation Get:\n  output UInt64\n  return 1\ninterface Commands:\n  kind internal\n  exposes Get\n','A'),b=parse('operation Call:\n  output UInt64\n  return A.Get()\n','B');fails(()=>linkCommerceSourceModules([a,b]),'UnknownReference');
});
test('an entry cannot expose an undeclared private helper',()=>fails(()=>link('operation Hidden:\n  output UInt64\n  return 1\nentry Scope.HiddenEntry:\n  invokes Scope.Hidden\n  interaction request-response\n  access:\n    authenticated service\n    permission scope.hidden\n'),'UnknownReference'));
test('runtime service entry cycles remain distinct from forbidden value/call cycles',()=>{
 const body=(owner:string,peer:string)=>'operation Run:\n  output UInt64\n  return '+peer+'.RunEntry()\ninterface Commands:\n  kind internal\n  exposes Run\nentry '+owner+'.RunEntry:\n  invokes '+owner+'.Run\n  interaction request-response\n  access:\n    authenticated service\n    permission service.run\n';const linked=linkCommerceSourceModules([parse(body('A','B'),'A'),parse(body('B','A'),'B')]);assert.equal(linked.references.filter(r=>r.kind==='entry').length,2);
});
test('simple sort field spelling must select a real element field',()=>fails(()=>link('value-object Value:\n  amount UInt64\ncalculation Get:\n  pure\n  input values List<Value,100>\n  result UInt64\n  expression length(sort(values, missing ascending numeric))\n'),'UnknownReference'));
test('a reinterpreted predicate still needs its full declared signature',()=>fails(()=>link('rule Check:\n  input first Bool\n  input second Bool\n  expression first and second\noperation Select:\n  input value Bool\n  output UInt64\n  on Check(value) return 1\n  return 0\n'),'MissingMapping'));
test('workflow driver/result/step and resource binding errors reject on actual source roles',()=>{
 const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../../../../..'),root=path.join(repo,'examples/ecommerce-target-candidate'),files=readdirSync(root,{recursive:true}).map(String);
 const source=new Map(files.filter(f=>f.endsWith('.alch')).map(f=>[f,readFileSync(path.join(root,f),'utf8')])),contracts=new Map(files.filter(f=>f.endsWith('.json')).map(f=>[f,JSON.parse(readFileSync(path.join(root,f),'utf8')) as unknown]));
 const linked=(file:string,before:string,after:string)=>{assert.ok(source.get(file)?.includes(before));const modules=[...source].map(([name,value])=>parseCommerceModuleSource(name===file?value.replace(before,after):value,name));return linkCommerceSourceModules(modules,'Shop.Application.Ecommerce',contracts);};
 fails(()=>linked('workflows/checkout.alch','result snapshot CheckoutSnapshot','result snapshot Orders.OrderView'),'TypeMismatch');
 fails(()=>linked('workflows/checkout.alch','input orderId <- placed.orderId','input incorrectId <- placed.orderId'),'MissingMapping');
 fails(()=>linked('workflows/checkout.alch','AwaitingStock -> reserve','AwaitingStock -> missing-step'),'UnknownReference');
 fails(()=>linked('workflows/checkout.alch','on Applied(value) observe','on Missing(value) observe'),'UnknownReference');
 fails(()=>linked('contracts/access.alch','resource-condition input.commandId == causal.reserveCommandId','resource-condition input.commandId == causal.missingCommandId'),'UnknownReference');
});

// Source-owned technical records must remain generic and service-private.
function coordinationFixture(rename=false){
 const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../../../../..'),root=path.join(repo,'examples/ecommerce-target-candidate'),files=readdirSync(root,{recursive:true}).map(String);
 const rewrite=(s:string)=>rename?s.replaceAll('Shop.Application','Independent.Runtime'):s;
 const modules=files.filter(f=>f.endsWith('.alch')).map(f=>parseCommerceModuleSource(rewrite(readFileSync(path.join(root,f),'utf8')),f));
 const contracts=new Map(files.filter(f=>f.endsWith('.json')).map(f=>[f,JSON.parse(rewrite(readFileSync(path.join(root,f),'utf8'))) as unknown]));
 return {modules,contracts,application:rename?'Independent.Runtime.Ecommerce':'Shop.Application.Ecommerce'};
}
test('coordination ownership follows the selected declaration and contract under an unrelated namespace',()=>{
 for(const renamed of [false,true]){const f=coordinationFixture(renamed),linked=linkCommerceSourceModules(f.modules,f.application,f.contracts),journal=(renamed?'Independent.Runtime':'Shop.Application')+'.StepJournal';
  assert.ok(linked.references.some(r=>r.kind==='local-table'&&r.source==='Orders.RecordCheckoutObservation'&&r.target===journal));}
});
test('coordination records do not grant a foreign service access or accept an undeclared owner',()=>{
 for(const owner of ['payments','missing-service']){const f=coordinationFixture(),contract=f.contracts.get('contracts/application-composition.json') as {coordination:{owner_service:string}};contract.coordination.owner_service=owner;
  fails(()=>linkCommerceSourceModules(f.modules,f.application,f.contracts),'UnknownReference');}
});
test('coordination ownership rejects missing contracts and incomplete or foreign selector declarations',()=>{
 const absent=coordinationFixture();absent.contracts.delete('contracts/application-composition.json');fails(()=>linkCommerceSourceModules(absent.modules,absent.application,absent.contracts),'MissingMapping');
 const missing=coordinationFixture(),contract=missing.contracts.get('contracts/application-composition.json') as {coordination:{schema_selectors:Record<string,string>}};delete contract.coordination.schema_selectors.journal;fails(()=>linkCommerceSourceModules(missing.modules,missing.application,missing.contracts),'UnknownReference');
 const foreign=coordinationFixture(),other=foreign.contracts.get('contracts/application-composition.json') as {coordination:{schema_selectors:Record<string,string>}};other.coordination.schema_selectors.journal='Orders.Order';fails(()=>linkCommerceSourceModules(foreign.modules,foreign.application,foreign.contracts),'UnknownReference');
});
