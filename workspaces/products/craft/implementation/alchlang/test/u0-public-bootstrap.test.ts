import assert from 'node:assert/strict';
import test from 'node:test';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Public compiled frontend/backend only. No original selections or decisions fabricated.
// Open Questions: J02 onward qualify source/accepted/graph/native prefix witnesses.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const core=path.resolve(root,'../../../../../../craft/projects/domainspec-v2/impl/cli');
const api=await import(pathToFileURL(path.join(root,'dist/index.js')).href);
const compiler=await import(pathToFileURL(path.join(root,'dist/domainspec-cli.js')).href);

test('built Alch public entry exposes additive prefix and preserves existing project API',()=>{
 for(const name of ['prepareDirectBusinessAuthoringProjectV2','replayDirectBusinessAuthoringPrefixV2','assertPreparedDirectBusinessAuthoringProjectV2Current','disposeDirectBusinessAuthoringProjectV2','prepareBusinessAuthoringProject'])assert.equal(typeof api[name],'function',name);
 assert.throws(()=>api.assertPreparedDirectBusinessAuthoringProjectV2Current({kind:'prepared-direct-business-authoring-project-v2'}),/original prepared/);
});

test('public compiler bridge captures actual built frontend and Core native basis',async()=>{
 const bound=await compiler.loadDomainSpecCompiler(core),factory=bound.profileEngine.createBusinessU0RuntimeV4;assert.equal(typeof factory,'function');
 const runtime=await factory({frontend_root:root});runtime.assertCurrent();assert.equal(runtime.basis.descriptor,'node-http-entry-u0-v4');
 assert.equal(Object.hasOwn(runtime.basis,'callable_sha256'),false);assert.equal(runtime.basis.artifacts.find((row:any)=>row.requirement.artifact_id==='node').resolved_version,process.versions.node);
 runtime.dispose();assert.throws(()=>runtime.assertCurrent());
});

test('public preparation rejects absent or unsupported explicit profile/output selection before reading business source',async()=>{
 for(const choice of [undefined,{}, {profile:'node-http-entry-v3',output:'code'}, {profile:'node-http-entry-u0-v4',output:'formal-models'}, {profile:'node-http-entry-u0-v4',output:'code',ready:true}])await assert.rejects(()=>api.prepareDirectBusinessAuthoringProjectV2('/unselected','missing.alch',choice));
});
