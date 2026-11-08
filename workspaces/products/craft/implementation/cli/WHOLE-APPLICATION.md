# Whole-application compilation

DomainSpec compiles the domain and integration declarations into one typed
application graph and a coherent TypeScript, Python, or Rust formation candidate.
An explicit provider selection
adds reference PostgreSQL 16, NATS JetStream, outbound HTTP, and signed inbound
HTTP adapter source. Compilation writes source code, manifests, locks,
migrations, and a digest-bound receipt; it does not prove that the adapters are
wired into an executable business flow, connect to providers, or deploy the
project.

## Installed product surface

The npm package includes:

- `@domainspec-v2/cli/whole-application` for pure whole-application and provider planning;
- `@domainspec-v2/cli/reference-runtime` for the bounded TypeScript runtime plan;
- the coherent commerce source, selections, provider selections, and executable startup scenarios under `examples/reconciled-commerce/`;
- `contracts/integration-generation-source-v2.schema.json`;
- `contracts/application-integration-binding-v1.schema.json`;
- `contracts/compiled-application-graph-v1.schema.json`;
- `contracts/provider-pack-selection-v1.schema.json`;
- `contracts/provider-application-runtime-evidence-v1.schema.json`;
- `contracts/whole-application-plan-v1.schema.json`;
- the persistence, messaging, external API, observation, and integration-kernel schemas needed to resolve the integration source schema's relative references entirely inside the installed package.

Provider selection is required for provider code. DomainSpec never silently
chooses a database, broker, HTTP client, inbound framework, or credential.

## Generate and verify a formation candidate

Run these commands from a consumer project that has installed
`@domainspec-v2/cli`. The temporary root is owned by this shell session, and the
trap removes it when the session exits.

```bash
PACKAGE_ROOT="$(node --input-type=module -e "import{fileURLToPath}from'node:url';console.log(fileURLToPath(new URL('../',import.meta.resolve('@domainspec-v2/cli'))))")"
EXAMPLE="$PACKAGE_ROOT/examples/reconciled-commerce"
RUN_ROOT="$(mktemp -d)"
trap 'rm -rf -- "$RUN_ROOT"' EXIT
mkdir -p "$RUN_ROOT/observations"
```

Choose one language and use the matching selection files throughout:

```bash
LANGUAGE=typescript # or python, or rust
TARGET="$RUN_ROOT/application-$LANGUAGE"

npx --no-install domainspec-v2 build "$EXAMPLE/source" \
  --language "$LANGUAGE" \
  --target-root "$TARGET" \
  --compilation-selection "$EXAMPLE/selections/$LANGUAGE.json" \
  --integration-source "$EXAMPLE/integrations/application.json" \
  --provider-selection "$EXAMPLE/providers/$LANGUAGE.json" \
  >"$RUN_ROOT/observations/$LANGUAGE-build.json"

npx --no-install domainspec-v2 verify "$EXAMPLE/source" \
  --language "$LANGUAGE" \
  --target-root "$TARGET" \
  --compilation-selection "$EXAMPLE/selections/$LANGUAGE.json" \
  --integration-source "$EXAMPLE/integrations/application.json" \
  --provider-selection "$EXAMPLE/providers/$LANGUAGE.json" \
  >"$RUN_ROOT/observations/$LANGUAGE-verify-before.json"
```

Every generated language includes the same language-neutral
`.domainspec/application-graph.json`. Its nodes, edges, authority digests, source
provenance, and graph digest make the application wiring inspectable without
reading generated source code. The graph uses these canonical relationships:

```text
Mapping          --reads-payload-from--------> Event
Mapping          --produces-message-contract-> Message Contract
Inbound Endpoint --invokes-------------------> Operation
Operation        --accepts-request-----------> Request Contract
Publication      --publishes-event-----------> Event
```

`publishes-event` is deliberately distinct from the domain relationship
`Entity --emits--> Event`: creating a domain event and publishing it through a
transport are different facts.

The generated `.domainspec/whole-application.json` receipt binds the domain
source manifest, integration source, compiler selection, application plan,
compiled application graph, integration contribution, binding, and every
generated artifact. `verify`
rejects stale receipts, changed bytes, missing files, and unexpected paths.
This is exact formation evidence, not runtime evidence. The optional bounded
TypeScript reference-runtime plan is a separate surface and is not silently
included by `build`.

