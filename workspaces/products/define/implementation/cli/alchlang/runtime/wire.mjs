/** CLI data transport; representation and import choices are generated AlchLang. */
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {generate,root,fingerprint,selected} from '../package-construction-build.mjs';
import {evaluateArtifact} from '../../../../../../../implementation/artifact-runtime/pure-operation.mjs';
const R=path.resolve(root,'../../../../../..');
const port=path.join(R,'implementation/artifact-runtime/json-port.py');
const values=new Map();
let selectedSource;
function assertSource(){const current=fingerprint();if(selectedSource!==undefined&&selectedSource!==current)throw Error('wire-source-changed-during-execution');selectedSource??=current;return current;}
function io(value){const p=spawnSync('python3',['-B',port],{input:JSON.stringify(value),encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});if(p.status!==0)throw Error(p.stdout||p.stderr||'data-codec-refused');return JSON.parse(p.stdout).result;}
async function native(name,args){
 assertSource();
 const artifact=generate(name),result=await evaluateArtifact(artifact.output,artifact.member,args,{manifest_sha256:artifact.manifest_sha256});assertSource();if(!result.ok)throw Error('data-codec-evaluation-'+result.error.code);
 const value=JSON.parse(new TextDecoder().decode(result.wire));
 if(selected.components.find(row=>row.name===name).kind==='operation'){if(value.tag!=='Returned')throw Error(value.fields.code);return value.fields.value;}
 return value;
}
async function constant(name){const key=assertSource()+':'+name;if(!values.has(key))values.set(key,await native(name,{marker:true}));return values.get(key);}
async function represent(name,value){return io({operation:'represent-json',value,plan:await constant(name)}).value;}
async function checkRequest(value){
 const selection=await represent('ExportWireCodec',await constant('RequestSchema'));
 const result=io({operation:'validate-json',root:R,value,schema_binding:selection.binding,schema_selector:selection.selector});
 if(!result.valid)throw Error('request-structural-contract-invalid');
}
export async function exportWireRequest(value){const encoded=await represent('ExportWireCodec',value);await checkRequest(encoded);return encoded;}
export async function importWireRequest(value){await checkRequest(value);return represent('ImportWireCodec',value);}
export async function importRequest({request,context,project,work,successor=false,current_present=false,prefix_present=false}){
 await native('VerifyImportSelection',{value:{current_present,prefix_present,successor}});
 const decoded=await importWireRequest(request);
 const header=io({operation:'construct-value',documents:{request:decoded,selection:{project,work}},batches:[await constant('ImportStartPlan')]}).value;
 const groups=await native('ImportGroups',{successor});
 const payloads=io({operation:'expand-variants',documents:{request:decoded,start:header.start,context},groups}).values;
 return {seed:header.seed,payloads};
}
export async function normalizeTypedDocument(value){return represent('ImportWireCodec',await represent('ExportWireCodec',value));}

export async function importTypedDocument(value){return represent('ImportWireCodec',value);}

/** Original-byte JSON decoding is generic I/O; it rejects duplicate keys and unsafe numbers. */
export const decodeOriginalJson=raw=>io({operation:'decode',bytes_base64:Buffer.from(raw).toString('base64')}).value;
