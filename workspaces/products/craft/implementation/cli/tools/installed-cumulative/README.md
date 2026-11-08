# Installed cumulative transaction and HTTP checks

Run the original C08/C09/C10 assertions against locally built archives in an isolated
consumer. This development runner does not publish, host an application, run TDE
or EVF, or claim final acceptance.

Example from the CLI directory:

~~~sh
node tools/installed-cumulative/run.mjs --craft-archive /absolute/craft.tgz --alch-archive /absolute/alchlang-core.tgz --inputs /absolute/cumulative-working/http --consumer /absolute/installed-consumer --suite c09-cli
~~~

Suites: c08 (the original complete transaction/crash/replay cases), c09-cli (the installed CLI-to-protected-HTTP case), c09-formation (formation and artifact identities), c09 (all original HTTP
and Schedule test files), c10 (all external provider/happy-probe test files), or all (C09/C10).
Use the public AlchLang core archive, which includes the installed CLI/examples.
For c08, --inputs points to a directory containing its original tests/ and fixtures/ (the retained E13-E45-E43-full72-test-composition-001 contract). It uses a fresh owned work directory per execution and preserves every original .test.mjs case. It does not import the historical derived isolation-guard probe as a product test.

For C09/C10, the input directory supplies the existing tests, fixtures and provider bytes;
their business assertions and expected results remain in those input files.

Overlays contain the working API setup repairs: separate application/HTTP profile
paths and controlled-provider socket-close completion. The copied C09 CLI argument
list receives the explicit HTTP option; its assertions are preserved. Historical
runtime-gate values are retained because the original harness requires them;
setting them for a working-source diagnostic does not constitute a frozen proof.

Archive inputs are copied under content hashes inside the consumer, so npm cannot silently reuse an older tarball with the same package version/path. Logs append to the consumer's results directory. The latest JSON result gives the
command, selected files and log byte range. A failed check is repaired in the same
implementation/consumer. Full C01-C15 acceptance still requires the final matrix.

For long source-authored integration cases, `--import ./tools/installed-cumulative/installed-runtime.mjs` redirects compiler imports from this checkout to the canonical installed package named by `CRAFT_TEST_INSTALLED_CLI_ROOT`. Test and fixture source stays unchanged; compiler modules and profile assets come only from that installed package. Missing members reject instead of falling back to mutable source. Select `CRAFT_COMMERCE_AUTH_COMPONENT=selected` for the bundled genuine native Auth component. This allows ordinary source edits while an installed diagnostic runs without invalidating its implementation pins.

The additive C09 overlay also repairs authored test producers that were invalid under the existing language rules: text length uses `length-scalars`, and the response-size cases build more than 9000 output bytes from three bounded 3000-character fields instead of a string literal exceeding the 4096-character source-line limit. The response byte limit remains 8192, runtime/HTTP expectations are unchanged, and the original test assertion files are copied without modification.

The C08 scheduling overlay adds one initial-journal barrier: worker 1 waits for worker 0 to finish its real initial journal lookup before both proceed to the original protected-read barrier. This prevents an unrelated zero-wait SQLite writer-reservation collision from aborting before the intended two-read/revision race. It observes PRAGMA database_list solely to identify the original store connection; every original SQL call executes once. All original business outcomes, read/write barriers, time limits and assertions remain. Historical test inputs are untouched.

## Open Questions

See ../../docs/GENERIC-APPLICATIONS.md#open-questions.
