import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {verifier,active,configuration,validateProfile} from '../../../../../../../../auth-foundation/implementation/authentication-https/src/identity.mjs';
// Trusted adapter, no network authorization input. Open Questions: PLAN.md.
const fail=code=>{throw Object.assign(new Error(code),{code});};
const valid=s=>typeof s==='string'&&s.length>0&&Buffer.byteLength(s)<=256&&!/[\x00-\x1f\x7f]/.test(s);
export function createTenantAuthorizer({binary,policy}){
 if(![binary,policy].every(x=>typeof x==='string'&&x.startsWith('/')))throw Error('AUTH_FOUNDATION_BINDING');
 return async(identity,tenant,permissions)=>{
  const input=JSON.stringify({identity,tenant,permissions});if(Buffer.byteLength(input)>262144)fail('FORBIDDEN');
  return new Promise(resolve=>{
   const child=spawn(binary,[policy],{stdio:['pipe','pipe','pipe']});let output='',done=false;
   const finish=value=>{if(!done){done=true;clearTimeout(timer);resolve(value);}};
   const timer=setTimeout(()=>{child.kill('SIGKILL');finish([]);},2000);
   child.on('error',()=>finish([]));child.stdin.on('error',()=>finish([]));child.stderr.resume();
   child.stdout.on('data',chunk=>{output+=chunk;if(output.length>16384){child.kill('SIGKILL');finish([]);}});
   child.on('close',code=>{try{const r=JSON.parse(output);finish(code===0&&Object.keys(r).join(',')==='decisions'&&Array.isArray(r.decisions)&&r.decisions.length===permissions.length&&r.decisions.every(x=>typeof x==='boolean')?r.decisions:[]);}catch{finish([]);}});
   child.stdin.end(input);
  });
 };
}
// Injection is a trusted application boundary, also used by isolated signed-token tests.
export function createTenantSecurityPort({verifyToken,assertActive,authorize}){
 if(![verifyToken,assertActive,authorize].every(x=>typeof x==='function'))throw Error('AUTH_FOUNDATION_BINDING');
 async function authenticate(request){
  try{
   const header=request.headers.get('authorization')??'';if(!/^Bearer [^\s,]+$/.test(header)||header.length>16007)fail('UNAUTHENTICATED');
   const token=header.slice(7),payload=await verifyToken(token);await assertActive(token,payload);
   const kind=payload.azp==='prototype-browser'?'human':payload.azp==='prototype-service'?'service':null;
   const identity={issuer:payload.iss,subject:payload.sub,kind,client:payload.azp,expires_at:payload.exp,jti:payload.jti};
   if(![identity.issuer,identity.subject,identity.kind,identity.client,identity.jti].every(valid)||!Number.isSafeInteger(identity.expires_at)||identity.expires_at<=Math.floor(Date.now()/1000))fail('UNAUTHENTICATED');
   const tenant=request.headers.get('x-tenant-id');if(typeof tenant!=='string'||!/^[-A-Za-z0-9_]{1,128}$/.test(tenant))fail('FORBIDDEN');
   if(request.signal.aborted)fail('CANCELLED');
   return {identity,tenant,token};
  }catch(error){if(error.code==='FORBIDDEN'||error.code==='CANCELLED')throw error;fail('UNAUTHENTICATED');}
 }
 async function check(context,permissions){
  try{
   const payload=await verifyToken(context.token);await assertActive(context.token,payload);
   if(payload.iss!==context.identity.issuer||payload.sub!==context.identity.subject||payload.jti!==context.identity.jti||payload.azp!==context.identity.client||payload.exp!==context.identity.expires_at)fail('FORBIDDEN');
   const decisions=await authorize(context.identity,context.tenant,permissions);
   if(!Array.isArray(decisions)||decisions.length!==permissions.length||decisions.some(x=>typeof x!=='boolean'))fail('FORBIDDEN');
   return decisions;
  }catch{fail('FORBIDDEN');}
 }
 const scope=context=>createHash('sha256').update(JSON.stringify([context.tenant,context.identity.issuer,context.identity.subject,context.identity.kind])).digest('hex');
 return {authenticate,check,scope};
}
export function createAuthFoundation({profile,binary,policy}={}){
 if(!profile)throw Error('AUTH_FOUNDATION_BINDING');profile=structuredClone(profile);validateProfile(profile);const verifyToken=verifier(profile);let config;
 return createTenantSecurityPort({verifyToken,assertActive:async(token,payload)=>{config??=configuration(profile,true).catch(error=>{config=undefined;throw error;});await active(await config,token,payload);},authorize:createTenantAuthorizer({binary,policy})});
}
