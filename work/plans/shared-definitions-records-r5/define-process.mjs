import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {node} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
const root=path.resolve(import.meta.dirname,'../../..'),here=import.meta.dirname;
const session=path.join(here,'define-session'),cli=path.join(root,'workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs');
const start={session_id:'session:shared-lab-r5-contract-repair',scope:{project:null,work:null,goal:'Close all ten shared Lab workflow audit findings through the definitions-to-generation chain',originating_intent:'Make shared construction, admission, publication and recovery actually enforce their contracts',
 context_description:'Reuse admitted definitions; preserve original owner decisions; keep shared responsibilities outside Define',consumer:'lab:shared-runtime',intended_use:'prepare-construction-contracts'},request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},validation_scope:{required_checks:[],evidence_scope:'Admitted meaning lookup and R5 contract preparation',claim_ceiling:'Define preparation does not grant admission or construction authority.'}};
mkdirSync(path.join(here,'.local'),{recursive:true});
const file=path.join(here,'.local/define-start.json');writeFileSync(file,JSON.stringify(start));
const receipts=[];
function call(args){const x=spawnSync(node,[cli,...args],{encoding:'utf8',timeout:300000,maxBuffer:16*1024*1024});if(x.status!==0)throw Error(x.stderr+x.stdout);const result=JSON.parse(x.stdout);receipts.push({command:args[0],result});return result;}
call(['start','--work',session,'--file',file,'--actor','person:<vrondelli>','--id','r5:start']);
const definitions=JSON.parse(readFileSync(path.join(here,'DEFINITIONS.json'))).definitions;
for(const d of definitions)call(['discover','--work',session,'--query',d.definition_id,'--actor','person:<vrondelli>','--id','r5:reuse:'+d.definition_id]);
call(['replay','--work',session]);
writeFileSync(path.join(here,'DEFINE-PROCESS.json'),JSON.stringify({status:'PASS',scope:'Meaning reuse and shared contract preparation only; no shared authority moved into Define',receipts},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',lookups:definitions.length}));
