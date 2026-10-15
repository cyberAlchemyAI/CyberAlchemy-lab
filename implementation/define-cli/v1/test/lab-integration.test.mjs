import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
import test, {before} from 'node:test';
import {PassThrough} from 'node:stream';
import {composeDefineContext,runDefineSession,validateDefinitionPack,evaluateDefineLanguageQuality,runDefineConversation,
  compileDefinitionPackToAlch,createDurableDefineRuntime,InMemorySessionRepository,JsonFileSessionRepository} from '../index.mjs';
import {runLabDefine,saveCandidate} from '../src/lab-cli.mjs';
import {digest} from '../src/canonical.mjs';
import {createAppServerDefineAgent} from '../src/app-server-agent.mjs';
const root=resolve(import.meta.dirname,'../../../..');
const scope={goal:'Define complete export for an incident',intent:'Investigate missing rows without changing customer data',context:'One source snapshot, account A and declared filters F',consumer:'incident-investigator'};
const concepts=[{concept_id:'concept:complete-export',term:'complete export',owner_route:'incident-commander'}];
const responses=[{concept_id:concepts[0].concept_id,action:'propose',payload:{definition:'A complete export contains every required identifier for the selected snapshot, account and filter set.',boundary:'Does not establish value accuracy or authorize incident closure.'}}];
const language={user_phrases:['complete export'],terms:['complete export'],distinctions:[],relationships:[],constraints:[],owners:[],open_questions:[]};
const quality={schema_version:'cav2.define-language-quality/v1',grounding:[{field:'terms',item_index:0,source_phrase_index:0,posture:'direct',rationale:'Exact user term'}],non_collapse:[],orthogonality:{applicability:'not-applicable',rationale:'No classification axes are introduced',axes:[],pair_checks:[]}};
let ctx;
before(()=>{ctx=composeDefineContext(scope,root);assert.equal(ctx.ok,true,JSON.stringify(ctx));});
function complete(){return runDefineSession({...scope,concepts,responses,context_result:ctx,
  language_scope:language,language_quality_evidence:quality,language_quality_evaluation:evaluateDefineLanguageQuality({language,language_quality:quality},[],{user_confirmed:true})});}
function capture(){let value='';const stream=new PassThrough();stream.on('data',c=>value+=c);return{stream,value:()=>value};}

