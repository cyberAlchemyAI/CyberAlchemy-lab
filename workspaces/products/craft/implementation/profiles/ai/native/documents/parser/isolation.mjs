// Linux x86-64-only boundary. Refuse unavailable primitives; never run unsandboxed.
import {spawn} from 'node:child_process';
import {realpathSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {dirname} from 'node:path';

export const ISOLATION_VERSION = 'linux-bwrap-seccomp-rlimit/v1';
const home = fileURLToPath(new URL('.', import.meta.url));
const require=createRequire(import.meta.url);
const libs = ['libatomic.so.1','libdl.so.2','libm.so.6','libstdc++.so.6','libgcc_s.so.1','libpthread.so.0','libc.so.6'];

// Classic BPF, struct sock_filter; arch must be AUDIT_ARCH_X86_64.
function seccomp() {
  const code=[];
  const emit=(c,jt,jf,k)=>code.push([c,jt,jf,k]);
  emit(0x20,0,0,4); emit(0x15,1,0,0xc000003e); emit(0x06,0,0,0x80000000);
  emit(0x20,0,0,0); emit(0x35,0,1,0x40000000); emit(0x06,0,0,0x80000000);
  // clone3: force libc's clone fallback, where CLONE_THREAD is inspectable.
  emit(0x15,0,1,435); emit(0x06,0,0,0x00050000|38);
  emit(0x15,0,4,56); emit(0x20,0,0,16); emit(0x45,1,0,0x10000);
  emit(0x06,0,0,0x00050000|1); emit(0x06,0,0,0x7fff0000);
  // No sockets (including Unix sockets), process creation, namespaces, kernel APIs,
  // ptrace or filesystem mount changes. Threads remain bounded by address space.
  // Inherited stdio uses Unix socketpairs in Node: allow their I/O/introspection,
  // while creating or connecting any new socket remains impossible.
  for(const n of [41,42,43,49,50,53,57,58,101,155,161,165,166,167,168,169,170,171,172,173,175,176,246,248,249,250,272,288,298,303,304,308,310,311,313,317,321,323,425,426,427,428,429,430,431,432,433,434,438,442]) {
    emit(0x15,0,1,n); emit(0x06,0,0,0x00050000|1);
  }
  emit(0x06,0,0,0x7fff0000);
  const b=Buffer.alloc(code.length*8);
  code.forEach(([c,jt,jf,k],i)=>{b.writeUInt16LE(c,i*8);b[i*8+2]=jt;b[i*8+3]=jf;b.writeUInt32LE(k>>>0,i*8+4);});
  return b;
}

export function runIsolated({nodePath, limits, request, mode='parse'}) {
  if(process.platform!=='linux'||process.arch!=='x64')return Promise.reject(Error('ISOLATION_UNAVAILABLE'));
  const args=[`--as=${limits.memoryBytes}`,`--cpu=${Math.max(1,Math.ceil(limits.timeMs/1000))}`, '--fsize=0','--core=0','--nofile=64','--', '/usr/bin/bwrap',
    '--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv',
    '--ro-bind',realpathSync(nodePath),'/node'];
  for(const name of libs){const p='/usr/lib/x86_64-linux-gnu/'+name;args.push('--ro-bind',realpathSync(p),p);}
  args.push('--ro-bind',realpathSync('/lib64/ld-linux-x86-64.so.2'),'/lib64/ld-linux-x86-64.so.2',
    '--ro-bind',home+'worker.mjs','/app/worker.mjs',
    '--ro-bind',dirname(require.resolve('pdfjs-dist/package.json')),'/app/node_modules/pdfjs-dist',
    '--proc','/proc','--dev','/dev','--remount-ro','/proc','--remount-ro','/dev','--remount-ro','/',
    '--chdir','/app','--as-pid-1','--seccomp','3','/node','--jitless','--disallow-code-generation-from-strings',
    '--max-old-space-size=128','--disable-proto=throw','/app/worker.mjs',mode);
  return new Promise((resolve,reject)=>{
    let child;
    try{child=spawn('/usr/bin/prlimit',args,{stdio:['pipe','pipe','pipe','pipe'],detached:true,env:{}});}catch{reject(Error('ISOLATION_UNAVAILABLE'));return;}
    const chunks=[];let size=0,errSize=0,finished=false,cause=null;
    const kill=(reason)=>{cause??=reason;try{process.kill(-child.pid,'SIGKILL');}catch{child.kill('SIGKILL');}};
    const timer=setTimeout(()=>kill('TIME_LIMIT'),limits.timeMs);
    child.stdout.on('data',b=>{size+=b.length;if(size>limits.outputBytes)kill('OUTPUT_LIMIT');else chunks.push(b);});
    child.stderr.on('data',b=>{errSize+=b.length;if(errSize>65536)kill('OUTPUT_LIMIT');});
    child.on('error',()=>{cause='ISOLATION_UNAVAILABLE';});
    for(const stream of [child.stdin,child.stdio[3]])stream.on('error',()=>{});
    child.stdio[3].end(seccomp());
    child.stdin.end(JSON.stringify(request));
    child.on('close',(code,signal)=>{
      if(finished)return;finished=true;clearTimeout(timer);
      if(cause){reject(Error(cause));return;}
      if(code!==0){reject(Error(signal==='SIGXCPU'?'TIME_LIMIT':'PARSER_RESOURCE_OR_ISOLATION_FAILURE'));return;}
      try{resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));}catch{reject(Error('PARSER_PROTOCOL_INVALID'));}
    });
  });
}
