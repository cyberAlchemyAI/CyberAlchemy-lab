import {cpSync,mkdirSync} from 'node:fs';
const destination=new URL('../dist/event-templates/',import.meta.url);
mkdirSync(destination,{recursive:true});
for(const name of ['handler.mjs','lib.rs','main.rs','serve.py','local_worker.py','semantic-handler.mjs','semantic-lib.rs','semantic-main.rs','semantic-binding.json','semantic-serve.py'])cpSync(new URL(`../src/event-templates/${name}`,import.meta.url),new URL(name,destination));
cpSync(new URL('../src/event-templates/rust-runtime/',import.meta.url),new URL('rust-runtime/',destination),{recursive:true});
