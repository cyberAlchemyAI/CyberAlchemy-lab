import {createHttpInvocation} from '../../implementation/dist/http-invocation-adapter.js';
// Generated invocation/stream dependencies only. Open questions: stream/PLAN.md.
const fail=code=>{throw Object.assign(new Error(code),{code});};
export function createDispatcher({invocationFactory,streamFactory,bindings,fetchImpl=fetch,timeoutMs=5000,maxBytes=65536,maxConcurrent=2,allowLoopbackFixtures=false}){
 if(typeof invocationFactory!=='function')fail('INVOCATION_BINDING_REQUIRED');
 const dependencies=createHttpInvocation({bindings,fetchImpl,allowLoopbackFixtures});
 if(streamFactory)dependencies.stream=session=>streamFactory({...session,observe:event=>session.observe?.({...event,...(event.value?.usage?{usage:event.value.usage}:{})})});
 const invoke=invocationFactory(dependencies,{timeoutMs,maxBytes,maxConcurrent});
 return ({request,catalog,messages,signal,observe,beforeAttempt})=>{
  if(request?.stream&&!dependencies.stream)return Promise.reject(Object.assign(Error('STREAMING_NOT_SUPPORTED'),{code:'STREAMING_NOT_SUPPORTED'}));
  return invoke({request,catalog,messages},{signal,observe,beforeAttempt});
 };
}