## Record bounded native runtime evidence

`verify-runtime` preserves both earlier command meanings: `build` still forms
the candidate, and `verify` still checks exact artifact currentness. The new
command copies a current provider target into a task-owned temporary directory,
installs its locked dependencies there, compiles it, starts the packaged
loopback webhook scenario, removes the temporary directory, verifies the
original target again, and writes one external receipt.
Both `--temporary-parent` and `--receipt` are rejected when they resolve to the
generated target or any of its descendants, so evidence collection cannot use
the target as working or receipt storage.

Use the tool pair for the selected language:

```bash
case "$LANGUAGE" in
  typescript)
    LANGUAGE_TOOLS="--node-executable $(command -v node) --npm-executable $(command -v npm)"
    ;;
  python)
    PYTHON_IMAGE="python:3.11.2-slim@sha256:9ad4ffc502779e5508f7ac1eccab4a22786b80bd53d721d735f6de0840b245a1"
    LANGUAGE_TOOLS="--docker-executable $(command -v docker) --python-image $PYTHON_IMAGE"
    ;;
  rust)
    LANGUAGE_TOOLS="--cargo-executable $(command -v cargo)"
    ;;
esac

# LANGUAGE_TOOLS intentionally expands into option/value pairs.
# shellcheck disable=SC2086
npx --no-install domainspec-v2 verify-runtime "$EXAMPLE/source" \
  --language "$LANGUAGE" \
  --target-root "$TARGET" \
  --temporary-parent "$RUN_ROOT" \
  --receipt "$RUN_ROOT/observations/$LANGUAGE-runtime-evidence.json" \
  --compilation-selection "$EXAMPLE/selections/$LANGUAGE.json" \
  --integration-source "$EXAMPLE/integrations/application.json" \
  --provider-selection "$EXAMPLE/providers/$LANGUAGE.json" \
  $LANGUAGE_TOOLS
```

Python may instead use `--python-executable <absolute-file>` when that
interpreter provides pip. The command may download locked registry dependencies.
Working dependency installations and compiler output remain under the temporary
root and are removed before the receipt is written. Rust reuses Cargo's
caller-managed registry cache while keeping `CARGO_TARGET_DIR` disposable; the
receipt records that cache boundary. The generated target is never used as a
dependency or build-output directory.

The receipt separately records formation currentness, dependency installation,
native compilation, listener startup, invalid-signature rejection, and
valid-signature acceptance. PostgreSQL, NATS, outbound HTTP, transport
delivery, consumer completion, and production runtime guarantees remain
explicitly unobserved.

## Compile and run the installed startup scenario

The startup scenarios use loopback HTTP. Each sends an invalid HMAC-SHA256
signature first and requires `401` with zero application-handler calls. It then
sends a valid signature and requires `202` with exactly one call. The JSON result
is the direct observation for this installed-language smoke boundary.

### TypeScript

```bash
(
  cd "$TARGET"
  npm_config_cache="$RUN_ROOT/npm-cache" npm ci --ignore-scripts --no-audit --no-fund
  npm_config_cache="$RUN_ROOT/npm-cache" npx --no-install tsc --noEmit --pretty false
  npm_config_cache="$RUN_ROOT/npm-cache" npx --no-install tsc --noEmit false --outDir dist --pretty false
  node "$EXAMPLE/scenarios/typescript-webhook.mjs" "$TARGET" \
    >"$RUN_ROOT/observations/typescript-webhook.json"
  rm -rf -- "$TARGET/node_modules" "$TARGET/dist"
)
```

### Python

The qualified flow uses the pinned Python 3.11.2 Linux image. The generated
target and packaged scenario are mounted read-only. Compiled bytecode,
dependencies, and pip state live only inside the disposable container.

```bash
PYTHON_IMAGE="python:3.11.2-slim@sha256:9ad4ffc502779e5508f7ac1eccab4a22786b80bd53d721d735f6de0840b245a1"
docker run --rm --platform linux/amd64 \
  --mount "type=bind,src=$TARGET,dst=/application,readonly" \
  --mount "type=bind,src=$EXAMPLE/scenarios/python-webhook.py,dst=/scenario.py,readonly" \
  --env PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON_IMAGE" /bin/sh -ceu \
  'PYTHONPYCACHEPREFIX=/tmp/bytecode python -m compileall -q /application/src &&
   python -m pip install --disable-pip-version-check --no-input --no-cache-dir --quiet --target /tmp/dependencies -r /application/requirements.lock >/tmp/pip.log &&
   PYTHONPATH=/tmp/dependencies:/application/src python /scenario.py /application' \
  >"$RUN_ROOT/observations/python-webhook.json"
```

