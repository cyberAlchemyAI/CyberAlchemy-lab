import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const exampleRoot=path.dirname(fileURLToPath(import.meta.url));
const coreRoot=path.resolve(exampleRoot,'../../..');
const require=createRequire(import.meta.url);

export async function runRuleQuery({output}) {
  assert.ok(path.isAbsolute(output),'output must be an absolute path');
  assert.equal(fs.existsSync(output),false,'output must be absent');
  assert.ok(fs.statSync(path.dirname(output)).isDirectory(),'output parent must exist');
  const typescriptPackage=require.resolve('typescript/package.json');
  const tsc=path.join(path.dirname(typescriptPackage),'bin/tsc');
  assert.equal(JSON.parse(fs.readFileSync(typescriptPackage)).version,'6.0.3');
  const nodeTypes=require.resolve('@types/node/package.json');
  assert.equal(JSON.parse(fs.readFileSync(nodeTypes)).version,'26.4.0');
  fs.mkdirSync(output,{mode:0o700});
  const write=(name,value)=>fs.writeFileSync(path.join(output,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
  const source=path.join(exampleRoot,'model.alch'),generated=path.join(output,'generated');
  const env={...process.env};delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
  const observations=[];
  const command=(name,argv,status)=>{
    const result=spawnSync(process.execPath,[path.join(coreRoot,'dist/core-cli.js'),...argv],{encoding:'utf8',cwd:output,env,maxBuffer:32*1024*1024});
    write(name+'.json',{status:result.status,stdout:result.stdout,stderr:result.stderr});
    assert.equal(result.status,0,result.stderr||result.stdout);
    const value=JSON.parse(result.stdout);assert.equal(value.status,status);
    assert.deepEqual(value.unsupported_residue,[]);
    observations.push({id:name,result:'pass',status:value.status});
  };
  command('check',[ 'check',source ],'valid');
  command('build',[ 'build',source,'--out',generated ],'built');
  command('verify',[ 'verify',source,'--out',generated ],'verified');
  const js=path.join(output,'js');
  write('tsconfig.json',{compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',types:['node'],typeRoots:[path.dirname(path.dirname(nodeTypes))],rootDir:generated,outDir:js},include:[generated+'/**/*.ts']});
  const compiled=spawnSync(process.execPath,[tsc,'--project',path.join(output,'tsconfig.json')],{encoding:'utf8',cwd:output,maxBuffer:32*1024*1024});
  write('native-compile.json',{status:compiled.status,stdout:compiled.stdout,stderr:compiled.stderr});
  assert.equal(compiled.status,0,compiled.stderr||compiled.stdout);
  fs.writeFileSync(path.join(js,'package.json'),'{"type":"commonjs"}\n',{flag:'wx'});
  observations.push({id:'native-compile',result:'pass',typescript:'6.0.3'});
  const module=(role,name)=>require(path.join(js,'application/features/commerce/src',role,name+'.js'));
  const eligible=module('domain/rules','eligible-order').ruleEligibleOrder;
  const list=module('application/queries','find-eligible-orders').queryFindEligibleOrders;
  const optional=module('application/queries','find-eligible-order').queryFindEligibleOrder;
  const operation=module('application/operations','submit-order').operationSubmitOrder;
  const record=(id,fn)=>{fn();observations.push({id,result:'pass'});};
  const rows=[{id:'18446744073709551615',accepted:true},{id:'2',accepted:false},{id:'3',accepted:true}];
  const one={id:18446744073709551615n,accepted:true};
  record('named-rule-true-false',()=>{
    assert.equal(eligible({order:rows[0]}),true);assert.equal(eligible({order:rows[1]}),false);
    assert.throws(()=>eligible({order:{id:'1',accepted:'true'}}));
  });
  record('named-rule-list-zero-one-many',()=>{
    assert.deepEqual(list([],{}),[]);assert.deepEqual(list([rows[1]],{}),[]);
    assert.deepEqual(list([rows[0]],{}),[one]);assert.deepEqual(list(rows,{}),[one,{id:3n,accepted:true}]);
  });
  record('named-rule-optional-zero-one-many',()=>{
    assert.equal(optional([],{}),null);assert.equal(optional([rows[1]],{}),null);
    assert.deepEqual(optional([rows[0]],{}),one);
    assert.throws(()=>optional(rows,{}),/QUERY_CARDINALITY/);
    assert.throws(()=>optional([rows[0],rows[0]],{}),/QUERY_CARDINALITY/);
  });
  record('named-rule-query-input-and-output-boundaries',()=>{
    assert.throws(()=>list([{id:'-1',accepted:true}],{}));
    assert.throws(()=>list([{id:'1',accepted:'true'}],{}));
    assert.throws(()=>list(rows,{hidden:true}));
    const found=list(rows,{});assert.ok(Object.isFrozen(found));assert.ok(Object.isFrozen(found[0]));
    assert.equal(rows[0].id,'18446744073709551615');
  });
  const projected=JSON.parse(fs.readFileSync(path.join(generated,'.alch/project/specs/commerce/nodes/find-eligible-order.json'))).body.typed_contract;
  record('named-rule-projection-exact-meaning',()=>{
    assert.deepEqual(projected.filter,{op:'eq',left:{kind:'field',name:'accepted'},right:{kind:'literal',type:'Bool',value:true}});
    assert.equal(projected.result_cardinality,'optional');assert.equal(projected.limit,null);
    assert.deepEqual(projected.projection,['id','accepted']);
  });
  for(const scenario of ['success','guard-rejection','missing','read-failure','commit-rejection','commit-uncertain','malformed']) {
    const calls=[],committed=[];
    const store={begin:async()=>{calls.push('begin');return {
      read:async request=>{calls.push('read');assert.deepEqual(request,{slot:'commerce:order',target:'commerce:order',key:1n});if(scenario==='read-failure')throw Error('read failed');return scenario==='missing'?null:{id:'1',accepted:scenario!=='guard-rejection'};},
      commit:async batch=>{calls.push('commit');if(scenario==='commit-uncertain')throw Error('unknown settlement');if(scenario==='commit-rejection')return {status:'rejected'};committed.push(batch);return {status:'committed'};},
      rollback:async()=>{calls.push('rollback');},
    };}};
    const outcome=await operation({request:{id:scenario==='malformed'?'-1':'1',accepted:scenario!=='success'}},{store,clocks:{}});
    if(scenario==='success') {
      assert.equal(outcome.status,'committed');assert.deepEqual(outcome.value,{id:1n,accepted:false});
      assert.deepEqual(calls,['begin','read','commit']);
      assert.deepEqual(committed,[{writes:[{slot:'commerce:order',target:'commerce:order',mode:'replace',value:{id:1n,accepted:false}}],events:[]}]);
    } else {
      const expected={
        'guard-rejection':['rejected','guard','RULE_REJECTED:commerce:eligible-order'],
        missing:['failed','read','READ_NOT_FOUND'],'read-failure':['failed','read','OPERATION_FAILED'],
        'commit-rejection':['rejected','commit','COMMIT_REJECTED'],'commit-uncertain':['indeterminate','commit','COMMIT_UNCERTAIN'],
        malformed:['failed','input','OPERATION_INPUT'],
      }[scenario];
      assert.deepEqual([outcome.status,outcome.stage,outcome.code],expected);assert.equal(committed.length,0);
      assert.equal(outcome.continuation,'return-submission-error');
      assert.deepEqual(calls,scenario==='malformed'?[]:scenario.startsWith('commit-')?['begin','read','commit']:['begin','read','rollback']);
    }
    observations.push({id:'read-bound-operation-'+scenario,result:'pass',calls,status:outcome.status,committed_batches:committed.length});
  }
  command('verify-after-runtime',['verify',source,'--out',generated],'verified');
  const summary={schema_version:'alchlang.named-rule-query-operation-journey/v1-candidate',result:'pass',profile:'application-v1',native_profile:'domainspec.reconciled-typescript/v1-candidate',observations,
    scope:'named Rule Query projection and supplied rows; read-bound Operation with explicit in-memory transaction mock',formal_proof:false,durable_runtime_claim:false,authority_effect:'none'};
  write('summary.json',summary);return summary;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2);
  if(args.length===1&&args[0]==='--help'){console.log('Usage: node run.mjs --output <new-absolute-directory>');}
  else {assert.equal(args.length,2);assert.equal(args[0],'--output');console.log(JSON.stringify(await runRuleQuery({output:args[1]}),null,2));}
}
