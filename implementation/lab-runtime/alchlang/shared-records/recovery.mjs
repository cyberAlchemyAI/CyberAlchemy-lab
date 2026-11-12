import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,renameSync,rmSync,chmodSync} from 'node:fs';
import path from 'node:path';
import {gzipSync,gunzipSync} from 'node:zlib';
import {Snapshots} from './snapshots.mjs';
import {Journal} from './journal.mjs';
import {digest} from './verified-projection.mjs';
import {verifyOperationalReadiness} from './readiness.mjs';
const tables={snapshots:['blobs','snapshots','selectors','publications'],journal:['runs','commands','events']};
export function captureRecovery(active,nativeFiles){
 const data={version:1,workspace:active.workspace,selector:active.selector,native:nativeFiles,databases:{}};
 for(const kind of ['snapshots','journal']){
  const store=kind==='snapshots'?new Snapshots(active.database,{readOnly:true}):new Journal(active.journal,{readOnly:true});
  try{data.databases[kind]=Object.fromEntries(tables[kind].map(table=>[table,store.db.prepare('SELECT * FROM '+table).all().map(row=>
   Object.fromEntries(Object.entries(row).map(([k,v])=>[k,v instanceof Uint8Array?{blob:Buffer.from(v).toString('base64')}:v])))]));}
  finally{store.close();}
 }
 return gzipSync(Buffer.from(JSON.stringify(data)),{mtime:0});
}
export async function restoreRecovery(archive,binding,destination,active,trust){
 if(digest(archive)!==binding.sha256||archive.length!==Number(binding.bytes))throw Error('recovery-archive-binding-mismatch');
 const declared=binding.uncompressed_bytes,limit=declared??64*1024*1024;
 if(!Number.isSafeInteger(limit)||limit<1||limit>512*1024*1024)throw Error('recovery-uncompressed-limit-invalid');
 const inflated=gunzipSync(archive,{maxOutputLength:limit});
 if(declared!==undefined&&inflated.length!==declared)throw Error('recovery-uncompressed-size-mismatch');
 const data=JSON.parse(inflated);
 if(data.version!==1||data.workspace!==active.workspace||JSON.stringify(data.selector)!==JSON.stringify(active.selector))throw Error('recovery-selection-mismatch');
 if(existsSync(destination))throw Error('recovery-destination-must-be-new');
 mkdirSync(path.dirname(destination),{recursive:true});
 const staging=mkdtempSync(path.join(path.dirname(destination),'.restore-'));chmodSync(staging,0o700);
 try{
  for(const [name,base64]of Object.entries(data.native)){
   if(!/^(native-store|current-store)\/(config\.json|baseline\.json|HEAD\.json|transactions\/[0-9]{10}\.json)$/.test(name))throw Error('recovery-native-path-invalid');
   const file=path.join(staging,name);mkdirSync(path.dirname(file),{recursive:true,mode:0o700});writeFileSync(file,Buffer.from(base64,'base64'),{mode:0o600});
  }
  for(const kind of ['snapshots','journal']){
   if(Object.keys(data.databases[kind]).some(t=>!tables[kind].includes(t)))throw Error('recovery-table-invalid');
   const store=kind==='snapshots'?new Snapshots(path.join(staging,'snapshots.sqlite'),{trust}):new Journal(path.join(staging,'journal.sqlite'),{trust});
   try{
    store.db.exec('BEGIN IMMEDIATE');
    for(const table of tables[kind]){
     const allowed=new Set(store.db.prepare('PRAGMA table_info('+table+')').all().map(c=>c.name));
     for(const row of data.databases[kind][table]){
      const columns=Object.keys(row);if(columns.some(c=>!allowed.has(c)))throw Error('recovery-column-invalid');
      const values=columns.map(c=>row[c]?.blob?Buffer.from(row[c].blob,'base64'):row[c]);
      store.db.prepare('INSERT INTO '+table+'('+columns.join(',')+') VALUES('+columns.map(()=>'?').join(',')+')').run(...values);
     }
    }store.db.exec('COMMIT');
   }finally{store.close();}
  }
  const restored={...active,database:path.join(staging,'snapshots.sqlite'),journal:path.join(staging,'journal.sqlite'),
   native_store:path.join(staging,'current-store')};
  await verifyOperationalReadiness(restored,trust);
  renameSync(staging,destination);
  return {status:'restored',database:path.join(destination,'snapshots.sqlite'),journal:path.join(destination,'journal.sqlite'),
   native_store:path.join(destination,'current-store'),historical_publication_store:path.join(destination,'native-store'),selector:data.selector};
 }catch(error){rmSync(staging,{recursive:true,force:true});throw error;}
}
