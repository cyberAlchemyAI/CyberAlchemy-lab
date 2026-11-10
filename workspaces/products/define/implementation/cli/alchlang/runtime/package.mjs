import {importTypedDocument} from './wire.mjs';
import {captureLocalSnapshot} from '../../../../../../../implementation/artifact-runtime/capture-snapshot.mjs';
import {assembleSnapshotArtifact} from '../../../../../../../implementation/artifact-runtime/assemble-snapshot.mjs';
import {constructNativeData} from '../../../../../../../implementation/artifact-runtime/construct-native-data.mjs';
/** Package commands: authored policy and projections, shared byte adapters. */
import path from 'node:path';
import {root} from '../package-construction-build.mjs';
import {callNative as call,assertNativeSourceCurrent} from './native.mjs';
import {openJsonPort} from '../../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {readFrozenArtifact} from '../../../../../../../implementation/artifact-runtime/frozen-artifact.mjs';
import {deriveArtifacts} from '../../../../../../../implementation/artifact-runtime/derive-artifacts.mjs';
import {verifyEmbeddedReferences} from '../../../../../../../implementation/artifact-runtime/embedded-reference.mjs';
const R=path.resolve(root,'../../../../../..');
export async function inspectPackage(directory,{destination,cli=false,observe=false,memoryMembers=null,capture=null}={}){
 const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
 try{
  const protocol=await call('Define.PackageGraph.FrozenInspectionProtocol',{marker:true});
  const snapshot=await readFrozenArtifact({port,call,schemaRoot:R,protocol,read:byteReader(port,directory,memoryMembers,capture)});
  const references=await call('Define.PackageGraph.EmbeddedReferenceProtocol',{marker:true});
  await verifyEmbeddedReferences({port,call,protocol:references,body:snapshot.documents[snapshot.protocol.body_alias],bodyRef:snapshot.body_metadata.ref});
  const required_count=await call('Define.PackageGraph.RequiredCount',{state:snapshot.state});
  const steps=await call(snapshot.protocol.result_plan,{value:{root_sha256:snapshot.manifest_metadata.sha256,body_sha256:snapshot.body_metadata.sha256,required_count}});
  const result=(await port.request({operation:'construct-value',documents:{},batches:[steps]})).value;
  if(observe){
   const steps=await call('Define.PackageConstruction.ConfirmationObservationPlan',{marker:true});
   const portable=(await port.request({operation:'construct-value',documents:{...snapshot.documents,manifest_metadata:snapshot.manifest_metadata,document_metadata:snapshot.document_metadata},batches:[steps]})).value;
   const observation=await importTypedDocument(portable);assertNativeSourceCurrent();return {integrity:result,observation,body_binding:snapshot.body_metadata.binding};
  }
  const response=cli?(await port.request({operation:'construct-value',documents:{inspection:result},batches:[await call('Define.PackageConstruction.InspectionCliReply',{value:{reconstruct:!!destination,destination:destination?path.resolve(destination):''}})]})).value:result;
  assertNativeSourceCurrent();
  if(destination){
   await port.request({operation:'publish-refs',destination:path.resolve(destination),members:[{path:snapshot.protocol.manifest_path,ref:snapshot.manifest_metadata.ref},...Array.from(snapshot.metadata,([name,observed])=>({path:name,ref:observed.ref}))]});
  }
  return response;
 }finally{await port.close();}
}
export async function packageCli(directory,{destination}={}){
 return inspectPackage(directory,{destination,cli:true});
}

export async function materializePackage(directory,destination,{cli=false,memoryMembers=null,verifyOnly=false}={}){
 const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
 try{
  const protocol=await call('Define.PackageGraph.FrozenInspectionProtocol',{marker:true});
  const snapshot=await readFrozenArtifact({port,call,schemaRoot:R,protocol,read:byteReader(port,directory,memoryMembers,null)});
  await verifyEmbeddedReferences({port,call,protocol:await call('Define.PackageGraph.EmbeddedReferenceProtocol',{marker:true}),body:snapshot.documents[snapshot.protocol.body_alias],bodyRef:snapshot.body_metadata.ref});
  const derivation=await call('Define.PackageConstruction.MaterializationProtocol',{marker:true});
  const source=await call('Define.PackageConstruction.SelectMaterializationResources',{marker:true});
  const resources=(await port.request({operation:'represent-json',value:source,plan:await call('Define.PackageConstruction.ExportWireCodec',{marker:true})})).value;
  return await deriveArtifacts({port,call,snapshot,protocol:derivation,resources,schemaRoot:R,destination:verifyOnly?null:path.resolve(destination),publish:!verifyOnly,assertSource:assertNativeSourceCurrent,finalize:async report=>cli?(await port.request({operation:'construct-value',documents:{report},batches:[await call('Define.PackageConstruction.MaterializationCliReply',{destination:path.resolve(destination)})]})).value:report});
 }finally{await port.close();}
}

export async function materializeCli(directory,destination){
 return materializePackage(directory,destination,{cli:true});
}

