import {captureJson,canonicalJson,dataDigest,validateShape,reject,type ProfileLock} from './contracts.js';

/** Byte-bound portable lock; this is currentness evidence, not admission.
 * Open questions: docs/PROFILE-AUTHORING.md. */
export type LockInput=Omit<ProfileLock,'schema_version'|'lock_sha256'>;
export function createProfileLock(input:LockInput):ProfileLock {
 const packages=[...input.packages].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 if(new Set(packages.map(p=>p.id)).size!==packages.length)reject('PROFILE_LOCK_CONFLICT','/packages','one version/digest per identity required');
 const body={schema_version:'craft.profile-lock/v1' as const,engine_sha256:input.engine_sha256,tool_sha256:input.tool_sha256,source_sha256:input.source_sha256,packages};
 return validateShape<ProfileLock>('lock',{...body,lock_sha256:dataDigest(body)});
}
export function validateProfileLock(input:unknown):ProfileLock {
 const lock=validateShape<ProfileLock>('lock',input);const {lock_sha256,...body}=lock;
 if(dataDigest(body)!==lock_sha256)reject('PROFILE_LOCK_DIGEST','/lock_sha256','lock content changed');
 if(new Set(lock.packages.map(p=>p.id)).size!==lock.packages.length)reject('PROFILE_LOCK_CONFLICT','/packages','duplicate selected package');
 if(lock.packages.some((p,i)=>i>0&&lock.packages[i-1]!.id>=p.id))reject('PROFILE_LOCK_ORDER','/packages','canonical package ordering required');
 return lock;
}
export function assertProfileLockMatches(actual:ProfileLock,expected:unknown):void {
 const pinned=validateProfileLock(expected);
 if(canonicalJson(captureJson(actual))!==canonicalJson(captureJson(pinned)))reject('PROFILE_LOCK_STALE','/','source/package/core/tool closure differs from pinned lock');
}
