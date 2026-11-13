import {readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';
import {activation} from '../../../implementation/lab-runtime/alchlang/shared-records/activation.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {publishDirectoryView} from '../../../implementation/lab-workflows/records-workflow/publication.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),put=(name,x)=>{const f=path.join(here,name);writeFileSync(f,JSON.stringify(x,null,2)+'\n');return f;},active=activation({required:true}),prepared=JSON.parse(readFileSync(path.join(here,'.local/DIRECTORY-VIEW-READY.json'))),operation='PublishDirectoryView',scope=active.workspace,cut=prepared.cut,issuer='principal:lab-shared-operator',key=path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem');
let packet;
const file=path.join(here,'DIRECTORY-PUBLICATION-REQUEST.json');
try{packet=JSON.parse(readFileSync(file));}catch(e){
 if(e.code!=='ENOENT')throw e;
 const input=put('DIRECTORY-PUBLICATION-INPUT.json',prepared.input),original=await main(['attest','--file',put('DIRECTORY-PUBLICATION-ATTEST.json',{artifact:input,schema:operation,predicate:'qualified-operator-observation',operation,scope,cut}),'--trust',active.trust,'--issuer',issuer,'--key',key]);
 packet={operation,scope,cut,...await main(['issue','--file',put('DIRECTORY-PUBLICATION-ISSUE.json',{selection_id:operation,operation,scope,cut,originals:[original]}),'--trust',active.trust,'--issuer',issuer,'--key',key])};put('DIRECTORY-PUBLICATION-REQUEST.json',packet);
}
const result=await publishDirectoryView({...packet,files:prepared.files},loadTrust(active.trust),active);
put('DIRECTORY-PUBLICATION-RECEIPT.json',result);
const config=JSON.parse(readFileSync(path.join(root,'implementation/lab-runtime/shared-workflow.json')));config.selector=result.selected;writeFileSync(path.join(root,'implementation/lab-runtime/shared-workflow.json'),JSON.stringify(config,null,2)+'\n');
console.log(JSON.stringify({status:'PASS',selected:result.selected,views:result.views}));
