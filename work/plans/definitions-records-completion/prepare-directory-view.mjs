import {readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {prepareDirectoryView} from '../../../implementation/lab-workflows/records-workflow/publication.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),config=JSON.parse(readFileSync(path.join(root,'implementation/lab-runtime/shared-workflow.json'))),active={...config,root,...Object.fromEntries(['database','journal','native_store'].map(k=>[k,path.join(root,config[k])]))};
const file=path.join(here,'AUTHORIZATION.json'),raw=readFileSync(file);
const prepared=await prepareDirectoryView(active,loadTrust(path.join(root,config.trust)),{operation:'directory-view:definitions-records-nine-findings',viewRoot:'authority/admissions/directory-views/definitions-records-completion',authorization:{path:path.relative(root,file),sha256:digest(raw),bytes:raw.length}});
writeFileSync(path.join(here,'.local/DIRECTORY-VIEW-PREPARED.json'),JSON.stringify(prepared));writeFileSync(path.join(here,'DIRECTORY-PACKAGE-VERIFICATION.json'),JSON.stringify(prepared.packageVerification,null,2)+'\n');
console.log(JSON.stringify({status:'PASS',files:Object.keys(prepared.files).length,directories:prepared.packageVerification.directories.length}));
