import {createServer} from 'node:http';
import {setTimeout as delay} from 'node:timers/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
// Deterministic protocol fixture, not a model. Open Questions: README.md.
export function createEngineFixture(label,{waitMs=0,mode='normal'}={}){
 const calls=[];
 const server=createServer(async(req,res)=>{
  try{
   const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>65536){res.writeHead(413).end();return;}chunks.push(chunk);}
   const body=JSON.parse(Buffer.concat(chunks));calls.push({body,headers:req.headers});
   if(waitMs)await delay(waitMs);if(res.destroyed)return;
   if(mode==='redirect'){res.writeHead(302,{location:'http://127.0.0.1:1'}).end();return;}
   if(mode==='invalid'){res.writeHead(200,{'content-type':'application/json'}).end('{');return;}
   const tokens=Buffer.byteLength(body.messages.map(m=>m.content).join(''));
   if(body.stream){
    res.writeHead(200,{'content-type':'text/event-stream'});
    res.write('event: delta\r\ndata: '+JSON.stringify({text:label})+'\r\n\r\n');
    if(mode!=='incomplete')res.write('event: completed\ndata: '+JSON.stringify({stop_reason:'stop',prompt_tokens:tokens,completion_tokens:label.length})+'\n\n');
    res.end();
   }else res.writeHead(200,{'content-type':'application/json'}).end(JSON.stringify({answer:label,stop_reason:'stop',prompt_tokens:tokens,completion_tokens:label.length}));
  }catch{if(!res.destroyed)res.writeHead(400).end();}
 });
 return {server,calls};
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){
 const port=Number(process.argv[2]),label=process.argv[3]??'fixture';
 if(!Number.isInteger(port)||port<1||port>65535)throw Error('Usage: node fixture.mjs PORT LABEL');
 const {server}=createEngineFixture(label);server.listen(port,'127.0.0.1',()=>console.log('Fixture only: http://127.0.0.1:'+port+'/infer'));
 const stop=()=>{server.closeAllConnections();server.close();};process.once('SIGINT',stop);process.once('SIGTERM',stop);
}
