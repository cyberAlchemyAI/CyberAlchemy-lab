import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root=path.dirname(fileURLToPath(import.meta.url));
const source=path.join(root,'source/lab-submission.alch');
const generated=path.join(root,'generated');
const consumer=process.env.ALCHLANG_CONSUMER ?? '/home/vlad_/projects/cyberAlchemy-v2/release-candidates/business-authoring-v1/qualification/consumer';
const bin=path.join(consumer,'node_modules/.bin/alchlang');
const require=createRequire(path.join(consumer,'package.json'));
const tsRoot=path.dirname(require.resolve('typescript/package.json'));
assert.equal(require(path.join(tsRoot,'package.json')).version,'6.0.3');
const run=(name,args,expect)=>{const p=spawnSync(bin,[name,source,...args],{cwd:consumer,encoding:'utf8',maxBuffer:8e6});assert.equal(p.status,0,p.stderr||p.stdout);const value=JSON.parse(p.stdout);assert.equal(value.status,expect);assert.deepEqual(value.unsupported_residue,[]);return value;};
const check=run('check',[],'valid');
const verify=run('verify',['--out',generated],'verified');
assert.equal(check.source_sha256,verify.source_sha256);
const work=fs.mkdtempSync(path.join(os.tmpdir(),'lab-alchlang-ingress-'));
try {
  const js=path.join(work,'js');
  const tsconfig=path.join(work,'tsconfig.json');
  fs.writeFileSync(tsconfig,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',types:[],rootDir:generated,outDir:js},include:[generated+'/**/*.ts']}));
  const compile=spawnSync(process.execPath,[path.join(tsRoot,'bin/tsc'),'--project',tsconfig],{encoding:'utf8',cwd:work,maxBuffer:8e6});
  assert.equal(compile.status,0,compile.stderr||compile.stdout);
  fs.writeFileSync(path.join(js,'package.json'),'{}\n');
  const lib=(folder,name)=>require(path.join(js,'application/features/lab/src',folder,name+'.js'));
  const rule=lib('domain/rules','eligible-submission').ruleEligibleSubmission;
  const query=lib('application/queries','find-eligible-submission').queryFindEligibleSubmission;
  const operation=lib('application/operations','submit-submission').operationSubmitSubmission;
  assert.equal(rule({submission:{id:'7',accepted:true}}),true);
  assert.equal(rule({submission:{id:'7',accepted:false}}),false);
  assert.throws(()=>rule({submission:{id:'7',accepted:'true'}}));
  assert.equal(query([{id:'7',accepted:false}],{}),null);
  assert.deepEqual(query([{id:'7',accepted:true}],{}),{id:7n,accepted:true});
  assert.throws(()=>query([{id:'7',accepted:true},{id:'8',accepted:true}],{}),/QUERY_CARDINALITY/);
  const observations=[];
  for(const scenario of ['committed','guard-refused','missing','commit-rejected','commit-uncertain','invalid-input']){
    const calls=[],batches=[];
    const store={begin:async()=>{calls.push('begin');return {
      read:async request=>{calls.push('read');assert.deepEqual(request,{slot:'lab:submission',target:'lab:submission',key:7n});return scenario==='missing'?null:{id:'7',accepted:scenario!=='guard-refused'};},
      commit:async batch=>{calls.push('commit');if(scenario==='commit-uncertain')throw Error('unknown settlement');if(scenario==='commit-rejected')return {status:'rejected'};batches.push(batch);return {status:'committed'};},
      rollback:async()=>{calls.push('rollback');},
    };}};
    const outcome=await operation({request:{id:scenario==='invalid-input'?'-1':'7',accepted:false}},{store,clocks:{}});
    const expected={committed:['committed',undefined,undefined],'guard-refused':['rejected','guard','RULE_REJECTED:lab:eligible-submission'],missing:['failed','read','READ_NOT_FOUND'],'commit-rejected':['rejected','commit','COMMIT_REJECTED'],'commit-uncertain':['indeterminate','commit','COMMIT_UNCERTAIN'],'invalid-input':['failed','input','OPERATION_INPUT']}[scenario];
    assert.deepEqual([outcome.status,outcome.stage,outcome.code],expected);
    assert.equal(batches.length,scenario==='committed'?1:0);
    if(scenario==='committed')assert.deepEqual(batches[0],{writes:[{slot:'lab:submission',target:'lab:submission',mode:'replace',value:{id:7n,accepted:false}}],events:[]});
    observations.push({scenario,status:outcome.status,calls,committed_batches:batches.length});
  }
  const again=run('verify',['--out',generated],'verified');
  assert.equal(again.manifest_sha256,verify.manifest_sha256);
  const summary={status:'pass',source_sha256:check.source_sha256,inputs_sha256:check.inputs_sha256,manifest_sha256:verify.manifest_sha256,package_version:require(path.join(consumer,'node_modules/@cyberalchemy/alchlang/package.json')).version,typescript_version:'6.0.3',nodes:check.nodes,generated_artifacts:check.generated_artifacts,observations,authority_effect:'none',actual_issuer:false,durable_store:false,host_effect:false};
  fs.writeFileSync(path.join(root,'RUN.json'),JSON.stringify(summary,null,2)+'\n');
  console.log(JSON.stringify(summary));
} finally {fs.rmSync(work,{recursive:true,force:true});}
