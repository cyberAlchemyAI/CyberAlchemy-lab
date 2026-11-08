/** Build-only pins from actual existing schema/policy/native source bytes.
 * Observation of tools is not a completed build. Open Questions: COMMERCE-SDK-V5.md. */
import {readFileSync,writeFileSync,realpathSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=fileURLToPath(new URL('../',import.meta.url)),source=readFileSync(path.join(root,'src/commerce/commerce-registry-v1.ts'),'utf8'),resources=[...source.matchAll(/Object\.freeze\((\{[^\n]+\})\)/g)].map(m=>JSON.parse(m[1]));
if(resources.length!==9)throw new Error('COMMERCE_SCHEMA_REGISTRY_COUNT');
const packageMeta=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8')),compiler=realpathSync(path.join(root,'node_modules/typescript/bin/tsc')),compilerMeta=JSON.parse(readFileSync(path.join(path.dirname(compiler),'../package.json'),'utf8'));
const paths=[...resources.map(r=>'contracts/'+r.file),'profiles/commerce-local-v1-candidate/technical-contract.json',...['values-and-codecs','values-api-v5','pure-api-v5'].map(n=>'profiles/commerce-local-v1-candidate/runtime/'+n+'.ts')];
const members=paths.map(relative=>{const b=readFileSync(path.join(root,relative));return {path:relative,sha256:createHash('sha256').update(b).digest('hex'),bytes:b.length};}),value={schema_version:'craft.commerce-sdk-resource-pins/v5-candidate',package_name:packageMeta.name,package_version:packageMeta.version,required_node:process.versions.node,toolchain_observation:{typescript:compilerMeta.version,node:process.versions.node,qualification:'tools-observed;public-build-receipt-still-required'},members,authority_effect:'none'};
const text='// GENERATED from actual existing bytes by tools/materialize-commerce-sdk-v5.mjs.\n// Open Questions: docs/COMMERCE-SDK-V5.md. No native availability or build claim.\nconst freeze=<T>(v:T):T=>{if(v&&typeof v===\'object\'){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};\nexport const COMMERCE_SDK_PINS_V5=freeze('+JSON.stringify(value,null,2)+' as const);\n',file=path.join(root,'src/profile-engine/commerce-sdk-pins-v5.generated.ts');
if(process.argv.length!==3||!['--write','--check'].includes(process.argv[2]))throw new Error('USAGE: --write|--check');
if(process.argv[2]==='--write')writeFileSync(file,text);else if(readFileSync(file,'utf8')!==text)throw new Error('COMMERCE_SDK_RESOURCE_PIN_DRIFT');
console.log(JSON.stringify({mode:process.argv[2],actual_members:members.length,actual_package_version:packageMeta.version,actual_node:process.versions.node,actual_typescript:compilerMeta.version,public_build_qualified:false,authority_effect:'none',open_questions_ref:'docs/COMMERCE-SDK-V5.md#open-questions'}));
