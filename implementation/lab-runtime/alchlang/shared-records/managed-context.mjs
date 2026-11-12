import {existsSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {Snapshots} from './snapshots.mjs';
import {digest} from './verified-projection.mjs';
function canonical(file){
 if(!file)return null;
 const absolute=path.resolve(file);if(existsSync(absolute))return realpathSync(absolute);
 const parent=path.dirname(absolute);return existsSync(parent)?path.join(realpathSync(parent),path.basename(absolute)):absolute;
}
export function enforceManagedContext(command,flags,request,active,trust){
 if(!active?.execution_selection)return;
 const nativeCommands=['native-apply','native-recover','native-review','create'];
 const dataCommands=['publish','stage','join-init','join-transition'];
 const managed=nativeCommands.includes(command)
  ? canonical(request.store)===canonical(active.native_store)
  : dataCommands.includes(command)&&[active.database,active.journal].some(file=>canonical(flags.db)===canonical(file));
 if(!managed)return;
 if(canonical(flags.trust)!==canonical(active.trust))throw Error('managed-resource-trust-mismatch');
 if(command==='publish'&&canonical(request.native_store)!==canonical(active.native_store)){
  const value=JSON.parse(Buffer.from(request.artifact,'base64')).input.value;
  const snapshots=new Snapshots(flags.db,{readOnly:true,trust});
  try{
   const prior=snapshots.inspectPublication(value.workspace,value.operation_ref);
   if(!prior||prior.artifact_digest!==digest(Buffer.from(request.artifact,'base64')))throw Error('managed-publication-native-store-mismatch');
  }finally{snapshots.close();}
 }
}
