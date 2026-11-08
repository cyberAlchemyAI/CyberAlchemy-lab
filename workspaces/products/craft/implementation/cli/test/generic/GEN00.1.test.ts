/** Baseline evidence gates, not application behavior tests. Open questions: baseline/README.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const base=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r2/baseline');
const {assertFiles,digest,requireCurrentBehaviorReceipt}=await import(path.join(base,'verify.mjs'));
const load=(name:string)=>JSON.parse(readFileSync(path.join(base,name),'utf8'));
test('GEN00.1:positive — frozen capture manifest and selected beforeimages retain their exact bytes',()=>{
 const seal=load('capture-seal.json');assert.equal(seal.task,'GEN00.1');assertFiles(root,seal.files);
 const source=load('source-manifest.json');assert.ok(source.files.length>100);
 for(const row of source.files.filter((r:any)=>r.beforeimage))assertFiles(base,[{...row,path:row.beforeimage}]);
 assert.equal(load('dirty-inventory.json').count,seal.dirty_count);
 assert.deepEqual(load('legacy-evidence.json').counts,{completed:55,pending:23});
 const positive={kind:'behavior',exit_code:0,subjects:[{path:'unit.ts',sha256:digest('current')}],counts:{tests:1,pass:1,fail:0,skipped:0,cancelled:0}};
 assert.equal(requireCurrentBehaviorReceipt(positive,positive.subjects),true);
});
test('GEN00.1:negative — changed source, changed beforeimage, unbound strict and incomplete evidence reject',()=>{
 const tmp=mkdtempSync(path.join(os.tmpdir(),'gen001-integrity-'));
 try{writeFileSync(path.join(tmp,'file'),'captured');const row={path:'file',bytes:8,kind:'file',sha256:digest('captured')};assertFiles(tmp,[row]);writeFileSync(path.join(tmp,'file'),'modified');assert.throws(()=>assertFiles(tmp,[row]),/mismatch/);}finally{rmSync(tmp,{recursive:true,force:true});}
 const subjects=[{path:'unit.ts',sha256:digest('current')}];
 const good={kind:'behavior',exit_code:0,subjects,counts:{tests:1,pass:1,fail:0,skipped:0,cancelled:0}};
 assert.throws(()=>requireCurrentBehaviorReceipt({...good,subjects:[{path:'unit.ts',sha256:digest('old')}]},subjects),/stale/);
 assert.throws(()=>requireCurrentBehaviorReceipt({...good,subjects:[]},subjects),/unbound/);
 assert.throws(()=>requireCurrentBehaviorReceipt({...good,counts:{...good.counts,skipped:1}},subjects),/incomplete/);
 const strict=JSON.parse(readFileSync(path.join(root,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/source-invocation-target-cache-strict-fourth.json'),'utf8'));
 assert.throws(()=>requireCurrentBehaviorReceipt(strict,subjects),/not successful behavior/);
 const chronology=load('receipt-chronology.json');assert.ok(chronology.chronology.every((r:any)=>r.behavior_reusable_for_current_epoch===false));
 const latest=chronology.chronology.find((r:any)=>r.receipt.endsWith('source-snapshot-011.json'));
 assert.ok(latest.comparison.mismatches.some((r:any)=>r.path.endsWith('commerce-source-invocation-owner-v1.ts')));
});
for(const revision of ['r3','r4']){
 test(`legacy:${revision}:EC00:inputs:0 — inherited candidate/test/support identities are explicitly compared`,()=>{
  const legacy=load('legacy-evidence.json');assert.ok(legacy.inherited_frozen_epoch.members>0);assert.equal(legacy.inherited_frozen_epoch.mismatches.length,0);
  const task=JSON.parse(readFileSync(path.join(root,`goals/plans/craft-alchlang-commerce-2026-10-16-${revision}/tasks.json`),'utf8')).tasks.find((t:any)=>t.id==='EC00');
  assert.equal(task.inputs[0],'exact inherited U0 candidate/test/support receipt');
  assert.equal(legacy.inherited_u0_receipts.mismatches.length,0);assert.ok(legacy.inherited_u0_receipts.members>100);
 });
 test(`legacy:${revision}:EC00:inputs:1 — original ecommerce demo and review identities stay preserved`,()=>{
  const legacy=load('legacy-evidence.json');const groups=Object.values(legacy.original_demo_review) as any[];assert.ok(groups.length>=2);
  for(const g of groups){assert.ok(g.members>0);assert.equal(g.mismatches.length,0);}
  const task=JSON.parse(readFileSync(path.join(root,`goals/plans/craft-alchlang-commerce-2026-10-16-${revision}/tasks.json`),'utf8')).tasks.find((t:any)=>t.id==='EC00');assert.equal(task.inputs[1],'original ecommerce review/demo identities');
 });
}
