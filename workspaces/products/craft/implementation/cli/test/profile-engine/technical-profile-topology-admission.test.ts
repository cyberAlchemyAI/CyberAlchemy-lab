import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.ts';
import {lowerTechnicalProfileArchitecture} from '../../src/profile-engine/technical-profile-architecture.ts';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const examples=path.join(repo,'goals/plans/craft-technical-profiles-2026-10-31/examples');
function fixture(t:any,consumer='craft.profile-engine/v1'){
 const root=mkdtempSync(path.join(os.tmpdir(),'craft-topology-admission-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const name='architecture-entry-local';
 for(const relative of ['library.alch',name+'.alch',name+'.profile.json','contracts/family.json','contracts/obligations.json','contracts/ports.json']){
  const dest=path.join(root,relative);mkdirSync(path.dirname(dest),{recursive:true});writeFileSync(dest,readFileSync(path.join(examples,relative)));
 }
 const manifestPath=path.join(root,name+'.profile.json'),sourcePath=path.join(root,name+'.alch'),envelope=JSON.parse(readFileSync(manifestPath,'utf8'));
 if(consumer!=='craft.profile-engine/v1'){
  envelope.target={consumer,package_schema:consumer,status:'resolved-schema-design-only'};
  // Preserve Options and bounds Rule; only the finite selected result omits
  // architecture's requestBytes slot. These tests exercise source admission,
  // not the later composition/native constructor consumers.
  writeFileSync(sourcePath,readFileSync(sourcePath,'utf8').replace('value-object Plan:\n  requestBytes UInt64\n','value-object Plan:\n').replace('  field requestBytes <- options.requestBytes\n',''));
  writeFileSync(manifestPath,JSON.stringify(envelope));
 }
 const owner=createTechnicalProfileSourceOwner(),prepare=()=>owner.prepare({sourceRoot:root,manifestPath});
 return {owner,prepare,envelope,mutate(){writeFileSync(sourcePath,readFileSync(sourcePath,'utf8').replace('value-object Plan:\n','value-object Plan:\n  unsupportedConsumerSlot Bool\n').replace('  field nodes <-','  field unsupportedConsumerSlot <- true\n  field nodes <-'));}};
}
for(const consumer of ['craft.profile-engine/v1','craft.technical-profile-composition/v1','craft.technical-profile-runtime/v1']){
 test('genuine source admission rejects unknown topology root slots for '+consumer,t=>{
  const f=fixture(t,consumer),baseline=f.prepare();f.owner.dispose(baseline);
  f.mutate();let admitted:ReturnType<typeof f.prepare>|undefined;
  try{assert.throws(()=>{admitted=f.prepare();},(error:any)=>error.code==='TECHNICAL_PROFILE_TOPOLOGY'&&error.pointer==='technical-profile/topology/unsupportedConsumerSlot');}finally{if(admitted)f.owner.dispose(admitted);}
 });
}
test('public architecture lowerer rejects an unknown root slot on otherwise checked topology',t=>{
 const f=fixture(t),handle=f.prepare();
 try{
  const checked=f.owner.inspect(handle);f.owner.lowerArchitecture(handle,repo);
  assert.throws(()=>lowerTechnicalProfileArchitecture({envelope:f.envelope,topology:{...checked.topology,unsupportedConsumerSlot:true},provenance:checked,repositoryRoot:repo}),(error:any)=>error.code==='TECHNICAL_PROFILE_TOPOLOGY'&&error.pointer==='technical-profile/topology/unsupportedConsumerSlot');
 }finally{f.owner.dispose(handle);}
});