### Rust

The scenario source is a temporary consumer binary. Cargo build output is
redirected outside the generated target. Remove the consumer binary before the
final currentness check.

```bash
mkdir -p "$TARGET/src/bin"
cp "$EXAMPLE/scenarios/rust-webhook.rs" \
  "$TARGET/src/bin/domainspec-installed-scenario.rs"
CARGO_HOME="$RUN_ROOT/cargo-home" CARGO_TARGET_DIR="$RUN_ROOT/rust-target" cargo check \
  --manifest-path "$TARGET/Cargo.toml" --locked
CARGO_HOME="$RUN_ROOT/cargo-home" CARGO_TARGET_DIR="$RUN_ROOT/rust-target" cargo run \
  --manifest-path "$TARGET/Cargo.toml" --locked --quiet \
  --bin domainspec-installed-scenario \
  >"$RUN_ROOT/observations/rust-webhook.json"
rm -- "$TARGET/src/bin/domainspec-installed-scenario.rs"
rmdir "$TARGET/src/bin"
```

## Configuration references

The generated bootstrap requires these names at runtime:

| Name | Meaning | Classification |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection URL | secret reference |
| `NATS_URL` | NATS server URL | endpoint reference |
| `PAYMENT_BASE_URL` | outbound payment API base URL | endpoint reference |
| `INBOUND_BIND_ADDRESS` | inbound listener address | endpoint reference |
| `WEBHOOK_SECRET` | HMAC secret for inbound webhook verification | secret reference |

The generated files contain only these references. Supply values through the
runtime environment or a deployment-specific secret mechanism; do not write
credential values into the DomainSpec source or provider selection.

## Verify currentness after the scenario

After removing derived build output and temporary consumer files, repeat the
same `npx --no-install domainspec-v2 verify` command and save it as
`$RUN_ROOT/observations/$LANGUAGE-verify-after.json`. A passing result proves
that the authored inputs and generated target still match the recorded plan. It
does not infer runtime behavior from compilation; the scenario JSON is separate
runtime evidence.

Inspect the bounded observations before cleanup:

```bash
for observation in "$RUN_ROOT"/observations/*.json; do
  printf '%s\n' "== $observation"
  cat "$observation"
done
```

Then leave the shell or run the registered trap explicitly:

```bash
trap - EXIT
rm -rf -- "$RUN_ROOT"
```

## Programmatic planning

The public subpaths expose a pure planning sequence:

```typescript
import {
  planWholeApplicationV1,
  composeProviderApplicationV1,
} from "@domainspec-v2/cli/whole-application";
import { planReferenceRuntimeV1 } from "@domainspec-v2/cli/reference-runtime";

const whole = planWholeApplicationV1(sourceRoot, compilationSelection, integrationSource);
const providers = composeProviderApplicationV1(whole, providerSelection, integrationSource);
const runtime = planReferenceRuntimeV1(providers);
```

`planReferenceRuntimeV1` is TypeScript-only. It plans a PostgreSQL transaction
for `commerce:perform`, a transactional outbox, NATS channel setup and dispatch,
HTTP helpers, signed-webhook validation, an immutable ORODI observation, and a
bounded proof program. Planning performs no provider call.

The runtime keeps these facts separate:

- the domain Event is mapped into, but is not identical to, the transport Message;
- application commit does not imply broker acceptance;
- broker acceptance does not imply consumer completion;
- retryability classification does not select or execute a retry;
- ORODI receives an allowlisted observation and has no return or control edge.

## Evidence boundary

The installed startup scenarios prove generated-project installation,
compilation, listener startup, signature rejection, signature acceptance, and
handler isolation in each supported language. The separate bounded reference
runtime qualification exercises disposable PostgreSQL and NATS services plus
loopback HTTP fixtures for TypeScript. Neither proof establishes production
behavior, scale, deployment readiness, product approval, publication, release
authorization, or operational support.
