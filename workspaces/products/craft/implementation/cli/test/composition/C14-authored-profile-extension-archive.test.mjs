/** A new authored HTTP profile is selected by the same installed Craft archive.
 * Runtime behavior remains covered by the separate Schedule complete-app test.
 * Open Questions: goals/plans/craft-alchlang-generic-applications-2026-10-18-r5/BUILD-MODE.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {cpSync,existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {resolveGenericHttpProfile} from '../../src/generic/http-profile.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture');
const authored=fileURLToPath(new URL('./fixtures/C14-schedule-field-http-profile.json',import.meta.url));
const archive=process.env.CRAFT_C14_CLI_TARBALL;
const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');

test('C14 new declarative Schedule profile has its own identity, routes, and original Entry targets',()=>{
 const baseline=resolveGenericHttpProfile(readFileSync(path.join(source,'contracts/http-profile.json'),'utf8'),'baseline-http-profile.json');
 const added=resolveGenericHttpProfile(readFileSync(authored,'utf8'),authored);
 assert.notEqual(added.id,baseline.id);
 assert.notEqual(added.route_prefix,baseline.route_prefix);
 assert.deepEqual(added.routes.map(row=>row.entry),baseline.routes.map(row=>row.entry));
 assert.deepEqual(added.routes.map(row=>row.response_mapping),baseline.routes.map(row=>row.response_mapping));
 assert.notDeepEqual(added.routes.map(row=>[row.id,row.path]),baseline.routes.map(row=>[row.id,row.path]));
 assert.equal(added.application_profile,baseline.application_profile);
});

test('C14 clean-installed unchanged Craft archive emits complete Schedule graph and bridge from the new profile',
 {skip:!archive},()=>{
  assert.equal(path.isAbsolute(archive),true);
  assert.equal(existsSync(archive),true);
  const archiveSha=sha(archive),work=mkdtempSync(path.join(tmpdir(),'craft-c14-new-profile-'));
  try{
   const consumer=path.join(work,'consumer'),application=path.join(work,'authored');
   mkdirSync(consumer);cpSync(source,application,{recursive:true});
   const business=path.join(application,'business.alch'),originalBusiness=readFileSync(business);
   cpSync(authored,path.join(application,'contracts/http-profile.json'));
   writeFileSync(path.join(consumer,'package.json'),'{"name":"c14-new-profile-consumer","private":true,"type":"module"}\n');
   const install=spawnSync('npm',['install','--offline','--ignore-scripts','--no-audit','--no-fund','--no-save',archive],
    {cwd:consumer,encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024,
     env:{...process.env,npm_config_update_notifier:'false'}});
   assert.equal(install.status,0,`clean archive install failed:\n${install.stdout}\n${install.stderr}`);
   const child=`import {createGenericHttpCompositionOwner,createGenericServiceArtifactOwner} from '@domainspec-v2/cli/generic';
import {readFileSync} from 'node:fs';
import path from 'node:path';
const [root,work]=process.argv.slice(1);
const compiler=createGenericHttpCompositionOwner();let handle;
try{
 handle=await compiler.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')});
 const inspected=compiler.inspect(handle),review=compiler.review(handle,'C14-new-profile');
 compiler.accept(handle,{decision_id:'C14-new-profile',owner:'C14-new-profile',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'decision.json'));
 const artifactOwner=createGenericServiceArtifactOwner(compiler,handle),output=path.join(work,'generated');
 const entries=[...new Set(inspected.http_contract.entries.map(row=>row.route.entry))];
 const artifact=artifactOwner.emit({outputDirectory:output,entries,requireCompleteApplication:true});
 const manifest=artifactOwner.inspect(artifact),graph=JSON.parse(readFileSync(path.join(output,'application-system-graph.json'),'utf8')),
  bridge=JSON.parse(readFileSync(path.join(output,'application-business-system-bridge.json'),'utf8'));
 process.stdout.write(JSON.stringify({resolved:import.meta.resolve('@domainspec-v2/cli/generic'),
  profile:inspected.http_contract.profile.id,complete:manifest.complete_application,
  missing:manifest.missing_complete_application_classes,
  services:manifest.services.map(row=>row.service),
  routes:graph.nodes.filter(node=>node.kind==='original-generated-profile-http-handler').map(node=>({id:node.route.id,path:node.route.path})),
  graph_closed:graph.edges.every(edge=>graph.nodes.some(node=>node.id===edge.from)&&graph.nodes.some(node=>node.id===edge.to)),
  bridge_closed:bridge.links.every(link=>graph.nodes.some(node=>node.id===link.system))}));
}finally{if(handle)compiler.dispose(handle);}`;
   const run=spawnSync(process.execPath,['--input-type=module','-e',child,application,work],
    {cwd:consumer,encoding:'utf8',timeout:900000,maxBuffer:8*1024*1024,env:{...process.env,NODE_PATH:''}});
   assert.equal(run.status,0,`installed profile generation failed:\n${run.stdout}\n${run.stderr}`);
   const result=JSON.parse(run.stdout);
   assert.ok(result.resolved.startsWith('file://'+path.join(consumer,'node_modules/@domainspec-v2/cli/')));
   assert.equal(result.profile,'ScheduleFieldOperationsHttp');
   assert.equal(result.complete,true);
   assert.deepEqual(result.missing,[]);
   assert.deepEqual(result.services,['ScheduleService']);
   assert.deepEqual(result.routes.sort((a,b)=>a.id.localeCompare(b.id)),[
    {id:'ScheduleField.ReadDay',path:'/field/calendar/{dayId}'},
    {id:'ScheduleField.Reserve',path:'/field/bookings'},
   ]);
   assert.equal(result.graph_closed,true);
   assert.equal(result.bridge_closed,true);
   assert.deepEqual(readFileSync(business),originalBusiness);
   assert.equal(sha(archive),archiveSha);
  }finally{rmSync(work,{recursive:true,force:true});}
 });
