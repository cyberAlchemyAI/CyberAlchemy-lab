import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';import path from 'node:path';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
export const here=import.meta.dirname,root=path.resolve(here,'../../..'),trustFile=path.join(here,'runtime-trust.json'),database=path.join(root,'.local/lab-runtime/shared/snapshots.sqlite'),journal=path.join(root,'.local/lab-runtime/shared/journal.sqlite'),scope='workspace:cyberalchemy-lab:lab',issuer='principal:lab-shared-operator';
export const load=f=>JSON.parse(readFileSync(f)),put=(name,v)=>{const file=path.isAbsolute(name)?name:path.join(here,name);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,JSON.stringify(v,null,2)+'\n');return file;};
export const context=load(path.join(here,'NATIVE-CONTEXT.json')),cut=context.cut,key=path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem');
let ordinal=0;
export async function issue(operation,input,label=operation){
 const dir=path.join(here,'issuance',label+'-'+(++ordinal)),file=put(path.join(dir,'input.json'),input);
 const request=put(path.join(dir,'attest.json'),{artifact:file,schema:operation,predicate:'qualified-operator-observation',operation,scope,cut});
 const original=await main(['attest','--file',request,'--trust',trustFile,'--issuer',issuer,'--key',key]);
 const issued=await main(['issue','--file',put(path.join(dir,'issue.json'),{selection_id:operation,operation,scope,cut,originals:[original]}),'--trust',trustFile,'--issuer',issuer,'--key',key]);
 return {operation,scope,cut,...issued};
}
export const trust=()=>loadTrust(trustFile);
