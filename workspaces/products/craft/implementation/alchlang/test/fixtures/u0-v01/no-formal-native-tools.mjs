import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {pathToFileURL} from 'node:url';
// Denial-only qualification environment. Never supplies business behavior or results.
// Open Questions: V01 CONTEXT. Ordinary JS syntax modules are not removed.
const core=process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT,traceFile=process.env.CRAFT_V01_NATIVE_TRACE;
if(!core||!traceFile)throw Error('V01 actual core root and trace destination required');
const {ATOMIC_NATIVE}=await import(pathToFileURL(path.join(core,'dist/generation/atomic-publication-native.generated.js')).href);
const trace={external_process_attempts:[],native_loads:[],allowed_native_sha256:ATOMIC_NATIVE.sha256,policy:'No external child process and only the exact existing atomic rename native payload',authority_effect:'none'};
for(const name of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])childProcess[name]=(...args)=>{trace.external_process_attempts.push({method:name,command:String(args[0])});throw Error('V01_OPTIONAL_NATIVE_TOOL_DENIED:'+name);};
syncBuiltinESMExports();const dlopen=process.dlopen;
process.dlopen=function(module,file,...args){const bytes=fs.readFileSync(file),sha=crypto.createHash('sha256').update(bytes).digest('hex');trace.native_loads.push({file:String(file),sha256:sha,allowed:sha===ATOMIC_NATIVE.sha256});if(sha!==ATOMIC_NATIVE.sha256)throw Error('V01_OPTIONAL_NATIVE_ADDON_DENIED');return Reflect.apply(dlopen,process,[module,file,...args]);};
process.once('exit',()=>{fs.writeFileSync(traceFile,JSON.stringify(trace,null,2)+'\n',{flag:'wx',mode:0o600});});
