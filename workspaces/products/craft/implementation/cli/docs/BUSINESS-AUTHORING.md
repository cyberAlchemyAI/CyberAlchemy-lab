# Business authoring from one source

Author business meaning in one `.alch` file, inspect the review, explicitly record the owner's decision, then generate and verify the selected profile. AlchLang owns parsing and normalization; Core owns captured profiles, review/decision custody and the existing checked graph/request/runtime protocols. This guide is mirrored in both packages; their complete source examples are byte-identical.

This is the source-candidate tutorial. Its command blocks are pinned to AlchLang `0.7.0-candidate.0`, Core `1.3.0`, and the three v3 profiles at `1.0.0`. Source tutorial replay is tracked separately from installed archive qualification. Existing [profile generation](PROFILE-GENERATION.md) and v1/v2 explicit application workflows retain their behavior.

## The complete sources

Copy `delivery-acknowledgement.alch` and `publication-consent.alch` from `examples/profile-engine/business-authoring/` in either package into a new writable working directory. Run the commands from that directory. Both files are complete authored inputs, with no semantic, project, request or acceptance companion. The delivery source explicitly links sort `DeliveryValue` to Entity `Submission`, and predicate `DeliveryPermitted` to definition `Eligibility`. The publication source uses its own namespace and a different genuine Boolean field, while repeating local declaration names.

Each source includes requirement context, applicability, actors, example/counterexample and a boundary; field meanings and identity; an explicit Boolean-field definition; formal claim, interpretation and ceiling; a whole-input guarded Operation with `effects none`; and an explicit public capability. The supplied flag controls that guard. It does not prove physical delivery, legal permission, identity or authenticity. Actors are informational; rejection continuation text does not install recovery logic. Claims remain unproved within their authored ceilings. These Operations write no persistent state and publish no content.

Install the compatible candidate packages or use the source candidate's built public CLI on your PATH. No compiler override is required. The following commands create only new temporary tutorial projects and generated output. The fixture owners and decisions are explicitly synthetic demonstrations, with no owner authentication or product approval implied. For a real project, the actual owner must inspect and choose the outcome for its exact displayed review digest.

## Initialize, inspect and explicitly decide

The tool creates the project/profile selection and copies the original business bytes into it. Check and plan do not grant acceptance. The review includes exact business facts and complete definitions, alongside a separate technical profile section; generated Mapping metadata stays outside the business subject.

```sh
set -eu
tutorial_root=$(mktemp -d)
alchlang business init "$tutorial_root/local" --model delivery_ack=delivery-acknowledgement.alch --profile node-http-entry-local-v3
alchlang business check "$tutorial_root/local/project.json"
alchlang business plan "$tutorial_root/local/project.json" > "$tutorial_root/prospective-plan.json"
alchlang business review "$tutorial_root/local/project.json" > "$tutorial_root/local-review.json"
node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1],"utf8")); console.log(r.reviews[0].text)' "$tutorial_root/local-review.json"
digest=$(node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1],"utf8")); console.log(r.reviews[0].digest)' "$tutorial_root/local-review.json")
alchlang business decision "$tutorial_root/local/project.json" --model delivery_ack --owner dispatch-fixture-owner --outcome accepted --digest "$digest" --decision-id tutorial-delivery --record decision.json --out "$tutorial_root/local/accepted.json"
alchlang business generate "$tutorial_root/local/accepted.json" --out "$tutorial_root/generated-local"
alchlang business view "$tutorial_root/local/accepted.json" > "$tutorial_root/local-views.json"
alchlang business verify "$tutorial_root/local/accepted.json" --out "$tutorial_root/generated-local"
```

Read the displayed review before making the decision. `accepted` and `declined` are explicit choices. The recorder creates a new decision file exclusively; it preserves occupied files. The new selection is written beside the original selection. Tools derive acceptance bindings only after the exact current accepted guard. Only selected/transitive complete definitions receive accepted status; unused visible definitions remain outside the accepted carrier. Users do not hand-edit generated semantic, project, request or acceptance JSON.

## Change profile through data

All profiles select the same finite `ground-entity-bool-operation/v1-candidate` recipe, whole-input JSON POST, `fol-core/1-candidate`, `node-typescript`, and effects `none`.

| Profile 1.0.0 | Actual transport owner | Route | Request bytes | Body-read timeout ms |
| --- | --- | --- | --- | --- |
| `node-http-entry-local-v3` | Each generated entry | `/<public-name>` | 16384 | 2000 |
| `node-http-shared-ports-v3` | One shared module imported by entries | `/<public-name>` | 16384 | 2000 |
| `node-http-api-prefix-v3` | Each entry; prefix from package rule | `/api/<public-name>` | 8192 | 1500 |

`select` copies the authored models into a new project with the selected profile and no carried approval. The business review digest stays the same; the technical lock changes. The tutorial explicitly records a fresh synthetic decision for each new selection. The prefix is a package data-rule concatenation and dispatcher path; no Core change or business rewrite is needed.

