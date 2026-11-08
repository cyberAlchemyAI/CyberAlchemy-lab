import {RECONCILED_SOURCE_SNAPSHOT} from './reconciled-sources.generated.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';

export const RECONCILED_SOURCE_CAPSULE_SHA256='39ac2a9238417e27091a41a0e0a587806f7338927ce82abe229803fad0a62c00';
export const MINIMAL_VALUE_CONTEXT_SHA256='187e86508003eab90669ebe31a7f6268d394cd4ba5182fb8a6687ca11e4213dc';
export type ReconciledSourceId=typeof RECONCILED_SOURCE_SNAPSHOT.sources[number]['id'];
const fail=(m:string):never=>{throw new TypeError('DS_RECONCILED_SOURCES:'+m);};
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
/** Validate against the selected compiler capsule, not a caller-supplied digest. */
export function validateReconciledSourceCapsule(value:unknown) {
 assertInterfaceData(value);
 if(!value||typeof value!=='object'||Array.isArray(value))return fail('capsule');
 const v=value as typeof RECONCILED_SOURCE_SNAPSHOT;
 if(canonicalJson(Object.keys(v).sort())!==canonicalJson(['schema_version','authority_effect','selection_sha256','sources','capsule_sha256'].sort()))fail('closed capsule');
 const {capsule_sha256,...body}=v;
 if(capsule_sha256!==RECONCILED_SOURCE_CAPSULE_SHA256||sha256(canonicalJson(body))!==RECONCILED_SOURCE_CAPSULE_SHA256)fail('selected capsule drift');
 for(const row of v.sources)if(sha256(row.content)!==row.sha256||Buffer.byteLength(row.content)!==row.size_bytes)fail('source content drift');
 return freeze(structuredClone(v));
}
const capsule=validateReconciledSourceCapsule(RECONCILED_SOURCE_SNAPSHOT);
export function getReconciledSourceCapsule(){return capsule;}
export function getReconciledSource(id:ReconciledSourceId):string {
 if(typeof id!=='string')return fail('source ID');
 return capsule.sources.find(s=>s.id===id)?.content??fail('unknown source:'+id);
}
export function findReconciledSourceByDigest(digest:string) {
 return capsule.sources.find(s=>s.sha256===digest)??null;
}
