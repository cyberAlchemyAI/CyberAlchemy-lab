/** Process-local SQLite worker custody for one physical service store.
 * This is a prerequisite for recovery, not a WorkSchedule reclaim or dispatch permit.
 * Open Questions: the workflow owner must require this custody on every worker path
 * and couple any reclaim to its own durable schedule transaction. */
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {constants,closeSync,fchmodSync,fstatSync,lstatSync,openSync,realpathSync,unlinkSync,type BigIntStats} from 'node:fs';

export type CommerceWorkerQuiescenceModeV1='create'|'reopen';
export interface CommerceWorkerQuiescenceTargetV1 {
 readonly storePath:string;
 readonly storeId:string;
 readonly schemaSha256:string;
}
export interface CommerceWorkerQuiescenceInspectionV1 {
 readonly storePath:string;
 readonly storeId:string;
 readonly schemaSha256:string;
 readonly lockPath:string;
 readonly qualification:'process-local-exclusive-sqlite-sidecar-custody-only';
 readonly authority_effect:'none';
}
export interface CommerceWorkerQuiescenceOwnerV1 {
 inspect():CommerceWorkerQuiescenceInspectionV1;
 assertCurrent():void;
 close():void;
}
export class CommerceWorkerQuiescenceErrorV1 extends Error {
 constructor(readonly code:'InvalidTarget'|'StorePathRejected'|'LockPathRejected'|'LockIdentityMissing'|'LockIdentityChanged'|'PredecessorActive'|'DisposedOwner',cause?:unknown){super(code,{cause});this.name='CommerceWorkerQuiescenceErrorV1';}
}
function fail(code:CommerceWorkerQuiescenceErrorV1['code'],cause?:unknown):never {throw new CommerceWorkerQuiescenceErrorV1(code,cause);}
function identity(s:BigIntStats):string {return `${s.dev}:${s.ino}`;}
function privateDirectory(s:BigIntStats):void {
 if(!s.isDirectory()||(s.mode&0o077n)!==0n||typeof process.getuid!=='function'||s.uid!==BigInt(process.getuid()))fail('StorePathRejected');
}
function privateFile(s:BigIntStats,code:'StorePathRejected'|'LockPathRejected'):void {
 if(!s.isFile()||(s.mode&0o077n)!==0n||typeof process.getuid!=='function'||s.uid!==BigInt(process.getuid()))fail(code);
}
function locked(error:unknown):boolean {
 return error instanceof Error && /(?:database is locked|SQLITE_BUSY)/i.test(error.message);
}
function validTarget(target:CommerceWorkerQuiescenceTargetV1):void {
 if(!target||typeof target.storePath!=='string'||!path.isAbsolute(target.storePath)||path.normalize(target.storePath)!==target.storePath||
  typeof target.storeId!=='string'||!target.storeId.trim()||typeof target.schemaSha256!=='string'||!/^[a-f0-9]{64}$/.test(target.schemaSha256))fail('InvalidTarget');
}
/** The sidecar is created exactly once for a fresh store. A reopened store must
 * already have it; a missing sidecar cannot establish predecessor custody. */
