import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync,cpSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkflowExpressionOwnerV1,CommerceWorkflowExpressionErrorV1} from '../../src/commerce/commerce-workflow-expression-v1.js';
import {createCommerceWorkflowBranchSelectionOwnerV1,assertCommerceWorkflowBranchSelectionOwnerV1}
 from '../../src/commerce/commerce-workflow-branch-selection-v1.js';
import {projectCommerceWorkflowValueToNativeV1,CommerceWorkflowValueNativeErrorV1}
 from '../../src/commerce/commerce-workflow-value-native-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
const code=(name:string)=>(error:unknown)=>error instanceof CommerceWorkflowExpressionErrorV1&&error.code===name;

test('checked Workflow expression paths evaluate inert data and require exact native producer callsites',async()=>{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(row=>row.path)),
  texts=captured.files.filter(row=>paths.has(row.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
  stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch'),
  domain=createCommerceComputationDomainOwner(stage,source),
  limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,
  baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits)),
  binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
 const owner=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
 try{
  const confirmed=owner.bind('$.terminals[0].guard'),cancelled=owner.bind('$.terminals[1].guard');
  assert.equal(owner.evaluate(confirmed,{Orders:{Order:{status:'Confirmed'},
   CheckoutProgress:{state:'Confirmed'}}}),true);
  assert.equal(owner.evaluate(confirmed,{Orders:{Order:{status:'Confirmed'},
   CheckoutProgress:{state:'Cancelling'}}}),false);
  assert.equal(owner.evaluate(cancelled,{Orders:{Order:{status:'Cancelled'},
   CheckoutProgress:{state:'Cancelled'}}}),true);
  const orderIdPath='$.steps[0].call.arguments[0].value';
  assert.ok(owner.paths().includes(orderIdPath));
  const orderId=owner.bind(orderIdPath),view=owner.inspect(orderId);
  assert.equal(view.workflow,'Orders.Checkout.Checkout');
  assert.equal(view.path,orderIdPath);
  assert.deepEqual(view.callsites,[]);
  assert.equal(view.authority_effect,'none');
  assert.equal(owner.evaluate(orderId,{snapshot:{order:{id:'order-one'}}}),'order-one');
  assert.throws(()=>owner.bind('$.steps[999].call.arguments[0].value'),code('UnknownReference'));
  assert.throws(()=>owner.inspect({...orderId}),code('ForeignOwner'));
  assert.throws(()=>owner.evaluate(orderId,new Proxy({snapshot:{order:{id:'order-one'}}},{})),code('InputType'));

  const fingerprintPath='$.steps[1].call.arguments[2].value';
  const fingerprint=owner.bind(fingerprintPath),sites=owner.inspect(fingerprint).callsites;
  assert.equal(sites.length,1);
  assert.equal(sites[0]!.kind,'native');
  assert.equal(sites[0]!.method,'stockCommandFingerprint');
  assert.equal(sites[0]!.path,fingerprintPath+'.expression');
  const env={snapshot:{order:{id:'order-one',lines:[]},progress:{reserveCommandId:'command-one'}}};
  assert.throws(()=>owner.evaluate(fingerprint,env),code('ProducerRequired'));
  const seen:string[]=[];
  const result=owner.evaluate(fingerprint,env,{native:(site,args)=>{
   seen.push(site.path);
   assert.equal(site.method,'stockCommandFingerprint');
   assert.equal(site.abi,'craft.commerce-identity/v1-candidate');
   assert.deepEqual(args,['reserve','order-one',[],{kind:'none'}]);
   return 'a'.repeat(64);
  }});
  assert.equal(result,'a'.repeat(64));
  assert.deepEqual(seen,[fingerprintPath+'.expression']);

  const local=owner.bind('$.steps[2].observe'),localType=owner.inspect(local).result,
   flowValue=owner.evaluate(local,{snapshot:{progress:{captureAttemptKey:'attempt-one'}}}),
   native=projectCommerceWorkflowValueToNativeV1(flowValue,localType,
    domain.inspect(baseline).contract.values);
  assert.deepEqual(native,{kind:'CaptureDispatched',attemptKey:'attempt-one'});
  assert.throws(()=>projectCommerceWorkflowValueToNativeV1(
   {...flowValue as object,unexpected:true},localType,domain.inspect(baseline).contract.values),
   CommerceWorkflowValueNativeErrorV1);
 }finally{owner.dispose();semantics.dispose(semantic);sources.dispose(capture);}
});

