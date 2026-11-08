/** Source-model disclosure guards, using the real original profile owner.
 * Open Questions: docs/APPLICATION-INPUT-PROFILES.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.js';
const examples=fileURLToPath(new URL('../../examples/technical-profile-source',import.meta.url));
for(const forbidden of ['sources.approval.json','approval','sources.preferences.json.record','principal.actor']){
 test('application input model projection rejects nondisclosed/owner path '+forbidden,t=>{
  const root=mkdtempSync(path.join(tmpdir(),'craft-input-disclosure-')),owner=createTechnicalProfileSourceOwner();let live:ReturnType<typeof owner.prepare>|undefined;cpSync(examples,root,{recursive:true});t.after(()=>{if(live)owner.dispose(live);rmSync(root,{recursive:true,force:true});});const source=path.join(root,'crm-application.alch'),original=readFileSync(source,'utf8');assert.ok(original.includes('from="sources.evidence.text"'));writeFileSync(source,original.replace('from="sources.evidence.text"','from='+JSON.stringify(forbidden)));assert.throws(()=>{live=owner.prepare({sourceRoot:root,manifestPath:path.join(root,'crm-application.profile.json')});},(error:any)=>error?.code==='TECHNICAL_PROFILE_APPLICATION_INPUTS');
 });
}
