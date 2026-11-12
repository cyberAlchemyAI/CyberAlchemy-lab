# AlchLang profiles: selection and creation

A **profile** selects a supported technical way to realize checked AlchLang meaning. The `.alch` source says what an account, decision, or operation means. A profile selects admitted capabilities, bounds, code layout, HTTP routes, storage, Auth binding, or another supported mechanism. It cannot supply missing business facts, change an authored permission, invent a native implementation, or turn a local check into a deployed service.

The [step-by-step Craft guide](../../COMPLETE-GUIDE.md) shows where profiles fit around a whole Customer Success application. Start profile editing with the [small ReviewDesk Rule](alchlang.md#start-with-one-rule): its source, profile and bounds are short enough to inspect together. The [syntax reference](../reference/alchlang-syntax.md) explains its declarations.

## First profile: keep the same ReviewDesk Rule

The [starter project](../../implementation/alchlang/examples/generic-rule/README.md) contains three inputs: `business.alch` declares `Request` and `IsVerified`; [profile.json](../../implementation/alchlang/examples/generic-rule/profile.json) selects the Node target, capabilities and limits; [contracts/bounds.json](../../implementation/alchlang/examples/generic-rule/contracts/bounds.json) declares matching authored computation limits. The starter exercise generates and runs the Rule.

After copying the starter into a project with the matching packages installed, or into the `$RUN` directory in the [checkout exercise](alchlang.md#start-with-one-rule), make a **new local profile variant** that accepts at most 2,048 input bytes instead of 4,096. Keep the business Rule unchanged. A profile cannot silently override the authored bounds, so change the limit in both files. Change into the directory containing `business.alch` (`cd "$RUN"` for the checkout exercise), then run:

```sh
node --input-type=module <<'JS'
import {readFileSync,writeFileSync} from 'node:fs';
const profile=JSON.parse(readFileSync('profile.json','utf8'));
const bounds=JSON.parse(readFileSync('contracts/bounds.json','utf8'));
profile.id='reviewdesk-rule-2048';
profile.limits.max_input_bytes=2048;
bounds.computation.limits.max_input_bytes=2048;
writeFileSync('profile.json',JSON.stringify(profile,null,2)+'\n');
writeFileSync('contracts/bounds.json',JSON.stringify(bounds,null,2)+'\n');
JS
```

With the **installed packages**, generate and exercise the variant:

```sh
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --rule ReviewDesk.IsVerified --out generated-2048 --accept-local-review reviewdesk-profile
node exercise.mjs generated-2048
```

With the **checkout**, use its built source CLI, then exercise the result:

```sh
ALCHLANG_DOMAINSPEC_PACKAGE_ROOT="$REPO/workspaces/products/craft/implementation/cli" \
  node "$REPO/workspaces/products/craft/implementation/alchlang/dist/generic-composition-cli.js" \
  generate --source business.alch --profile profile.json --rule ReviewDesk.IsVerified \
  --out generated-2048 --accept-local-review reviewdesk-profile > generation-2048.json
node exercise.mjs generated-2048
```

Use a new output directory. The generated Rule still returns true or false from `verified`; the profile change affects the maximum accepted input size and gives the selection a distinct ID. In a focused checkout test with the current source CLI, this variant generated successfully and the exercise passed its true, false and wrong-type cases. The example is a bounded **variant of an admitted recipe**, not a new generator or a different business rule. A project that needs storage, Auth or HTTP must use the corresponding admitted profile family.

## Which profile do you need?

The word “profile” appears in several command families. Match its schema and consumer, not just its filename.

| Profile or selection | What it controls | Working example / detailed contract |
| --- | --- | --- |
| Generic capability profile | Which generic declarations and effects a `module` source can generate, target, execution bounds, Auth ABI, storage and replay where supported. | [Customer Success selected-profile.json](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/selected-profile.json), [generic applications](../../implementation/alchlang/docs/GENERIC-APPLICATIONS.md) |
| Generic HTTP profile | Route prefix, method, path, selected Entry, response Mapping, request/response bounds. | [Customer Success http-profile.json](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/http-profile.json), [HTTP guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md#connect-a-checked-http-profile-to-the-generated-application) |
| Declarative package | A versioned `craft.profile-package/v1` recipe and assets for a supported application or service layout. | [Profile generation](../../implementation/alchlang/docs/PROFILE-GENERATION.md), [package contract](../../implementation/cli/docs/PROFILE-PACKAGES.md) |
| Technical source profile | AlchLang `Rule`/`Mapping`/`Interface` source plus a JSON envelope that binds its selection to an existing consumer and implementation basis. Compiles to a package or `selection.json`, depending on the target. | [Architecture source](../../implementation/cli/examples/technical-profile-source/architecture-shared.alch), [envelope](../../implementation/cli/examples/technical-profile-source/architecture-shared.profile.json), [source guide](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md) |
| Application-input profile | Reusable mappings from authored business roles to existing application, provider and layout inputs. | [CRM application-input guide](../../implementation/cli/docs/APPLICATION-INPUT-PROFILES.md) |
| Runtime or provider source selection | Select an existing native resource or provider decision contract. The operator supplies real resources and authority separately. | [Technical profile catalog](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md#start-with-the-local-examples) |
| `alchlang business` v3 package | A finite business-authoring technical convention with reviewed selection and supported route/output changes. | [Business authoring tutorial](../../implementation/cli/docs/BUSINESS-AUTHORING.md) |

These are distinct schemas. Copying a profile from one row into another command does not convert it.

## Select an existing profile first

1. **Write the business source.** Name its required types, declarations, access rules, and effects.
2. **Choose the command family.** The [overview](alchlang.md#choose-the-command-path) distinguishes generic, profile-source, package, business-authoring, and compatibility paths.
3. **Find a profile with the exact capability and version.** The [installed generic examples](../../implementation/alchlang/docs/GENERIC-APPLICATIONS.md) progress from a Rule, through pure decisions, to a protected SQLite API. The profile's capability list must cover the source; a similar name is not enough.
4. **Check its implementation basis and inputs.** Match compiler/CLI packages, profile schema and target, bounds, required assets, Auth/store/provider resources, and the intended output. Keep the profile file alongside the source and generated manifest.
5. **Generate into a new directory and exercise the result.** Review the exact local selection when the command requires it; preserve the input and observation. A generated handler is not a hosted listener.

For Customer Success, the [application profile](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/selected-profile.json) selects `node-esm`, supported `Rule`/`Policy`/`Entry`/transaction capabilities, the Auth ABI, SQLite atomic command storage, and limits. The separate [HTTP profile](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/http-profile.json) selects `injected-request-response/v1-candidate`, `/api`, and routes to exact Entries and response Mappings. Changing the route does not change `SuggestedAction` or `ReviewRenewal`.

## Create a small custom technical package

The **finite `alchlang business` path** has a tested profile extension that changes the technical convention without rewriting business source or compiler code. Its [complete tutorial](../../implementation/cli/docs/BUSINESS-AUTHORING.md#author-a-finite-custom-technical-package) first creates an initialized local project and `$tutorial_root/local/accepted.json`. That project contains `profiles/node-http-entry-local-v3`. Use the matching working CLI and an absent `./custom-profile` directory:

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
```

The ID, route prefix, derived route, and dispatcher artifact path change together. The original assets, recipe, effects, field semantics and compiler remain unchanged. Now select, review, decide the exact digest again, generate and verify:

```sh
alchlang business select "$tutorial_root/local/accepted.json" --profile ./custom-profile --out "$tutorial_root/custom"
alchlang business review "$tutorial_root/custom/project.json" > "$tutorial_root/custom-review.json"
custom_digest=$(node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1],"utf8")); console.log(r.reviews[0].digest)' "$tutorial_root/custom-review.json")
alchlang business decision "$tutorial_root/custom/project.json" --model delivery_ack --owner dispatch-fixture-owner --outcome accepted --digest "$custom_digest" --decision-id tutorial-custom --record decision.json --out "$tutorial_root/custom/accepted.json"
alchlang business generate "$tutorial_root/custom/accepted.json" --out "$tutorial_root/generated-custom"
alchlang business verify "$tutorial_root/custom/accepted.json" --out "$tutorial_root/generated-custom"
```

Follow the full tutorial to initialize `$tutorial_root` and exercise the generated `preview/index.mjs` handler with direct `Request` objects. Its tested path is deliberately narrow: `UInt64`/`String`/`Bool` fields, explicit Boolean guards, whole-input guarded return, public capability, and effects `none`. It does not create a protected database or arbitrary new HTTP implementation. A new profile selection requires a fresh review and owner decision for the exact selected digest.

## Create a reusable profile in AlchLang source

Use this path when a reusable technical choice can be expressed by existing `Rule`, `Mapping`, and `Interface` constructs and bound to an **existing consumer**. The [shared-port example](../../implementation/cli/examples/technical-profile-source/architecture-shared.alch) defines `Options`, `RequestWithinBounds`, and a pure `Build` Mapping that returns bounded `nodes` and `edges`. Its [JSON envelope](../../implementation/cli/examples/technical-profile-source/architecture-shared.profile.json) supplies information that Alch source cannot establish alone:

| Envelope part | Responsibility |
| --- | --- |
| `sources`, `boundary`, `selection` | Exact source closure, family Interface, Mapping, Rule checks and arguments. |
| `bindings`, `contracts` | Join roles and ports to checked business functions or registered original contracts. |
| `target` | Exact consumer and original package/implementation basis. |
| `limits` and resources | Admitted bounds and explicit external requirements. |

In the working build, check and compile the source envelope. `<examples>` is the matching installed Core `examples/technical-profile-source` directory, and `<new-package-directory>` must not already exist:

```sh
alchlang profile check-source <examples>/architecture-shared.profile.json \
  --source-root <examples>
alchlang profile compile-source <examples>/architecture-shared.profile.json \
  --source-root <examples> --out <new-package-directory>
```

This architecture target compiles a real package with a `profile.json` and captured original assets. Other technical source targets compile a `selection.json` instead. Use the [source guide](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md#check-and-compile-source) for the exact `target` and consumer requirements before copying or changing the example. Author a new ID/version, source closure, Mapping, checks, bindings and compatible target; then check, compile, reopen the emitted artifact and generate a consumer application. Merely editing the ID does not create a new mechanism.

For a new source profile based on an admitted family, make the edits in this order:

1. Copy the closest working `.alch` source, its `.profile.json` envelope, required source library and contract files into a new authoring folder. Give the profile and module a distinct identity and version; keep `sources` in the envelope aligned with the actual files.
2. Define the `Rule` checks and pure `Mapping` that return the supported selection shape. In the envelope, set `boundary` to the real `Interface` and `selection.mapping` to that Mapping. Set arguments and any preselection checks explicitly.
3. Bind every returned role and port to a real existing business owner, descriptor/recipe, asset or resource contract. Keep `target.consumer`, `selected_package`, and implementation basis on a supported combination. A source label cannot create a native role.
4. Run `check-source`, then `compile-source` into a new directory. Inspect the emitted `profile.json` or `selection.json` and its captured sources/assets; use the matching consumer to generate and test an application. Change the source or envelope only by checking and compiling a new selection.

For an application-input profile, the selected `target.consumer` and output shape differ. The [CRM application-input guide](../../implementation/cli/docs/APPLICATION-INPUT-PROFILES.md) has a complete role-to-input example and a checked `application-generation-project/v1` consumer.

For a protected service, the existing `protected-ServiceAssembly.profile.json` compiles to a source selection. The working CLI joins it to the separately checked Customer Success business source and profiles:

```sh
alchlang profile compile-source <examples>/protected-ServiceAssembly.profile.json \
  --source-root <examples> --out <new-selection-directory>
alchlang profile generate-source <new-selection-directory>/selection.json \
  --business <checked-business-root>/business.alch \
  --business-profile <checked-business-root>/contracts/selected-profile.json \
  --http-profile <checked-business-root>/contracts/http-profile.json \
  --out <new-application-directory>
```

The generated application still needs its matching Core runtime peer and separately supplied Auth/store resources. This source selection cannot grant access, invent a provider, or deploy a listener. The [full technical source guide](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md) details the exact consumer contracts and artifact shapes.

## When a new mechanism is needed

A profile can choose among mechanisms the compiler already admits. If the source requires a new native ABI, provider, persistence model, effect, descriptor/recipe pair, or unsupported type, changing JSON labels will fail validation or misdescribe the implementation. That work needs a new implementation contract and qualification in the owning capability, followed by a profile that selects it. The [package vocabulary](../../implementation/cli/docs/PROFILE-PACKAGES.md) and [profile authoring contract](../../implementation/cli/docs/PROFILE-AUTHORING.md) define the available operations and limits.