export function acquireCommerceWorkerQuiescenceV1(target:CommerceWorkerQuiescenceTargetV1,mode:CommerceWorkerQuiescenceModeV1):CommerceWorkerQuiescenceOwnerV1 {
 validTarget(target);
 if(mode!=='create'&&mode!=='reopen')fail('InvalidTarget');
 const storePath=target.storePath;
 const directory=path.dirname(storePath);
 const lockPath=storePath+'.worker-quiescence.sqlite';
 let parent=-1,storeFd=-1,lockFd=-1,db:DatabaseSync|undefined,created=false,createdIdentity:string|undefined,disposed=false;
 try {
  parent=openSync(directory,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW);
  privateDirectory(fstatSync(parent,{bigint:true}));
  if(realpathSync(directory)!==directory)fail('StorePathRejected');
  if(identity(fstatSync(parent,{bigint:true}))!==identity(lstatSync(directory,{bigint:true})))fail('StorePathRejected');
  const anchoredStore=`/proc/self/fd/${parent}/${path.basename(storePath)}`;
  const anchoredLock=`/proc/self/fd/${parent}/${path.basename(lockPath)}`;
  storeFd=openSync(anchoredStore,constants.O_RDONLY|constants.O_NOFOLLOW);
  const storeStat=fstatSync(storeFd,{bigint:true});privateFile(storeStat,'StorePathRejected');
  if(identity(storeStat)!==identity(lstatSync(anchoredStore,{bigint:true})))fail('StorePathRejected');
  lockFd=openSync(anchoredLock,constants.O_RDWR|constants.O_NOFOLLOW|(mode==='create'?constants.O_CREAT|constants.O_EXCL:0),0o600);
  created=mode==='create';
  if(created)fchmodSync(lockFd,0o600);
  const lockStat=fstatSync(lockFd,{bigint:true});privateFile(lockStat,'LockPathRejected');
  if(created)createdIdentity=identity(lockStat);
  if(identity(lockStat)!==identity(lstatSync(anchoredLock,{bigint:true})))fail('LockPathRejected');
  const expected={storePath,storeId:target.storeId,schemaSha256:target.schemaSha256,storeIdentity:identity(storeStat),lockIdentity:identity(lockStat)};
  db=new DatabaseSync(anchoredLock,{enableForeignKeyConstraints:true,enableDoubleQuotedStringLiterals:false,allowExtension:false,timeout:0,defensive:true});
  if(created){
   db.exec('PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA trusted_schema=OFF; PRAGMA busy_timeout=0;');
   db.exec('BEGIN IMMEDIATE; CREATE TABLE custody (id INTEGER PRIMARY KEY CHECK(id=1), store_path TEXT NOT NULL, store_id TEXT NOT NULL, schema_sha256 TEXT NOT NULL, store_identity TEXT NOT NULL, lock_identity TEXT NOT NULL) STRICT;');
   db.prepare('INSERT INTO custody VALUES(1,?,?,?,?,?)').run(storePath,target.storeId,target.schemaSha256,expected.storeIdentity,expected.lockIdentity);
   db.exec('COMMIT');
  }
  try {db.exec('BEGIN EXCLUSIVE');}catch(error){if(locked(error))fail('PredecessorActive',error);throw error;}
  if(!created){
   const journal=db.prepare('PRAGMA journal_mode').get() as {journal_mode?:unknown}|undefined;
   if(journal?.journal_mode!=='delete')fail('LockIdentityChanged');
   db.exec('PRAGMA trusted_schema=OFF; PRAGMA busy_timeout=0;');
  }
  const assertCurrent=()=>{
   if(disposed||!db?.isTransaction)fail('DisposedOwner');
   try {
    privateDirectory(fstatSync(parent,{bigint:true}));
    if(identity(fstatSync(parent,{bigint:true}))!==identity(lstatSync(directory,{bigint:true})))fail('StorePathRejected');
    privateFile(fstatSync(storeFd,{bigint:true}),'StorePathRejected');
    if(identity(fstatSync(storeFd,{bigint:true}))!==expected.storeIdentity||identity(lstatSync(anchoredStore,{bigint:true}))!==expected.storeIdentity)fail('LockIdentityChanged');
    privateFile(fstatSync(lockFd,{bigint:true}),'LockPathRejected');
    if(identity(fstatSync(lockFd,{bigint:true}))!==expected.lockIdentity||identity(lstatSync(anchoredLock,{bigint:true}))!==expected.lockIdentity)fail('LockIdentityChanged');
    const row=db.prepare('SELECT store_path,store_id,schema_sha256,store_identity,lock_identity FROM custody WHERE id=1').get() as Record<string,unknown>|undefined;
    if(!row||row.store_path!==storePath||row.store_id!==target.storeId||row.schema_sha256!==target.schemaSha256||row.store_identity!==expected.storeIdentity||row.lock_identity!==expected.lockIdentity)fail('LockIdentityChanged');
   }catch(error){if(error instanceof CommerceWorkerQuiescenceErrorV1)throw error;fail('LockIdentityMissing',error);}
  };
  assertCurrent();
  const inspection=Object.freeze({storePath,storeId:target.storeId,schemaSha256:target.schemaSha256,lockPath,qualification:'process-local-exclusive-sqlite-sidecar-custody-only' as const,authority_effect:'none' as const});
  return Object.freeze({inspect:()=>{assertCurrent();return inspection;},assertCurrent,close:()=>{
   if(disposed)return;
   disposed=true;
   try{if(db?.isTransaction)db.exec('ROLLBACK');}finally{try{db?.close();}finally{closeSync(lockFd);closeSync(storeFd);closeSync(parent);}}
  }});
 }catch(error){
  try{if(db?.isTransaction)db.exec('ROLLBACK');}catch{}
  try{db?.close();}catch{}
  if(lockFd>=0)try{closeSync(lockFd);}catch{}
  if(storeFd>=0)try{closeSync(storeFd);}catch{}
  if(parent>=0)try{closeSync(parent);}catch{}
  if(created&&createdIdentity)try{if(identity(lstatSync(lockPath,{bigint:true}))===createdIdentity)unlinkSync(lockPath);}catch{}
  if(error instanceof CommerceWorkerQuiescenceErrorV1)throw error;
  if(mode==='reopen'&&error instanceof Error&&'code' in error&&(error as NodeJS.ErrnoException).code==='ENOENT')fail('LockIdentityMissing',error);
  fail('LockPathRejected',error);
 }
}
