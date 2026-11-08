# Generate a small business API with Craft and AlchLang

This guide covers the `node-http-entry-u0-v4` preview cell. AlchLang is the text you write to describe business data and behavior. Craft checks that meaning, derives the technical bindings selected by a profile, and generates code plus linked business/system views.

The example describes one delivery acknowledgement. An acknowledgement has an exact integer identity and a caller-provided `verified` flag. The operation returns the acknowledgement when that flag is true; otherwise it rejects it. The flag is an input condition. It does not independently verify a delivery.

The result is an importable Node.js API handler. This cell uses Node's built-in `Request`/`Response` implementation and exact integer support. Its profile fixes the implementation, codec and resource limits. [Supported behavior and troubleshooting](SUPPORTED-CELL.md) give the precise boundary. The public repository and release are still deferred; these instructions describe the prepared preview bundle.

## 1. Install the prepared bundle

The selected environment is Linux x64, Node **26.8.1**, npm **11.19.0** and TypeScript **6.0.3**. Check your versions:

```bash
node --version
npm --version
```

The bundle contains `candidate.json` and these exact local package names:

- `archives/domainspec-v2-cli-1.3.0.tgz`
- `archives/cyberalchemy-alchlang-0.7.0-candidate.0.tgz`
- `archives/typescript-6.0.3.tgz`

From the bundle directory, check its declared archive bytes:

```bash
node --input-type=module -e 'import fs from "node:fs"; import crypto from "node:crypto"; const m=JSON.parse(fs.readFileSync("candidate.json","utf8")); for(const a of m.artifacts){const b=fs.readFileSync(a.path); if(b.length!==a.bytes||crypto.createHash("sha256").update(b).digest("hex")!==a.sha256)throw Error("Archive differs: "+a.path);} console.log("Archive bytes match candidate.json");'
```

Create a separate project so the archive bundle stays unchanged:

```bash
mkdir u0-demo
cd u0-demo
npm init --yes
npm install --offline --ignore-scripts --no-audit --no-fund --package-lock=false \
  ../archives/domainspec-v2-cli-1.3.0.tgz \
  ../archives/cyberalchemy-alchlang-0.7.0-candidate.0.tgz \
  ../archives/typescript-6.0.3.tgz
```

The two CLI packages provide `alchlang` and `domainspec-v2`. The commands below use their installed files explicitly so the selected package is visible.

## 2. Start from the business source

Copy the [complete source example](../examples/business.alch):

```bash
cp node_modules/@domainspec-v2/cli/profiles/node-http-entry-u0-v4/examples/business.alch ./business.alch
```

Its declarations have distinct jobs:

| Declaration | What you specify |
|---|---|
| `business-model` and `owner` | The business identity, version and accountable reviewer |
| `requirement` | Meaning, actors, examples, counterexamples and limits |
| `entity Submission` | `id UInt64`, its identity field and `verified Bool` |
| `rule CanProcess` | The executable condition `item.verified` |
| `operation Process` | The guard call, whole-input result, rejection code and `effects none` |
| `entry ProcessHttp` | The invoked operation, public name and `permission public` |

The important executable portion is:

```text
rule CanProcess:
  requirement Processing
  meaning "Require the supplied verified flag."
  input item Submission
  condition item.verified

operation Process:
  meaning "Return a supplied eligible acknowledgement."
  input request Submission
  output Submission
  requires CanProcess(item: request)
  returns request
  on-rejection delivery-verification-required
  effects none

entry ProcessHttp:
  invokes Process
  public-name confirm-delivery
  permission public
```

The copied file includes the required model, requirement and Entity declarations. A Rule's `condition` is the Boolean test. The Operation explicitly calls it and names the rejection outcome. No separate Definition or FormalClaim is needed to generate this code.

## 3. Select a profile and review the captured model

```bash
U0_CLI="./node_modules/@cyberalchemy/alchlang/dist/core-cli.js"
node "$U0_CLI" business direct review ./business.alch \
  --profile node-http-entry-u0-v4 --output code > review.json
cat review.json
```

Read `subject`, `source_capture` and `sdk_sha256`. The review captures both business meaning and the implementation inputs. Confirm the condition, guard, result, permission and rejection behavior before recording acceptance.

