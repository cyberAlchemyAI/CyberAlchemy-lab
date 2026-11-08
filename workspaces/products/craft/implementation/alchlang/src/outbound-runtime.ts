// Generic sequential composition. Contract and Open Questions: ../OUTBOUND.md.
const fail=(code:string):never=>{throw Object.assign(new Error(code),{code});};
const clone=(v:any)=>JSON.parse(JSON.stringify(v));
const at=(scope:any,ref:string)=>ref.split('.').reduce((v,k)=>v!=null&&Object.hasOwn(v,k)?v[k]:undefined,scope);
const argument=(scope:any,args:any)=>typeof args==='string'?at(scope,args):Object.fromEntries(Object.entries(args).map(([k,p])=>[k,at(scope,p as string)]).filter(([,v])=>v!==undefined));
export function createOutbound(contract:any,modules:Record<string,any>,dependencies:any,options:any={}){
 modules={...modules};
 const c=clone(contract),{http,resolveBinding,stream,clock={now:()=>performance.now(),schedule:(f:any,ms:number)=>{const t=setTimeout(f,ms);return ()=>clearTimeout(t);}}}=dependencies;
 if(!http||typeof http.sendOnce!=='function'||typeof resolveBinding!=='function'||Object.keys(c.modules).some(k=>typeof modules[k]!=='function'))fail('INVOCATION_BINDING_REQUIRED');
 const limits={deadline_ms:options.timeoutMs??c.limits.deadline_ms,max_bytes:options.maxBytes??c.limits.max_bytes,max_concurrent:options.maxConcurrent??c.limits.max_concurrent};
 for(const [k,v]of Object.entries(limits))if(!Number.isSafeInteger(v)||v<1||v>c.limits[k])fail('INVALID_LIMITS');
 let active=0;
 return async function invoke(input:any,{signal,observe,beforeAttempt}:any={}){
  if(signal?.aborted)fail('CANCELLED');if(active>=limits.max_concurrent)fail('OVERLOADED');active++;
  const notify=(event:any)=>{try{observe?.(event);}catch{}};
  const controller=new AbortController(),deadline=clock.now()+limits.deadline_ms;
  const check=()=>{if(!controller.signal.aborted&&clock.now()>=deadline)controller.abort('deadline');if(controller.signal.aborted)fail(controller.signal.reason==='cancelled'?'CANCELLED':'DEADLINE_EXCEEDED');};
  const cancel=()=>controller.abort('cancelled');signal?.addEventListener('abort',cancel,{once:true});
  const stopTimer=clock.schedule(()=>controller.abort('deadline'),limits.deadline_ms);
  let abortListener:any,attempt:any;const aborted=new Promise((_,reject)=>{abortListener=()=>{if(attempt)void attempt.cancel(controller.signal.reason==='cancelled'?'cancelled':'deadline').catch(()=>{});reject(Object.assign(Error(controller.signal.reason==='cancelled'?'CANCELLED':'DEADLINE_EXCEEDED'),{code:controller.signal.reason==='cancelled'?'CANCELLED':'DEADLINE_EXCEEDED'}));};controller.signal.addEventListener('abort',abortListener,{once:true});});
  let readyResolve:any;const ready=new Promise(resolve=>{readyResolve=resolve;});
  const work=(async()=>{
   const scope:any={input:clone(input)},policies=new Map<string,unknown>();
   for(const s of c.steps){
    check();
    if(s.kind==='local'){
     try{scope[s.id]=clone(await modules[s.module](argument(scope,s.args),{}, {localOnly:true,signal:controller.signal}));}catch{check();fail(s.error);}
     check();if(s.accept!==undefined&&scope[s.id].status!==s.accept)fail(s.reject);
    }else if(s.kind==='binding'){
     const selected={id:at(scope,s.binding_id),version:at(scope,s.version),model:at(scope,s.model)};
     const binding=resolveBinding(selected);if(!binding)fail('BINDING_MISMATCH');scope[s.id]=clone(binding);
     // Identity comes from authored references; secrets never enter the scope.
     policies.set(s.id,at(scope,s.policy));
    }else if(s.kind==='http'){
     const body=clone(at(scope,s.body));for(const k of s.omit)delete body[k];if(Buffer.byteLength(JSON.stringify(body))>limits.max_bytes)fail('REQUEST_TOO_LARGE');
     const binding=scope[s.binding];check();if(at(scope,s.stream)&&typeof stream!=='function')fail('STREAMING_NOT_SUPPORTED');
     if(beforeAttempt)await beforeAttempt({id:binding.id,version:binding.version,model:binding.model,policyVersion:policies.get(s.binding)});
     check();
     notify({type:'attempt_started',binding_id:binding.id,binding_version:binding.version,policy_version:policies.get(s.binding)});
     attempt=http.sendOnce({id:binding.id,version:binding.version,model:binding.model},body,{deadline,signal:controller.signal});
     let exchange;try{exchange=await attempt.response;}catch{check();fail('PROVIDER_TRANSPORT_FAILED');}
     check();if(!Number.isInteger(exchange.status)||exchange.status<200||exchange.status>299){await attempt.cancel('invalid-response');fail('PROVIDER_STATUS');}
     if(at(scope,s.stream)){
      const session=stream({exchange,cancelTransport:()=>attempt.cancel('invalid-response'),identity:argument(scope,s.identity),signal:controller.signal,abort:(reason:any)=>controller.abort(reason),maxBytes:limits.max_bytes,observe:notify});
      readyResolve(session.response);await session.finished;return;
     }
     const chunks:Uint8Array[]=[];let size=0;
     for await(const chunk of exchange.body){check();if(!(chunk instanceof Uint8Array))fail('INVALID_PROVIDER_RESPONSE');size+=chunk.byteLength;if(size>limits.max_bytes)fail('RESPONSE_TOO_LARGE');chunks.push(chunk);}
     check();try{scope[s.id]=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(chunks)));}catch{fail('INVALID_PROVIDER_RESPONSE');}
    }
   }
   check();return clone(at(scope,c.output));
  })();
  // Cleanup is awaited only by custody, never by the caller deadline race.
  work.finally(async()=>{let settled=false;try{if(attempt){void attempt.cancel(controller.signal.reason==='deadline'?'deadline':controller.signal.aborted?'cancelled':'invalid-response').catch(()=>{});await attempt.settled;}settled=true;}finally{stopTimer();signal?.removeEventListener('abort',cancel);controller.signal.removeEventListener('abort',abortListener);if(settled){active--;notify({type:'transport_settled'});}}}).catch(()=>{});
  return await Promise.race([work,aborted,ready]);
 };
}
