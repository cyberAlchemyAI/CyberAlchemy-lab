# Clean installed application consumers

The core AlchLang candidate package contains one complete `application-v1`
example for each supported target language. Each example is self-contained
under `examples/application-v1/<language>` and includes the `.alch` source,
its exact companion manifest, all selected inputs and the evidence files bound
by that manifest.

Install the exact local candidate archives for `@domainspec-v2/cli` and
`@cyberalchemy/alchlang` in a new consumer project. Rust consumers additionally
install `@cyberalchemy/alchlang-rust`. The experimental local-host archive is a
separate repository-bound layer and is not required by `application-v1`.

Resolve the installed example without referring to the source checkout:

```bash
PACKAGE_ROOT="$(node --input-type=module -e "import{fileURLToPath}from'node:url';console.log(fileURLToPath(new URL('../',import.meta.resolve('@cyberalchemy/alchlang'))))")"
LANGUAGE=typescript # or python, or rust
SOURCE="$PACKAGE_ROOT/examples/application-v1/$LANGUAGE/commerce.alch"
OUTPUT="$(mktemp -d)/generated-$LANGUAGE"

npx --no-install alchlang check "$SOURCE"
npx --no-install alchlang build "$SOURCE" --out "$OUTPUT"
npx --no-install alchlang verify "$SOURCE" --out "$OUTPUT"
```

`check` performs source and companion admission plus lowering without writing
the generated target. `build` creates a new provider-application target.
`verify` reconstructs the expected bytes from the installed inputs and rejects
any drift. The generated `.alch/manifest.json`, `.alch/whole/`, and
`.domainspec/` records are inspection evidence; they are not release admission
or production-runtime proof.

The P02 qualification follows the native compilation and loopback scenario
commands in the installed DomainSpec `WHOLE-APPLICATION.md`, verifies the
original Alch target again after the native scenario, and removes every
task-owned consumer and native root. Product-owner validation is intentionally
deferred until L4X.

## Open Questions

- P03 owns freezing the exact archive bytes and all environment identities.
- Product approval, publication, release, deployment and production operation
  remain separate owner decisions.
