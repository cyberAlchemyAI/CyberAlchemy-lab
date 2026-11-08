import {open,mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createEnrollment} from '../../../../../../../../../auth-foundation/implementation/inference-browser/enrollment.mjs';
import {createBrowserOAuth} from '../../../../../../../../../auth-foundation/implementation/inference-browser/oauth.mjs';
import {createBrowserGateway} from '../../../../../../../../../auth-foundation/implementation/inference-browser/gateway.mjs';
import {createTenantSecurityPort,createTenantAuthorizer} from '../auth-foundation.mjs';
import {createProtectedHandler} from '../host.mjs';
import {verifier,active,configuration} from '../../../../../../../../../auth-foundation/implementation/authentication-https/src/identity.mjs';
// Trusted native composition, no issuer or tenant authority in caller JSON. Open Questions: PLAN.md.
export async function createBrowserInference({profile,origin=profile.origin,policyPath,binary,state,...config}){
 profile=structuredClone(profile);
 const readPolicy=async()=>{const file=await open(policyPath,'r');try{const buffer=Buffer.alloc(1048577);let size=0;while(size<buffer.length){const {bytesRead}=await file.read(buffer,size,buffer.length-size,null);if(!bytesRead)break;size+=bytesRead;}if(size>1048576)throw Error('POLICY_BOUND');return JSON.parse(buffer.subarray(0,size).toString('utf8'));}finally{await file.close();}};
 const decide=async(policy,identity,tenant,permissions)=>{const dir=await mkdtemp(join(tmpdir(),'enrollment-policy-'));try{const path=join(dir,'policy.json');await writeFile(path,JSON.stringify(policy),{mode:0o600});return await createTenantAuthorizer({binary,policy:path})(identity,tenant,permissions);}finally{await rm(dir,{recursive:true,force:true});}};
 const enrollment=createEnrollment({readPolicy,decide,state}),api=await configuration(profile,true);
 const security=createTenantSecurityPort({verifyToken:verifier(profile),assertActive:(token,payload)=>active(api,token,payload),authorize:enrollment.authorize});
 const inference=createProtectedHandler({...config,security});
 const handler=createBrowserGateway({origin,oauth:await createBrowserOAuth(profile,{origin}),enrollment,inference,state});
 return {handler,enrollment,close:()=>inference.close(),stateMode:state?.mode??'ephemeral'};
}

// Explicit durable entry point: opening/configuration failures never choose memory.
export async function createDurableBrowserInference({statePath,stateKey,...config}){
 const {openSqliteState}=await import('../../../../../../../../../auth-foundation/implementation/inference-browser/state.mjs');
 const state=openSqliteState({path:statePath,key:stateKey});
 try{const app=await createBrowserInference({...config,state});return {...app,close:()=>{try{app.close();}finally{state.close();}}};}
 catch(error){state.close();throw error;}
}
