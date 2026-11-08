import {buildPublicPolicy} from './build-public-policy.mjs';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {once} from 'node:events';
import {createProtectedServer} from './security/host.mjs';
import {createAuthFoundation} from './security/auth-foundation.mjs';
// Invoke through run.mjs to verify the sibling compiler binding. Open questions: HOST.md.
const port=Number(process.argv[3]??3000);
if(!process.argv[2]||!Number.isInteger(port)||port<0||port>65535)throw Error('Usage: node run.mjs serve /absolute/operator-config.mjs [port]');
const config=(await import(pathToFileURL(resolve(process.argv[2])).href)).default;
const dir=mkdtempSync(join(tmpdir(),'inference-host-'));let server;
try{
 const handlers=await buildPublicPolicy(dir,{protectedService:true});
 server=createProtectedServer({...config,...handlers,security:createAuthFoundation(config.authFoundation)});
 server.listen(port,'127.0.0.1');await once(server,'listening');
 console.log('Inference host: http://127.0.0.1:'+server.address().port);
 await new Promise(resolve=>{const stop=()=>{process.off('SIGINT',stop);process.off('SIGTERM',stop);resolve();};process.once('SIGINT',stop);process.once('SIGTERM',stop);});
}finally{
 if(server){server.closeAllConnections();await new Promise(r=>server.close(r));}
 rmSync(dir,{recursive:true,force:true});
}