export async function preparePackage(requestRaw,sourceRoot,{destination,permitRetention=false,capturedAt=new Date().toISOString(),finalize=async value=>value,supplemental=new Map()}={}){
 const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
 try{
  const requestMetadata=await port.request({operation:'store-bytes',bytes_base64:Buffer.from(requestRaw).toString('base64')});
  const captured=await captureLocalSnapshot({port,call,protocol:await call('Define.PackageConstruction.LocalCaptureProtocolValue',{marker:true}),requestRef:requestMetadata.ref,read:async(name,maximum)=>{if(supplemental.has(name)){const raw=supplemental.get(name);if(raw.length>maximum)throw Error('supplemental-document-bound');const stored=await port.request({operation:'store-bytes',bytes_base64:raw.toString('base64')});return port.request({operation:'read-member-ref',members:[{path:name,ref:stored.ref}],path:name,maximum});}return port.request({operation:'read-file',root:path.resolve(sourceRoot),path:name,maximum});},schemaRoot:R,permitRetention,capturedAt});
  const protocol=await constructNativeData({port,call,selector:'Define.PackageConstruction.PreparationProtocolParts'});
  const assembled=await assembleSnapshotArtifact({port,call,protocol,captured,requestRef:requestMetadata.ref,schemaRoot:R});
  const members=new Map([[protocol.pack_path,await port.request({operation:'encode-ref',value:assembled.body})],[protocol.capture_path,captured.capture_metadata],[protocol.request_path,requestMetadata],[protocol.report_path,await port.request({operation:'encode-ref',value:assembled.report})]]);
  for(const [name,metadata]of captured.members)members.set(protocol.input_namespace+name,metadata);
  const paths=(await port.request({operation:'object-keys',value:Object.fromEntries(members)})).keys,body=members.get(protocol.pack_path);
  const batches=[await call(protocol.manifest_header,{value:{pack_ordinal:String(paths.indexOf(protocol.pack_path)),pack_sha256:body.sha256,pack_bytes:String(body.bytes)}})];
  for(let ordinal=0;ordinal<paths.length;ordinal++){
   const name=paths[ordinal],metadata=members.get(name),extension=path.extname(name).slice(1);
   batches.push(await call(protocol.manifest_member,{value:{ordinal:String(ordinal),path:name,extension,sha256:metadata.sha256,bytes:String(metadata.bytes)}}));
  }
  const steps=batches.flat(),packed=Array.from({length:Math.ceil(steps.length/100)},(_,index)=>steps.slice(index*100,index*100+100));
  const manifest=(await port.request({operation:'construct-value',documents:{pack:assembled.body},batches:packed})).value,manifestMetadata=await port.request({operation:'encode-ref',value:manifest});members.set(protocol.manifest_path,manifestMetadata);
  const references=Array.from(members,([path,row])=>({path,ref:row.ref}));
  const snapshot=await readFrozenArtifact({port,call,schemaRoot:R,protocol:await call('Define.PackageGraph.FrozenInspectionProtocol',{marker:true}),all:true,read:(path,maximum)=>port.request({operation:'read-member-ref',members:references,path,maximum})});
  await verifyEmbeddedReferences({port,call,protocol:await call('Define.PackageGraph.EmbeddedReferenceProtocol',{marker:true}),body:snapshot.documents[snapshot.protocol.body_alias],bodyRef:snapshot.body_metadata.ref});
  const result={...assembled,manifest,root_sha256:manifestMetadata.sha256,pack_sha256:body.sha256,member_count:members.size};
  const response=await finalize(result,port,call);assertNativeSourceCurrent();
  if(destination)await port.request({operation:'publish-refs',destination:path.resolve(destination),members:references});
  return response;
 }finally{await port.close();}
}

export async function prepareCli(requestRaw,sourceRoot,destination,{permitRetention=false,capturedAt,supplemental=new Map()}={}){
 return preparePackage(requestRaw,sourceRoot,{destination,permitRetention,capturedAt,supplemental,finalize:async(prepared,port,call)=>{
  const args={gap_count:String(prepared.body.gaps.length)},batches=[];
  for(const selector of ['Define.PackageConstruction.PreparationCliPart0','Define.PackageConstruction.PreparationCliPart1'])batches.push(await call(selector,args));
  return (await port.request({operation:'construct-value',documents:{prepared,publication:{destination:path.resolve(destination)}},batches})).value;
 }});
}

function byteReader(port,directory,memoryMembers,capture){return async(name,maximum)=>{
 let metadata;
 if(memoryMembers){if(!memoryMembers.has(name))throw Error('frozen-memory-member-missing:'+name);const stored=await port.request({operation:'store-bytes',bytes_base64:memoryMembers.get(name).toString('base64')});metadata=await port.request({operation:'read-member-ref',members:[{path:name,ref:stored.ref}],path:name,maximum});}
 else metadata=await port.request({operation:'read-file',root:path.resolve(directory),path:name,maximum});
 if(capture){const raw=await port.request({operation:'export-bytes',ref:metadata.ref});capture.set(name,Buffer.from(raw.bytes_base64,'base64'));}return metadata;
};}
