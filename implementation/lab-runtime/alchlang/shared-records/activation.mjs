import {readFileSync,existsSync} from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../../..');
export function activation({required=false}={}){
 const filename=path.join(root,'implementation/lab-runtime/shared-workflow.json');
 if(!existsSync(filename)){if(required)throw Error('shared-workflow-not-activated');return null;}
 const config=JSON.parse(readFileSync(filename));
 if(config.status!=='active'){if(required)throw Error('shared-workflow-not-active');return null;}
 function local(name){const p=path.resolve(root,config[name]);if(!p.startsWith(root+path.sep))throw Error('activation-path-outside-repository');return p;}
 return {...config,database:local('database'),journal:local('journal'),trust:local('trust'),native_store:local('native_store'),root};
}
