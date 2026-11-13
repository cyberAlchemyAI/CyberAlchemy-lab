import {readFileSync} from 'node:fs';
import {verifyDirectoryPackages} from './directories.mjs';
const [input,index,width]=process.argv.slice(2),data=JSON.parse(readFileSync(input)),current=data.registry.entries.filter(e=>data.registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version),entries=current.filter((_,i)=>i%Number(width)===Number(index));
const result=await verifyDirectoryPackages(data.source,{...data.registry,entries},b=>Buffer.from(data.files[b.ref??b.path],'base64'),{singleProcess:true});
console.log(JSON.stringify(result));
