import {createServer} from 'node:https';
import {createNodeServiceListener} from '../../../../implementation/dist/node-service-host.js';
// Local direct-TLS trust boundary. Open Questions: PLAN.md.
export function createHttpsIngress({origin,key,cert,handler}){
 const url=new URL(origin);
 if(url.origin!==origin||url.protocol!=='https:'||url.hostname!=='localhost'||!url.port||!key||!cert||typeof handler!=='function')throw Error('HTTPS_INGRESS_BINDING');
 const listener=createNodeServiceListener(request=>{
  const path=new URL(request.url);return handler(new Request(origin+path.pathname+path.search,request));
 },async()=>Response.json({error:'INTERNAL_ERROR'},{status:500}));
 const server=createServer({key,cert,minVersion:'TLSv1.2',maxVersion:'TLSv1.3',handshakeTimeout:5000,maxHeaderSize:8192},(req,res)=>{
  const names=req.rawHeaders.filter((_,i)=>i%2===0).map(x=>x.toLowerCase());
  if(!req.socket.encrypted||req.headers.host!==url.host||names.filter(x=>x==='host').length!==1||names.some(x=>x==='forwarded'||x.startsWith('x-forwarded-'))||!req.url?.startsWith('/')||req.url.startsWith('//')){
   res.writeHead(400,{'content-type':'application/json','cache-control':'no-store','connection':'close'});res.end('{"error":"INVALID_INGRESS"}');return;
  }
  void listener(req,res);
 });
 server.requestTimeout=10000;server.headersTimeout=5000;server.maxHeadersCount=40;server.maxRequestsPerSocket=100;
 return server;
}
