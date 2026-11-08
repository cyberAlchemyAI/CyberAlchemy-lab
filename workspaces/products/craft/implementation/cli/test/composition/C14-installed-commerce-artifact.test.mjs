/** Clean-installed pair compiles the unchanged five-service business source.
 * The source runtime end-to-end test separately proves executable behavior.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const craft=process.env.CRAFT_C14_CLI_TARBALL;
const alch=process.env.CRAFT_C14_ALCH_TARBALL;
const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');

test('C14 clean-installed Craft and AlchLang build the complete original Commerce graph and bridge',
 {skip:process.env.CRAFT_C14_INSTALLED_COMMERCE_RUN!=='1'},()=>{
  for(const archive of [craft,alch]){
   assert.equal(typeof archive,'string','both exact archive paths are required');
   assert.equal(path.isAbsolute(archive),true);
   assert.equal(existsSync(archive),true);
  }
  const before={craft:sha(craft),alch:sha(alch),
   business:sha(path.join(source,'application.alch'))};
  const work=mkdtempSync(path.join('/var/tmp','craft-c14-installed-commerce-'));
  let successful=false;
  try{
   const consumer=path.join(work,'consumer');mkdirSync(consumer);
   writeFileSync(path.join(consumer,'package.json'),
    '{"name":"c14-installed-commerce-consumer","private":true,"type":"module"}\n');
   const env={...process.env,npm_config_update_notifier:'false',NODE_PATH:''};
   delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
   const install=spawnSync('npm',['install','--offline','--ignore-scripts','--no-audit',
    '--no-fund','--no-save',craft,alch],{cwd:consumer,env,encoding:'utf8',
    timeout:180000,maxBuffer:8*1024*1024});
   assert.equal(install.status,0,`clean archive install failed:\n${install.stdout}\n${install.stderr}`);
   const child=`import {createCoreCommerceServiceArtifactOwner} from '@domainspec-v2/cli/generic';
import {readFileSync} from 'node:fs';
import path from 'node:path';
const [source,output]=process.argv.slice(1);
let owner;
try{
 owner=await createCoreCommerceServiceArtifactOwner(source,output);
 const manifest=owner.inspect(),artifacts=path.join(output,'artifacts');
 const graph=JSON.parse(readFileSync(path.join(artifacts,'system-graph.json'),'utf8'));
 const bridge=JSON.parse(readFileSync(path.join(artifacts,'business-system-bridge.json'),'utf8'));
 process.stdout.write(JSON.stringify({resolved:import.meta.resolve('@domainspec-v2/cli/generic'),
  manifest:{complete:manifest.complete_application,
   missing:manifest.missing_complete_application_classes,
   services:manifest.services.map(row=>row.id),
   source:manifest.source_capture_sha256,profile:manifest.family_sha256},
  graph:{source:graph.source_capture_sha256,profile:graph.family_sha256,
   nodes:graph.nodes.map(row=>row.id),
   edges:graph.edges.map(row=>[row.from,row.relation,row.to]),
   closed:graph.edges.every(row=>graph.nodes.some(node=>node.id===row.from)&&
    graph.nodes.some(node=>node.id===row.to))},
  bridge:{source:bridge.source_capture_sha256,profile:bridge.family_sha256,
   links:bridge.links.map(row=>[row.business,row.system]),
   closed:bridge.links.every(row=>graph.nodes.some(node=>node.id===row.system))}}));
}finally{owner?.close();}`;
   const output=path.join(work,'generated');
   const run=spawnSync(process.execPath,['--input-type=module','-e',child,source,output],
    {cwd:consumer,env,encoding:'utf8',timeout:900000,maxBuffer:8*1024*1024});
   assert.equal(run.status,0,`installed Commerce generation failed:\n${run.stdout}\n${run.stderr}`);
   const result=JSON.parse(run.stdout);
   assert.ok(result.resolved.startsWith('file://'+
    path.join(consumer,'node_modules/@domainspec-v2/cli/')));
   assert.deepEqual(result.manifest.services,
    ['catalog','fulfillment','inventory','orders','payments']);
   assert.equal(result.graph.source,result.manifest.source);
   assert.equal(result.bridge.source,result.manifest.source);
   assert.equal(result.graph.profile,result.manifest.profile);
   assert.equal(result.bridge.profile,result.manifest.profile);
   assert.equal(result.graph.closed,true);
   assert.equal(result.bridge.closed,true);
   for(const id of ['workflow:Orders.Checkout.Checkout',
    'event:Shop.Events.OrderConfirmed','outbox:Orders.OrderConfirmedOutbox',
    'inbox:Fulfillment.ShipmentInbox'])
    assert.ok(result.graph.nodes.includes(id),`missing original system node ${id}`);
   for(const relation of ['owns-workflow','produces-event','delivers-event',
    'commits-inbox','transitions-outbox'])
    assert.ok(result.graph.edges.some(row=>row[1]===relation),
     `missing original relationship ${relation}`);
   for(const link of [['Orders.Checkout.Checkout','workflow:Orders.Checkout.Checkout'],
    ['Shop.Events.OrderConfirmed','event:Shop.Events.OrderConfirmed'],
    ['Fulfillment.ShipmentInbox','inbox:Fulfillment.ShipmentInbox']])
    assert.ok(result.bridge.links.some(row=>row[0]===link[0]&&row[1]===link[1]),
     `missing original bridge link ${link[0]}`);
   assert.equal(result.manifest.complete,true,'the installed artifact must be a complete application');
   assert.deepEqual(result.manifest.missing,[]);
   assert.deepEqual({craft:sha(craft),alch:sha(alch),
    business:sha(path.join(source,'application.alch'))},before);
   successful=true;
  }finally{
   if(successful)rmSync(work,{recursive:true,force:true});
   else console.error('C14 installed Commerce diagnostic fixture retained at '+work);
  }
 });
