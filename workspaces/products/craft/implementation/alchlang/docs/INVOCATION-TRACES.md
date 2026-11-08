# Invocation explanations

`alchlang trace` explains one local invocation of a declarative function using supplied JSON input. It compiles the current `.alch` source into a temporary bundle, executes generated code, returns a JSON receipt on stdout, and removes the temporary bundle.

```sh
node dist/cli.js trace ../extensions/invocation-trace-v1/quantity-price.alch --input ../extensions/invocation-trace-v1/input.json
```

The input envelope must provide every integration snapshot. This command does not load environment credentials or fetch remote data. Missing supplied data produces a failed receipt and exit code 1. A successful invocation returns exit code 0, including business results such as no_price. The command accepts at most 1 MiB of input JSON; the authored boundary schema applies its own constraints.

## What the answer means

The receipt identifies the matched result case, observed Rule results, query counts and individual candidate decisions. Each observation links to the generated ontology identity and the relevant source declaration or clause. For example, a rejected Cheapest candidate records its actual row, its collection-relative index, `accepted: false`, and the authored `not exists` predicate.

These are observations of the composite predicate. They do not assert that every subexpression executed, or invent an unrecorded quantified witness. Short-circuit evaluation and filter-before-projection order are preserved. Mapping and Calculation outcomes are observed at their actual calls; memoized declarations are not reevaluated to produce an explanation.

The binding includes source, ontology, behavior, composition and build-manifest digests, plus a canonical input digest. Exact bigint values in events use `{"$uint64":"..."}`; the ordinary result stays unchanged. An absent value uses `{"$absent":true}`. Input hashing uses data properties without invoking getters or toJSON hooks; unencodable input has a null input digest and is still subject to boundary validation.

Execution status and capture completeness are independent. A failed assertion can have a complete trace of the failed execution. A successful invocation can have truncated capture. Missing evidence in a truncated trace is marked `not_fully_observed`, never success or skipped work. On a complete trace, declarations that were never invoked are marked `not_evaluated`. Result-case selection does not imply that its output mapping subsequently succeeded.

## Programmatic use and limits

A generated declarative bundle exports:

```js
const receipt = await invokeWithTrace(input, {maxEvents: 10000, maxBytes: 2097152});
```

This export is also local/provided-input only. It returns failed receipts rather than throwing for application execution failures; invalid capture options throw. Defaults allow 10,000 events and 2 MiB of serialized event data. Options permit 1–20,000 events and 256 bytes–4 MiB. The event limit excludes the ordinary result and receipt metadata. Once capture fills, evaluation continues and the receipt reports dropped events. Separate invocations have separate collectors.

`invoke` and the HTTP handler retain their ordinary response shapes; traces are not exposed by the endpoint. Trace records contain application candidate and mapped values, but no runtime environment, authorization headers or credentials are captured. Nothing persists automatically. Production retention/access policy is outside this prototype.

The selected DomainSpec build must advertise `domainspec.declarative-observation/v1` in its composition metadata. Alch fails explicitly if the installed generator lacks tracing hooks. Observer callbacks receive detached event data, and exceptions in observation do not affect computation.

## Construction and open questions

This is local generated-code evidence, not a signed attestation, proof of remote provider behavior, registry admission, or an expanded DomainSpec project certificate. Digests identify the declared build and inputs; they do not establish authenticity of externally edited receipts. Persisted receipt verification, production transport tracing, and individual quantified witnesses remain future work. See ../../extensions/invocation-trace-v1/PLAN.md for the construction boundary and operational residue.
