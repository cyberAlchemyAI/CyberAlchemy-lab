import {createServer} from 'node:http';
import {Readable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
// Generic socket adapter. Open questions: ../SERVICE.md.
// Cancel body consumption without destroying the socket before an error response is sent.
function incomingBody(req:import('node:http').IncomingMessage){
 let cleanup=()=>{};
 return new ReadableStream({
  start(controller){
   const data=(chunk:Buffer)=>{controller.enqueue(chunk);if((controller.desiredSize??0)<=0)req.pause();};
   const end=()=>{cleanup();controller.close();};
   const error=(error:Error)=>{cleanup();controller.error(error);};
   cleanup=()=>{req.off('data',data);req.off('end',end);req.off('error',error);};
   req.pause();req.on('data',data);req.once('end',end);req.once('error',error);
  },
  pull(){req.resume();},
  cancel(){cleanup();req.pause();}
 });
}

// Incoming client disconnects cancel provider work; pipeline honors socket backpressure.
export function createNodeServiceServer(handle:(request:Request)=>Promise<Response>,errorResponse:(error:any)=>Promise<Response>){
 return createServer(async(req,res)=>{
  const controller=new AbortController();
  const abort=()=>controller.abort();
  const closed=()=>{if(!res.writableEnded)abort();};
  req.once('aborted',abort);res.once('close',closed);
  try{
   const method=req.method??'GET';
   const request=new Request(new URL(req.url??'/','http://localhost'),{method,headers:req.headers as HeadersInit,signal:controller.signal,...(!['GET','HEAD'].includes(method)?{body:incomingBody(req),duplex:'half'}:{})} as RequestInit);
   const response=await handle(request);
   await request.body?.cancel().catch(()=>{});
   if(!req.readableEnded&&request.body)res.setHeader('connection','close');
   res.writeHead(response.status,Object.fromEntries(response.headers));
   if(response.body)await pipeline(Readable.fromWeb(response.body as any),res,{signal:controller.signal});else res.end();
  }catch{
   if(!res.headersSent&&!res.destroyed){try{const response=await errorResponse({code:''});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(await response.text());}catch{res.writeHead(500);res.end();}}
   else res.destroy();
  }finally{req.off('aborted',abort);res.off('close',closed);}
 });
}
