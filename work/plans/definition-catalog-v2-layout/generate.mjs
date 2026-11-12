import {assertEpoch} from './source-epoch.mjs';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {prepareCli,packageCli,materializeCli} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),load=f=>JSON.parse(readFileSync(f)),sha=b=>createHash('sha256').update(b).digest('hex');
const mapping=load(path.join(here,'MAPPING.json')),results=[];const sourceEpoch=assertEpoch();
const only=process.argv[2],shard=process.env.CATALOG_SHARD;
async function generate(row){
 const work=path.join(root,row.work),run=path.join(work,'run-'+sha(readFileSync(path.join(work,'request.json'))).slice(0,16)),pack=path.join(run,'pack'),out=path.join(run,'materialized');mkdirSync(run,{recursive:true});
 const priorFile=path.join(work,'DEFINE-RECEIPT.json');
 if(existsSync(priorFile)){
  const prior=load(priorFile),manifestFile=path.join(pack,'manifest.json');
  if(prior.status==='PASS'&&prior.request_sha256===sha(readFileSync(path.join(work,'request.json')))&&existsSync(manifestFile)&&sha(readFileSync(manifestFile))===prior.inspected?.data?.root_sha256){
   const manifest=load(manifestFile);
   for(const member of Object.values(manifest.members)){const raw=readFileSync(path.join(pack,member.path));assert.equal(raw.length,member.bytes);assert.equal(sha(raw),member.sha256);}
   assert.equal(sha(readFileSync(path.join(root,prior.definition.path))),prior.definition.sha256);assert.equal(sha(readFileSync(path.join(root,prior.projection.path))),prior.projection.sha256);
   results.push(prior);console.log(JSON.stringify({definition_id:row.definition_id,status:'PASS',resumed_exact_verified_package:true}));return;
  }
 }
 let prepared;
 if(!existsSync(pack))prepared=await prepareCli(readFileSync(path.join(work,'request.json')),work,pack);
 const inspected=await packageCli(pack);
 let materialized;if(!existsSync(out))materialized=await materializeCli(pack,out);
 const files=[];function walk(dir){for(const e of readdirSync(dir,{withFileTypes:true})){const f=path.join(dir,e.name);if(e.isDirectory())walk(f);else files.push(f);}}walk(out);
 const def=files.find(f=>path.basename(f)==='definition.json'),md=files.find(f=>path.basename(f)==='DEFINITION.md');
 assert(def&&md,'materialization outputs missing '+JSON.stringify(files));
 const generated=readFileSync(def),expected=load(path.join(work,'definition.json'));assert.deepEqual(JSON.parse(generated),expected);if(!row.converted)assert.deepEqual(generated,readFileSync(path.join(root,row.source.body.path)));
 const result={source_epoch:sourceEpoch,request_sha256:sha(readFileSync(path.join(work,'request.json'))),definition_id:row.definition_id,version:row.version,status:'PASS',prepared,inspected,materialized,definition:{path:path.relative(root,def),sha256:sha(generated),bytes:generated.length},projection:{path:path.relative(root,md),sha256:sha(readFileSync(md)),bytes:readFileSync(md).length}};
 writeFileSync(path.join(work,'DEFINE-RECEIPT.json'),JSON.stringify(result,null,2)+'\n');
 results.push(result);console.log(JSON.stringify({definition_id:row.definition_id,status:'PASS',converted:row.converted}));
}
const selected=mapping.entries.filter((x,i)=>(!only||x.definition_id===only)&&(shard===undefined||i%8===Number(shard)));
for(let i=0;i<selected.length;i+=1)await Promise.all(selected.slice(i,i+1).map(generate));
results.sort((a,b)=>a.definition_id.localeCompare(b.definition_id));
writeFileSync(path.join(here,only?'PROTOTYPE.json':shard===undefined?'DEFINE-VERIFICATION.json':'DEFINE-VERIFICATION.shard'+shard+'.json'),JSON.stringify({status:'PASS',source_epoch:assertEpoch(),count:results.length,results},null,2)+'\n');
