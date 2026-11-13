import {readFileSync,writeFileSync,mkdirSync,existsSync,renameSync,lstatSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {enforce} from './kernel.mjs';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {bind} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
const json=x=>Buffer.from(JSON.stringify(x,null,2)+'\n'),slug=x=>x.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
export async function planRecordCustody({root,profile,native,version_ref,assignment}){
 const row=native.projection.subjects[version_ref];if(!row||!['admitted-current','local-admitted-current'].includes(row.effective_state))throw Error('current-native-record-required');
 const body=row.record,contract=native.projection.contracts[row.carrier_ref];
 if(!contract||contract.effective_state==='admitted-historical')throw Error('current-record-carrier-required');
 const fields=contract.artifact.instance_contract,kind=contract.semantic_kind;
 const recordOwner=body.owner_ref??body.semantic_owner_ref??body.accountable_owner_ref;
 // Assignment must come from an authenticated publication, never a caller home flag.
 if(assignment.version_ref!==version_ref||assignment.workspace!==profile.workspace_ref||assignment.owner!==recordOwner||assignment.body_sha256!==digest(Buffer.from(JSON.stringify(body))))throw Error('record-custody-assignment-mismatch');
 const area=await enforce('PlanRecordCustody',{kind:kind==='product-identity'?'Product':kind==='project-identity'?'Project':kind==='work'?'Work':'Other',workspace_verified:assignment.workspace===profile.workspace_ref,native_record_verified:true,owner_binding_verified:recordOwner===assignment.owner,carrier_verified:row.carrier_ref===contract.artifact.artifact_type_ref,home_safe:!path.isAbsolute(profile.home.path)&&!profile.home.path.split('/').includes('..')});
 const identity=slug(body.name??row.identity),revision=slug(version_ref.split('@').at(-1));
 if(!identity||!revision)throw Error('record-readable-path-required');
 const folder=path.posix.join(profile.home.path,area.area,area.collection,identity,revision),canonical=fields.canonical_filename;
 if(!/^[A-Za-z0-9._-]+$/.test(canonical))throw Error('record-filename-invalid');
 const descriptorPath=path.posix.join(path.posix.dirname(contract.schema_path),'artifact.json'),descriptor=JSON.parse(readFileSync(path.join(root,descriptorPath)));
 if(JSON.stringify(descriptor)!==JSON.stringify(native.projection.subjects[row.carrier_ref]?.record)){
  // Object ordering is immaterial; registered descriptor content is exact.
  const {isDeepStrictEqual}=await import('node:util');if(!isDeepStrictEqual(descriptor,native.projection.subjects[row.carrier_ref]?.record))throw Error('record-renderer-descriptor-mismatch');
 }
 const generator=path.join(root,path.posix.dirname(contract.schema_path),'generator.py'),rendered=spawnSync('python3',['-B',path.join(import.meta.dirname,'render-record.py')],{input:JSON.stringify({generator,descriptor,body}),encoding:'utf8',maxBuffer:1024*1024});
 if(rendered.status!==0)throw Error('registered-record-renderer-refused:'+rendered.stderr);
 if(!/^[A-Za-z0-9._-]+$/.test(fields.human_filename))throw Error('record-human-filename-invalid');
 const humanRaw=Buffer.from(JSON.parse(rendered.stdout).markdown),human={filename:fields.human_filename,binding:bind(folder+'/'+fields.human_filename,humanRaw),bytes_base64:humanRaw.toString('base64')};
 return {version_ref,workspace:profile.workspace_ref,folder,filename:canonical,body:row.record,human,assignment,source_cut:native.baseline.snapshot_digest,body_binding:bind(folder+'/'+canonical,json(body)),carrier:row.carrier_ref,owner:recordOwner,native_head:native.head,semantic_project:assignment.semantic_project??null,technical_host:native.projection.state.payload.project_ref,authority_effect:'none'};
}
export function placeAdmittedRecord(root,plan){
 const dir=path.resolve(root,plan.folder);
 if(!dir.startsWith(root+path.sep))throw Error('record-custody-escape');
 let current=dir;while(current.startsWith(root+path.sep)){if(existsSync(current)&&lstatSync(current).isSymbolicLink())throw Error('record-custody-symlink');current=path.dirname(current);}
 mkdirSync(dir,{recursive:true});
 const members={[plan.filename]:json(plan.body),[plan.human.filename]:Buffer.from(plan.human.bytes_base64,'base64'),'custody.json':json({...plan,body:undefined,human:{filename:plan.human.filename,binding:plan.human.binding}})};
 for(const [name,raw]of Object.entries(members)){
  const file=path.join(dir,name);
  if(existsSync(file)){if(lstatSync(file).isSymbolicLink())throw Error('record-custody-symlink');if(!readFileSync(file).equals(raw))throw Error('record-custody-existing-version-conflict');}
  else{const tmp=file+'.staging-'+process.pid;writeFileSync(tmp,raw,{flag:'wx'});renameSync(tmp,file);}
 }
 return {status:'placed',workspace:plan.workspace,version_ref:plan.version_ref,folder:plan.folder,authority_effect:'none'};
}
