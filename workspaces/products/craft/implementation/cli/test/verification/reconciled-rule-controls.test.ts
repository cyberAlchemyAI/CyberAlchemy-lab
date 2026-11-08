import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
import {createRuleFacts} from '../../src/verification/reconciled-rule-facts.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const scalar=(name:string)=>({kind:'scalar',name}),named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:unknown)=>({kind,element});
const p=(root:string,properties:string[]=[])=>({op:'path',root,properties}),lit=(type:string,value:unknown)=>({op:'literal',type,value}),eq=(left:unknown,right:unknown)=>({op:'eq',left,right});
function fixture(t:any,impossible=false,moduleRoot='domain',representative=false,comprehensive=false){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-record-witness-')),source=path.join(root,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const rule=(id:string,parameters:unknown[],expression:unknown)=>node(id,'Rule',{description:id,predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+id.toUpperCase(),parameters,expression}});
 rule('allowed',[{name:'value',type:scalar('String')}],eq(p('value'),lit('String','approved')));
 rule('nonempty',[{name:'value',type:scalar('String')}],{op:'not',term:eq(p('value'),lit('String',''))});
 rule('budget',[{name:'amount',type:scalar('UInt64')},{name:'approved',type:scalar('Bool')}],impossible?eq(lit('Bool',true),lit('Bool',false)):{op:'all',terms:[{op:'lt',left:lit('UInt64','0'),right:p('amount')},eq(p('approved'),lit('Bool',true))]});
 const pred=eq(p('item'),lit('String','approved')),self=eq(p('item'),p('item'));
 rule('customer-valid',[{name:'tags',type:wrap('list',scalar('String'))},{name:'credit',type:named('money')},{name:'label',type:scalar('String')}],{op:'all',terms:[
  {op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'value',value:p('label')}]},
  {op:'lt',left:lit('UInt64','0'),right:p('credit',['TEST-MONEY#amount'])},
  {op:'contains',left:p('tags'),right:lit('String','approved')},
  {op:'unique',binding:'item',collection:p('tags'),where:self},
  {op:'exactly_one',binding:'item',collection:p('tags'),where:pred},
  {op:'exists',binding:'item',collection:p('tags'),where:pred},
  {op:'any',terms:[eq(p('label'),lit('String','other')),eq(p('label'),lit('String','approved'))]},
  {op:'set_equal',left:{op:'to_set',value:p('tags')},right:{op:'to_set',value:p('tags')}}
 ]});
 const record=(id:string,kind:string,fields:[string,any][],invariants:string[]=[])=>node(id,kind,{description:id,fields:fields.map(([name])=>name),...(invariants.length?{invariant_refs:invariants}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-'+id.toUpperCase(),properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-'+id.toUpperCase()+'#'+name,identity:kind==='Entity'&&name==='id',cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name}))}});
 record('money','Value Object',[['amount',scalar('UInt64')],['approved',scalar('Bool')]],['alpha:budget']);
 record('customer','Entity',[['id',scalar('String')],['label',scalar('String')],['credit',named('money')],['tags',wrap('list',scalar('String'))],['note',wrap('optional',scalar('String'))]]);
 node('choice','Enum',{description:'Owned business payloads',values:['None','Customer','Money','Customers','CustomerSet','Optional'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-CHOICE',variants:[['None',null],['Customer',named('customer')],['Money',named('money')],['Customers',wrap('list',named('customer'))],['CustomerSet',wrap('set',named('customer'))],['Optional',wrap('optional',named('customer'))]].map(([name,payload])=>({name,payload,ontology_variant:'TEST-CHOICE#'+name}))}});
 if(representative)rule('first-customer',[{name:'customers',type:wrap('list',named('customer'))}],{op:'exists',binding:'item',collection:{op:'to_set',value:p('customers')},where:eq(p('item',['TEST-CUSTOMER#label']),lit('String','approved'))});

 if(comprehensive){
  const variants=[{name:'Off',payload:null,ontology_variant:'TEST-SIGNAL#off'},{name:'On',payload:scalar('UInt64'),ontology_variant:'TEST-SIGNAL#on'}];
  node('signal','Enum',{description:'Exact signal',values:['Off','On'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-SIGNAL',variants}});
  rule('signal-equal',[{name:'left',type:named('signal')},{name:'right',type:named('signal')}],eq(p('left'),p('right')));
  for(const [id,type] of [['optional-equal',wrap('optional',scalar('String'))],['inline-equal',{kind:'sum',variants:[{name:'Empty',payload:null,ontology_variant:'TEST-INLINE#empty'},{name:'Value',payload:scalar('String'),ontology_variant:'TEST-INLINE#value'}]}]] as [string,any][])rule(id,[{name:'left',type},{name:'right',type}],eq(p('left'),p('right')));
  for(const [id,type] of [['entity-equal',named('customer')],['value-equal',named('money')],['sum-equal',named('choice')],['string-order',scalar('String')]] as [string,any][]){
   rule(id,[{name:'left',type},{name:'right',type}],id==='string-order'?{op:'lt',left:p('left'),right:p('right')}:eq(p('left'),p('right')));
  }
  for(const kind of ['list','set'])rule(kind+'-image',[{name:'customers',type:wrap(kind,named('customer'))}],{op:'exactly_one',binding:'item',collection:p('customers',['TEST-CUSTOMER#label']),where:eq(p('item'),p('item'))});
 }
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'record-witness',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:[]});
 const selection={...publicSelection(),module_root:moduleRoot,factories:[
  {selector:'alpha:money',base_validators:[{rule:'alpha:budget',arguments:[{parameter:'amount',field:'amount'},{parameter:'approved',field:'approved'}]}],extensions:[]},
  {selector:'alpha:customer',base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',field:'id'}]},{rule:'alpha:budget',arguments:[{parameter:'amount',path:['credit','amount']},{parameter:'approved',path:['credit','approved']}]},{rule:'alpha:customer-valid',arguments:[{parameter:'tags',field:'tags'},{parameter:'credit',field:'credit'},{parameter:'label',field:'label'}]}],extensions:[]}
 ],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}

test('standalone Rules use structural facts even when every factory witness fails',t=>{
 const f=fixture(t,true,'domain',true),controls=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(controls.node_count,8);
 const rules=controls.rows.filter(r=>r.kind==='Rule');assert.equal(rules.length,5);
 for(const row of rules){
  assert.equal(row.state,'ready',(row as any).reason);assert.ok('recipes' in row);
  assert.equal(row.adapter,'rule');assert.ok(row.cases.length>0);
  const ref=(r:any,parent:number)=>{assert.equal(r.tag,'ref');assert.match(r.value,/^(0|[1-9][0-9]*)$/);assert.ok(Number(r.value)<parent,'recipe edges point to earlier nodes');};
  row.recipes.forEach((r,index)=>{for(const child of [r.base,r.input,r.payload,...(r.items??[]),...Object.values(r.fields??{})])if(child)ref(child,index);});
  for(const c of row.cases){assert.equal(c.values.length,1);assert.ok(Number(c.values[0])<row.recipes.length);}
 }
 assert.equal(controls.ready_count,5,JSON.stringify(controls.rows.map(r=>({selector:r.selector,state:r.state,...('reason' in r?{reason:r.reason}:{})}))));
 assert.equal(controls.not_evaluable_count,3);
 const budget=rules.find(r=>r.selector==='alpha:budget') as any;
 assert.ok(budget.cases.some((c:any)=>c.expected.kind==='value'));assert.ok(budget.cases.filter((c:any)=>c.expected.kind==='value').every((c:any)=>c.expected.value==='false'));
 const facts=createRuleFacts(f.graph,'alpha:first-customer'),values=facts.samples(named('customer') as any);
 assert.ok(values.some(r=>r.fields!.label!.value!=='approved'),'factory-rejected label remains a lawful structural fact');
 const row=rules.find(r=>r.selector==='alpha:first-customer') as any;
 assert.ok(row.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value==='true'));
 assert.ok(row.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value==='false'));
 assert.ok(row.module_paths.every((p:string)=>p.includes('/rules/')),'Rule adapter has no factory dependency');
 const moved=fixture(t,true,'elsewhere/source',true),other=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const r of rules){const relocated=other.rows.find(n=>n.selector===r.selector) as any;assert.deepEqual(relocated.cases,(r as any).cases);assert.deepEqual(relocated.recipes,(r as any).recipes);}
});
test('native standalone Rule controls do not construct factory-owned records',t=>{
 const f=fixture(t,true,'domain',true),n=nativeContext(f);
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'not_evaluable',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 assert.equal(semantic.evidence.tested_node_count,5);assert.equal(semantic.evidence.remaining.length,3);
 assert.ok(semantic.evidence.tested.every((n:any)=>n.kind==='Rule'));assert.equal(report.checks.find((c:any)=>c.id==='semantic-workspace-currentness').result,'pass');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});

test('Rule source cases preserve identity versus value, String order, sum tags and list versus set images',t=>{
 const f=fixture(t,true,'domain',true,true),controls=createReconciledSemanticControls(f.graph,f.plan),rules=controls.rows.filter(r=>r.kind==='Rule');
 assert.equal(controls.node_count,18);assert.equal(rules.length,14);
 for(const row of rules)if(row.selector==='alpha:sum-equal'){assert.equal(row.state,'not_evaluable');assert.match((row as any).reason,/bounded Rule (case capacity|vector expansion|fact expansion|serialized case capacity)/);assert.equal('cases' in row,false);}else assert.equal(row.state,'ready',row.selector+':'+(row as any).reason);
 for(const id of ['entity-equal','value-equal','signal-equal','optional-equal','inline-equal','string-order','list-image','set-image']){
  const row=rules.find(r=>r.selector==='alpha:'+id) as any;
  assert.ok(row.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value==='true'),id+' has true witness');
  assert.ok(row.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value==='false'),id+' has false witness');
 }
 const facts=createRuleFacts(f.graph,'alpha:set-image'),rows=facts.samples(wrap('set',named('customer')) as any);
 assert.ok(rows.some(r=>r.items!.length===2&&r.items![0]!.fields!.label!.value===r.items![1]!.fields!.label!.value),'distinct identities can have the same projected value');
 const n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'not_evaluable',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));assert.equal(semantic.evidence.tested_node_count,14);assert.equal(semantic.evidence.remaining.length,4);
});

