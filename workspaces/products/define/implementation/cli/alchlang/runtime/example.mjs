/** Example transport over native projections and the one real selected Definition. */
import path from 'node:path';
import {root} from '../example-build.mjs';
import {callNative as call,assertNativeSourceCurrent} from './native.mjs';
import {importTypedDocument} from './wire.mjs';
import {openJsonPort} from '../../../../../../../implementation/artifact-runtime/json-pipe.mjs';
const R=path.resolve(root,'../../../../../..');
export async function exampleData({destination}={}){
 const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
 const project=async(name,documents,args={marker:true})=>(await port.request({operation:'construct-value',documents,batches:[await call('Define.PackageConstruction.'+name,args)]})).value;
 try{
  const selection=await project('ExampleSelection',{}),original=await port.request({operation:'read-file',root:R,path:selection.binding.path,maximum:selection.binding.bytes});
  await call('Define.PackEngine.VerifyBinding',await importTypedDocument(await project('MemberBindingPlan',{item:selection.binding,observed:original.binding})));
  const definition=(await port.request({operation:'view-bytes',ref:original.ref})).value,definition_binding=await project('ControlBinding',{observed:original},{path:selection.input_path}),fields=[];
  for(const selector of (await port.request({operation:'value-leaves',value:definition})).selectors)fields.push(await project('ExampleLineageRow',{definition_binding},{selector}));
  const lineage=await project('ExampleLineage',{fields}),lineageMetadata=await port.request({operation:'encode-ref',value:lineage}),lineage_binding=await project('ControlBinding',{observed:lineageMetadata},{path:selection.lineage_path});
  const meaning=await project('ExampleMeaning',{definition,definition_binding}),identity=await project('ExampleIdentity',{}),meaningMetadata=await port.request({operation:'select-value',value:meaning,selector:'',metadata_only:true});
  const reference=await project('LocalMeaningReference',{request:identity,meaning},{value:{ordinal:'0',entry_digest:meaningMetadata.canonical_value_sha256}}),documents={definition,definition_binding,lineage_binding,meaning,identity,reference};
  const batches=[];for(let index=0;index<5;index++)batches.push(await call('Define.PackageConstruction.ExampleRequestPart'+index,{marker:true}));
  const request=(await port.request({operation:'construct-value',documents,batches})).value,requestMetadata=await port.request({operation:'encode-ref',value:request});
  const members=[{path:selection.source_directory+'/'+selection.input_path,ref:original.ref},{path:selection.source_directory+'/'+selection.lineage_path,ref:lineageMetadata.ref},{path:selection.request_path,ref:requestMetadata.ref}];
  const reply=destination?await project('ExampleReply',{publication:{destination:path.resolve(destination)}}):null;
  const sourceMembers={};for(const [name,metadata]of [[selection.input_path,original],[selection.lineage_path,lineageMetadata]])sourceMembers[name]=(await port.request({operation:'export-bytes',ref:metadata.ref})).bytes_base64;
  assertNativeSourceCurrent();if(destination)await port.request({operation:'publish-refs',destination:path.resolve(destination),members});
  return {request,members:sourceMembers,reply};
 }finally{await port.close();}
}