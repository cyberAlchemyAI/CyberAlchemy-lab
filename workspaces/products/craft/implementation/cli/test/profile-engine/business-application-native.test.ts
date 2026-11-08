import test from 'node:test';
import assert from 'node:assert/strict';
import {createBusinessApplicationFixture} from '../helpers/business-profile.ts';
import {prepareProfileProject,planProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
import {loadDomainSpecCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/domainspec-cli.js';

// Open questions: BA19 exact scope audit; no business execution or final output here.
test('v2 native qualification rejects wrong typed settlement and missing actual transport imports',async t=>{
 const fixture=createBusinessApplicationFixture(t,'node-http-entry-local-v2'),prepared=await prepareProfileProject(fixture.file);t.after(()=>disposeProfileProject(prepared));
 const compiler=await loadDomainSpecCompiler(),engine=compiler.profileEngine!,plan=planProfileProject(prepared);
 const files=engine.compileProfileDomainFiles(prepared.snapshot,plan.files,prepared.compilerPath),entry='applications/receiveNotice/src/profile-entry.ts';
 const wrong={...files,[entry]:files[entry]!.replace('store:createEmptyEffectsStore()','store:{begin:async()=>({read:async()=>0,commit:async()=>({status:"wrong"}),rollback:async()=>{}})}')};
 assert.notEqual(wrong[entry],files[entry]);assert.throws(()=>engine.qualifyNativeFiles(prepared.snapshot,wrong,prepared.compilerPath),/PROFILE_NATIVE_CHECK_FAILED/);
 const missing={...files};delete missing['applications/receiveNotice/src/application-http.mts'];delete missing['applications/receiveNotice/lib/application-http.mjs'];delete missing['applications/receiveNotice/lib/application-http.d.mts'];
 assert.throws(()=>engine.qualifyNativeFiles(prepared.snapshot,missing,prepared.compilerPath),/PROFILE_NATIVE_(IMPORT|CHECK_FAILED|SOURCE)/);
});
