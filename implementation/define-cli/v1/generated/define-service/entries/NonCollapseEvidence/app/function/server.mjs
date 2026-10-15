import {createServer} from 'node:http';
import {handler} from './index.mjs';
const server=createServer(async(req,res)=>{try{const request=new Request('http://localhost'+req.url,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:req,duplex:'half'}:{})});const out=await handler(request,process.env);res.writeHead(out.status,Object.fromEntries(out.headers));res.end(Buffer.from(await out.arrayBuffer()));}catch{res.writeHead(500,{'content-type':'application/json'});res.end('{"error":"FUNCTION_INTERNAL"}');}});
server.requestTimeout=30000;server.headersTimeout=15000;
server.listen(Number(process.env.PORT??3000),process.env.HOST??'127.0.0.1',()=>console.log(JSON.stringify({address:server.address()})));
