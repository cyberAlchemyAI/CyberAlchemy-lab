import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {build,node,root,sha} from './runtime/build.mjs';
import {commit,load,variant,exportRequest,canonical} from './runtime/runtime.mjs';
import {evaluatePipeline} from '../../../../../../implementation/artifact-runtime/pure-pipeline.mjs';
const artifact=build(),directory=mkdtempSync(path.join(root,'.local/current-cli-proof-')),checks=[];
const scope={project:'project:local-fixture',work:'work:current-source-proof',goal:'Preserve selected meaning',originating_intent:'Check current source execution',context_description:'Isolated local candidate fixture',consumer:'fixture-consumer',intended_use:'inspect-preparation'};
const start={session_id:'current-source-proof',request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},scope,validation_scope:{required_checks:['Exact candidate bytes'],evidence_scope:'Isolated fixture',claim_ceiling:'No authority admission'}};
const input=path.join(directory,'start.json');writeFileSync(input,JSON.stringify(start));
function cli(args){const p=spawnSync(node,[path.join(root,'cli.mjs'),...args],{encoding:'utf8'});assert.equal(p.status,0,p.stderr||p.stdout);return JSON.parse(p.stdout);}
const first=cli(['init','--work',directory,'--file',input,'--actor','actor:local-fixture','--id','initial']);assert.equal(first.current.revision,'1');checks.push('CLI-init-current-source');
const values=[variant('SetContext',{project:scope.project,work:scope.work,source_snapshot:'local:fixture',status:'Sufficient',explanation:'Exact local candidate scope',evidence:[]}),variant('RequireConcept',{concept_id:'concept:one',question:'What is one?',scope:'Fixture scope'}),variant('HandleMeaning',variant('Propose',{concept_id:'concept:one',working_meaning:{meaning_id:'meaning:one',revision:'1',statement:'A local candidate meaning',scope:'Fixture scope',boundaries:['No semantic authority'],parameters:[],ownership_posture:'Candidate only',lineage:[],status:'local-proposed',authority_effect:'none'},applicability:'Candidate examination'}))];
let current=first.current,lastCommand;
for(let index=0;index<values.length;index++){lastCommand={command_id:'command-'+index,session_id:current.session_id,project:scope.project,work:scope.work,actor:'actor:local-fixture',expected_revision:current.revision,payload:values[index]};const value=await commit(directory,lastCommand);current=value.current;}
checks.push('current-operations-author-meaning');
const request=await exportRequest(current);assert.equal(request.handling[0].fields.value.working_meaning.meaning_id,'meaning:one');checks.push('current-model-request-export');
const portable=cli(['request','--work',directory]);assert.equal(portable.handling[0].disposition,'propose');assert.equal(portable.request_revision,1);checks.push('CLI-request-uses-native-wire-codec');
const reopened=cli(['show','--work',directory]);assert.deepEqual(reopened.current,current);checks.push('fresh-process-journal-replay');
const replay=await commit(directory,lastCommand);assert.equal(replay.outcome,'replayed');assert.equal((await load(directory)).events.length,4);checks.push('idempotent-command-replay');
const before=(await load(directory)).head;
await assert.rejects(()=>commit(directory,{...lastCommand,command_id:'foreign-scope',expected_revision:current.revision,project:'project:foreign'}),/project-mismatch/);assert.equal((await load(directory)).head,before);checks.push('foreign-project-refuses-before-journal-write');
await assert.rejects(()=>commit(directory,{...lastCommand,payload:variant('RequireConcept',{concept_id:'changed',question:'Changed?',scope:'Fixture'})}),/command-id-conflict/);checks.push('conflicting-command-identity-refused');
const old=mkdtempSync(path.join(root,'.local/predecessor-proof-'));mkdirSync(path.join(old,'define'));const record=JSON.parse(readFileSync(path.join(directory,'define/session.jsonl'),'utf8').split('\n')[0]);delete record.event_sha256;record.model='0'.repeat(64);record.event_sha256=sha(canonical(record));writeFileSync(path.join(old,'define/session.jsonl'),canonical(record)+'\n');await assert.rejects(()=>load(old),/model-mismatch/);checks.push('unsupported-predecessor-epoch-refused');
await assert.rejects(()=>evaluatePipeline(artifact.output,'0'.repeat(64),{}),/pipeline-manifest-drift/);checks.push('pipeline-manifest-pin-enforced');
const doctor=cli(['doctor']);assert.equal(doctor.session_engine,'current-authored-source');assert.equal(doctor.source,artifact.source);checks.push('doctor-identifies-current-source');
const report={schema_version:'define-current-source-cli-verification/v1',status:'PASS',source:artifact.source,application_source:artifact.application_source,checks,check_count:checks.length,python_define_engine_imported:false,fixture_auth_used:false,qualification:'Local candidate authoring and journal replay only; package workflow retirement not inferred.'};
writeFileSync(path.resolve(root,'../.local/CURRENT-CLI-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));