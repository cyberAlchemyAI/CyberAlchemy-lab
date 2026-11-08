/** Generated view budget is distinct from source limits and keeps file custody.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {captureTechnicalServiceArchitectureArtifacts} from '../../src/profile-engine/technical-profile-service-architecture.ts';
import {readCorePhysicalFile,pinCorePhysicalCaptures} from '../../src/commerce/commerce-core-physical.ts';
const limit=(error:any)=>error.diagnostics?.some((d:any)=>d.code==='ResourceLimit');
function fixture(t:any){const root=mkdtempSync(path.join(tmpdir(),'craft-view-budget-'));t.after(()=>rmSync(root,{recursive:true,force:true}));return root;}
test('large generated aggregate graph is bounded and pinned without widening source reads',t=>{
 const root=fixture(t),file=path.join(root,'system-graph.json'),bytes=JSON.stringify({nodes:[],padding:'x'.repeat(1048576)});writeFileSync(file,bytes);
 assert.throws(()=>readCorePhysicalFile(file),limit);
 const captures=captureTechnicalServiceArchitectureArtifacts(root);assert.equal(captures.length,1);assert.equal(captures[0]!.file.bytes,Buffer.byteLength(bytes));
 const pin=pinCorePhysicalCaptures(captures);pin.assertCurrent();writeFileSync(file,bytes.replace('padding','paddinh'));assert.throws(()=>pin.assertCurrent(),(error:any)=>error.diagnostics?.some((d:any)=>d.code==='StaleOwner'));
});
test('ordinary files and nested graphs retain the source-sized budget',t=>{
 for(const relative of ['business.alch','entries/example/system-graph.json']){const root=fixture(t),file=path.join(root,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,'x'.repeat(1048577));assert.throws(()=>captureTechnicalServiceArchitectureArtifacts(root),limit);}
});
test('aggregate graph limit remains finite',t=>{
 const root=fixture(t);writeFileSync(path.join(root,'system-graph.json'),'x'.repeat(16*1024*1024+1));assert.throws(()=>captureTechnicalServiceArchitectureArtifacts(root),limit);
});
