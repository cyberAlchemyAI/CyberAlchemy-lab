# Author a generation profile package

A profile.json package declares identity/version, exact dependencies, capabilities, finite rules, resource budgets and digest-pinned assets. Start from the shipped entry-local or shared-port package and change a bounded supported recipe. Application users supply business sources and formal claims; profile authors supply reusable technical recipes.

Rules use select, project, bounded join/traversal, defaults, require-one and emit. They cannot execute JavaScript, read files, call a network, run a process or recurse without bounds. Every required role needs one owner; conflicting owners and output paths reject. New semantic primitives, graph relationships, guarantees or targets require Core changes and qualification.

Templates use declared typed holes: identifier, string, JSON and relative import path. `{{name}}` substitutes one value; `{{> child}}` includes a declared owned template; `{{#each rows}}...{{/each}}` iterates a bounded record array. Inserted strings/JSON are never parsed as templates. Adjacent opening braces in native template text are reserved; use whitespace in record-type JSDoc. Includes remain within the declared closure. No evaluator helpers or build hooks are permitted. Native runtime code is checked and tested; finite tests do not certify arbitrary code as a sandbox.

Use the existing descriptor/recipe references from the shipped packages. Factory descriptors and recipes remain distinct. A selected package is not admitted merely because it has a digest. Locks include all selected/transitive package bytes plus complete core/tool/source identities. Qualify your package on independently authored domains and structurally different dependency graphs while keeping the complete shared Core unchanged.

## Create a v2 API-prefix profile without compiler changes

Use the installed entry-local v2 package as a reusable technical base. Copy it into a new directory; keep its formal, identity, settlement and typed transport asset bytes and declared digests. Change finite rules and package identity:

```sh
cp -R node_modules/@domainspec-v2/cli/profiles/node-http-entry-local-v2 my-api-profile
node --input-type=module <<'JS'
import fs from 'node:fs';
const file='my-api-profile/profile.json',profile=JSON.parse(fs.readFileSync(file,'utf8'));
profile.id='node-http-api-prefix-v2';
for(const rule of profile.rules) {
  if(rule.role==='application-operation') {
    rule.fields.route.concat[0].literal='/api/';
    rule.fields.technical.literal={request_bytes:8192,timeout_ms:1500};
  }
  if(rule.id==='dispatcher-row')rule.values.artifact_path='api/index.mjs';
}
fs.writeFileSync(file,JSON.stringify(profile,null,2)+'\n');
const project=JSON.parse(fs.readFileSync('project.json','utf8'));
project.profiles=[{id:profile.id,version:profile.version,path:'my-api-profile'}];
fs.writeFileSync('project.json',JSON.stringify(project,null,2)+'\n');
JS
npx --no-install alchlang profile select project.json > api-profile-selection.json
npx --no-install alchlang profile check project.json
npx --no-install alchlang profile generate project.json --out generated-api
npx --no-install alchlang profile verify project.json --out generated-api
```

The notice handler is now generated-api/api/index.mjs, with /api/receiveNotice. The dispatch example uses /api/confirmDelivery. Re-run the independent success, false-guard and malformed-input examples for your profile. The compiler bytes remain unchanged; the selected package/source identity changes, so the old lock is invalid.

The v2 application engine has one selected application-runtime owner. Choose an entry-local or shared transport mechanism and preserve its typed ownership/dependencies. You can vary finite routing, limits, dispatcher placement and supported asset recipes. The core still owns semantic lowering, exact UInt64, Mapping/Operation checks and the registered effect vocabulary. New semantic primitives, targets, providers or guarantees require core work and renewed qualification. Native assets are reusable technical code, not a way to hide business logic or create a proof.

## Open Questions

The supported vocabulary and callable contracts are finite. New providers, effects, ontology adapters, runtime guarantees and operational evidence mechanisms need separate qualification. Local hosting, TDE, EVF and publication remain deferred.