```sh
for variant in shared prefix; do
  if [ "$variant" = shared ]; then profile=node-http-shared-ports-v3; else profile=node-http-api-prefix-v3; fi
  alchlang business select "$tutorial_root/local/accepted.json" --profile "$profile" --out "$tutorial_root/$variant"
  if alchlang business generate "$tutorial_root/$variant/project.json" --out "$tutorial_root/unapproved-$variant"; then
    echo "Unapproved generation unexpectedly succeeded" >&2; exit 1
  fi
  alchlang business review "$tutorial_root/$variant/project.json" > "$tutorial_root/$variant-review.json"
  next_digest=$(node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1],"utf8")); console.log(r.reviews[0].digest)' "$tutorial_root/$variant-review.json")
  test "$next_digest" = "$digest"
  alchlang business decision "$tutorial_root/$variant/project.json" --model delivery_ack --owner dispatch-fixture-owner --outcome accepted --digest "$next_digest" --decision-id "tutorial-$variant" --record decision.json --out "$tutorial_root/$variant/accepted.json"
  alchlang business generate "$tutorial_root/$variant/accepted.json" --out "$tutorial_root/generated-$variant"
  alchlang business view "$tutorial_root/$variant/accepted.json" > "$tutorial_root/$variant-views.json"
  alchlang business verify "$tutorial_root/$variant/accepted.json" --out "$tutorial_root/generated-$variant"
done
```

The shared package emits one `runtime/application-http.mts`; generated entries import its compiled `runtime/lib/application-http.mjs`. Local entries each own a transport copy. Reviewed formal, identity, transport and empty-settlement assets are copied from the corresponding v2 package with exact hashes; the new v3 manifest adds authoring/wire conventions. No v2 bundle or old release archive is rewritten.

## Invoke direct Requests without a listener

The body is the complete Operation input, with no invented envelope. UInt64 values use exact decimal JSON strings, including values above JavaScript's safe-integer limit. The following independently specified checks exercise true/false flags, retained fields, malformed types, cancellation and committed/rejected/indeterminate settlement. They import generated handlers and create in-memory `Request` objects; they open no listener and make no network request.

```sh
for variant in local shared prefix; do
  if [ "$variant" = prefix ]; then dispatcher=api; route=/api/confirmDelivery; else dispatcher=app; route=/confirmDelivery; fi
  node --input-type=module - "$tutorial_root/generated-$variant/$dispatcher/index.mjs" "$route" <<'JS'
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {handler}=await import(pathToFileURL(process.argv[2]).href);
const route=process.argv[3];
const input={id:'18446744073709551615',verified:true,recipient_confirmed:false,label:'north-hub'};
const request=body=>new Request('https://tutorial.invalid'+route,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
const success=await handler(request(input));
assert.equal(success.status,200);
const returned=await success.json();
assert.equal(returned.status,'returned');
assert.equal(returned.outcome.status,'committed');
assert.deepEqual(returned.value,input);
const aboveSafeInteger={...input,id:'9007199254740993',recipient_confirmed:true,label:'verbatim'};
assert.deepEqual((await (await handler(request(aboveSafeInteger))).json()).value,aboveSafeInteger);
const blocked=await handler(request({...input,verified:false}));
assert.equal(blocked.status,409);
const rejection=await blocked.json();
assert.equal(rejection.status,'not-returned');
assert.equal(rejection.failure.status,'rejected');
assert.equal(rejection.failure.stage,'guard');
assert.equal(rejection.failure.continuation,'delivery-verification-required');
for(const invalid of [{...input,verified:'true'},{...input,id:1.5},{...input,id:'18446744073709551616'}])assert.equal((await handler(request(invalid))).status,400);
const abort=new AbortController();abort.abort();
assert.equal((await handler(request(input),{},{signal:abort.signal})).status,409);
assert.equal((await handler(request(input),{},{cancellation:'required'})).status,409);
for(const status of ['rejected','indeterminate']){
  const response=await handler(request(input),{},{applications:{confirmDelivery:{store:{begin:async()=>({commit:async()=>({status}),rollback:async()=>{}})}}}});
  assert.equal(response.status,409);
  const failure=(await response.json()).failure;
  assert.equal(failure.status,status);assert.equal(failure.stage,'commit');
  assert.equal(failure.continuation,'delivery-verification-required');
}
console.log('Direct Request checks passed for '+route);
JS
done
```

The body-read deadline bounds transport reading; it does not cancel unsettled business work. Cancellation is preflight-only. Empty settlement implements the required zero-effect protocol; it is not a persistence system. A claim being accepted for this input does not prove the supplied flag or a broader theorem.

## Reject a stale approval

Changing the Boolean definition while leaving its prose unchanged changes the business subject. The existing decision cannot approve the new interpretation. This last block deliberately edits the tutorial's authored copy, verifies rejection, and restores the original bytes. It does not modify the public example or generated files.

