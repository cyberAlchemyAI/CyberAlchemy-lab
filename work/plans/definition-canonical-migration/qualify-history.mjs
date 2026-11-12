import {readFileSync} from 'node:fs';import path from 'node:path';import {DatabaseSync} from 'node:sqlite';
import {here,root,trustFile,load,put} from './operator.mjs';
import {inputs,fingerprint} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
const shared=path.join(root,'implementation/lab-runtime/alchlang/shared-records'),selection=load(path.join(shared,'sources.json')),files=Object.fromEntries([...new Set([...inputs,selection.primary,...selection.additional])].map(f=>[f,readFileSync(path.join(shared,f)).toString('base64')]));
const archive=put('MODEL-1029-ORIGINAL.json',{schema_version:'lab-original-model-source/v1',source:fingerprint(),files,qualification:'Exact unchanged authored model for already recorded migration transition events.'}),binding={path:path.relative(root,archive),sha256:digest(readFileSync(archive))};
const t=load(trustFile),db=new DatabaseSync(path.join(root,'.local/lab-runtime/shared/journal.sqlite'),{readOnly:true});
for(const row of db.prepare('SELECT evidence FROM commands').all()){
 const request=JSON.parse(row.evidence),raw=Buffer.from(request.artifact,'base64'),v=JSON.parse(raw);
 if(!t.historical_artifacts[digest(raw)]&&v.implementation)t.historical_artifacts[digest(raw)]={operation:request.operation,scope:request.scope,cut:request.cut,implementation:v.implementation,model_archive:binding};
}
db.close();
const publications=new DatabaseSync(path.join(root,'.local/lab-runtime/shared/snapshots.sqlite'),{readOnly:true});
for(const row of publications.prepare('SELECT evidence FROM publications').all()){
 const request=JSON.parse(row.evidence),raw=Buffer.from(request.artifact,'base64'),v=JSON.parse(raw);
 if(!t.historical_artifacts[digest(raw)]&&v.implementation)t.historical_artifacts[digest(raw)]={operation:request.operation,scope:request.scope,cut:request.cut,implementation:v.implementation,model_archive:binding};
}
publications.close();
const transferred=load(path.join(here,'TRANSFER-REQUEST.json')).construction,transferRaw=Buffer.from(transferred.artifact,'base64'),transferValue=JSON.parse(transferRaw),transferManifest=load(path.join(here,'implementation-history',transferValue.implementation+'.json'));
if(transferManifest.digest!==transferValue.implementation||digest(Buffer.from(JSON.stringify(transferManifest.manifest)))!==transferValue.implementation)throw Error('transfer-original-manifest-not-exact');
t.historical_artifacts[digest(transferRaw)]={operation:transferred.operation,scope:transferred.scope,cut:transferred.cut,implementation:transferValue.implementation,model_archive:binding};
put(trustFile,t);console.log(JSON.stringify({qualified_artifacts:Object.keys(t.historical_artifacts).length,model:fingerprint()}));
