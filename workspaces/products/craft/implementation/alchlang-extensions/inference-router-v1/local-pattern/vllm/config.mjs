import {homedir} from 'node:os';
import {join,resolve,relative} from 'node:path';
import {mkdirSync,writeFileSync,readFileSync,lstatSync,realpathSync} from 'node:fs';
import {root} from '../product/package.mjs';
// Operator-owned settings; credentials remain environment/SSH references. Open Questions: README.md.
export const defaultConfig=join(homedir(),'.config/alch-inference/engine.json');
export const fail=code=>{throw Error(code);};
export const integer=(v,min,max)=>{if(!Number.isSafeInteger(v)||v<min||v>max)fail('INVALID_ENGINE_NUMBER');return v;};
const closed=(v,keys)=>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!keys.includes(k)))fail('INVALID_ENGINE_CONFIGURATION');};
export function endpoint(value){
 let u;try{u=new URL(value);}catch{fail('INVALID_ENGINE_URL');}
 if(u.username||u.password||u.search||u.hash||u.pathname!=='/'||!(u.protocol==='https:'||u.protocol==='http:'&&u.hostname==='127.0.0.1'))fail('ENGINE_REQUIRES_HTTPS_OR_LOOPBACK');
 return u.origin;
}
export function sshSettings(s){
 closed(s,['host','port','user','identityFile','remotePort']);
 if(typeof s.host!=='string'||s.host.length>253||! /^[a-zA-Z0-9][a-zA-Z0-9.-]*$/.test(s.host)||typeof s.user!=='string'||! /^[a-zA-Z_][a-zA-Z0-9_-]*$/.test(s.user))fail('INVALID_SSH_DESTINATION');
 integer(s.port,1,65535);if(s.remotePort!==undefined)integer(s.remotePort,1,65535);
 if(s.identityFile!==undefined&&(typeof s.identityFile!=='string'||!s.identityFile.startsWith('/')||s.identityFile.includes('\0')))fail('INVALID_SSH_IDENTITY_PATH');
 return s;
}
export function configuration(c){
 closed(c,['schema_version','connection','model','alias','contextLimit','outputLimit','timeoutMs','tokenEnv']);
 if(c.schema_version!=='alch.vllm-engine/v1')fail('INVALID_ENGINE_CONFIGURATION');
 for(const v of [c.model,c.alias])if(typeof v!=='string'||!v.trim()||v.length>128||/[\x00-\x1f\x7f]/.test(v))fail('INVALID_MODEL_ID');
 integer(c.contextLimit,2,1000000);integer(c.outputLimit,1,c.contextLimit-1);integer(c.timeoutMs,1,30000);
 if(c.tokenEnv!==undefined&&(typeof c.tokenEnv!=='string'||!/^[_A-Z][_A-Z0-9]*$/.test(c.tokenEnv)))fail('INVALID_TOKEN_ENV');
 if(c.connection?.type==='ssh'){
  closed(c.connection,['type','ssh']);sshSettings(c.connection.ssh);integer(c.connection.ssh.remotePort,1,65535);
 }else if(c.connection?.type==='direct'){
  closed(c.connection,['type','baseUrl']);endpoint(c.connection.baseUrl);
 }else fail('INVALID_ENGINE_CONNECTION');
 return c;
}
export function authHeaders(c,env=process.env){
 if(!c.tokenEnv)return {};
 const token=env[c.tokenEnv];if(typeof token!=='string'||!token||/[\r\n]/.test(token))fail('ENGINE_TOKEN_ENV_MISSING');
 return {authorization:'Bearer '+token};
}
export function saveConfiguration(path,c){
 configuration(c);path=resolve(path);
 const outside=p=>{const rel=relative(root,p);if(!rel.startsWith('../'))fail('ENGINE_CONFIG_MUST_BE_OUTSIDE_REPOSITORY');};
 outside(path);const dir=resolve(path,'..');mkdirSync(dir,{recursive:true,mode:0o700});outside(realpathSync(dir));
 writeFileSync(path,JSON.stringify(c,null,2)+'\n',{flag:'wx',mode:0o600});return path;
}
export function readConfiguration(path=defaultConfig){
 const stat=lstatSync(path);if(!stat.isFile()||stat.isSymbolicLink()||(stat.mode&0o077)!==0)fail('ENGINE_CONFIG_REQUIRES_PRIVATE_REGULAR_FILE');
 return configuration(JSON.parse(readFileSync(path,'utf8')));
}