```sh
cp "$tutorial_root/local/models/delivery_ack/business.alch" "$tutorial_root/original-business.alch"
node --input-type=module - "$tutorial_root/local/models/delivery_ack/business.alch" <<'JS'
import {readFileSync,writeFileSync} from 'node:fs';
const file=process.argv[2],source=readFileSync(file,'utf8');
if(!source.includes('boolean-field item.verified'))throw Error('expected authored definition');
writeFileSync(file,source.replace('boolean-field item.verified','boolean-field item.recipient_confirmed'));
JS
if alchlang business generate "$tutorial_root/local/accepted.json" --out "$tutorial_root/stale-output"; then
  echo "Stale decision unexpectedly authorized changed source" >&2; exit 1
fi
cp "$tutorial_root/original-business.alch" "$tutorial_root/local/models/delivery_ack/business.alch"
printf 'Tutorial artifacts preserved at %s\n' "$tutorial_root"
```

## Author a finite custom technical package

A profile author can create a new technical convention using the installed vocabulary. This is separate from the per-feature business source: copy the initialized project's captured package and edit only its technical ID, route prefix, matching route concatenation and dispatcher path. Assets, recipe, effects, field semantics and Core/compiler bytes remain unchanged. This example creates `node-http-preview-v3` locally; it does not publish a package.

```sh
test ! -e ./custom-profile
cp -R "$tutorial_root/local/profiles/node-http-entry-local-v3" ./custom-profile
node --input-type=module - ./custom-profile/profile.json <<'JS'
import {readFileSync,writeFileSync} from 'node:fs';
const file=process.argv[2],profile=JSON.parse(readFileSync(file,'utf8'));
profile.id='node-http-preview-v3';
profile.authoring.wire.route_prefix='/preview/';
const application=profile.rules.find(rule=>rule.id==='applications'&&rule.role==='application-operation');
application.fields.route.concat[0].literal='/preview/';
const dispatcher=profile.rules.find(rule=>rule.id==='dispatcher-row'&&rule.op==='defaults');
dispatcher.values.artifact_path='preview/index.mjs';
writeFileSync(file,JSON.stringify(profile,null,2)+'\n');
JS
alchlang business select "$tutorial_root/local/accepted.json" --profile ./custom-profile --out "$tutorial_root/custom"
alchlang business review "$tutorial_root/custom/project.json" > "$tutorial_root/custom-review.json"
custom_digest=$(node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1],"utf8")); console.log(r.reviews[0].digest)' "$tutorial_root/custom-review.json")
test "$custom_digest" = "$digest"
alchlang business decision "$tutorial_root/custom/project.json" --model delivery_ack --owner dispatch-fixture-owner --outcome accepted --digest "$custom_digest" --decision-id tutorial-custom --record decision.json --out "$tutorial_root/custom/accepted.json"
alchlang business generate "$tutorial_root/custom/accepted.json" --out "$tutorial_root/generated-custom"
alchlang business verify "$tutorial_root/custom/accepted.json" --out "$tutorial_root/generated-custom"
node --input-type=module - "$tutorial_root/generated-custom/preview/index.mjs" <<'JS'
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {handler}=await import(pathToFileURL(process.argv[2]).href);
const input={id:'18446744073709551615',verified:true,recipient_confirmed:false,label:'custom-preview'};
const request=value=>new Request('https://tutorial.invalid/preview/confirmDelivery',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(value)});
const response=await handler(request(input));assert.equal(response.status,200);
assert.deepEqual((await response.json()).value,input);
const rejected=await handler(request({...input,verified:false}));assert.equal(rejected.status,409);
assert.equal((await rejected.json()).failure.continuation,'delivery-verification-required');
console.log('Custom /preview/ direct Request checks passed');
JS
```

The same business digest is reviewed explicitly again for this new selection. The tutorial receipt pins unchanged compiler/tool identities and asset hashes around these edits; the package data changes its technical lock and output route. No business-source or compiler modification supplies the new prefix.

For composition, `business init` accepts repeated `--model id=source.alch` arguments. Use `delivery_ack=delivery-acknowledgement.alch` and `publication_consent=publication-consent.alch`; inspect and decide each exact model separately, writing each new selection beside the preceding one. Their repeated local names remain namespace-local and their public routes remain distinct.

## Supported boundary

| Supported now | Requires a separate capability or qualification |
| --- | --- |
| `UInt64`, `String`, `Bool` Entity fields and explicit Boolean guards | Arbitrary types, arithmetic/native authoring clauses, macros/imports |
| Whole-input guarded return, effects `none` | Persistence, events, external providers or publication |
| Explicit public capability | Protected audiences, authentication or authorization inference |
| Exact reviewed facts and unproved formal claims | Formal proof, external fact verification or admission |
| Direct generated handler Requests | Listener operation or hosting |

Coverage and lineage views must distinguish source obligations, generated outputs and claim residue. Checked graphs/plans, native compilation, direct Request behavior and installed archive replay are separate evidence surfaces. Disposal revokes private preparation handles and preserves scratch for inspection. Keep tutorial artifacts until their evidence has been reviewed.

## Open Questions

- The tutorial harness owns the exact source replay record; B11.3 owns replay from frozen installed archives with compatible public peers.
- Full independent cross-profile/HTTP/source-composition qualification is retained under B09.2/B10 rather than inferred from this example.
- Hosting, TDE, EVF and publication remain deferred. No owner authentication, real product approval or formal proof is claimed.