test('syntax-valid Rule semantic mutants and late drift cannot produce passing evidence',t=>{
 const f=fixture(t,true,'domain',true,true);
 const manifestPath=path.join(f.source,'specs/alpha/feature.json'),manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));manifest.nodes.push('forwarded');
 fs.writeFileSync(manifestPath,JSON.stringify(manifest)+'\n');
 fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/forwarded.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'forwarded',kind:'Rule',body:{description:'Explicit Rule reference',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-FORWARDED',parameters:[{name:'value',type:scalar('String')}],expression:{op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'value',value:p('value')}]}}}})+'\n');
 const n=nativeContext(f);
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 const targets={predicate:'allowed',reference:'forwarded',identity:'entity-equal',value:'value-equal',exact:'signal-equal',first:'first-customer',list:'list-image',set:'set-image',sum:'signal-equal',getter:'allowed',mutation:'allowed',error:'allowed',carrier:'allowed',late:'allowed'};
 for(const mode of Object.keys(targets)){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated Rule controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain/rules'),file=path.join(folder,targets[mode]+'.js'),old=fs.readFileSync(file,'utf8');
    let changed=old;
    if(mode==='predicate')changed=old.replace('return (ruleString.key(p0) === ruleString.key("approved"));','return false;');
    if(mode==='carrier')changed=old.replace('return (ruleString.key(p0) === ruleString.key("approved"));','return "false";');
    if(mode==='reference')changed=old.replace(/dependency0\\(\\{[^\\n]*\\}\\)/,'false');
    if(mode==='identity')changed=old.replace('ruleString.key(value["id"])','ruleString.key(value["label"])');
    if(mode==='value')changed=old.replace('ruleUInt64.key(value["amount"])','ruleUInt64.key(0n)');
    if(mode==='exact')changed=old.replace('return value;','return BigInt(Number(value));');
    if(mode==='first')changed=old.replace('if (!rows.has(key))','if (true)');
    if(mode==='list')changed=old.replace('if (unique)','if (true)');
    if(mode==='set')changed=old.replace('if (new Set(rows.map(row => row.key)).size !== rows.length)','if (false)');
    if(mode==='sum')changed=old.replace(/rulePart\\(protocol.key\\(.*?\\)\\)\\)/,'rulePart("lost-payload")');
    if(mode==='getter')changed=old.replace('const descriptors = Object.getOwnPropertyDescriptors(input);','for(const key of Object.keys(input)) void input[key]; const descriptors = Object.getOwnPropertyDescriptors(input);');
    if(mode==='mutation')changed=old.replace('const descriptors = Object.getOwnPropertyDescriptors(input);','Object.freeze(input); const descriptors = Object.getOwnPropertyDescriptors(input);');
    if(mode==='error')changed=old.replace("TypeError('RULE_INPUT')","TypeError('INVALID_COMPONENT')");
    if(changed===old)throw Error('Rule mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});
    if(syntax.error||syntax.status!==0)throw Error('Rule mutant must remain syntactically valid:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/rules/allowed.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 assert.deepEqual(reports.filter(({mode,report}:any)=>mode!=='late'&&report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls').result!=='fail').map(({mode,report}:any)=>{const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');return {mode,result:semantic.result,reason:semantic.reason};}),[],'every compiling mutant must fail semantic observation');
 for(const {mode,report} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');assert.ok(semantic.blocked_by.includes('semantic-workspace-currentness'));}
  else {assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.match(semantic.reason,/observation mismatch/);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});
function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici = path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
