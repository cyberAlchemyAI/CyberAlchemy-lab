import {existsSync,lstatSync,realpathSync,unlinkSync,symlinkSync,mkdirSync} from 'node:fs';import path from 'node:path';import {implementationRoot} from '../../../workspaces/products/craft/implementation/source-bindings.mjs';
const local=path.resolve(import.meta.dirname,'../../../implementation/lab-runtime/alchlang/.local'),peer=path.join(local,'node_modules/@domainspec-v2/cli'),target=path.join(implementationRoot,'cli');
if(!peer.startsWith(local+path.sep)||!existsSync(target))throw Error('module-binding-boundary-invalid');
mkdirSync(path.dirname(peer),{recursive:true});let stat;try{stat=lstatSync(peer);}catch(e){if(e.code!=='ENOENT')throw e;}
if(stat&&(!existsSync(peer)||realpathSync(peer)!==target)){if(!stat.isSymbolicLink())throw Error('unexpected-private-module-directory');unlinkSync(peer);stat=null;}
if(!stat)symlinkSync(target,peer,'dir');if(realpathSync(peer)!==target)throw Error('module-binding-not-reconciled');console.log(JSON.stringify({status:'PASS',module:target,runtime_copies:0}));
