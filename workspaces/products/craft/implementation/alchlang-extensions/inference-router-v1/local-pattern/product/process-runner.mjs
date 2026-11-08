import {spawn} from 'node:child_process';
import {createWriteStream} from 'node:fs';
// POSIX process groups keep nested compiler/test workers inside cancellation.
// Open Questions: OPERATOR.md.
export function createRunner({cwd,env,graceMs=500}){
 let current,stopping=false;
 const stop=signal=>{stopping=true;current?.stop(signal);};
 const run=(args,log)=>new Promise((yes,no)=>{
  if(stopping)return no(Error('VALIDATION_CANCELLED'));
  const sink=log?createWriteStream(log,{flags:'wx'}):null;
  const child=spawn(process.execPath,args,{cwd,env,detached:true,stdio:['ignore',sink?'pipe':'inherit',sink?'pipe':'inherit']});
  let failure,timer,closed=false,cleanupDone=true;
  const kill=signal=>{if(child.pid)try{process.kill(-child.pid,signal);}catch(error){if(error.code!=='ESRCH')failure??=error;}};
  const finish=()=>{
   if(!closed||!cleanupDone)return;
   current=null;
   const done=()=>failure?no(failure):yes();
   if(sink&&!sink.destroyed)sink.end(done);else done();
  };
  const cancel=signal=>{
   failure??=Error('VALIDATION_CANCELLED');kill(signal);
   if(timer)return;
   cleanupDone=false;
   timer=setTimeout(()=>{kill('SIGKILL');cleanupDone=true;finish();},graceMs);
  };
  current={stop:cancel};
  if(sink){sink.on('error',error=>{failure=error;cancel('SIGTERM');});child.stdout.pipe(sink,{end:false});child.stderr.pipe(sink,{end:false});}
  child.on('error',error=>{failure=error;});
  child.on('close',(code,signal)=>{if(code!==0)failure??=Error('COMMAND_FAILED: '+(signal??code));closed=true;finish();});
 });
 return {run,stop};
}
