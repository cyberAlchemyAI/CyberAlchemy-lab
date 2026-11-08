import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync,existsSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.ts';
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const examples=path.join(repo,'goals/plans/craft-technical-profiles-2026-10-31/examples');
function fixture(t:any,name='architecture-entry-local'){
 const root=mkdtempSync(path.join(os.tmpdir(),'craft-profile-source-test-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 for(const relative of ['library.alch',name+'.alch',name+'.profile.json','contracts/family.json','contracts/obligations.json','contracts/ports.json']){mkdirSync(path.dirname(path.join(root,relative)),{recursive:true});writeFileSync(path.join(root,relative),readFileSync(path.join(examples,relative)));}
 const manifestPath=path.join(root,name+'.profile.json'),owner=createTechnicalProfileSourceOwner();return {root,manifestPath,owner,load:()=>owner.prepare({sourceRoot:root,manifestPath}),edit:(change:(data:any)=>void)=>{const data=JSON.parse(readFileSync(manifestPath,'utf8'));change(data);writeFileSync(manifestPath,JSON.stringify(data));}};
}
test('actual checked Alch Mapping compiles both original architecture packages deterministically',t=>{
 for(const name of ['architecture-entry-local','architecture-shared']){
  const f=fixture(t,name),h=f.load();try{const checked=f.owner.inspect(h),one=f.owner.lowerArchitecture(h,repo),two=f.owner.lowerArchitecture(h,repo);assert.equal(checked.topology.requestBytes,'16384');assert.equal(checked.qualification,'original-core-checked-profile-source-and-pure-topology');assert.deepEqual(one,two);const fresh=createTechnicalProfileSourceOwner(),freshHandle=fresh.prepare({sourceRoot:f.root,manifestPath:f.manifestPath});try{assert.deepEqual(fresh.lowerArchitecture(freshHandle,repo),one,'fresh source capture must not leak random staging paths into identity');}finally{fresh.dispose(freshHandle);}assert.equal(one.package.capabilities.some((c:any)=>c.role==='shared-http-port'),name==='architecture-shared');assert.equal(checked.source_files.some((x:any)=>x.path==='library.alch'),true);}finally{f.owner.dispose(h);}
 }
});
test('source-selected request bounds change the actual generated package',t=>{
 const f=fixture(t);f.edit(d=>{d.selection.arguments.options.requestBytes='8192';});const h=f.load();try{const output=f.owner.lowerArchitecture(h,repo);assert.equal(output.manifest.request_bytes,8192);assert.match(output.files['profile.json']!,/8192/);}finally{f.owner.dispose(h);}
});
test('original Mapping requires rejects even without the envelope selection Rule',t=>{
 const f=fixture(t);f.edit(d=>{d.selection.checks=[];d.selection.arguments.options.requestBytes='0';});assert.throws(f.load,/EVALUATION|outside|invalid|rejected/i);
});
test('profile source rejects undeclared roles, phase forgery and extra executable hooks',t=>{
 for(const change of [(d:any)=>{d.execute='javascript';},(d:any)=>{d.selection.checks[0].phase='runtime';},(d:any)=>{d.selection.mapping='Profiles.ArchitectureEntryLocal.Missing';}]){const f=fixture(t);f.edit(change);assert.throws(f.load);}
});
test('compatible port matching rejects unresolved direction even with valid source types',t=>{
 const f=fixture(t);f.edit(d=>{d.bindings.entryA.ports.invoke.direction='provides';});assert.throws(f.load,/PORT/);
});
test('physical source mutation and forged handles cannot reuse checked profile custody',t=>{
 const f=fixture(t),h=f.load();assert.throws(()=>createTechnicalProfileSourceOwner().inspect(h),/OWNER/);assert.throws(()=>f.owner.inspect({kind:'original-checked-technical-profile-source/v1'}),/OWNER/);writeFileSync(path.join(f.root,'library.alch'),readFileSync(path.join(f.root,'library.alch'),'utf8')+'\n');assert.throws(()=>f.owner.lowerArchitecture(h,repo),/STALE/);f.owner.dispose(h);
});
test('source publication is fresh, original-owner checked and includes derivation origins',t=>{
 const f=fixture(t),h=f.load(),out=path.join(f.root,'generated-profile');try{f.owner.publishArchitecture(h,repo,out);assert.ok(existsSync(path.join(out,'profile.json')));const lineage=JSON.parse(readFileSync(path.join(out,'technical-profile-derivation.json'),'utf8'));assert.equal(lineage.provenance.mapping,'Profiles.ArchitectureEntryLocal.Build');assert.throws(()=>f.owner.publishArchitecture(h,repo,out));}finally{f.owner.dispose(h);}
});

test('compiled source selection round-trips exact source closure and detects descriptor mutation',t=>{
 const f=fixture(t),h=f.load(),target=path.join(f.root,'selection-output');
 try{f.owner.publishSelection(h,target);const owner=createTechnicalProfileSourceOwner(),compiled=owner.prepareCompiled(path.join(target,'selection.json'));try{assert.equal(owner.inspect(compiled).source_closure_sha256,f.owner.inspect(h).source_closure_sha256);assert.deepEqual(owner.lowerArchitecture(compiled,repo),f.owner.lowerArchitecture(h,repo));const descriptor=path.join(target,'selection.json');writeFileSync(descriptor,readFileSync(descriptor,'utf8')+'\n');assert.throws(()=>owner.assertCurrent(compiled),/STALE/);}finally{owner.dispose(compiled);}}finally{f.owner.dispose(h);}
});
