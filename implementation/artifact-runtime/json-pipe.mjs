/** A bounded JSON pipe for generic I/O/data adapters; contains no domain policy. */
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
export function openJsonPort(program){
 const child=spawn('python3',['-B',program,'--stream'],{stdio:['pipe','pipe','pipe'],env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
 const lines=createInterface({input:child.stdout,crlfDelay:Infinity}),pending=[];let closed=false,diagnostic='';
 child.stderr.on('data',chunk=>{if(diagnostic.length<8192)diagnostic+=chunk;});
 function failure(error){for(const waiter of pending.splice(0))waiter.reject(error);}
 lines.on('line',line=>{const waiter=pending.shift();if(!waiter)return failure(Error('unexpected-json-port-response'));try{const value=JSON.parse(line);if(value.error)waiter.reject(Error(value.error+' ['+waiter.operation+']'));else waiter.resolve(value.result);}catch(error){waiter.reject(error);}});
 child.on('error',failure);child.on('close',(code,signal)=>{closed=true;if(pending.length)failure(Error('generic-port-outcome-unknown: '+(diagnostic||code||signal)));});
 return Object.freeze({request(value){if(pending.length>=256)return Promise.reject(Error('json-port-pending-bound'));if(closed)return Promise.reject(Error('generic-port-closed'));const raw=JSON.stringify(value)+'\n';if(Buffer.byteLength(raw)>67108864)return Promise.reject(Error('frame-budget'));return new Promise((resolve,reject)=>{pending.push({resolve,reject,operation:value.operation});child.stdin.write(raw,error=>{if(error)failure(error);});});},async close(){if(closed)return;child.stdin.end();await new Promise(resolve=>child.once('close',resolve));lines.close();}});
}