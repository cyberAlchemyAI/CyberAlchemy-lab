import {spawn} from 'node:child_process';
import {createServer,createConnection} from 'node:net';
import {once} from 'node:events';
import {setTimeout as delay} from 'node:timers/promises';
import {readFileSync} from 'node:fs';
import {sshSettings,integer,fail} from './config.mjs';
// No shell interpolation, host-key enrollment, passwords, remote mutation or detached SSH.
// Open Questions: README.md.
export function sshArguments(settings){
 const s=sshSettings(settings);
 return ['-F','/dev/null','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2','-o','ControlPath=none','-o','ExitOnForwardFailure=yes','-p',String(s.port),...(s.identityFile?['-i',s.identityFile]:[])];
}
async function stopChild(child){
 if(child.exitCode!==null||child.signalCode)return;
 const done=once(child,'close').catch(()=>{});child.kill('SIGTERM');
 const timer=setTimeout(()=>child.kill('SIGKILL'),500);try{await done;}finally{clearTimeout(timer);}
}
export async function discoverRemote(settings,{signal,spawnProcess=spawn}={}){
 signal?.throwIfAborted();
 const child=spawnProcess('ssh',[...sshArguments(settings),settings.user+'@'+settings.host,'python3 -'],{stdio:['pipe','pipe','pipe']});
 let text='',errorText='',failure;
 child.stdout.on('data',data=>{text+=data;if(Buffer.byteLength(text)>65536){failure=Error('SSH_DISCOVERY_TOO_LARGE');child.kill();}});
 child.stderr.on('data',data=>{if(errorText.length<4096)errorText+=data;});
 child.stdin.on('error',()=>{});child.stdin.end(readFileSync(new URL('./discover.py',import.meta.url)));
 const stop=()=>child.kill('SIGTERM');signal?.addEventListener('abort',stop,{once:true});
 const timer=setTimeout(stop,20000);
 try{
  const [code]=await once(child,'close');signal?.throwIfAborted();
  if(failure)throw failure;
  if(code!==0)fail(/Host key verification failed/.test(errorText)?'SSH_HOST_KEY_NOT_TRUSTED: connect with ssh and verify its fingerprint first':'SSH_DISCOVERY_FAILED: check SSH key, user, port and Python 3');
  let result;try{result=JSON.parse(text);}catch{fail('SSH_DISCOVERY_INVALID');}
  if(!Array.isArray(result)||result.length>64)fail('SSH_DISCOVERY_INVALID');
  return result.filter(r=>Number.isSafeInteger(r.port)&&r.port>0&&r.port<65536&&Array.isArray(r.models));
 }finally{clearTimeout(timer);signal?.removeEventListener('abort',stop);await stopChild(child);}
}
const availablePort=async()=>{const server=createServer();server.listen(0,'127.0.0.1');await once(server,'listening');const port=server.address().port;await new Promise(r=>server.close(r));return port;};
const openPort=port=>new Promise(resolve=>{const socket=createConnection({host:'127.0.0.1',port});const done=v=>{socket.destroy();resolve(v);};socket.setTimeout(100,()=>done(false));socket.once('connect',()=>done(true));socket.once('error',()=>done(false));});
export async function startTunnel(settings,{signal,spawnProcess=spawn}={}){
 sshSettings(settings);integer(settings.remotePort,1,65535);signal?.throwIfAborted();const port=await availablePort();signal?.throwIfAborted();
 const child=spawnProcess('ssh',[...sshArguments(settings),'-N','-L',`127.0.0.1:${port}:127.0.0.1:${settings.remotePort}`,settings.user+'@'+settings.host],{stdio:['ignore','ignore','pipe']});
 let failed=false;child.on('error',()=>{failed=true;});child.stderr.resume();
 const closed=once(child,'close').catch(()=>{});const stop=()=>child.kill('SIGTERM');signal?.addEventListener('abort',stop,{once:true});
 const close=async()=>{signal?.removeEventListener('abort',stop);await stopChild(child);};
 try{
  for(let i=0;i<100;i++){
   signal?.throwIfAborted();if(failed||child.exitCode!==null||child.signalCode)fail('SSH_TUNNEL_FAILED: verify SSH access and host trust');
   if(await openPort(port)){await delay(100);if(failed||child.exitCode!==null||child.signalCode)fail('SSH_TUNNEL_FAILED');return {baseUrl:`http://127.0.0.1:${port}`,close,closed};}
   await delay(100);
  }
  fail('SSH_TUNNEL_TIMEOUT');
 }catch(error){await close();throw error;}
}
