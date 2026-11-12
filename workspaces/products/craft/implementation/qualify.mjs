/** One replaceable current local result; no historical run archive.
 * Open questions: README.md (broader matrix and semantic source standing).
 */
import {createHash} from 'node:crypto';
import {existsSync,readFileSync,writeFileSync,readdirSync,statSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {labRoot,upstreamRoot,implementationRoot as root} from './source-bindings.mjs';

const json=f=>JSON.parse(readFileSync(f,'utf8'));
const sha=f=>createHash('sha256').update(readFileSync(f)).digest('hex');
const review=path.join(labRoot,'docs/migration-plans/0007-craft-current-import-20261104');
const imported=[...json(path.join(review,'IMPORT.json')).payload,...json(path.join(review,'EVIDENCE-EXPORT.json')).payload];
const functionalFiles=directory=>readdirSync(directory,{withFileTypes:true}).flatMap(e=>
  ['node_modules','.local','__pycache__'].includes(e.name)?[]:e.isDirectory()?functionalFiles(path.join(directory,e.name)):e.isFile()?[path.relative(labRoot,path.join(directory,e.name))]:[]);
const extras=['source-bindings.mjs','configure.py','build-core.mjs','run.mjs','relocation.test.mjs','qualify.mjs','.gitignore',
  'alchlang/src/generated/operation-patterns.generated.ts'].map(p=>'craft/implementation/'+p)
  .concat(['craft/ontology/application/derive.mjs','craft/ontology/application/derive.test.mjs',
    'craft/ontology/application/reconcile.py','craft/ontology/sources/reconciliation.json',
    'craft/ontology/sources/review.json','craft/work/experiments/body-war-reference/application.json',
    'craft/work/experiments/body-war-reference/README.md','craft/implementation/source-bindings.d.mts'])
  .concat(functionalFiles(path.join(root,'verification')));
const selected=[...new Set([...imported.map(r=>r.target),...extras])].sort();
const snapshot=()=>selected.map(p=>({path:p,sha256:sha(path.join(labRoot,p))}));
const before=snapshot();
const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
const check=spawnSync(node,[path.join(root,'run.mjs'),'check'],{cwd:labRoot,encoding:'utf8',maxBuffer:4*1024*1024});
writeFileSync(path.join(root,'.local/qualification-check.log'),String(check.stdout??'')+String(check.stderr??''));
if(check.status!==0)throw Error(String(check.stderr||check.stdout||check.error));
if(JSON.stringify(before)!==JSON.stringify(snapshot()))throw Error('Selected source changed during qualification');
const build=json(path.join(root,'.local/core-build/WORKING-BUILD.json'));
if(build.packageRoot!==path.join(root,'cli')||!build.checks.length||build.checks.some(c=>c.status!==0))throw Error('Missing exact local Core build result');
const counters=[];
for(const name of ['relocation-tests','ontology-tests']){
  const log=path.join(root,'.local',name+'.log'),text=readFileSync(log,'utf8');
  const tests=Number(text.match(/(?:ℹ|#) tests (\d+)/)?.[1]);
  const passed=Number(text.match(/(?:ℹ|#) pass (\d+)/)?.[1]);
  const failed=Number(text.match(/(?:ℹ|#) fail (\d+)/)?.[1]);
  if(!tests||tests!==passed||failed!==0)throw Error('Incomplete test accounting: '+name);
  counters.push({id:name,tests,passed,failed,log_sha256:sha(log)});
}
if(counters[0].tests!==3||counters[1].tests!==7)throw Error('Selected test coverage changed');
const applied=json(path.join(review,'APPLIED.json'));
for(const [relative,expected] of Object.entries(applied.protected_files))
  if(sha(path.join(labRoot,relative))!==expected)throw Error('Protected entrypoint changed: '+relative);
let checked=0;
for(const row of json(path.join(review,'IMPORT.json')).payload){
  if(row.current_source?.root==='upstream'){
    if(sha(path.join(upstreamRoot,row.current_source.path))!==row.current_source.sha256)throw Error('Upstream source changed: '+row.current_source.path);
    checked++;
  }
}
const files=directory=>readdirSync(directory,{withFileTypes:true}).flatMap(e=>{
  const f=path.join(directory,e.name);return e.isDirectory()?files(f):e.isFile()?[f]:[];
});
const outputs=['cli/dist','alchlang/dist'].flatMap(d=>files(path.join(root,d))).sort()
  .map(f=>({path:path.relative(labRoot,f),sha256:sha(f)}));
const runtime=path.join(root,'.local/ontology-build/release/cal-ontology-source-runtime');
const reconciliation=json(path.join(labRoot,'craft/ontology/sources/reconciliation.json'));
const report={schema_version:'craft.local-relocation-qualification/v1',status:'passed-local-scope',authority_effect:'none',
  finished_at:new Date().toISOString(),scope:'Local source/build plus generated protected HTTP/Auth/SQLite fixture and native ontology readers. Linked local consumer, not clean archive installation or full Craft certification.',
  cases:['401 without Auth','atomic SQLite commit','stable command replay','stored state read','unknown Entry rejection without publication','AI profiles resolve local Core',
    'native ontology import/replay/export','eight named outputs from nine declared inputs','distinct business/system branches and 52 bridge relations',
    'reviewed current semantic pins and reference-only Body War classification',
    'incomplete/duplicate/forged/unknown/traversal/identity/stale document/semantic code rejection'],
  totals:{tests:counters.reduce((n,c)=>n+c.tests,0),passed:counters.reduce((n,c)=>n+c.passed,0),failed:0},checks:counters,
  builds:{core:{version:build.version,build_check_count:build.checks.length,checks:build.checks,toolchain:build.toolchain},
    alchlang:{name:json(path.join(root,'alchlang/package.json')).name,version:json(path.join(root,'alchlang/package.json')).version,
      successful_build_log_sha256:sha(path.join(root,'.local/alchlang-build.log'))},
    ontology_consumer:{source_manifest:'implementation/bindings/ontology-product-event-runtime/v4/Cargo.toml',binary_sha256:sha(runtime)}},
  selected_sources_unchanged_during_checks:true,source_inputs:before,compiled_outputs:outputs,
  upstream_source_files_unchanged:checked,protected_files:applied.protected_files,
  native_source_manifest_sha256:sha(path.join(labRoot,'workspaces/products/craft/ontology/application/source-manifest.json')),
  legacy_semantic_lineage:{status:reconciliation.status,counts:reconciliation.counts},
  runtime_copied:false,global_consumer_cutover:false,publication:false,listeners_started:0,
  not_qualified:['full Craft/application matrix','TDE/EVF runtime','real provider accounts','measured model quality','production identity','deployment',
    'clean archive install','Product capability admission/effective authority','Body War reference execution/commissioning'],
  open_questions_ref:'craft/implementation/README.md#open-questions'};
const target=path.join(labRoot,'craft/work/outcomes/current-verification/lab-qualification.json');
writeFileSync(target,JSON.stringify(report,null,2)+'\n');
const changed=imported.filter(r=>sha(path.join(labRoot,r.target))!==r.sha256).map(r=>({path:r.target,imported_sha256:r.sha256,local_sha256:sha(path.join(labRoot,r.target))}));
writeFileSync(path.join(review,'LOCAL-CHANGES.json'),JSON.stringify({schema_version:'craft.local-relocation-changes/v1',authority_effect:'none',
  changes:changed,added_source_inputs:extras,qualification_ref:path.relative(labRoot,target),
  interpretation:'Explicit local relocation/configuration, generated build inputs, current Work/status/navigation and representation bindings; original Product capability candidate standing retained.'},null,2)+'\n');
console.log(JSON.stringify({status:report.status,tests:report.totals,source_files:before.length,compiled_files:outputs.length,
  protected_files:Object.keys(applied.protected_files).length,upstream_sources_checked:checked,report:path.relative(labRoot,target),legacy_lineage:reconciliation.counts}));
