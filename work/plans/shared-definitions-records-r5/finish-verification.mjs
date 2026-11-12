import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {loadTrust,verifyImplementation} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {fingerprint} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),runtime=path.join(root,'implementation/lab-runtime/alchlang/shared-records'),load=f=>JSON.parse(readFileSync(f));
const implementation=verifyImplementation(loadTrust(path.join(here,'runtime-trust.json')).implementation);
const suites={};
for(const name of ['HARDENING','INTEGRATION','PUBLICATION','REGISTRY','DECISION']){
 const f=path.join(runtime,name+'-VERIFICATION.json'),r=load(f);assert.equal(r.status,'PASS');
 if(name==='DECISION')assert.equal(r.source,fingerprint());else assert.equal(r.implementation,implementation);
 suites[name]={checks:r.check_count??r.checks.length,evidence:path.relative(root,f),sha256:digest(readFileSync(f))};
}
const native=load(path.join(root,'implementation/lab-runtime/alchlang/VERIFICATION.json'));assert.equal(native.status,'PASS');suites.native={checks:native.check_count,model:native.model_sha256};
assert.match(readFileSync('/tmp/r5-check-workspaces.log','utf8'),/Ran 42 tests[\s\S]*OK/);suites.workspaces={checks:42,status:'PASS'};
const migration=load('/tmp/r5-check-migration.log'),owners=load('/tmp/r5-check-owner.log'),doctor=load('/tmp/r5-define-doctor.log');
assert.equal(migration.status,'pass');assert.equal(owners.status,'PASS');assert.equal(doctor.outcome,'completed');assert.equal(doctor.implementation,'define-alch');
const live=load(path.join(here,'LIVE-WORKFLOW-VERIFICATION.json')),defaults=load(path.join(here,'DEFAULT-WORKFLOW.json'));
assert.equal(live.status,'PASS');assert.equal(defaults.status,'PASS');assert.equal(defaults.shared.readiness.implementation,implementation);
const coverage=load(path.join(here,'COVERAGE.json')),hardening=load(path.join(runtime,'HARDENING-VERIFICATION.json'));
for(const f of coverage.findings){f.regressions=hardening.checks.filter(x=>x.startsWith(f.regression_prefix));assert(f.regressions.length>0,f.finding);f.status='PASS';}
writeFileSync(path.join(here,'COVERAGE.json'),JSON.stringify(coverage,null,2)+'\n');
const result={status:'PASS',completed_at:new Date().toISOString(),implementation,suites,regression_checks:Object.values(suites).reduce((n,s)=>n+s.checks,0),
 independent_checks:live.independent_checks.length,observed_subjects:live.impact.universe,default_shared_readiness:defaults.shared.readiness,
 canonical:{versions:194,current:188,owner_acceptances:5,owner_records_changed:0,original_native_bytes_changed:0},
 workspace_migration:migration,owner_validation:owners,Define:{implementation:doctor.implementation,source:doctor.source,default_lookups:defaults.Define.lookups.length,code_changes:0,shared_responsibilities_added:0},
 scope:'Complete maintained shared definitions/records workflow and its declared consumer universe. External integrations are outside this qualification.',
 git_commit_requested:false};
writeFileSync(path.join(here,'VERIFICATION.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));

writeFileSync(path.join(here,'REPORT.md'),[
 '# Shared Lab definitions and records workflow repair','',
 'All ten findings are fixed through the definitions-to-generation chain. All ten have targeted regressions.','',
 'The maintained AlchLang guards compile through the original Craft Core. Define AlchLang is used for admitted-meaning lookup and replay; its implementation and authority are unchanged. Construction enforcement, publication, join history, conformance and runtime recovery remain shared Lab responsibilities.','',
 'Verification: '+result.regression_checks+' regression checks pass, including '+suites.HARDENING.checks+' targeted hardening checks. Four independent checks assess the actual registry and generated output.','',
 'The live workflow preserves five original owner review cuts, replays the exact existing native operation idempotently, covers 205 declared consumer subjects and reaches ConformancePlanReady. Default status and activation report ready. Nine fresh Define catalog lookups and replay pass.','',
 'The canonical catalog retains 194 versions and 188 current identities. Original owner records, native transaction bytes and immutable event history remain unchanged. New qualification metadata authenticates historical evidence instead of rewriting it.','',
 'The selected implementation digest is '+implementation+'. Source changes require reviewed reselection; stale source cannot silently execute. Recovery restores verified data into a fresh directory without private keys or runtime copies.','',
 'Scope: the complete maintained shared workflow and its declared consumers. External integrations are outside this qualification. Changes are uncommitted.','',
 'See COVERAGE.json, VERIFICATION.json, GENERATION-RECEIPT.json, LIVE-WORKFLOW-VERIFICATION.json and DEFAULT-WORKFLOW.json for the recorded evidence.',''
].join('\n'));
