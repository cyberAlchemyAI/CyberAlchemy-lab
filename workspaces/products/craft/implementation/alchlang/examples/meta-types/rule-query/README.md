# Named Rules in Queries and read-bound Operations

This executable `application-v1` example declares `EligibleOrder` once. Both
`FindEligibleOrders` and `FindEligibleOrder` explicitly bind their supplied Order
row to that Rule. AlchLang projects the supported ground Rule expression into
the generated Query filter; the projection preserves the Rule's identity and
exact interpretation inputs. A Rule inside a Query is supported through this
application profile, even though a directly authored Craft typed Query contract
has an inline predicate.

From a consumer project containing the exact installed AlchLang and Craft
packages, `typescript@6.0.3` and `@types/node@26.4.0`, run:

```bash
node node_modules/@cyberalchemy/alchlang/examples/meta-types/rule-query/run.mjs --output /absolute/path/to/new-directory
```

The output directory must be absent and its parent must exist. The runner uses
the packaged AlchLang CLI to check, build and verify `model.alch`, then compiles
the generated TypeScript with the consumer's compiler. It tests zero, one and
several eligible rows. The list returns every matching row; the optional Query
returns null or one row and rejects several matches. It has no limit that could
hide ambiguous results. Invalid row types and hidden Query arguments reject.

`SubmitOrder` explicitly reads the current Order through a supplied transaction
binding. Its guard checks that read value, and its write replaces it with the
request. The successful example starts from an accepted current Order and writes
an unaccepted replacement, demonstrating which value the guard actually checks.
The runner separately verifies guard refusal, missing records, read failures,
commit rejection, uncertain commit and malformed input. Refused and failed
precommit cases create no committed batch. An uncertain commit returns an
indeterminate outcome; it is not automatically retried or reported successful.

The binding is an explicit in-memory test transaction. This qualifies the
generated operation's read/guard/write/settlement protocol, not durable storage,
remote effects, recovery or hosting.

`fixture/` contains synthetic meaning, acceptance and definition records used
to make the exact formal interpretation portable. Their accepted-shaped fields
are example inputs with `authority_effect: none`; they confer no production
approval. The companion hashes bind exact bytes and do not constitute a proof
that the business meaning is correct. The runtime witness is finite behavioral
evidence, not a formal proof.

## Open Questions

Installed successor qualification and public publication are owned by the
meta-type completion execution records. Additional Rule expressions and Query
authoring profiles need their own qualification. Local hosting, TDE and EVF
remain deferred.