test('source-checked map, filter, fold, match variant and stable multi-key sort evaluate inert data',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-workflow-expression-'));
 try{
  cpSync(candidate,root,{recursive:true});
  const workflowFile=path.join(root,'workflows/checkout.alch');
  const original=readFileSync(workflowFile,'utf8');
  const expression='sort(filter(map(snapshot.order.lines,line:StockLine => line),line:StockLine => line.quantity > 1),line:StockLine => [line.sku ascending binary-utf8,line.quantity descending numeric])';
  assert.ok(original.includes('input lines <- snapshot.order.lines'));
  writeFileSync(workflowFile,original.replace('use Shop.Values.Identifier, WorkerContext, IdentityProducers',
   'use Shop.Values.Identifier, WorkerContext, IdentityProducers, StockLine')
   .replace('input lines <- snapshot.order.lines','input lines <- '+expression)
   .replace('require snapshot.order.id == placed.orderId',
    'require snapshot.order.id == placed.orderId and fold(snapshot.order.lines,0,total:UInt64,line:StockLine => total + line.quantity) > 0 and (match snapshot.order.status AwaitingStock => true else false)'));
  const identityFile=path.join(root,'contracts/contract-identities.json'),identities=JSON.parse(readFileSync(identityFile,'utf8'));
  const artifact=identities.modules.find((row:{artifact:{path:string}})=>row.artifact.path==='workflows/checkout.alch').artifact;
  const bytes=readFileSync(workflowFile);artifact.sha256=createHash('sha256').update(bytes).digest('hex');artifact.bytes=bytes.length;
  writeFileSync(identityFile,JSON.stringify(identities,null,2)+'\n');
  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root),captured=sources.inspect(capture);
  const paths=new Set(captured.reconstruction.modules.map(row=>row.path)),texts=captured.files.filter(row=>paths.has(row.path));
  const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
   stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(root,'application.alch'),
   domain=createCommerceComputationDomainOwner(stage,source),
   limits=JSON.parse(readFileSync(path.join(root,'contracts/compute-bounds.json'),'utf8')).computation.limits,
   baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits)),
   binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout'),
   owner=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
  let branch:ReturnType<typeof createCommerceWorkflowBranchSelectionOwnerV1>|undefined,stale=false;
  try{
   const handle=owner.bind('$.steps[0].call.arguments[2].value');
   assert.equal(owner.inspect(handle).callsites.length,0);
   const rows=[{sku:'sku-2',quantity:2n},{sku:'sku-10',quantity:1n},{sku:'sku-1',quantity:2n},
    {sku:'sku-1',quantity:3n}];
   assert.deepEqual(JSON.parse(JSON.stringify(owner.evaluate(handle,{snapshot:{order:{lines:rows}}}),
    (_name,value)=>typeof value==='bigint'?String(value):value)),
    [{sku:'sku-1',quantity:'3'},{sku:'sku-1',quantity:'2'},{sku:'sku-2',quantity:'2'}]);
   const guard=owner.bind('$.drivers[0].guard');
   assert.equal(owner.evaluate(guard,{snapshot:{order:{id:'order-one',status:'AwaitingStock',lines:rows}},placed:{orderId:'order-one'}}),true);
   assert.equal(owner.evaluate(guard,{snapshot:{order:{id:'order-one',status:'AwaitingStock',lines:[]}},placed:{orderId:'order-one'}}),false);
   assert.equal(owner.evaluate(guard,{snapshot:{order:{id:'order-one',status:'Cancelled',lines:rows}},placed:{orderId:'order-one'}}),false);
   branch=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
   assertCommerceWorkflowBranchSelectionOwnerV1(branch);
   assert.throws(()=>assertCommerceWorkflowBranchSelectionOwnerV1({...branch} as any),
    (error:any)=>error?.code==='ForeignOwner');
   stale=true;
   writeFileSync(workflowFile,readFileSync(workflowFile,'utf8')+'\n');
   const staleSource=(error:any)=>error?.diagnostics?.[0]?.code==='StaleOwner'||error?.code==='StaleOwner';
   assert.throws(()=>owner.assertCurrent(),staleSource);
   assert.throws(()=>branch!.assertCurrent(),staleSource);
  }finally{if(!stale){branch?.dispose();owner.dispose();semantics.dispose(semantic);sources.dispose(capture);}}
 }finally{rmSync(root,{recursive:true,force:true});}
});