test('Lab context carries exact current definitions, selected state and independent views',()=>{
 assert.equal(ctx.context_envelope.freshness_state,'current');assert.ok(ctx.context_envelope.inline_bytes<=256*1024);
 assert.equal(ctx.lab_views.project_state.kind,'project-state');assert.equal(ctx.lab_views.context_view.kind,'context-view');
 assert.equal(ctx.lab_views.ontology_view.kind,'ontology-view');assert.equal(ctx.context_envelope.authority_effect,'none');
 assert.ok(ctx.context_envelope.included_items.some(r=>r.context_item_id==='definition:cal.definition.definition'));
 assert.equal(ctx.lab_views.short_memory_persisted,false);
 assert.equal(new Set(ctx.lab_views.agent_session.payload.input_refs).size,ctx.lab_views.agent_session.payload.input_refs.length);
});
test('Default command works outside repository cwd',()=>{const p=spawnSync('node',[join(root,'implementation/define-cli/v1/bin/define.mjs'),'--help'],{cwd:tmpdir(),encoding:'utf8'});assert.equal(p.status,0);assert.match(p.stdout,/Lab interfaces/);});
test('Pack binds source epoch and remains candidate',()=>{const r=complete();assert.equal(r.ok,true);assert.equal(r.definition_pack.source_epoch,ctx.source_epoch);assert.equal(r.authority_effect,'none');assert.equal(r.validation.validation_scope,'deterministic-structure-and-language-quality');});
test('Absent quality remains visibly structure-only',()=>{const r=runDefineSession({...scope,concepts,responses,context_result:ctx});assert.equal(r.validation.validation_scope,'deterministic-structure-only');const dir=mkdtempSync(join(tmpdir(),'define-no-quality-'));assert.throws(()=>compileDefinitionPackToAlch(r,join(dir,'out')),/language-quality/);});
test('Missing answer stays open',()=>{const r=runDefineSession({...scope,concepts,responses:[],context_result:ctx});assert.equal(r.ok,true);assert.equal(r.validation.handoff_ready,false);assert.equal(r.definition_pack.open_questions.length,1);});
test('Duplicate responses are rejected rather than silently replaced',()=>{const r=runDefineSession({...scope,concepts,responses:[...responses,...responses],context_result:ctx});assert.equal(r.ok,false);assert.ok(r.reason_codes.includes('define-session.duplicate-response'));});
test('Duplicate concept IDs and undeclared responses are rejected',()=>{
 assert.equal(runDefineSession({...scope,concepts:[...concepts,...concepts],responses,context_result:ctx}).ok,false);
 assert.equal(runDefineSession({...scope,concepts,responses:[{...responses[0],concept_id:'unknown'}],context_result:ctx}).ok,false);
});
test('Semantic grounding requires exact direct phrase',()=>{const bad={...language,user_phrases:['unrelated']};assert.equal(evaluateDefineLanguageQuality({language:bad,language_quality:quality},[],{user_confirmed:true}).status,'block');});
test('Candidate inference needs user confirmation',()=>{const q=structuredClone(quality);q.grounding[0].posture='candidate-inference';assert.equal(evaluateDefineLanguageQuality({language,language_quality:q},[],{user_confirmed:false}).status,'review');});
test('Non-collapse detects identical candidate meanings',()=>{
 const l={...language,user_phrases:['export','investigation'],terms:['export','investigation']};const q=structuredClone(quality);
 q.grounding=[0,1].map(i=>({...quality.grounding[0],item_index:i,source_phrase_index:i}));q.non_collapse=[{left_term_index:0,right_term_index:1,status:'distinct',difference:'Output and work episode are separate.'}];
 const r=evaluateDefineLanguageQuality({language:l,language_quality:q},[{term:'export',candidate_definition:'same meaning'},{term:'investigation',candidate_definition:'same meaning'}],{user_confirmed:true});assert.equal(r.status,'block');
});
test('Unnamed axis coupling blocks readiness',()=>{
 const q=structuredClone(quality);q.orthogonality={applicability:'applicable',rationale:'Different axes',axes:[{axis_id:'a',label:'Authority',unique_question:'Who decides?',values:['candidate','admitted']},{axis_id:'b',label:'Lifecycle',unique_question:'What happens next?',values:['active','closed']}],pair_checks:[{left_axis_id:'a',right_axis_id:'b',status:'coupled',difference:'A declared gate couples these axes.'}]};
 assert.equal(evaluateDefineLanguageQuality({language,language_quality:q},[],{user_confirmed:true}).status,'block');
});
test('Real semantic Alch to existing Craft compilation uses Calculations',()=>{
 const dir=mkdtempSync(join(tmpdir(),'define-compile-'));const r=compileDefinitionPackToAlch(complete(),join(dir,'out'));
 assert.equal(r.ok,true);const graph=JSON.parse(readFileSync(join(dir,'out/compiled/provenance/craft/graph.json')));
 assert.ok(graph.nodes.some(n=>n.kind==='Calculation'||n.meta_type_id==='calculation'||String(n.meta_type_id).toLowerCase().includes('calculation')));
 assert.equal(JSON.parse(readFileSync(join(dir,'out/compiled/evidence/craft/certificate.json'))).compiler.version,'0.0.0-candidate.5');
 assert.equal(r.receipt.authority_effect,'none');assert.throws(()=>compileDefinitionPackToAlch(complete(),join(dir,'out')),/output directory/);
});
test('Tampered pack or forged language PASS cannot compile',()=>{
 const dir=mkdtempSync(join(tmpdir(),'define-tamper-'));const r=complete();r.definition_pack.goal='changed';assert.throws(()=>compileDefinitionPackToAlch(r,join(dir,'a')),/not handoff-ready/);
 const p=complete().definition_pack;p.language_quality_evidence.grounding=[];const {pack_id,...body}=p;p.pack_id='definition-pack:'+digest(body);assert.throws(()=>compileDefinitionPackToAlch(p,join(dir,'b')),/not handoff-ready/);
});
test('One-by-one conversation creates a reviewed pack through Lab context',async()=>{
 const turn={schema_version:'cav2.define-conversation-turn/v2',phase:'scope-review',message:'Review the incident meaning.',question:null,scope_ready:true,
 covered_dimensions:['domain-and-subject','desired-outcome','consumers','terms','distinctions-and-relationships','constraints','ownership','open-questions'],
 scope:{domain:'SaaS',subject:'Export incident',project:'Incident investigation',context:scope.context,desired_outcome:scope.goal,intent:scope.intent,consumer:scope.consumer,language,language_quality:quality},
 options:[{option_id:'complete-export',term:'complete export',question:'What counts as complete?',why_it_matters:'Sets a falsifiable criterion',candidate_definition:responses[0].payload.definition,boundary:responses[0].payload.boundary}]};
 const answers=['yes','accept','yes'];const r=await runDefineConversation({agent:{respond:async()=>turn},ask:async()=>answers.shift(),write:()=>{},opening:'Investigate an export incident',repository_root:root});assert.equal(r.ok,true);assert.equal(r.route.route_id,'CAL-DEFINE-EXPLICIT-ENTRY');
});
test('RPC agent uses Lab context, ephemeral native thread and initialized notification',async()=>{
 let thread,turn,initialized=false;
 const client={ready:async()=>null,initialize:async()=>({}),notify:(method)=>{initialized=method==='initialized';},startThread:async p=>{thread=p;return{thread:{id:'thread:test'}};},runTurn:async p=>{turn=p;return{completed:{turn:{status:'completed'}},text:JSON.stringify({schema_version:'cav2.define-conversation-turn/v2',phase:'discover',message:'Name the context.',question:'Which account?',scope_ready:false,covered_dimensions:[],scope:{language:{user_phrases:[],terms:[],distinctions:[],relationships:[],constraints:[],owners:[],open_questions:[]}},options:[]})};},close:async()=>{}};
 const agent=createAppServerDefineAgent({repository_root:root,rpc_client:client});await agent.respond({user_input:'An export incident'});await agent.close();
 assert.equal(initialized,true);assert.equal(thread.ephemeral,true);assert.equal(thread.sandbox,'read-only');assert.equal(turn.sandboxPolicy.networkAccess,false);assert.match(turn.input[0].text,/cal.define-context-envelope/);assert.equal(turn.additionalContext,undefined);
});
test('Candidate file output cannot overwrite an existing file',()=>{const d=mkdtempSync(join(tmpdir(),'define-write-'));const p=join(d,'record.json');saveCandidate(p,{x:1});assert.throws(()=>saveCandidate(p,{x:2}));assert.equal(JSON.parse(readFileSync(p)).x,1);});
test('Unknown CLI option yields a visible failure',async()=>{const o=capture(),e=capture();assert.equal(await runLabDefine(['run','--bad'],{stdout:o.stream,stderr:e.stream}),2);});
test('Ontology query delegates to Lab bounded graph',async()=>{const o=capture(),e=capture();assert.equal(await runLabDefine(['ontology','Authority'],{stdout:o.stream,stderr:e.stream}),0,e.value());const r=JSON.parse(o.value());assert.ok(r.nodes.length>0);assert.equal(r.authority_effect,'none');});
test('Review requires an explicitly selected initialized Lab store',async()=>{const o=capture(),e=capture();assert.equal(await runLabDefine(['review','--proposal','missing'],{stdout:o.stream,stderr:e.stream}),3);assert.match(e.value(),/explicitly provisioned/);});
