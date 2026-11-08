/** EC07 source foundation controls. No generated/runtime qualification.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {CoreCommerceSourceError,parseCoreCommerceSyntax,lexCoreCommerceSource,coreSourceDescendants} from '../../src/commerce/commerce-core-syntax.js';
import {reconstructCoreCommerceModule,reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.js';
const composition='interface Application:\n  kind application-composition\n  service shop module Shop\n  formal-claims optional\n';
const model='module Shop version 1\n\nentity Item:\n  id UInt64\n  verified Bool\n  version UInt64\n  identity id\n  immutable id\n\nrule Verified:\n  input item Item\n  expression item.verified == true\n\noperation Check:\n  input item Item\n  output Item\n  requires Verified(item)\n  return item\n\ninterface Internal:\n  kind internal\n  exposes Check\n\n'+composition;
const reconstruct=(s=model)=>reconstructCoreCommerceSources([{path:'application.alch',text:s}]);
const failure=(fn:()=>unknown,code?:string)=>assert.throws(fn,(error:unknown)=>error instanceof CoreCommerceSourceError&&(!code||error.diagnostics[0]!.code===code));
const entry='\nentry Shop.CheckEntry:\n  invokes Shop.Check\n  interaction request-response\n  access:\n    authenticated customer\n    permission item.check\n    auth-resource item\n    auth-action check\n    auth-scope shop\n    auth-route commerce:Shop.CheckEntry\n    context CustomerContext\n    native-requires craft.context.current-owner/v1-candidate\n    current-action before replay-and-effects\n';

test('Core independently recognizes the 14 unchanged modules and the 12 meta-types actually used there',()=>{
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url));
 const source=readdirSync(root,{recursive:true}).filter((f):f is string=>typeof f==='string'&&f.endsWith('.alch')).map(path=>({path,text:readFileSync(root+path,'utf8')}));
 const result=reconstructCoreCommerceSources(source),ds=result.modules.flatMap(m=>m.declarations);
 assert.equal(result.modules.length,14);assert.equal(ds.length,204);assert.equal(ds.filter(d=>d.surface==='Entry').length,22);assert.equal(ds.filter(d=>d.surface==='FormalClaim').length,0);
 assert.equal(new Set(ds.flatMap(d=>d.meta_type?[d.meta_type]:[])).size,12);assert.equal(result.services.length,5);assert.equal(ds.reduce((n,d)=>n+d.fields.length,0),328);
 assert.ok(result.obligations.length>2000);assert.ok(result.obligations.every(o=>o.status==='requires-semantic-check'));assert.equal(result.qualification,'independent-source-structure-only');
});
test('Policy, the thirteenth meta-type absent from the commerce example, reconstructs from its explicit source',()=>{
 const extra='\ncalculation Base:\n  pure\n  input item Item\n  result UInt64\n  expression 1\n\npolicy Price:\n  input item Item\n  result UInt64\n  ordered-cases:\n    verified when Verified(item) -> Base(item)\n    otherwise -> Base(item)\n';
 const r=reconstruct(model+extra),policy=r.modules[0]!.declarations.at(-1)!;assert.equal(policy.meta_type,'Policy');assert.equal(policy.result!.kind,'UInt64');
});
test('zero claims reconstruct direct predicates, guards and records',()=>{const r=reconstruct();assert.equal(r.modules[0]!.declarations.find(d=>d.surface==='Rule')!.result!.kind,'Bool');assert.ok(r.obligations.some(o=>o.kind==='guard'));assert.equal(r.authority_effect,'none');});
test('source whitespace/comments do not change executable source projection',()=>{assert.equal(reconstruct().executable_source_sha256,reconstruct('# comment\n'+model.replace('  requires Verified(item)','  requires   Verified( item ) # comment')).executable_source_sha256);});
test('guard condition changes executable source subject',()=>{assert.notEqual(reconstruct().executable_source_sha256,reconstruct(model.replace('item.verified == true','item.verified == false')).executable_source_sha256);});
test('transaction/effect changes executable source subject',()=>{const body='transaction save:\n    atomic-participants Item\n    create saved Item:\n      id <- item.id\n      verified <- item.verified\n      version <- 0';assert.notEqual(reconstruct().executable_source_sha256,reconstruct(model.replace('return item',body+'\n  return item')).executable_source_sha256);});
test('permission changes executable source subject',()=>{assert.notEqual(reconstruct(model+entry).executable_source_sha256,reconstruct(model+entry.replace('item.check','item.approve')).executable_source_sha256);});
test('optional established-language claim is separate from executable source subject',()=>{const claim='\nformal-claim VerifiedClaim:\n  language smtlib2\n  source claims/verified.smt2\n  targets Verified\n';const a=reconstruct(),b=reconstruct(model+claim);assert.equal(a.executable_source_sha256,b.executable_source_sha256);assert.notEqual(a.optional_assurance_source_sha256,b.optional_assurance_source_sha256);assert.equal(b.modules[0]!.declarations.at(-1)!.meta_type,null);});
test('unknown import cannot be recovered through a globally unique alias',()=>failure(()=>reconstruct(model.replace('module Shop version 1','module Shop version 1\nuse Else.Unknown')),'UnknownReference'));
test('grouped import expands against its explicit preceding module',()=>{const value='module Values version 1\nvalue-object Key:\n  number UInt64\nvalue-object Data:\n  key Key\n';const s=model.replace('module Shop version 1','module Shop version 1\nuse Values.Key, Data');const r=reconstructCoreCommerceSources([{path:'application.alch',text:s},{path:'values.alch',text:value}]);assert.equal(r.modules[0]!.imports[1]!.target,'Values.Data');});
for(const [name,source,code] of [
 ['unknown named type',model.replace('verified Bool','verified Missing'),'UnknownReference'],
 ['callable as value type',model.replace('verified Bool','verified Verified'),'TypeMismatch'],
 ['unknown identity field',model.replace('identity id','identity absent'),'UnknownReference'],
 ['missing identity',model.replace('  identity id\n',''),'InvalidContract'],
 ['duplicate field',model.replace('  verified Bool','  id UInt64\n  verified Bool'),'DuplicateSymbol'],
 ['duplicate immutable clause',model.replace('  immutable id','  immutable id\n  immutable id'),'DuplicateSymbol'],
 ['duplicate unique key',model.replace('  immutable id','  unique id\n  unique id\n  immutable id'),'DuplicateSymbol'],
 ['undeclared immutable',model.replace('immutable id','immutable absent'),'UnknownReference'],
 ['duplicate parameter',model.replace('  input item Item','  input item Item\n  input item Item'),'DuplicateSymbol'],
 ['nonlocal Interface expose',model.replace('exposes Check','exposes Verified'),'TypeMismatch'],
 ['duplicate source module',model+'\n'+model,'Syntax'],
 ['unbounded list',model.replace('verified Bool','verified List<Bool,101>'),'ResourceLimit'],
 ['zero bounded list',model.replace('verified Bool','verified List<Bool,0>'),'ResourceLimit'],
 ['recursive data',model.replace('verified Bool','verified Item'),'InvalidContract'],
 ['mixed enum wires',model+'\nenum Mixed:\n  value A\n  variant B number UInt64\n','InvalidContract'],
 ['duplicate enum payload',model+'\nenum Mixed:\n  variant A number UInt64 number UInt64\n','DuplicateSymbol'],
 ['duplicate enum wire',model+'\nenum Mixed:\n  value A wire "x"\n  value B wire "x"\n','DuplicateSymbol'],
 ['Event missing schema version',model+'\nevent Created:\n  id UInt64\n','InvalidContract'],
 ['private context serialized',model+'\ninterface Context:\n  kind trusted-context\n  custody private-registered-entry-auth-owner\nvalue-object Leaked:\n  context Context\n','TypeMismatch'],
 ['Event schema metadata is not an Entity field',model.replace('  identity id','  identity id\n  version 1'),'InvalidContract'],
]as const)test(name,()=>failure(()=>reconstruct(source),code));
test('duplicate metadata version field is actually distinct from Event schema metadata',()=>{const r=reconstruct(model+'\nevent Created:\n  version 1\n  dataVersion UInt64\n  id UInt64\n');assert.deepEqual(r.modules[0]!.declarations.at(-1)!.fields.map(f=>f.name),['dataVersion','id']);});
test('private service tables cannot be read through a foreign module',()=>{const other='module Other version 1\nentity Stock:\n  id UInt64\n  identity id\n';const source=model.replace('  requires Verified(item)','  read stock Other.Stock by id=item.id\n  requires Verified(item)').replace('  formal-claims optional','  service other module Other\n  formal-claims optional');failure(()=>reconstructCoreCommerceSources([{path:'application.alch',text:source},{path:'other.alch',text:other}]),'InvalidContract');});
test('technical profile source cannot introduce business effects or entries',()=>failure(()=>reconstruct(model+'\ninterface Family:\n  kind technical-profile-family\n  callbacks forbidden\n'),'InvalidContract'));
test('entry cannot elevate a private operation',()=>failure(()=>reconstruct(model.replace('  exposes Check','  exposes Missing')+entry),'UnknownReference'));
test('entry needs its inline permission even without claims',()=>failure(()=>reconstruct(model+entry.replace('    permission item.check\n','')),'MissingMapping'));
test('entry duplicate permission rejects',()=>failure(()=>reconstruct(model+entry.replace('    permission item.check','    permission item.check\n    permission item.check')),'MissingMapping'));
test('service owner mappings cannot overlap prefixes',()=>failure(()=>reconstructCoreCommerceSources([{path:'application.alch',text:model.replace('  formal-claims optional','  service child module Shop.Child\n  formal-claims optional')},{path:'child.alch',text:'module Shop.Child version 1\nvalue-object Data:\n  number UInt64\n'}]),'InvalidContract'));
test('module/declaration source inventory is frozen',()=>{const r=reconstruct();assert.ok(Object.isFrozen(r));assert.ok(Object.isFrozen(r.modules[0]!.declarations[0]!.fields));});
test('syntax diagnostics contain only bounded original byte locations',()=>{try{reconstruct(model.replace('verified Bool','verified Missing'));assert.fail('expected diagnostic');}catch(error){assert.ok(error instanceof CoreCommerceSourceError);assert.deepEqual(Object.keys(error.diagnostics[0]!).sort(),['code','end','message','path','start']);}});
test('UTF8 source spans reflect original scalar bytes',()=>{const s=model+'\nvalue-object Name:\n  carrier String\n  pattern "é"\n  utf8-bytes 1..4\n';const r=reconstructCoreCommerceModule(s,'unicode.alch'),node=coreSourceDescendants(r.syntax,'json-string').at(-1)!;assert.equal(Buffer.from(s).subarray(node.start,node.end).toString(),'"é"');});
for(const [name,source]of [
 ['layout tokens are not names','module Shop version 1\nINDENT\n'+composition],
 ['trailing source tokens',model+'execute(unsafe)\n'],
 ['tabs',model.replace('  verified Bool','\tverified Bool')],
 ['bare terminal CR',model+'\r'],
 ['non-ASCII indentation',model.replace('  verified Bool','\u00a0\u00a0verified Bool')],
 ['unpaired scalar',model+'\n# \ud800'],
 ['skipped indentation',model.replace('  verified Bool','      verified Bool')],
 ['unbounded range intrinsic',model.replace('item.verified == true','range(0,10,1)')],
 ['unknown evaluator clause',model.replace('  expression item.verified == true','  evaluator arbitraryCallback')],
 ['source version 2',model.replace('version 1','version 2')],
]as const)test(name,()=>failure(()=>parseCoreCommerceSyntax(source,'application.alch')));
test('deep parentheses fail with a diagnostic instead of host stack exhaustion',()=>failure(()=>parseCoreCommerceSyntax(model.replace('item.verified == true','('.repeat(100)+'true'+')'.repeat(100)),'application.alch'),'ResourceLimit'));
test('CRLF lines preserve valid original source byte locations',()=>{const s=model.replace(/\n/g,'\r\n');const r=reconstructCoreCommerceModule(s,'crlf.alch');assert.equal(r.bytes,Buffer.byteLength(s));assert.equal(r.declarations.length,5);});
test('unsafe relative source path rejects',()=>failure(()=>lexCoreCommerceSource(model,'../application.alch'),'InvalidContract'));
