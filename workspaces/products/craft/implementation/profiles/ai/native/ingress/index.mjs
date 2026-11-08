/** W01 raw Request authentication -> original generated command/inbox commit.
 * This module owns no listener, business transaction or second message journal.
 * Open Questions: README.md#open-questions. */
import {createHmac,timingSafeEqual} from 'node:crypto';
import {assert,canonical,capture,closed,count,freeze,sha256,text} from '../shared.mjs';
export const INGRESS_ABI='craft.verified-inbound/v1';
const decodedUri=uri=>uri.replace(/%(3A|2F|3F|40|21|24|27|28|29|2A|2C|3B)/gi,hex=>String.fromCharCode(parseInt(hex.slice(1),16)));
export function createVerifiedIngress({mode='manual-authenticated',url,account,entry,identity,clientSecret,serviceActor,commitEvent,assertCommitted,assertCurrent,now=Date.now,maxBytes=65536,timeoutMs=3000,subscriptionTypes=['contact.creation','contact.propertyChange']}){
 assert(['manual-authenticated','hubspot-v3'].includes(mode),'UnsupportedCapability','selected inbound verification profile');const target=new URL(url);assert(target.protocol==='https:'&&!target.username&&!target.password&&!target.hash,'InvalidContract','explicit HTTPS route');for(const [k,v] of Object.entries({account,entry}))text(v,k);for(const f of [commitEvent,assertCommitted,assertCurrent,now])assert(typeof f==='function','InvalidContract','original generated inbox host port');count(maxBytes,'body bound',1048576);count(timeoutMs,'deadline',10000);assert(maxBytes>0&&timeoutMs>0,'InvalidContract','finite request bounds');
 if(mode==='manual-authenticated')assert(identity?.abi==='craft.credential-actor/v1','ForeignOwner','original credential adapter');else{assert(typeof clientSecret?.current==='function'&&typeof serviceActor==='function','InvalidContract','selected app-secret/service actor ports');assert(Array.isArray(subscriptionTypes)&&subscriptionTypes.length>0&&subscriptionTypes.length<=32,'InvalidContract','finite subscriptions');}
 const identityNumber=(v,name)=>{if(typeof v==='number')assert(Number.isSafeInteger(v)&&v>=0,'InvalidInput','exact event identity');else assert(typeof v==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(v),'InvalidInput','exact event identity');return String(v);};
 const live=()=>{assertCurrent();};
 return Object.freeze({abi:INGRESS_ABI,mode,
  async receive(request){live();assert(request instanceof Request&&request.method==='POST'&&request.url===target.href,'PermissionDenied','exact inbound method/URL');assert(request.headers.get('content-type')?.split(';')[0].trim().toLowerCase()==='application/json','InvalidInput','JSON raw request');
   const contentLength=request.headers.get('content-length');if(contentLength!==null)assert(/^[0-9]+$/.test(contentLength)&&Number(contentLength)<=maxBytes,'ResourceLimit','inbound byte limit');
   const reader=request.body?.getReader();assert(reader,'InvalidInput','raw body required');let timer;const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{reader.cancel().catch(()=>{});const e=new Error('inbound body timeout');e.code='Timeout';reject(e);},timeoutMs);});
   const reading=(async()=>{const chunks=[];let length=0;for(;;){const {done,value}=await reader.read();live();if(done)break;length+=value.byteLength;assert(length<=maxBytes,'ResourceLimit','inbound byte limit');chunks.push(value);}return Buffer.concat(chunks);})();let raw;try{raw=await Promise.race([reading,timeout]);}finally{clearTimeout(timer);await reader.cancel().catch(()=>{});}live();
   let utf8;try{utf8=new TextDecoder('utf-8',{fatal:true}).decode(raw);}catch{assert(false,'InvalidInput','UTF8 inbound body');}
   let credential,providerActor;
   if(mode==='manual-authenticated'){const auth=request.headers.get('authorization');assert(auth?.startsWith('Bearer ')&&auth.length<=16400,'AuthenticationRequired','bearer credential');credential=await identity.verifyCredential(auth.slice(7),{entry});live();}
   else{const timestamp=request.headers.get('x-hubspot-request-timestamp'),signature=request.headers.get('x-hubspot-signature-v3');assert(timestamp&&/^[0-9]{1,16}$/.test(timestamp)&&Number.isSafeInteger(Number(timestamp))&&Math.abs(now()-Number(timestamp))<=300000,'PermissionDenied','inbound replay window');assert(signature&&/^[A-Za-z0-9+/]{43}=$/.test(signature),'PermissionDenied','v3 signature');
    const secret=await clientSecret.current();live();assert(secret&&secret.account===account&&secret.status==='active'&&typeof secret.secret==='string'&&secret.secret.length>=16&&secret.expiresAt>now(),'PermissionDenied','current selected app secret');
    text(secret.revision,'app secret revision');assert(Number.isSafeInteger(secret.expiresAt),'InvalidContract','finite credential expiry');
    const expected=createHmac('sha256',secret.secret).update('POST'+decodedUri(target.href)+utf8+timestamp,'utf8').digest(),actual=Buffer.from(signature,'base64');assert(actual.length===expected.length&&timingSafeEqual(expected,actual),'PermissionDenied','raw-byte signature mismatch');
    const again=await clientSecret.current();live();assert(again.revision===secret.revision&&again.account===secret.account&&again.status==='active'&&again.secret===secret.secret&&again.expiresAt>now(),'PermissionDenied','app secret changed during verification');providerActor=await serviceActor({provider:'hubspot',account,entry,secretRevision:secret.revision});live();
   }
   let parsed;try{parsed=capture(JSON.parse(utf8),{maxBytes,maxDepth:16});}catch{assert(false,'InvalidInput','bounded inbound JSON');}const batch=Array.isArray(parsed)?parsed:[parsed];assert(batch.length>0&&batch.length<=100,'ResourceLimit','inbound event batch');
   const events=batch.map(value=>{if(mode==='hubspot-v3'){assert(identityNumber(value.portalId,'account')===account&&subscriptionTypes.includes(value.subscriptionType),'PermissionDenied','provider account/subscription');const eventId=identityNumber(value.eventId,'event');const objectId=identityNumber(value.objectId,'object');return {eventId,objectId,body:value};}const v=closed(value,['eventId','payload']);text(v.eventId,'manual event',128);return {eventId:v.eventId,body:v.payload};});
   const results=[];for(const event of events){live();const messageIdentity=sha256(canonical({provider:mode==='hubspot-v3'?'hubspot':'manual-authenticated',account,eventId:event.eventId,entry}));
    const invoke=async actor=>{const receipt=await commitEvent({actor,entry,messageIdentity,event:freeze({source:mode,account,eventId:event.eventId,...(mode==='hubspot-v3'?{objectId:event.objectId}:{}),payload:event.body}),rawSha256:sha256(raw)});live();await assertCommitted(receipt,{entry,messageIdentity});live();return receipt;};
    const receipt=mode==='manual-authenticated'?await identity.withActor(credential,invoke):await invoke(providerActor);results.push({messageIdentity,commitment:'original-generated-inbox-or-command'});
   }
   return freeze({status:200,acknowledgement:'committed',events:results});
  },
 });
}
