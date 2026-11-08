import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {mkdtempSync,readFileSync,rmSync,statSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {buildFunction} from './function-builder.js';

export async function traceFunction(sourcePath:string,inputPath:string){
 if(statSync(inputPath).size>1048576)throw Error('TRACE_INPUT_LIMIT');
 const input=JSON.parse(readFileSync(inputPath,'utf8'));
 const temporary=mkdtempSync(path.join(os.tmpdir(),'alch-trace-'));
 try{
  const bundle=path.join(temporary,'bundle');await buildFunction(sourcePath,bundle);
  const api=await import(pathToFileURL(path.join(bundle,(await loadDomainSpecCompiler()).applicationPaths.entry)).href);
  if(typeof api.invokeWithTrace!=='function')throw Error('TRACE_DECLARATIVE_PROFILE_REQUIRED');
  return await api.invokeWithTrace(input);
 }finally{rmSync(temporary,{recursive:true,force:true});}
}
