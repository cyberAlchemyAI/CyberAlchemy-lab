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
import {STATE_MACHINE_EFFECT_AUDIT_RUNNER} from '../../src/verification/reconciled-state-machine-effect-audit.ts';
import {sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const field=(field_id:string,name:string,required=true)=>({field_id,type_ref:{kind:'primitive',name},required});
const ref=(field_id:string,selector:string)=>({field_id,type_ref:{kind:'reference',selector},required:true});
function fixture(t:any,moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-event-controls-')),source=path.join(temp,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 node('valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-VALID',parameters:[{name:'value',type:{kind:'scalar',name:'String'}}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}});
 for(const [id,kind,name]of [['record','Entity','id'],['value','Value Object','code']]){
  node(id! ,kind!,{fields:[name],...(kind==='Value Object'?{invariant_refs:['alpha:valid']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-'+id!.toUpperCase(),properties:[{name,type:{kind:'scalar',name:'String'},ontology_property:'TEST-'+id!.toUpperCase()+'#'+name,meaning:name,identity:kind==='Entity',cardinality:'one'}]}});
 }
 node('status','Enum',{values:['Ready','Closed'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:['Ready','Closed'].map(name=>({name,ontology_variant:'TEST-STATUS#'+name,payload:null}))}});
 const bodies:any={};
 for(const [id,policy]of [['supplied','required'],['clocked','generated'],['empty','required']]){
  const body={event_type:id,version:'2',occurrence_id:field('occurrence-id',id==='empty'?'integer':'uuid'),occurred_at_policy:policy,payload:id==='empty'?[]:[field('amount','integer'),field('ratio','decimal'),field('enabled','boolean'),field('label','string'),field('time','timestamp'),field('uuid','uuid'),field('note','string',false),ref('entity','alpha:record'),ref('value','alpha:value'),ref('status','alpha:status'),ref('previous','alpha:'+id)]};
  bodies[id!]=body;node(id!,'Event',body);
 }
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'event-controls',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:[]});};save();
 const selection={...publicSelection(moduleRoot),factories:[['record','id'],['value','code']].map(([id,name])=>({selector:'alpha:'+id,base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:name}]}],extensions:[]})),operations:[]};
 const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,root:temp,source,selection,graph,plan,node,save,bodies};
}
test('Event controls preserve explicit time, occurrence, signed values, optional absence and reference-only closures',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),rows=controls.rows.filter(r=>r.kind==='Event') as any[];
 assert.equal(rows.length,3);assert.equal(controls.node_count,f.graph.nodes.length);assert.equal(controls.not_evaluable_count,0);
 for(const row of rows){
  assert.equal(row.state,'ready');assert.equal(row.module_paths.length,2);assert.ok(row.module_paths.every((p:string)=>p.includes('/events/')));
  assert.deepEqual(row.native_imports.map((r:any)=>r.relative_path),row.module_paths);assert.ok(Object.isFrozen(row.cases));
  const cases=row.cases.filter((c:any)=>c.mode==='event'),outcomes=cases.map((c:any)=>JSON.parse(c.expected.value)),recipes=cases.map((c:any)=>JSON.parse(c.values[0]));
  assert.equal(row.cases[0].mode,'event-descriptor');assert.equal(JSON.parse(row.cases[0].expected.value).occurrence_registration,false);
  assert.ok(outcomes.some((o:any)=>o.result.kind==='value'&&o.result.values.length===2&&o.result.fresh));
  assert.ok(outcomes.some((o:any)=>o.result.kind==='error'&&o.clock_calls===0));
  if(row.selector==='alpha:clocked'){
   assert.ok(outcomes.some((o:any)=>o.clock_calls===1&&o.result.same_clock_error===true));
   assert.ok(outcomes.some((o:any)=>o.clock_calls===1&&o.result.name==='TypeError'));
  }else assert.ok(outcomes.every((o:any)=>o.clock_calls===0));
  if(row.selector!=='alpha:empty')assert.ok(recipes.some((r:any)=>!Object.hasOwn(r.input.payload,'note')));
 }
 const moved=fixture(t,'moved/native'),other=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const row of rows)assert.deepEqual(row.cases,(other.rows.find(r=>r.selector===row.selector) as any).cases);
 assert.equal(sha256(STATE_MACHINE_EFFECT_AUDIT_RUNNER),'3886564a2d7be63ba192845540abd106a5ccf41c67b737dacee1c06f5a9cf0e7','shared parser extraction preserves State Machine observer bytes');
});
test('native Event controls and effect audits pass with complete independent accounting',t=>{
 const f=fixture(t),n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',semantic.reason);assert.equal(semantic.evidence.tested_node_count,f.graph.nodes.length);assert.deepEqual(semantic.evidence.remaining,[]);
 for(const phase of ['source','native']){
  const audit=check('event-'+phase+'-effect-audit');assert.equal(audit.result,'pass',audit.reason);assert.equal(audit.evidence.phase,phase);assert.equal(audit.evidence.module_count,6);
  assert.deepEqual(audit.evidence.selectors,['alpha:clocked','alpha:empty','alpha:supplied']);assert.ok(audit.evidence.modules.every((m:any)=>m.relative_path.includes('/events/')));
 }
 for(const id of ['event-effect-audit-currentness','semantic-workspace-currentness','verification-workspace-cleanup'])assert.equal(check(id).result,'pass',id);
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('compiling Event semantic mutations, forbidden dependencies and late drift cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f),reports:any[]=[];
 const modes=['bind-callable','bind-claim','bind-source','bind-reference','bind-getter','bind-cycle','type','version','occurrence','time','amount','ratio','optional','root-freeze','payload-freeze','occurrence-freeze','alias','mutation','range','error','clock-twice','clock-ignored','clock-early','clock-coerce','clock-error','dedup','getter','static-import','caught-import','global','source-global','late'];
 for(let offset=0;offset<modes.length;offset+=2){
  const batch=modes.slice(offset,offset+2);
  const observed=n.run(`import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ${JSON.stringify(batch)}){
  let nativeCalls=0,getterValueMismatches=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated Event controls'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1];
   if(mode==='source-global'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/domain/events/supplied.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&!['source-global','late'].includes(mode)){
    const folder=path.join(path.dirname(config),'modules/domain/features/alpha/src/domain/events'),file=path.join(folder,mode.startsWith('bind-')?'supplied.js':(mode.startsWith('clock-')?'clocked':'supplied')+'.provider.js'),old=fs.readFileSync(file,'utf8');let changed=old;
    if(mode==='bind-callable')changed=old.replace('Object.freeze(Object.assign(make,','Object(Object.assign(make,');
    if(['bind-claim','bind-source','bind-reference'].includes(mode)){
     const cases=JSON.parse(fs.readFileSync(path.join(path.dirname(config),'cases.json'),'utf8')),descriptor=JSON.parse(cases.rows.find(r=>r.selector==='alpha:supplied').cases.find(c=>c.mode==='event-descriptor').expected.value);
     if(mode==='bind-claim')descriptor.publication=true;
     if(mode==='bind-source')descriptor.contract_sha256='0'.repeat(64);
     if(mode==='bind-reference')descriptor.references[0].body_sha256='0'.repeat(64);
     delete descriptor.descriptor_sha256;
     const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
     descriptor.descriptor_sha256=createHash('sha256').update(canonical(descriptor)).digest('hex');
     changed='import {make} from "./supplied.provider.js";const freeze=v=>{if(v&&typeof v==="object"){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};export const eventSupplied=Object.freeze(Object.assign(make,{descriptor:freeze('+JSON.stringify(descriptor)+')}));';
    }
    if(mode==='bind-getter')changed='import {make} from "./supplied.provider.js";let reads=0;const construct=(...args)=>{const v=make(...args);if(reads)throw new Error("DESCRIPTOR_GETTER_READ");return v;};export const eventSupplied=Object.freeze(Object.defineProperty(construct,"descriptor",{enumerable:true,get(){reads++;throw new Error("DESCRIPTOR_GETTER_READ");}}));';
    if(mode==='bind-cycle')changed='import {make} from "./supplied.provider.js";const d={};d.self=d;Object.freeze(d);export const eventSupplied=Object.freeze(Object.assign(make,{descriptor:d}));';
    if(mode==='type')changed=old.replace('type: "supplied"','type: "empty"');
    if(mode==='version')changed=old.replace('version: "2"','version: "3"');
    if(mode==='occurrence')changed=old.replace('eventText(o["occurrence-id"].value)','eventText(p["entity"].value)');
    if(mode==='time')changed=old.replace('eventText(d["occurredAt"].value)','eventText("fixed")');
    if(mode==='amount')changed=old.replace('eventInteger(p["amount"].value)','(eventInteger(p["amount"].value)+1n)');
    if(mode==='ratio')changed=old.replace('eventDecimal(p["ratio"].value)','eventDecimal(1)');
    if(mode==='optional')changed=old.replace('Object.hasOwn(p, "note")','false');
    if(mode==='root-freeze')changed=old.replace('return Object.freeze({ type:','return ({ type:');
    if(mode==='payload-freeze')changed=old.replace('const payload = Object.freeze(','const payload = (');
    if(mode==='occurrence-freeze')changed=old.replace('const occurrence = Object.freeze(','const occurrence = (');
    if(mode==='alias')changed=old.replace('version: "2", occurrence, occurredAt, payload','version: "2", occurrence, occurredAt, payload: Object.freeze(input.payload)');
    if(mode==='mutation')changed=old.replace('const make = (input) => {','const make = (input) => { Object.preventExtensions(input);');
    if(mode==='range')changed=old.replace('return n >= -9223372036854775808n && n <= 9223372036854775807n ? n : eventFail();','return n;');
    if(mode==='error')changed=old.replace('new TypeError("EVENT_INPUT")','new RangeError("EVENT_INPUT")');
    if(mode==='clock-twice')changed=old.replace('eventText(clock())','eventText((clock(),clock()))');
    if(mode==='clock-ignored')changed=old.replace('eventText(clock())','eventText("fixed")');
    if(mode==='clock-early')changed=old.replace('const make = (input, clock) => {','const make = (input, clock) => { clock();');
    if(mode==='clock-coerce')changed=old.replace('eventText(clock())','eventText(String(clock()))');
    if(mode==='clock-error')changed=old.replace('eventText(clock())','eventText((()=>{try{return clock();}catch(e){throw new Error(e.message);}})())');
    if(mode==='dedup')changed='let previous;\\n'+old.replace('const make = (input) => {','const make = (input) => { if(previous)return previous;').replace('return Object.freeze({ type:','return previous = Object.freeze({ type:');
    if(mode==='getter')changed=old.replace('type: "supplied"','get type(){throw new Error("OUTPUT_GETTER_READ");}');
    if(mode==='static-import')changed=old+'\\nimport "./empty.js";\\n';
    if(mode==='caught-import')changed=old+'\\nimport("./empty.js").catch(()=>{});\\n';
    if(mode==='global')changed=old+'\\nObject.defineProperty(globalThis,"eventLeak",{value:1});\\n';
    if(changed===old)throw Error('Event mutant not installed:'+mode+':'+old.slice(-1800));fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Event mutant must compile:'+mode+':'+syntax.stderr);
   }
   if(mode==='bind-getter'&&args.includes('--permission')&&result.status===0){
    const cases=JSON.parse(fs.readFileSync(args.find(a=>String(a).endsWith('/cases.json')),'utf8')).rows.find(r=>r.selector==='alpha:supplied'),observed=JSON.parse(result.stdout).find(r=>r.selector==='alpha:supplied');
    getterValueMismatches=cases.cases.filter(c=>c.mode==='event'&&JSON.stringify(c.expected)!==JSON.stringify(observed.cases.find(o=>o.id===c.id).outcome)).length;
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/events/supplied.provider.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls,getterValueMismatches});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
  assert.deepEqual(observed.map((r:any)=>r.mode),batch,'complete native mutation batch');
  reports.push(...observed);
  t.diagnostic('native mutation batch completed: '+batch.join(', '));
 }
 assert.deepEqual(reports.map(r=>r.mode),modes,'complete ordered mutation coverage');
 for(const {mode,report,nativeCalls,getterValueMismatches}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='source-global'){assert.equal(check('event-source-effect-audit').result,'fail');assert.equal(nativeCalls,0);}
  else if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(check('event-native-effect-audit').result,'not_evaluable');assert.equal(semantic.result,'not_evaluable');}
  else{
   assert.equal(semantic.result,'fail',mode+':'+semantic.reason);
   if(['caught-import','global'].includes(mode)){assert.equal(check('event-native-effect-audit').result,'fail');assert.equal(nativeCalls,0);assert.match(semantic.reason,/EVENT_EFFECT_AUDIT/);}
   else if(mode==='static-import')assert.match(semantic.reason,/EVENT_NATIVE_IMPORT_BOUNDARY/);
   else{assert.ok(nativeCalls>0,mode);assert.match(semantic.reason,/observation mismatch/,mode);}
  }
  if(mode==='bind-getter')assert.equal(getterValueMismatches,0,'descriptor inspection must not execute a getter');
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('Event audit observations and scripts stay bound before execution and after late changes',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-omit','native-phase','native-hash','source-script','native-script','late']){
  let nativeCalls=0,auditScript='';
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for Event audit custody'};
   if(args.includes('--permission'))nativeCalls++;
   const result=original(command,args,settings),script=args.find(a=>String(a).endsWith('/event-effects.mjs'));
   if(script&&result.status===0){
    auditScript=script;const observed=JSON.parse(result.stdout);
    if(mode==='source-omit'&&observed.phase==='source'){observed.modules.pop();result.stdout=JSON.stringify(observed);}
    if(mode==='native-phase'&&observed.phase==='native'){observed.phase='source';result.stdout=JSON.stringify(observed);}
    if(mode==='native-hash'&&observed.phase==='native'){observed.modules[0].source_sha256='0'.repeat(64);result.stdout=JSON.stringify(observed);}
    if(mode===observed.phase+'-script')fs.appendFileSync(script,'\\n// drift\\n');
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(auditScript,'\\n// late drift\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);assert.equal(report.result,'fail',mode);
  if(mode==='late'){assert.ok(nativeCalls>0);assert.equal(check('event-effect-audit-currentness').result,'fail');for(const id of ['event-source-effect-audit','event-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);}
  else{assert.equal(nativeCalls,0,mode);assert.equal(check(mode.startsWith('source')?'event-source-effect-audit':'event-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('Event source audits retain whole unmet Events and ignore literal ambient words',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 const file=path.join(source,'specs/alpha/nodes/clocked.json'),baseline=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const mode of ['literal','capacity','capacity-forbidden']){
  const node=JSON.parse(JSON.stringify(baseline));if(mode!=='literal')node.body.payload=Array.from({length:200},(_,i)=>({field_id:'amount-'+i,type_ref:{kind:'primitive',name:'integer'},required:true}));fs.writeFileSync(file,JSON.stringify(node));let nativeCalls=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for Event audit capacity'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1];
   if(mode==='capacity-forbidden'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/domain/events/clocked.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(mode==='literal'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))fs.appendFileSync(path.join(path.dirname(config),'modules/domain/features/alpha/src/domain/events/clocked.provider.js'),'\\n// class await globalThis Date Promise Function\\nvoid "class await globalThis process Date Math Promise fetch require eval Function setTimeout setInterval queueMicrotask WebSocket";\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),source=check('event-source-effect-audit'),native=check('event-native-effect-audit'),semantic=check('selected-generator-semantic-controls');
  if(mode==='capacity-forbidden'){assert.equal(source.result,'fail');assert.equal(nativeCalls,0);}
  else{
   assert.equal(source.result,'pass',source.reason);assert.equal(source.evidence.module_count,6);assert.deepEqual(source.evidence.selectors,['alpha:clocked','alpha:empty','alpha:supplied']);assert.ok(nativeCalls>0);
   assert.equal(native.result,'pass',native.reason);
   if(mode==='capacity'){
    assert.equal(semantic.result,'not_evaluable');assert.deepEqual(semantic.evidence.remaining.map((r:any)=>r.selector),['alpha:clocked']);assert.match(semantic.evidence.remaining[0].reason,/bounded Event/);
    assert.deepEqual(native.evidence.selectors,['alpha:empty','alpha:supplied']);assert.equal(native.evidence.module_count,4);
    const row=report.semantic_coverage.rows.find((r:any)=>r.selector==='alpha:clocked');assert.equal(row.adapter_status,'not_evaluable');assert.equal(Object.hasOwn(row,'case_count'),false);
   }else{assert.equal(semantic.result,'pass',semantic.reason);assert.equal(native.evidence.module_count,6);}
  }
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('native occurrence fields and optional payloads cover all admitted primitive and reference carriers',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 const file=path.join(source,'specs/alpha/nodes/empty.json'),baseline=JSON.parse(fs.readFileSync(file,'utf8')),names=['string','boolean','integer','decimal','timestamp','uuid','reference'];
 const type=name=>name==='reference'?{kind:'reference',selector:'alpha:record'}:{kind:'primitive',name};
 for(const name of names){
  const node=JSON.parse(JSON.stringify(baseline));node.body.occurrence_id.type_ref=type(name);node.body.payload=names.map(n=>({field_id:'optional-'+n,type_ref:type(n),required:false}));fs.writeFileSync(file,JSON.stringify(node));
  cp.spawnSync=(command,args,settings)=>command===tools.lean_executable?{status:1,stdout:'',stderr:'injected Lean failure for occurrence carriers'}:original(command,args,settings);syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({name,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {name,report}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);assert.equal(check('selected-generator-semantic-controls').result,'pass',name+':'+check('selected-generator-semantic-controls').reason);
  assert.equal(check('event-native-effect-audit').result,'pass',name);assert.equal(check('verification-workspace-cleanup').result,'pass',name);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('Event constructors run with every referenced declaration module poisoned',t=>{
 const f=fixture(t),n=nativeContext(f),result=n.run(`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {execFileSync,spawnSync} from 'node:child_process';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),tools=${JSON.stringify(n.options)},source=path.resolve('products'),output=path.resolve('compiled-products');fs.mkdirSync(source);
 fs.writeFileSync(path.join(source,'package.json'),'{"type":"module"}');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(source,'tsconfig.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:source,outDir:output,types:['node'],typeRoots:[tools.node_type_root]},files:plan.resolved.modules.map(m=>path.join(source,m.relative_path))}));
 execFileSync(process.execPath,[path.join(tools.typescript_root,'bin/tsc'),'--project',config],{encoding:'utf8',timeout:60000});fs.writeFileSync(path.join(output,'package.json'),'{"type":"module"}');
 const referenced=plan.resolved.modules.filter(m=>m.qualified_selectors.some(s=>graph.nodes.find(n=>n.selector===s).kind!=='Event'));
 for(const m of referenced)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("REFERENCED_MODULE_LOADED");\\n');
 const event=id=>plan.resolved.modules.find(m=>m.qualified_selectors.includes('alpha:'+id)&&m.exports.some(e=>e.name==='event'+id[0].toUpperCase()+id.slice(1))),filename=id=>path.join(output,event(id).relative_path.replace(/\\.ts$/,'.js'));
 const input={occurrence:{'occurrence-id':'explicit-occurrence'},occurredAt:'explicit-time',payload:{amount:'-9223372036854775808',ratio:-0,enabled:false,label:'',time:'not-a-date',uuid:'not-a-uuid',entity:'not-looked-up',value:'value-ref',status:'unknown-member',previous:'other-event'}};
 const client=path.resolve('event-client.mjs');fs.writeFileSync(client,'import assert from "node:assert/strict";\\nimport {eventSupplied} from '+JSON.stringify(filename('supplied'))+';\\nimport {eventClocked} from '+JSON.stringify(filename('clocked'))+';\\nconst input='+JSON.stringify(input)+';\\nconst value=eventSupplied(input);assert.equal(value.payload.amount,-9223372036854775808n);assert.equal(value.payload.entity,"not-looked-up");assert.equal(value.payload.status,"unknown-member");assert.equal(value.payload.time,"not-a-date");assert.equal(value.occurrence["occurrence-id"],"explicit-occurrence");assert.equal(Object.hasOwn(value.payload,"note"),false);assert.equal(Object.is(value.payload.ratio,-0),false);assert.notEqual(value.payload,input.payload);assert.notEqual(value.occurrence,input.occurrence);const {occurredAt,...facts}=input;let calls=0;assert.equal(eventClocked(facts,()=>{calls++;return "fixture-clock";}).occurredAt,"fixture-clock");assert.equal(calls,1);console.log("event-reference-isolation-pass");');
 const before=execFileSync(process.execPath,[client],{encoding:'utf8',timeout:60000});
 const provider=path.join(output,event('supplied').relative_path.replace(/\\.ts$/,'.provider.js')),dependency=path.join(output,referenced[0].relative_path.replace(/\\.ts$/,'.js'));let specifier=path.relative(path.dirname(provider),dependency).split(path.sep).join('/');if(!specifier.startsWith('.'))specifier='./'+specifier;
 fs.appendFileSync(provider,'\\nimport '+JSON.stringify(specifier)+';\\n');const after=spawnSync(process.execPath,[client],{encoding:'utf8',timeout:60000});assert.notEqual(after.status,0);assert.match(after.stderr,/REFERENCED_MODULE_LOADED/);
 console.log(JSON.stringify({pass:before.trim(),poisoned:referenced.length,negative_rejected:after.status!==0}));`);
 assert.equal(result.pass,'event-reference-isolation-pass');assert.ok(result.poisoned>0);assert.equal(result.negative_rejected,true);
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
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
