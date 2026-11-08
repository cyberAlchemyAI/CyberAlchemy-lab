import {readFileSync} from 'node:fs';
import {once} from 'node:events';
import {createServer} from './index.mjs';
// Run inside a generated bundle. Open Questions: README.md.
const port=Number(process.argv[3]??3000);
if(!process.argv[2]||!Number.isInteger(port)||port<0||port>65535)throw Error('Usage: node start.mjs /absolute/configuration.json [port]');
const server=createServer(JSON.parse(readFileSync(process.argv[2],'utf8')),process.env);
try{
 server.listen(port,'127.0.0.1');await once(server,'listening');
 console.log('Local inference: http://127.0.0.1:'+server.address().port);
 await new Promise(r=>{const stop=()=>{process.off('SIGINT',stop);process.off('SIGTERM',stop);r();};process.once('SIGINT',stop);process.once('SIGTERM',stop);});
}finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
