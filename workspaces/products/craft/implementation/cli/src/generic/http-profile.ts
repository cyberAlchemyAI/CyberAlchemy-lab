/** Finite injected HTTP profile over an unchanged checked transaction application.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {GenericHttpProfileV1} from './http-data-v1.js';

export const GENERIC_HTTP_CAPABILITIES=Object.freeze(['injected-http-get','injected-http-post','checked-response-mapping','original-entry-auth'] as const);
const closed=(value:unknown,names:readonly string[])=>!!value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join(',')===[...names].sort().join(',');
const qualified=(value:unknown)=>typeof value==='string'&&value.length<=192&&/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(value);
const property=(value:unknown)=>typeof value==='string'&&value.length<=128&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(value);

export function resolveGenericHttpProfile(text:string,file:string):GenericHttpProfileV1{
 const value=parseCoreCommerceJson(text,file) as any,at={path:file,start:0,end:0};
 if(!closed(value,['schema_version','id','target','realization','capabilities','application_profile','route_prefix','limits','routes'])||value.schema_version!=='craft.generic-http-profile/v1-candidate'||!qualified(value.id)||value.target!=='node-esm'||value.realization!=='injected-request-response/v1-candidate'||!['contracts/selected-profile.json','selected-profile.json'].includes(value.application_profile)||dataDigest(value.capabilities)!==dataDigest(GENERIC_HTTP_CAPABILITIES))fail('InvalidContract',at,'exact finite injected HTTP profile required');
 const ranges:Record<string,readonly [number,number]>={url_bytes:[64,4096],header_bytes:[256,16384],request_bytes:[1,65536],response_bytes:[8192,131072],body_timeout_ms:[1,30000]};
 if(!closed(value.limits,Object.keys(ranges))||Object.entries(ranges).some(([name,[min,max]])=>!Number.isSafeInteger(value.limits[name])||value.limits[name]<min||value.limits[name]>max))fail('InvalidContract',at,'bounded HTTP limits required');
 if(typeof value.route_prefix!=='string'||Buffer.byteLength(value.route_prefix)>128||value.route_prefix!==''&&!/^\/[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*$/.test(value.route_prefix))fail('InvalidContract',at,'literal absolute HTTP prefix required');
 if(!Array.isArray(value.routes)||value.routes.length<1||value.routes.length>64)fail('InvalidContract',at,'bounded HTTP route array required');
 const ids=new Set<string>(),patterns:{method:string;segments:string[]}[]=[];
 for(const route of value.routes){
  if(!closed(route,['id','service','entry','method','path','query','response_mapping'])||![route.id,route.service,route.entry,route.response_mapping].every(qualified)||!['GET','POST'].includes(route.method)||typeof route.path!=='string'||Buffer.byteLength(route.path)>1024||!/^\/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\})(?:\/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\}))*$/.test(route.path))fail('InvalidContract',at,'closed method/path/source route required');
  if(ids.has(route.id))fail('DuplicateSymbol',at,'duplicate HTTP route id');ids.add(route.id);
  const segments=(value.route_prefix+route.path).slice(1).split('/'),placeholders=segments.filter((part:string)=>part.startsWith('{')).map((part:string)=>part.slice(1,-1));
  if(segments.length>16||placeholders.some((name:string)=>!property(name))||new Set(placeholders).size!==placeholders.length||!Array.isArray(route.query)||route.query.length>32||route.query.some((q:any)=>!closed(q,['key','parameter'])||!property(q.key)||!property(q.parameter))||new Set(route.query.map((q:any)=>q.key)).size!==route.query.length||new Set([...placeholders,...route.query.map((q:any)=>q.parameter)]).size!==placeholders.length+route.query.length||route.method==='POST'&&(placeholders.length||route.query.length))fail('InvalidContract',at,'unique complete bounded request carriers required');
  if(patterns.some(other=>other.method===route.method&&other.segments.length===segments.length&&other.segments.every((part,index)=>part===segments[index]||part.startsWith('{')||segments[index]!.startsWith('{'))))fail('InvalidContract',at,'overlapping same-method HTTP routes');
  patterns.push({method:route.method,segments});
 }
 return coreFreeze(value) as GenericHttpProfileV1;
}
