/** Proves a technical profile change with one clean-installed compiler archive.
 * Set CRAFT_C14_CLI_TARBALL to a freshly built, absolute CLI .tgz path.
 * Open Questions: goals/plans/craft-alchlang-generic-applications-2026-10-18-r5/BUILD-MODE.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {cpSync,existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture');
const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');
const tarball=process.env.CRAFT_C14_CLI_TARBALL;

test('C14 one installed compiler archive admits a declarative profile-only route change',{skip:!tarball},()=>{
 assert.equal(path.isAbsolute(tarball),true,'CRAFT_C14_CLI_TARBALL must be absolute');
 assert.equal(existsSync(tarball),true,'CRAFT_C14_CLI_TARBALL must exist');
 const compilerSha=sha(tarball),work=mkdtempSync(path.join(tmpdir(),'craft-c14-installed-profile-'));
 try{
  const consumer=path.join(work,'consumer');mkdirSync(consumer);
  writeFileSync(path.join(consumer,'package.json'),'{"name":"c14-profile-consumer","private":true,"type":"module"}\n');
  const installed=spawnSync('npm',['install','--offline','--ignore-scripts','--no-audit','--no-fund','--no-save',tarball],{
   cwd:consumer,encoding:'utf8',timeout:120000,env:{...process.env,npm_config_update_notifier:'false'}
  });
  assert.equal(installed.status,0,`clean install failed:\n${installed.stdout}\n${installed.stderr}`);
  assert.equal(sha(tarball),compilerSha,'compiler archive changed during install');
  const baseline=path.join(work,'baseline'),changed=path.join(work,'changed');
  cpSync(fixture,baseline,{recursive:true});cpSync(fixture,changed,{recursive:true});
  const business='business.alch',profile='contracts/selected-profile.json',http='contracts/http-profile.json';
  const unchangedBusiness=readFileSync(path.join(baseline,business));
  assert.deepEqual(readFileSync(path.join(changed,business)),unchangedBusiness);
  const originalHttp=JSON.parse(readFileSync(path.join(changed,http),'utf8'));
  writeFileSync(path.join(changed,http),JSON.stringify({...originalHttp,route_prefix:'/schedule'},null,2)+'\n');
  const child=`import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import path from 'node:path';
const [baseline,changed,work]=process.argv.slice(1);
async function generate(root,name){
 const owner=createGenericHttpCompositionOwner();let handle;
 try{
  handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')});
  const inspected=owner.inspect(handle),review=owner.review(handle,'C14-'+name);
  owner.accept(handle,{decision_id:'C14-'+name,owner:'C14-'+name,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,name+'-decision.json'));
  const out=path.join(work,name+'-generated');
  owner.generate(handle,{entry:'Schedule.ReserveBookingEntry',outputDirectory:out});
  const graph=JSON.parse(readFileSync(path.join(out,'system-graph.json'),'utf8'));
  return {route_prefix:inspected.http_contract.profile.route_prefix,
   route_nodes:graph.nodes.filter(node=>node.kind==='injected-http-handler').map(node=>({
    id:node.route.id,path:inspected.http_contract.profile.route_prefix+node.route.path})),
   generated_module_sha256:createHash('sha256').update(readFileSync(path.join(out,'application.mjs'))).digest('hex')};
 }finally{if(handle)owner.dispose(handle);}
}
const first=await generate(baseline,'baseline'),second=await generate(changed,'changed');
process.stdout.write(JSON.stringify({resolved:import.meta.resolve('@domainspec-v2/cli/generic'),first,second}));`;
  const run=spawnSync(process.execPath,['--input-type=module','-e',child,baseline,changed,work],{
   cwd:consumer,encoding:'utf8',timeout:180000,env:{...process.env,NODE_PATH:''}
  });
  assert.equal(run.status,0,`installed generation failed:\n${run.stdout}\n${run.stderr}`);
  const result=JSON.parse(run.stdout);
  assert.ok(result.resolved.startsWith('file://'+path.join(consumer,'node_modules/@domainspec-v2/cli/') ),
   'generic compiler must resolve inside the clean consumer');
  assert.equal(result.first.route_prefix,'/api');
  assert.equal(result.second.route_prefix,'/schedule');
  assert.ok(result.first.route_nodes.every(row=>row.path.startsWith('/api/')));
  assert.ok(result.second.route_nodes.every(row=>row.path.startsWith('/schedule/')));
  assert.deepEqual(result.first.route_nodes.map(row=>row.id),result.second.route_nodes.map(row=>row.id),
   'profile change must preserve logical entry identity');
  assert.notDeepEqual(result.first.route_nodes,result.second.route_nodes,
   'profile change must alter generated technical routes');
  assert.notEqual(result.first.generated_module_sha256,result.second.generated_module_sha256,
   'profile change must alter emitted application bytes');
  assert.deepEqual(readFileSync(path.join(changed,business)),unchangedBusiness);
  assert.equal(sha(tarball),compilerSha,'both generations must use unchanged compiler archive');
 }finally{rmSync(work,{recursive:true,force:true});}
});
