/** Fresh immutable GEN00.2 attempt gate; runtime behavior is exercised separately.
 * Open Questions: implementation/craft-alchlang-generic-applications-2026-10-18-r2/evidence/GEN00.2/attempts/query-cache-replay-001/README.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
const attempt='implementation/craft-alchlang-generic-applications-2026-10-18-r2/evidence/GEN00.2/attempts/query-cache-replay-001';
const json=(p:string)=>JSON.parse(readFileSync(path.join(repo,p),'utf8'));
const read=(name:string)=>json(attempt+'/'+name);
const hash=(p:string)=>createHash('sha256').update(readFileSync(path.isAbsolute(p)?p:path.join(repo,p))).digest('hex');
const checkPin=(pin:any)=>assert.equal(hash(pin.path),pin.sha256,pin.path);
function verify(behavior:any,strict:any,measurements:any,config:any):void{
 assert.equal(config.attempt_root,attempt);assert.equal(json(config.compiler_package).version,'6.0.3');assert.equal(config.expected_tests,10);for(const pin of [config.baseline_seal,config.repair_result,config.repair_delta,config.source_delta,...config.subjects,...config.tools])checkPin(pin);
 const repair=json(config.repair_result.path);assert.ok(['passed','completed'].includes(repair.status),'GEN00.R must actually pass');
 const delta=json(config.source_delta.path);assert.equal(delta.schema_version,'craft.gen00-owned-delta/v1');assert.equal(delta.baseline_seal_sha256,config.baseline_seal.sha256);assert.deepEqual(delta.predecessor_delta,config.repair_delta);for(const change of delta.changes)assert.equal(hash(change.path),change.after_sha256);for(const created of delta.created_paths)checkPin(created);
 for(const r of [behavior,strict]){assert.equal(r.exit_code,0);assert.equal(r.unchanged_subjects_after,true);assert.equal(r.config_sha256,hash(attempt+'/attempt-config.json'));checkPin({path:r.log,sha256:r.log_sha256});assert.deepEqual(r.subject_files,config.subjects);for(const f of r.subject_files)checkPin(f);}
 assert.deepEqual(behavior.counts,{tests:10,pass:10,fail:0,cancelled:0,skipped:0,todo:0});
 assert.equal(strict.compiler.selected_version,'6.0.3');checkPin({path:strict.compiler.executable,sha256:strict.compiler.sha256});assert.ok(behavior.command.includes('test/commerce-source-invocation-v1.test.ts'));assert.ok(strict.command.includes('--strict'));assert.ok(strict.command.includes('--noEmit'));
 const phases=new Set(measurements.measurements.map((m:any)=>m.phase));for(const phase of ['prepared-process-first-codec-generation','prepared-process-repeated-codec-generation','uncached-target-preparation','cached-target-preparation'])assert.ok(phases.has(phase));assert.ok(![...phases].some(p=>String(p).includes('cold')));
 assert.ok(measurements.workload.captured_files>0);assert.ok(measurements.workload.captured_bytes>0);assert.ok(measurements.workload.modules>0);assert.ok(measurements.workload.generated_bytes>0);assert.equal(measurements.workload.generated_members.length,2);assert.deepEqual(measurements.workload.generated_members,measurements.workload.repeated_generated_members);
 for(const m of measurements.measurements){assert.ok(Number.isFinite(m.wall_ms)&&m.wall_ms>=0);assert.ok(m.rss_before_bytes>0);assert.ok(m.rss_after_bytes>0);assert.ok(m.process_cumulative_max_rss_kib>0);}
 const preservation=read('preservation.json');assert.equal(preservation.status,'passed');assert.equal(preservation.source_delta_sha256,config.source_delta.sha256);
}
test('GEN00.2:positive current ten-case behavior, exact repaired epoch, pinned strict and prepared-process observations',()=>verify(read('behavior.json'),read('strict.json'),read('measurements.json'),read('attempt-config.json')));
test('GEN00.2:negative stale, skipped, failed, wrong-epoch and cache-only evidence cannot satisfy completion',()=>{
 const b=read('behavior.json'),s=read('strict.json'),m=read('measurements.json'),c=read('attempt-config.json');
 const stale=structuredClone(b);stale.subject_files[0].sha256='0'.repeat(64);assert.throws(()=>verify(stale,s,m,c));
 const skip=structuredClone(b);skip.counts.skipped=1;assert.throws(()=>verify(skip,s,m,c));
 const failed=structuredClone(b);failed.exit_code=1;assert.throws(()=>verify(failed,s,m,c));
 const lookupOnly=structuredClone(m);lookupOnly.measurements=lookupOnly.measurements.filter((x:any)=>!x.phase.includes('codec-generation'));assert.throws(()=>verify(b,s,lookupOnly,c));
 const wrongCompiler=structuredClone(s);wrongCompiler.compiler.selected_version='7.0.2';assert.throws(()=>verify(b,wrongCompiler,m,c));
 const wrongEpoch=structuredClone(c);wrongEpoch.repair_delta.sha256='0'.repeat(64);assert.throws(()=>verify(b,s,m,wrongEpoch));
 const changedOutput=structuredClone(m);changedOutput.workload.repeated_generated_members[0].sha256='0'.repeat(64);assert.throws(()=>verify(b,s,changedOutput,c));
});
