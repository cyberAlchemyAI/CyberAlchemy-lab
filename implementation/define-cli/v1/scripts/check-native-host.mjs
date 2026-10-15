// Checks the native protocol without sending a model turn or using live credentials.
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {createAppServerRpcClient,spawnAppServerRpcTransport} from '../vendor/app-server/src/rpc-client.mjs';
const directory=mkdtempSync(join(tmpdir(),'define-native-host-'));
const transport=spawnAppServerRpcTransport({command:process.env.DEFINE_CODEX_BINARY ?? 'codex',args:['app-server','--listen','stdio://'],env:{...process.env,CODEX_HOME:directory},close_timeout_ms:2000});
const client=createAppServerRpcClient({transport,request_timeout_ms:15000,thread_start_timeout_ms:15000});
try {
 const host=await client.initialize({clientInfo:{name:'cyberalchemy-define-host-check',title:'Define host compatibility',version:'0.1.0-candidate'},capabilities:{experimentalApi:true}});
 await client.notify('initialized',{});
 const thread=await client.startThread({cwd:resolve(import.meta.dirname,'../../../..'),ephemeral:true,approvalPolicy:'on-request',sandbox:'read-only'});
 if(!thread.thread.id)throw new Error('Host did not return a thread identity');
 process.stdout.write(JSON.stringify({ok:true,checks:['native-process','initialize','initialized','ephemeral-read-only-thread','transport-teardown'],host,model_turns:0,credentials_used:false,authority_effect:'none'})+'\n');
} finally {await client.close();rmSync(directory,{recursive:true,force:true});}
