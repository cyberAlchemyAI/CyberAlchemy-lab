import {readFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {loadTrust,verifyImplementation} from './implementation.mjs';
import {digest} from './verified-projection.mjs';
const root=path.resolve(import.meta.dirname,'../../../..');
export function activation({required=false}={}){
 const filename=path.join(root,'implementation/lab-runtime/shared-workflow.json');
 if(!existsSync(filename)){if(required)throw Error('shared-workflow-not-activated');return null;}
 const config=JSON.parse(readFileSync(filename));
 if(config.status!=='active'){if(required)throw Error('shared-workflow-not-active');return null;}
 function local(name){const p=path.resolve(root,config[name]);if(!p.startsWith(root+path.sep))throw Error('activation-path-outside-repository');return p;}
 if(config.execution_selection){
  const binding=config.execution_selection;
  const raw=readFileSync(path.resolve(root,binding.path));
  if(digest(raw)!==binding.sha256)throw Error('execution-selection-binding-mismatch');
  const selected=JSON.parse(raw);
  const authorization=readFileSync(path.resolve(root,selected.authorization.path));
  if(digest(authorization)!==selected.authorization.sha256||!JSON.parse(authorization).verbatim)throw Error('implementation-authorization-unverified');
  const trust=loadTrust(local('trust'),root);
  if(verifyImplementation(trust.implementation,root)!==selected.implementation)throw Error('implementation-not-selected');
 }
 return {...config,database:local('database'),journal:local('journal'),trust:local('trust'),native_store:local('native_store'),root};
}
