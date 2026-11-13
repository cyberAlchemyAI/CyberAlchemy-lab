import {Snapshots} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {isDeepStrictEqual} from 'node:util';
export function projectRecordCatalog(native,profiles,assignments=[]){
 const rows=Object.entries(native.projection.subjects).filter(([,r])=>r.category==='artifact-instance').map(([version,row])=>({version_ref:version,identity:row.identity,kind:row.kind,carrier:row.carrier_ref,standing:row.effective_state,decision_ref:row.decision_ref,body:row.record,workspaces:[...new Set([...Object.values(profiles).filter(p=>p.primary_subject.ref===row.identity||p.linked_project_refs.includes(row.identity)).map(p=>p.workspace_ref),...assignments.filter(a=>a.version_ref===version).map(a=>a.workspace)])]}));
 return {schema_version:'lab-record-catalog/v1',source_cut:native.baseline.snapshot_digest,native_head:native.head,records:rows,coverage:'Every artifact-instance in this exact native projection. External workspace identities retain their external authority and are not manufactured as local admissions.'};
}
export function readPublishedRecords(active,trust){
 const db=new Snapshots(active.database,{readOnly:true,trust});
 try{
  const selected=db.current(active.workspace),sourceMaterial=db.material(selected.digest,'source.json'),pub=db.inspectPublication(active.workspace,sourceMaterial.manifest.operation);
  if(!pub||!isDeepStrictEqual(pub.selected,{...selected}))throw Error('record-catalog-publication-unverified');
  const source=JSON.parse(sourceMaterial.bytes),binding=source.record_catalog;
  if(!binding)throw Error('record-catalog-not-published');
  const material=db.material(selected.digest,binding.ref??binding.path);
  if(material.binding.sha256!==binding.sha256||Number(material.binding.bytes)!==Number(binding.bytes))throw Error('record-catalog-binding-mismatch');
  const catalog=JSON.parse(material.bytes);
  if(!isDeepStrictEqual(catalog.native_head,source.directory_native_head)||catalog.source_cut!==sourceMaterial.manifest.cut)throw Error('record-catalog-native-context-mismatch');
  return {selector:{...selected},...catalog};
 }finally{db.close();}
}
