import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// This preparer uses the exact installed core candidate. The resulting source
// and companions are self-contained inputs to its public CLI.
const packageRoot = process.env.ALCHLANG_PACKAGE_ROOT ?? '/home/vlad_/projects/cyberAlchemy-v2/release-candidates/business-authoring-v1/qualification/consumer/node_modules/@cyberalchemy/alchlang';
const exampleRoot = path.join(packageRoot, 'examples/meta-types/rule-query');
const out = path.join(path.dirname(new URL(import.meta.url).pathname), 'source');
if (fs.existsSync(out)) throw Error(`source already exists: ${out}`);
const mod = async name => import(pathToFileURL(path.join(packageRoot, 'dist', name)).href);
const {digest, json} = await mod('domainspec-profile.js');
const {businessAcceptanceSubjectDigest} = await mod('formal-claim-lowering.js');
const {lowerApplicationDomain} = await mod('application-domain-lowering.js');
const {lowerApplicationRuleProjections} = await mod('application-rule-projection.js');
const src = (relative) => fs.readFileSync(path.join(exampleRoot, relative));
const replace = value => {
  if (typeof value === 'string') return value
    .replaceAll('commerce', 'lab').replaceAll('Commerce', 'Lab')
    .replaceAll('ORDERS', 'SUBMISSIONS').replaceAll('ORDER', 'SUBMISSION')
    .replaceAll('Orders', 'Submissions').replaceAll('Order', 'Submission')
    .replaceAll('orders', 'submissions').replaceAll('order', 'submission');
  if (Array.isArray(value)) return value.map(replace);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k,v])=>[replace(k),replace(v)]));
  return value;
};
const canonical = value => Array.isArray(value) ? `[${value.map(canonical).join(',')}]` : value && typeof value === 'object'
  ? `{${Object.keys(value).sort().map(k=>`${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}` : JSON.stringify(value);
const sha = value => createHash('sha256').update(value).digest('hex');
const source = replace(src('model.alch').toString());
const sourceBytes = Buffer.from(source);
const data = new Map();
const read = relative => replace(JSON.parse(src(relative).toString()));
const put = (relative, value) => {const bytes=Buffer.from(JSON.stringify(value));data.set(relative,bytes);return {path:relative,sha256:sha(bytes),size_bytes:bytes.length,current:true};};
const ref = relative => {const bytes=data.get(relative);if(!bytes)throw Error(`missing companion: ${relative}`);return {path:relative,sha256:sha(bytes),size_bytes:bytes.length,current:true};};
const definitions=read('fixture/definitions.json');
const defRef=put('fixture/definitions.json',definitions);
const definition=definitions.definitions[0];
for (const file of ['fixture/definition-binding.json','fixture/identity-definition-binding.json']) {
  const graph=read(file);
  graph.definition_authority_ref=defRef;
  graph.definition_nodes[0].definition_digest=sha(canonical(definition));
  graph.definition_closure.digest=sha(canonical([definition]));
  put(file,graph);
}
const acceptance=read('fixture/acceptance.json');
const meaning=read('fixture/meaning.json');
acceptance.subject.digest=businessAcceptanceSubjectDigest(meaning);
const acceptanceRef=put('fixture/acceptance.json',acceptance);
meaning.acceptance.acceptance_digest=acceptanceRef.sha256;
const meaningRef=put('fixture/meaning.json',meaning);
const profileBytes=src('fixture/profile.json');
data.set('fixture/profile.json',profileBytes);
const profileRef={path:'fixture/profile.json',sha256:sha(profileBytes),size_bytes:profileBytes.length,current:true};
const identityBytes=src('fixture/identity.json');
data.set('fixture/identity.json',identityBytes);
const identityRef={path:'fixture/identity.json',sha256:sha(identityBytes),size_bytes:identityBytes.length,current:true};
const bindings=read('inputs/bindings.json');
bindings.source_sha256=sha(sourceBytes);
bindings.formal.source_sha256=sha(sourceBytes);
for (const claim of Object.values(bindings.formal.formal_claims)) {
  claim.business_meaning_ref=meaningRef;
  claim.business_acceptance_ref=acceptanceRef;
  claim.definition_binding_ref=ref(claim.definition_binding_ref.path);
  claim.formal_language_profile_ref=profileRef;
  claim.identity_algorithm_ref=identityRef;
}
const formation=lowerApplicationDomain(source,bindings,data);
const interpretation=read('inputs/interpretation.json');
interpretation.formation_sha256=digest(json(formation));
for (const [rule,row] of Object.entries(interpretation.rules)) {
  const claim=bindings.declarations[rule] && rule==='EligibleSubmission'?'EligibleClaim':'IdentityClaim';
  row.claim_identity_inputs_digest=formation.trace.declarations.find(x=>x.source_id===claim).identity_inputs_digest;
}
const projection=lowerApplicationRuleProjections(source,bindings,data,interpretation);
const execution=read('inputs/execution.json');
execution.projection_sha256=digest(json(projection));
const bindingsRef=put('inputs/bindings.json',bindings);
const interpretationRef=put('inputs/interpretation.json',interpretation);
const executionRef=put('inputs/execution.json',execution);
const evidence=[...data.keys()].filter(p=>p.startsWith('fixture/')).sort().map(p=>({path:p,sha256:sha(data.get(p)),size_bytes:data.get(p).length,current:true}));
const manifest={schema_version:'alchlang.application-file/v1-candidate',source_sha256:sha(sourceBytes),bindings:bindingsRef,interpretation:interpretationRef,execution:executionRef,evidence};
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'lab-submission.alch'),sourceBytes);
for (const [relative,bytes] of data) {const target=path.join(out,relative);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes);}
fs.writeFileSync(path.join(out,'lab-submission.alch.application.json'),json(manifest));
console.log(JSON.stringify({source_sha256:manifest.source_sha256,files:data.size+2,package_version:JSON.parse(fs.readFileSync(path.join(packageRoot,'package.json'))).version}));
