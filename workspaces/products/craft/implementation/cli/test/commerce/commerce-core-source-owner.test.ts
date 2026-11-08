/** Independent source custody tests, never selected/native custody.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,renameSync,rmSync,symlinkSync,statSync,utimesSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {createCoreCommerceSourceOwner,assertCoreCommerceSourceOwner,parseCoreCommerceJson} from '../../src/commerce/commerce-core-source-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const source='module Test version 1\nvalue-object Item:\n  verified Bool\ninterface Application:\n  kind application-composition\n  formal-claims optional\n';
const fixture=(run:(root:string)=>void)=>{const root=mkdtempSync(path.join(tmpdir(),'core-commerce-source-'));try{writeFileSync(path.join(root,'application.alch'),source);run(root);}finally{rmSync(root,{recursive:true,force:true});}};
const failure=(fn:()=>unknown,code?:string)=>assert.throws(fn,(error:unknown)=>error instanceof CoreCommerceSourceError&&(!code||error.diagnostics[0]!.code===code));
test('Core captures actual 26 commerce files independently and refuses all copied owners',()=>{
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),o=createCoreCommerceSourceOwner(),h=o.prepare(root),i=o.inspect(h);
 assert.equal(i.files.length,26);assert.equal(i.reconstruction.modules.length,14);assert.equal(i.reconstruction.modules.flatMap(m=>m.declarations).length,206);o.assertCurrent(h);assertCoreCommerceSourceOwner(o);
 for(const fake of [JSON.parse(JSON.stringify(h)),Object.create(h),{...h}])failure(()=>o.inspect(fake),'ForeignOwner');
 failure(()=>createCoreCommerceSourceOwner().inspect(h),'ForeignOwner');failure(()=>assertCoreCommerceSourceOwner({...o}),'ForeignOwner');
 assert.ok(Object.isFrozen(i.files));assert.equal(i.authority_effect,'none');o.dispose(h);failure(()=>o.assertCurrent(h),'DisposedOwner');
});
test('file content drift invalidates an original capture',()=>fixture(root=>{const o=createCoreCommerceSourceOwner(),h=o.prepare(root);writeFileSync(path.join(root,'application.alch'),source+'# changed\n');failure(()=>o.assertCurrent(h),'StaleOwner');}));
test('same-size content drift with restored mtime invalidates an original capture',()=>fixture(root=>{const file=path.join(root,'application.alch'),o=createCoreCommerceSourceOwner(),h=o.prepare(root),before=statSync(file);writeFileSync(file,source.replace('verified Bool','verified Text'));utimesSync(file,before.atime,before.mtime);failure(()=>o.assertCurrent(h),'StaleOwner');}));
test('same-byte replacement still invalidates physical ownership',()=>fixture(root=>{const o=createCoreCommerceSourceOwner(),h=o.prepare(root);writeFileSync(path.join(root,'replacement.alch'),source);renameSync(path.join(root,'replacement.alch'),path.join(root,'application.alch'));failure(()=>o.inspect(h),'StaleOwner');}));
test('missing original file invalidates capture',()=>fixture(root=>{const o=createCoreCommerceSourceOwner(),h=o.prepare(root);rmSync(path.join(root,'application.alch'));failure(()=>o.assertCurrent(h),'StaleOwner');}));
test('root replacement invalidates capture even with matching source bytes',()=>fixture(root=>{const o=createCoreCommerceSourceOwner(),h=o.prepare(root),old=root+'-old';renameSync(root,old);try{mkdirSync(root);writeFileSync(path.join(root,'application.alch'),source);failure(()=>o.assertCurrent(h),'StaleOwner');}finally{rmSync(old,{recursive:true,force:true});}}));
test('internal symlink capture records target identity',()=>fixture(root=>{writeFileSync(path.join(root,'real.alch'),source);rmSync(path.join(root,'application.alch'));symlinkSync('real.alch',path.join(root,'application.alch'));const o=createCoreCommerceSourceOwner(),h=o.prepare(root);o.assertCurrent(h);writeFileSync(path.join(root,'real.alch'),source+'#changed');failure(()=>o.assertCurrent(h),'StaleOwner');}));
test('a hidden intermediate symlink retarget cannot reuse an unchanged captured lexical and physical chain',()=>fixture(root=>{
 mkdirSync(path.join(root,'first'));mkdirSync(path.join(root,'second'));
 writeFileSync(path.join(root,'first','source.alch'),source);writeFileSync(path.join(root,'second','source.alch'),source);
 rmSync(path.join(root,'application.alch'));symlinkSync('hop.alch',path.join(root,'application.alch'));
 symlinkSync('first/source.alch',path.join(root,'hop.alch'));
 const owner=createCoreCommerceSourceOwner(),capture=owner.prepare(root);owner.assertCurrent(capture);
 // Neither application.alch nor the original first/source.alch is replaced.
 // Only fresh resolution can see this intermediate alias changing its target.
 rmSync(path.join(root,'hop.alch'));symlinkSync('second/source.alch',path.join(root,'hop.alch'));
 failure(()=>owner.assertCurrent(capture),'StaleOwner');
}));
test('source symlink escapes reject before external file capture',()=>fixture(root=>{const external=mkdtempSync(path.join(tmpdir(),'core-commerce-outside-'));try{writeFileSync(path.join(external,'source.alch'),source);rmSync(path.join(root,'application.alch'));symlinkSync(path.join(external,'source.alch'),path.join(root,'application.alch'));failure(()=>createCoreCommerceSourceOwner().prepare(root),'InvalidContract');}finally{rmSync(external,{recursive:true,force:true});}}));
test('strict UTF8 failure has a bounded syntax diagnostic',()=>fixture(root=>{writeFileSync(path.join(root,'application.alch'),Buffer.from([0xc0,0xaf]));failure(()=>createCoreCommerceSourceOwner().prepare(root),'Syntax');}));
test('declared source closure excludes ambient files',()=>fixture(root=>{writeFileSync(path.join(root,'unused.alch'),'not a language file');const o=createCoreCommerceSourceOwner(),h=o.prepare(root);assert.equal(o.inspect(h).files.length,1);}));
test('duplicate declared module paths reject',()=>fixture(root=>{writeFileSync(path.join(root,'application.alch'),source.replace('  formal-claims optional','  source models/data.alch\n  source models/data.alch\n  formal-claims optional'));failure(()=>createCoreCommerceSourceOwner().prepare(root),'DuplicateSymbol');}));
test('optional claim file is captured without running a proof engine',()=>fixture(root=>{mkdirSync(path.join(root,'claims'));writeFileSync(path.join(root,'claims/item.smt2'),'(set-logic ALL)\n');writeFileSync(path.join(root,'application.alch'),source+'formal-claim ItemClaim:\n  language smtlib2\n  source claims/item.smt2\n  targets Item\n');const o=createCoreCommerceSourceOwner(),h=o.prepare(root);assert.equal(o.inspect(h).files.length,2);writeFileSync(path.join(root,'claims/item.smt2'),'(set-logic QF_UF)\n');failure(()=>o.assertCurrent(h),'StaleOwner');}));
test('registered JSON pointers must exist',()=>fixture(root=>{writeFileSync(path.join(root,'contract.json'),'{}');writeFileSync(path.join(root,'application.alch'),source.replace('  formal-claims optional','  parameters contract.json#/missing\n  formal-claims optional'));failure(()=>createCoreCommerceSourceOwner().prepare(root),'UnknownReference');}));
test('module-relative contract basename has no fallback lookup',()=>fixture(root=>{mkdirSync(path.join(root,'models'));writeFileSync(path.join(root,'application.alch'),source.replace('  formal-claims optional','  source models/value.alch\n  formal-claims optional'));writeFileSync(path.join(root,'models/value.alch'),'module Values version 1\ninterface Context:\n  kind trusted-context\n  fields contract.json#/fields\n');writeFileSync(path.join(root,'contract.json'),'{"fields":{}}');assert.throws(()=>createCoreCommerceSourceOwner().prepare(root));}));
test('contract asset drift invalidates source custody',()=>fixture(root=>{writeFileSync(path.join(root,'contract.json'),'{"parameters":{}}');writeFileSync(path.join(root,'application.alch'),source.replace('  formal-claims optional','  parameters contract.json#/parameters\n  formal-claims optional'));const o=createCoreCommerceSourceOwner(),h=o.prepare(root);writeFileSync(path.join(root,'contract.json'),'{"parameters":{"changed":true}}');failure(()=>o.inspect(h),'StaleOwner');}));
test('source identity contract is checked against original captured bytes, not treated as authority',()=>fixture(root=>{
 mkdirSync(path.join(root,'contracts'));const text=source.replace('  formal-claims optional','  source-identities contracts/identities.json\n  formal-claims optional');writeFileSync(path.join(root,'application.alch'),text);
 const manifest={schema_version:'craft.commerce-source-contract-identities/v1-candidate',root:'application.alch',application:'Test.Application',modules:[{module:'Test',version:1,artifact:{path:'application.alch',sha256:createHash('sha256').update(text).digest('hex'),bytes:Buffer.byteLength(text)}}],contract_assets:[]};
 const file=path.join(root,'contracts/identities.json');writeFileSync(file,JSON.stringify(manifest));const o=createCoreCommerceSourceOwner(),h=o.prepare(root);assert.equal(o.inspect(h).files.length,2);
 manifest.modules[0]!.artifact.sha256='0'.repeat(64);writeFileSync(file,JSON.stringify(manifest));failure(()=>o.assertCurrent(h),'StaleOwner');failure(()=>createCoreCommerceSourceOwner().prepare(root),'StaleOwner');
}));
test('missing root source produces a bounded diagnostic without raw filesystem error leakage',()=>fixture(root=>{rmSync(path.join(root,'application.alch'));failure(()=>createCoreCommerceSourceOwner().prepare(root),'UnknownReference');}));
for(const [name,value] of [
 ['decoded duplicate','{"a":1,"\\u0061":2}'],['unsafe integer','{"n":9007199254740992}'],['noninteger metadata','{"n":1.25}'],
 ['unpaired escaped Unicode','{"s":"\\ud800"}'],['trailing object','{}{}'],['malformed value','{"x":}'],
 ['trailing array comma','[1,]'],['trailing object comma','{"a":1,}'],['leading zero','{"a":01}'],
]as const)test('JSON rejects '+name,()=>failure(()=>parseCoreCommerceJson(value,'contract.json')));
test('JSON null-prototype objects preserve special member names as inert data',()=>{const result=parseCoreCommerceJson('{"__proto__":{"value":1},"a":[true,null,"é"]}','contract.json') as Record<string,unknown>;assert.equal(Object.getPrototypeOf(result),null);assert.ok(Object.hasOwn(result,'__proto__'));assert.ok(Object.isFrozen(result));});
test('JSON nesting bound fails deterministically',()=>failure(()=>parseCoreCommerceJson('['.repeat(66)+'0'+']'.repeat(66),'contract.json'),'ResourceLimit'));
test('source owner factory accepts no supplied transfer/DTO/semantic owner argument',()=>{const o=createCoreCommerceSourceOwner();failure(()=>o.prepare({kind:'fake'}as unknown as string),'InvalidContract');});
