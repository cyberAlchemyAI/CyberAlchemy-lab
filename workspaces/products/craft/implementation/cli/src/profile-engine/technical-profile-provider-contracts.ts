/** Finite source Mapping -> existing application provider-stage selections.
 * No callbacks, effects or new projection evaluator. Open Questions:
 * docs/TECHNICAL-PROFILE-SOURCE.md#open-questions. */
import {captureJson,reject} from './contracts.js';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
function fail(message:string):never{return reject('TECHNICAL_PROFILE_PROVIDER_STAGE','provider-stage',message);}
const record=(v:unknown):v is Record<string,any>=>!!v&&typeof v==='object'&&!Array.isArray(v);
const text=(v:unknown)=>typeof v==='string'&&v.length>0&&v.length<=256;
function projection(value:unknown,depth=0):void{
 if(!record(value)||depth>12||Object.keys(value).length>64)fail('bounded original projection record required');
 for(const [key,v]of Object.entries(value)){if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key)||!record(v))fail('actual projection field descriptor required');const keys=Object.keys(v).sort().join(',');
  if(keys==='literal'){captureJson(v.literal);continue;}
  if(keys==='from'||keys==='maybeFrom'||keys==='encoding,from'){const path=v.from??v.maybeFrom;if(typeof path!=='string'||path.length>512||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(path))fail('finite original projection path required');if(keys==='encoding,from'&&!['canonical-json','sha256-utf8','unix-seconds-utc','unix-seconds-milliseconds-number','unix-milliseconds-number'].includes(v.encoding))fail('unsupported original projection codec');continue;}
  if(keys==='fields'){projection(v.fields,depth+1);continue;}
  if(keys==='each,fields'){if(typeof v.each!=='string'||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(v.each))fail('finite collection projection path');projection(v.fields,depth+1);continue;}
  fail('original projection DSL only; executable expressions forbidden');
 }
}
export interface TechnicalProviderStageSelection {readonly binding:string;readonly selection:Readonly<Record<string,any>>}
export function validateTechnicalProviderStages(value:unknown,bindings:Readonly<Record<string,any>>):readonly TechnicalProviderStageSelection[]{
 if(value===undefined)return Object.freeze([]);const data=captureJson(value);if(!Array.isArray(data)||data.length>16)fail('bounded provider stage list required');const used=new Set<string>();
 for(const raw of data){if(!record(raw)||Object.keys(raw).sort().join(',')!=='binding,selection'||!text(raw.binding)||used.has(raw.binding)||bindings[raw.binding]?.kind!=='native'||!record(raw.selection))fail('one original source-selected native binding per provider stage');used.add(raw.binding);const s=raw.selection;
  const required=['previousOrdinal','operation','slotId','resourceId','action','policyId','payload','receipt','logicalIdentity','identityMode'],allowed=[...required,'provider','account','readCurrent','recipient','retryPolicy'];if(required.some(k=>!Object.hasOwn(s,k))||Object.keys(s).some(k=>!allowed.includes(k)))fail('closed original provider-stage selection required');
  const ordinal=typeof s.previousOrdinal==='string'&&/^[1-9][0-9]*$/.test(s.previousOrdinal)?Number(s.previousOrdinal):s.previousOrdinal;if(!Number.isSafeInteger(ordinal)||ordinal<1||ordinal>16)fail('bounded original previous stage ordinal');for(const key of ['operation','slotId','resourceId','action','policyId'])if(!text(s[key]))fail('finite original provider-stage identity required');if(s.identityMode!=='stable-command'||!record(s.logicalIdentity)||!['parentCommand','callSite','occurrence'].every(k=>Object.hasOwn(s.logicalIdentity,k)))fail('stable-command authored parent/callsite/occurrence projection required');if(s.readCurrent!==undefined&&typeof s.readCurrent!=='boolean')fail('explicit read-only classification');if(s.retryPolicy!==undefined&&s.retryPolicy!==null&&(!record(s.retryPolicy)||Object.keys(s.retryPolicy).sort().join(',')!=='maxAttempts,mode'||s.retryPolicy.mode!=='proven-no-effect'||!(typeof s.retryPolicy.maxAttempts==='string'&&/^[1-9][0-9]*$/.test(s.retryPolicy.maxAttempts)||typeof s.retryPolicy.maxAttempts==='number'&&Number.isSafeInteger(s.retryPolicy.maxAttempts)&&s.retryPolicy.maxAttempts>=1)||Number(s.retryPolicy.maxAttempts)>16))fail('explicit original proven-no-effect retry strategy only');for(const key of ['provider','account','recipient'])if(s[key]!==undefined&&!text(s[key]))fail('finite selected operator identity');projection(s.payload);projection(s.receipt);projection(s.logicalIdentity);
 }
 return coreFreeze(data) as unknown as readonly TechnicalProviderStageSelection[];
}
