import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {root,node,build} from './runtime/build.mjs';
const A=path.resolve(root,'..'),directory=mkdtempSync(path.join(A,'.local/cli-workflow-')),guard=path.join(directory,'no-legacy'),checks=[];mkdirSync(guard);
writeFileSync(path.join(guard,'sitecustomize.py'),`import sys,importlib.abc
class NoLegacy(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0]=='define_core':raise RuntimeError('legacy-Define-engine-forbidden')
sys.meta_path.insert(0,NoLegacy())
`);
const cli=args=>{const p=spawnSync(node,[path.join(root,'cli.mjs'),...args],{encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,PYTHONPATH:guard}});assert.equal(p.status,0,p.stderr||p.stdout);return JSON.parse(p.stdout);};
const example=path.join(directory,'example'),work=path.join(directory,'work'),pack=path.join(directory,'package'),context=path.join(directory,'context.json'),project='project:isolated-cli-verification',workRef='work:isolated-cli-verification',actor='actor:isolated-cli-verification';mkdirSync(work);
assert.equal(cli(['example','--output',example]).context_selection,'required');checks.push('native-example-with-explicit-context-selection');
writeFileSync(context,JSON.stringify({project,work:workRef,source_snapshot:'local:isolated-cli-proof',status:'Sufficient',explanation:'Isolated candidate test only, no canonical admission or grants.',evidence:[]}));
const imported=cli(['import-request','--work',work,'--file',path.join(example,'request.json'),'--context',context,'--project',project,'--work-ref',workRef,'--actor',actor]);checks.push('native-request-import-and-command-journal');
assert.deepEqual(cli(['request','--work',work]),JSON.parse(readFileSync(path.join(example,'request.json'))));checks.push('exact-portable-request-export');
const prepared=cli(['prepare','--work',work,'--source-root',path.join(example,'sources'),'--output',pack,'--permit-retention']);assert.equal(prepared.operation,'prepare');checks.push('actual-CLI-native-preparation');
const inspection=cli(['inspect','--package',pack]);assert.equal(inspection.operation,'inspect');checks.push('actual-CLI-native-frozen-inspection');
const confirmed=cli(['confirm','--work',work,'--package',pack,'--actor',actor,'--expected-revision',imported.current.revision]);assert.equal(confirmed.outcome,'recorded');checks.push('observed-package-confirmation');
const definitions=path.join(directory,'definitions'),materialized=cli(['materialize','--package',pack,'--output',definitions]);assert.equal(materialized.data.report.actual_owner_outcome,null);assert.deepEqual(readFileSync(path.join(definitions,'definitions/000/definition.json')),readFileSync(path.join(example,'sources/user-journey.json')));checks.push('actual-CLI-materialization-exact-Definition-without-owner-admission');
const reconstructed=path.join(directory,'reconstructed');cli(['reconstruct','--package',pack,'--output',reconstructed]);
const manifest=JSON.parse(readFileSync(path.join(pack,'manifest.json')));for(const row of Object.values(manifest.members))assert.deepEqual(readFileSync(path.join(reconstructed,row.path)),readFileSync(path.join(pack,row.path)));checks.push('actual-CLI-reconstruction-every-member-byte');
rmSync(pack,{recursive:true});assert.deepEqual(cli(['show','--work',work]).current,confirmed.current);checks.push('fresh-process-observation-and-session-replay-without-package');
const receipt={schema_version:'define-native-cli-workflow-verification/v1',status:'PASS',source:build().source,checks,check_count:checks.length,legacy_engine_runtime_imports:'actively blocked',canonical_owner_admission:false,fixture_context_only:true};writeFileSync(path.join(A,'.local/CLI-WORKFLOW-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
