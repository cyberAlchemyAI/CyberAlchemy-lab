import {lstatSync,readdirSync,readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {publishAtomicDirectory} from '../generation/atomic-publication.js';
import {captureJson,dataDigest,sha256,reject} from './contracts.js';
import {assertProfileSnapshotCurrent,type ProfileSnapshot,type ProfileSnapshotV2} from './loader.js';
import {assertBusinessAuthoringSnapshotCurrent,type BusinessAuthoringSnapshot} from './loader-v3.js';
import {assertNativeQualificationCurrent,type NativeQualification} from './native-check.js';


type NativeSnapshot=ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot;
function isAuthoring(snapshot:NativeSnapshot):snapshot is BusinessAuthoringSnapshot{return 'kind' in snapshot&&snapshot.kind==='business-authoring-snapshot';}
function assertNativeSnapshot(snapshot:NativeSnapshot):void {if(isAuthoring(snapshot))assertBusinessAuthoringSnapshotCurrent(snapshot);else assertProfileSnapshotCurrent(snapshot);}

/** Private atomic no-replace publication, exact manifests, no recursive cleanup.
 * Open questions: docs/PROFILE-GENERATION.md; release/publication remain held. */
const MANIFEST='.profile-manifest.json',COMPLETE='.profile-complete.json';
export function completeProfileOutput(snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot,files:Readonly<Record<string,string>>,qualification:NativeQualification,target:string):void {
 assertNativeQualificationCurrent(qualification,files,snapshot);const captured=captureJson(files) as Readonly<Record<string,string>>;
 if(Object.hasOwn(captured,MANIFEST)||Object.hasOwn(captured,COMPLETE))reject('PROFILE_OUTPUT_RESERVED','/','completion metadata is coordinator-owned');
 const inventory=Object.fromEntries(Object.keys(captured).sort().map(p=>[p,{sha256:sha256(captured[p]!),bytes:Buffer.byteLength(captured[p]!)}]));
 const manifest={schema_version:'craft.profile-output-manifest/v1',lock_sha256:snapshot.lock.lock_sha256,qualification_sha256:qualification.receipt_sha256,files:inventory,authority_effect:'none'};
 const marker={schema_version:'craft.profile-output-complete/v1',manifest_sha256:dataDigest(manifest),lock_sha256:snapshot.lock.lock_sha256,qualification_sha256:qualification.receipt_sha256,authority_effect:'none'};
 const artifacts=[...Object.entries(captured).map(([relative_path,content])=>({relative_path,content})),{relative_path:MANIFEST,content:JSON.stringify(manifest,null,2)+'\n'},{relative_path:COMPLETE,content:JSON.stringify(marker,null,2)+'\n'}];
 publishAtomicDirectory(path.resolve(target),artifacts,'.domainspec-profile-',()=>assertNativeQualificationCurrent(qualification,files,snapshot),isAuthoring(snapshot)?{preserveFailedStage:true}:undefined);
 verifyProfileOutput(snapshot,target,captured);assertNativeSnapshot(snapshot);
}
export function verifyProfileOutput(snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot,target:string,expectedFiles:Readonly<Record<string,string>>):void {
 assertNativeSnapshot(snapshot);const root=path.resolve(target);if(realpathSync(root)!==root||!lstatSync(root).isDirectory())reject('PROFILE_OUTPUT_PATH','/','real owned directory required');
 let manifest:any,marker:any;try{manifest=JSON.parse(readFileSync(path.join(root,MANIFEST),'utf8'));marker=JSON.parse(readFileSync(path.join(root,COMPLETE),'utf8'));}catch{return reject('PROFILE_OUTPUT_INCOMPLETE','/','complete bound marker and manifest required');}
 if(manifest.schema_version!=='craft.profile-output-manifest/v1'||marker.schema_version!=='craft.profile-output-complete/v1'||manifest.lock_sha256!==snapshot.lock.lock_sha256||marker.lock_sha256!==manifest.lock_sha256||marker.manifest_sha256!==dataDigest(manifest)||marker.qualification_sha256!==manifest.qualification_sha256)reject('PROFILE_OUTPUT_MARKER','/','marker does not bind exact manifest/source/qualification');
 const expectedInventory=Object.fromEntries(Object.keys(expectedFiles).sort().map(p=>[p,{sha256:sha256(expectedFiles[p]!),bytes:Buffer.byteLength(expectedFiles[p]!)}]));if(dataDigest(manifest.files)!==dataDigest(expectedInventory))reject('PROFILE_OUTPUT_PLAN_MISMATCH','/','output must match the independently reconstructed qualified plan');
 const actual:string[]=[],actualDirs:string[]=[];
 const walk=(directory:string)=>{for(const name of readdirSync(directory)){const file=path.join(directory,name),stat=lstatSync(file);if(stat.isSymbolicLink())reject('PROFILE_OUTPUT_SYMLINK',name,'symlinks cannot qualify output');if(stat.isDirectory()){actualDirs.push(path.relative(root,file).split(path.sep).join('/'));walk(file);}else if(stat.isFile())actual.push(path.relative(root,file).split(path.sep).join('/'));else reject('PROFILE_OUTPUT_SPECIAL',name,'regular files required');}};walk(root);
 const requiredDirs=new Set<string>();for(const relative of Object.keys(expectedFiles)){const parts=relative.split('/');parts.pop();while(parts.length){requiredDirs.add(parts.join('/'));parts.pop();}}if(JSON.stringify(actualDirs.sort())!==JSON.stringify([...requiredDirs].sort()))reject('PROFILE_OUTPUT_INVENTORY','/','foreign output directory');
 const expected=[...Object.keys(manifest.files),MANIFEST,COMPLETE].sort();if(JSON.stringify(actual.sort())!==JSON.stringify(expected))reject('PROFILE_OUTPUT_INVENTORY','/','missing or foreign output artifacts');
 for(const [relative,entry]of Object.entries(manifest.files) as [string,any][]){if(path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(p=>!p||p==='.'||p==='..'))reject('PROFILE_OUTPUT_PATH',relative,'manifest path escapes owned output');const bytes=readFileSync(path.join(root,relative));if(entry.sha256!==sha256(bytes)||entry.bytes!==bytes.length)reject('PROFILE_OUTPUT_ARTIFACT_STALE',relative,'output content differs from manifest');}
 assertNativeSnapshot(snapshot);
}
