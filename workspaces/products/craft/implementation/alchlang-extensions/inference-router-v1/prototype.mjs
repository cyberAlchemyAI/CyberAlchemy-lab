import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {parseDeclarativeSource} from '../../implementation/dist/declarative-profile.js';
const base=new URL('./',import.meta.url);
const source=readFileSync(new URL('provider-selection.alch',base),'utf8');
export const parsed=parseDeclarativeSource(source);
export const documents={
  'contract.json':parsed.contract,
  'boundary-model.json':parsed.model,
};
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const check=process.argv.includes('--check');
 if(!check)mkdirSync(new URL('generated/',base),{recursive:true});
 for(const [name,value] of Object.entries(documents)){
  const bytes=JSON.stringify(value,null,2)+'\n',path=new URL('generated/'+name,base);
  if(check){if(readFileSync(path,'utf8')!==bytes)throw Error('PROJECTION_DRIFT:'+name);}
  else writeFileSync(path,bytes);
 }
 console.log(JSON.stringify({status:'PASS',scope:'Alch parsing and DomainSpec contract projection only',source_sha256:createHash('sha256').update(source).digest('hex'),execution:'not_evaluable',authority_effect:'none'}));
}