The CLI displays two different digests. `review_sha256` identifies the reviewed business subject. **`decision_scope_sha256` is the digest required by the CLI's `--digest` option.** It also binds the captured implementation/source scope.

Record an explicit acceptance of this tutorial fixture:

```bash
U0_SCOPE="$(node --input-type=module -e 'import fs from "node:fs"; console.log(JSON.parse(fs.readFileSync("review.json","utf8")).decision_scope_sha256);')"
node "$U0_CLI" business direct decision ./business.alch \
  --profile node-http-entry-u0-v4 --output code \
  --owner dispatch-team --outcome accepted --digest "$U0_SCOPE" \
  --decision-id tutorial-accepted --record ./decision.json
```

`dispatch-team` is the example's declared owner. For your model, use its actual owner and reviewed scope. The recorded business decision is separate from product approval or publication. A declined decision is also recordable and prevents generation.

## 4. Generate the application

Use a fresh output directory:

```bash
node "$U0_CLI" business direct generate ./business.alch \
  --profile node-http-entry-u0-v4 --output code \
  --decision ./decision.json --out ./application \
  --optional-output base-model --optional-output conjecture-problems
```

The command returns an output-result ledger. Required code, API contracts and all three views must be produced together. The two optional formal outputs are currently `unsupported-optional` with `artifact: null`. Requiring either unavailable formal export rejects generation.

A complete result includes:

| File | Purpose |
|---|---|
| `application/entry.mjs` | Generated entry and injected HTTP handler |
| `application/callable/invoke.mjs` | Generated pure business operation |
| `application/runtime/` | Actual selected HTTP, codec and exact-value assets |
| `application/api/contracts.json` | Wire fields, operation and response mappings |
| `application/views/business.json` | Captured business facts and optional assurance |
| `application/views/system.json` | Checked domain structure, generated subjects and native selection |
| `application/views/bridge.json` | Links from business declarations to actual checked/generated owners |
| `application/evidence/output-lineage.json` | Original subject, native assets and portable-file lineage |
| `application/outputs/code.json` | Generated code inventory and content hashes |

Craft derives the Interface and input/output Mappings for this profile. You do not handwrite those bindings or the handler. The views retain the actual source/profile/native relationships; a saved JSON view does not itself grant runtime custody or ontology admission.

## 5. Exercise the generated API

```bash
node ./node_modules/@domainspec-v2/cli/profiles/node-http-entry-u0-v4/examples/exercise.mjs ./application
```

The consumer imports `entry.mjs` and calls its generated handler using a `Request`. It observes:

```json
{"status":200,"body":{"kind":"completed","value":{"id":"9007199254740993","verified":true}}}
{"status":422,"body":{"kind":"rejected","code":"delivery-verification-required"}}
```

On the JSON wire, UInt64 values are canonical decimal **strings**. Native generated callables use `bigint`, for example `9007199254740993n`. The JSON range is `"0"` through `"18446744073709551615"`; sending an ordinary JSON number rejects the payload. This preserves values beyond JavaScript's safe-number boundary.

The example consumer supplies requests and checks responses. Its business condition and operation come entirely from generated code. The URL is a Request value used for dispatch; these commands start no listener or hosted service.

## 6. Change the model deliberately

You continue to author the business meaning, fields, condition, guard, result, entry permission and failure contract. The selected profile generates supported technical bindings and code. Formal claims are optional assurance inputs. Changing a claim changes its assurance/review scope without making a proof run part of code generation.

After changing source, selected profile or captured tool/SDK inputs, run review again and record a new explicit decision for the displayed scope. Use new decision and output paths. Existing outputs are preserved; the writer refuses replacement, including an existing empty directory.

Complete generation of this small preview example currently takes several minutes in the qualification environment. No low-latency or scalability guarantee is qualified. See [limits and troubleshooting](SUPPORTED-CELL.md) before extending the example.

## Open Questions

[Supported-cell scope and follow-ons](SUPPORTED-CELL.md#open-questions) own the remaining capability questions. Local hosting, TDE, EVF, live activation, deployment and publication remain deferred.
