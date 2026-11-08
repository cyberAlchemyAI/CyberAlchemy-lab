# Business-only application generation

Status: candidate. Source runtime controls pass; frozen and fresh installed release qualification are tracked separately. Formal claims remain unproved; generated views are explanatory projections.

AlchLang describes your business types, Rules, Mappings, Operations and optional formal claims. Craft checks those declarations and generates their implementation. A locked architecture profile supplies request transport, technical layout and the empty-effects settlement component. You supply the business meaning and explicitly select public entries; you do not write feature-specific TypeScript ports.

The first supported application path accepts an HTTP POST request, uses an authored Mapping to create the Operation input, evaluates its declared Rule, settles an empty batch and returns the whole input value. It performs no persistence, event publication or external API call. Existing function-service profiles separately support explicitly configured read-only GET dependencies.

For the complete choice of installed paths, a quote API with an external read and calculation, and the separate source-backed Commerce artifact inspection, see [profile generation](PROFILE-GENERATION.md). The Commerce candidate demonstrates selected persistence, Event and Workflow wiring with fixtures; it is not a blank-project protected application recipe.

## Start from an empty consumer

Use Node26.8.1 and TypeScript6.0.3. Install the two successor archives with scripts disabled, then copy a bundled example into your consumer directory. Archive preparation and installed qualification are separate release gates; these names describe the selected successor versions.

```sh
npm init -y
npm install --ignore-scripts ./domainspec-v2-cli-1.3.0.tgz ./cyberalchemy-alchlang-0.7.0-candidate.0.tgz typescript@6.0.3
cp node_modules/@cyberalchemy/alchlang/examples/profile-engine/business-notice/* .
npx --no-install alchlang profile select project.json > selected.json
npx --no-install alchlang profile check project.json
npx --no-install alchlang profile plan project.json > plan.json
npx --no-install alchlang profile generate project.json --out generated
npx --no-install alchlang profile view project.json > views.json
npx --no-install alchlang profile verify project.json --out generated
```

The example profile path is `node_modules/@domainspec-v2/cli/profiles/node-http-entry-local-v2`, relative to project.json. Select `node-http-shared-ports-v2` by changing both profile id and path. The shared profile generates one typed request-transport module consumed by application entries; the local profile gives each entry its own module. Both preserve the same business behavior.

`select` returns an object containing `lock`. Save that property as a lock file and pass `--lock lock.json` to later commands when you need an exact source/profile/tool selection. Source, semantic, package, native asset, compiler or tool changes invalidate that lock. A generation destination must be new; existing directories are preserved.

## Author the business model

Start with the bundled domain.alch, business-semantics.json and project.json. The Alch source declares types and properties, the formal proposition and Rule, total field Mapping and Operation input/output. The semantic manifest gives explicit ontology identities and meanings, Rule sort/constant/predicate interpretations, invariant arguments, Operation guard arguments and result correspondence. The project selects model files, public Operation intents, request Mapping arguments and the architecture package.

An application needs no unrelated function or health endpoint. Multiple application models may use repeated local declaration names; project model IDs and public intent IDs distinguish their source and generated ownership. Cross-source linking within one application is currently unsupported.

The notice example uses typed identity reflexivity. It does not require a positive ID or establish eligibility. For a real false-guard example, use business-acknowledgement: its authored Entity Boolean flag controls confirmation and its label is retained in the result. Structural Entity normalization checks its fields and identity without inventing an invariant. Declared invariants and Operation guards remain explicit.

## Meaning, decisions and formal claims

The compiler requires accepted business-meaning and definition bodies with an explicit owner decision for the exact meaning subject. These are authored inputs. It does not turn candidate meaning, prose criteria, source hashes or passing examples into acceptance or formal proof. The bundled records are explicitly synthetic examples.

To calculate the subject digest while authoring your own record:

```sh
node --input-type=module <<'JS'
import {readFileSync} from 'node:fs';
import {profileEngine} from '@domainspec-v2/cli';
const semantic=JSON.parse(readFileSync('business-semantics.json','utf8'));
for(const [name,claim] of Object.entries(semantic.claim_meanings)) {
  console.log(name, profileEngine.dataDigest(claim.business_meaning));
}
JS
```

This computes the declared key-sorted JSON SHA-256 digest; it creates no acceptance. After the business owner explicitly accepts that exact meaning/version, record their decision and matching subject digest in owner_acceptance. A meaning edit needs a matching new decision. Preserve the authored claim identity, version, selected definitions and transitive definition correspondence. The public check command rejects mismatched decisions and unsupported formal interpretations. Claims remain visible as unproved residue in the bridge view.

## Invoke the generated API without hosting

```sh
node --input-type=module <<'JS'
import {handler} from './generated/app/index.mjs';
const request=new Request('https://example.invalid/receiveNotice', {
  method:'POST', headers:{'content-type':'application/json'},
  body:JSON.stringify({payload:{id:'7'}})
});
const response=await handler(request);
console.log(response.status, await response.json());
JS
```

This constructs a Request and calls the generated handler directly; it makes no network request and starts no server. The response contains status returned, value `{id:"7"}` and the full committed Operation outcome. The generated profile owns the empty-effects store. Injected ports are a controlled extension/testing surface for rejected, failed or indeterminate settlement; an invalid explicit override rejects before beginning a transaction. Observer failures do not change the outcome. Required in-flight cancellation is unsupported; request-body deadlines never claim to cancel an unsettled transaction.

## Create the three business input files yourself

For a blank project, create the following exact files instead of copying the bundled example. The records are synthetic; for your domain the business owner supplies and accepts their own meaning and definitions. No generated execution, interpretation, provider or request-binding companion is authored.

The source expresses the proposition, Rule, value fields, total Mapping and Operation. The project selects that Operation, maps body.payload into its Mapping parameter and explicitly permits public access. The manifest records meaning and the exact Rule/invariant/guard correspondence.

| Manifest field | What you supply |
|---|---|
| declarations | Meaning and ontology identity for declarations and fields; declared invariants |
| claim_meanings | Claim identity, business meaning, accepted definitions, explicit definition references and exact-subject owner decision |
| rule_meanings | Which business type/constant/predicate interprets each formal symbol |
| operation_behaviors | Exact guard argument paths and the whole-input result |
| value_invariant_bindings | Exact value field supplying each declared invariant argument |
| required_guarantees | Guarantees required by this application; unsupported requirements reject |

Create domain.alch:

```alch
# Synthetic business-only example; formal claims remain unproved.
# Open questions: README.md
domain commerce "Notice reception"
owner business-author
formal-claim IdentityClaim:
  profile fol-core/1-candidate
  sort Identity
  constant identity: Identity
  proposition identity = identity
  ceiling "Typed identity reflexivity only; no positive-ID or eligibility condition."
rule IdentityValid:
  claim IdentityClaim
value-object OrderNotice:
  id UInt64
mapping MessageToOrder:
  input payload OrderNotice
  target OrderNotice
  total true
  field id <- payload.id
operation ReceiveNotice:
  input OrderNotice
  output OrderNotice
  requires IdentityValid
```

Create project.json:

```json
{
  "schema_version": "craft.profile-project/v2-candidate",
  "id": "notice-reception",
  "domain_sources": [],
  "public_intents": [],
  "external_reads": [],
  "formal_claims": [],
  "application_models": [
    {
      "id": "commerce",
      "source": "domain.alch",
      "semantics": "business-semantics.json"
    }
  ],
  "application_intents": [
    {
      "id": "receiveNotice",
      "application_id": "commerce",
      "operation_ref": "ReceiveNotice",
      "mapping_ref": "MessageToOrder",
      "mapping_arguments": {
        "payload": {
          "root": "body",
          "path": [
            "payload"
          ]
        }
      },
      "access": {
        "kind": "public"
      }
    }
  ],
  "profiles": [
    {
      "id": "node-http-entry-local-v2",
      "version": "1.0.0",
      "path": "node_modules/@domainspec-v2/cli/profiles/node-http-entry-local-v2"
    }
  ]
}
```

Create business-semantics.json:

```json
{
  "schema_version": "craft.business-application/v1-candidate",
  "owner": "business-author",
  "declarations": {
    "IdentityValid": {
      "ontology": "BUSINESS-IDENTITY-VALID",
      "meaning": "Typed identity reflexivity."
    },
    "OrderNotice": {
      "ontology": "BUSINESS-ORDER-NOTICE",
      "meaning": "A received order identity, without persistence.",
      "invariants": [
        "IdentityValid"
      ],
      "properties": {
        "id": {
          "ontology": "BUSINESS-ORDER-NOTICE#id",
          "meaning": "Received exact unsigned identity."
        }
      }
    },
    "MessageToOrder": {
      "ontology": "BUSINESS-NOTICE-MAPPING",
      "meaning": "Project payload identity without changing it."
    },
    "ReceiveNotice": {
      "ontology": "BUSINESS-RECEIVE-NOTICE",
      "meaning": "Return the supplied notice after explicit settlement, with no persistence.",
      "failure_continuation": "return-notice-error"
    }
  },
  "claim_meanings": {
    "IdentityClaim": {
      "claim_id": "FormalClaim:notice-identity",
      "version": "1",
      "supersedes": null,
      "business_meaning": {
        "schema_version": "domainspec-v2.business-meaning/v1-candidate",
        "meaning_id": "Meaning:notice-identity",
        "version": "1",
        "owner": "business-author",
        "status": "accepted",
        "domain_context": "Notice receipt without persistence",
        "rule": "Every supplied UInt64 identity equals itself.",
        "applies_when": [
          "the input is a well-typed UInt64 notice"
        ],
        "actors": [
          "business-author"
        ],
        "inputs": [
          "OrderNotice.id"
        ],
        "outcomes": [
          "same identity is returned"
        ],
        "examples": [
          {
            "case_id": "identity-seven",
            "given": "a UInt64 identity7",
            "when": "received",
            "then": "identity7 is returned",
            "why": "typed identity reflexivity"
          }
        ],
        "counterexamples": [
          {
            "case_id": "outside-uint64",
            "given": "negative identifier text",
            "when": "received",
            "then": "input is rejected before settlement",
            "why": "outside the declared UInt64 domain, not a false reflexivity claim"
          }
        ],
        "boundaries": [
          "no positive-identity restriction",
          "no persistence/event publication"
        ],
        "claim_ceiling": "Explicit business meaning; formal property remains unproved.",
        "authority_effect": "none"
      },
      "owner_acceptance": {
        "schema_version": "domainspec-v2.business-acceptance-decision/v1-candidate",
        "decision_id": "notice-owner-decision-v1",
        "owner": "business-author",
        "outcome": "accepted",
        "subject": {
          "meaning_id": "Meaning:notice-identity",
          "version": "1",
          "canonicalization": "domainspec-json-keysort-excluding-acceptance-v1",
          "digest_algorithm": "sha256",
          "digest": "5670d47f08fbbcef608816c1e98fe0b85852a84362f93e6984041971d14b93dd"
        },
        "authority_effect": "none"
      },
      "definitions": [
        {
          "definition_id": "BUSINESS-IDENTITY",
          "term": "Identity",
          "definition_kind": "value-object",
          "formal": {
            "definition": "An integer between0 and18446744073709551615 inclusive.",
            "expression": "UInt64",
            "notation": [
              {
                "symbol": "Identity",
                "meaning": "the exact unsigned identifier"
              }
            ],
            "operational_interpretation": "Validate exact UInt64 input without a positivity requirement."
          },
          "plain_language": "An exact unsigned identity.",
          "domain_context": "Notice receipt",
          "depends_on": [],
          "business_fact_refs": [
            "#/rule"
          ],
          "interpretation_refs": [
            "#/inputs"
          ],
          "source_concept_refs": [
            "OrderNotice.id"
          ],
          "forbidden_collapses": [
            "Not an order eligibility decision",
            "Not evidence of persisted state"
          ],
          "status": "accepted"
        }
      ],
      "definition_refs": [
        "BUSINESS-IDENTITY"
      ]
    }
  },
  "rule_meanings": {
    "IdentityValid": {
      "sorts": {
        "Identity": "UInt64"
      },
      "constants": {
        "identity": "identity"
      },
      "predicates": {}
    }
  },
  "operation_behaviors": {
    "ReceiveNotice": {
      "input_name": "request",
      "guards": [
        {
          "rule": "IdentityValid",
          "arguments": {
            "identity": {
              "root": "request",
              "path": [
                "id"
              ]
            }
          }
        }
      ],
      "result": {
        "root": "request",
        "path": []
      }
    }
  },
  "required_guarantees": [
    "preserve-settlement-outcome",
    "preflight-cancellation-only"
  ],
  "value_invariant_bindings": {
    "OrderNotice": [
      {
        "rule": "IdentityValid",
        "arguments": {
          "identity": {
            "root": "value",
            "path": [
              "id"
            ]
          }
        }
      }
    ]
  }
}
```

Run the six profile commands from the first section, then invoke the generated handler. A named Entity does not imply a database; this Operation declares no writes or events.

## Revise meaning and record a new owner decision

This synthetic exercise demonstrates currentness. First edit the business meaning, leaving the old decision unchanged:

```sh
node --input-type=module <<'JS'
import fs from 'node:fs';
const file='business-semantics.json',s=JSON.parse(fs.readFileSync(file,'utf8'));
s.claim_meanings.IdentityClaim.business_meaning.version='2';
s.claim_meanings.IdentityClaim.business_meaning.domain_context='Notice receipt: return the input without persistence';
fs.writeFileSync(file,JSON.stringify(s,null,2)+'\n');
JS
npx --no-install alchlang profile check project.json
```

The check must reject with PROFILE_BUSINESS_ACCEPTANCE because the decision refers to the old subject. A checksum recalculation alone does not accept the new meaning. In this synthetic exercise, explicitly take the role of the example owner and record your decision for the revised subject:

```sh
node --input-type=module <<'JS'
import fs from 'node:fs';
import {profileEngine} from '@domainspec-v2/cli';
const file='business-semantics.json',s=JSON.parse(fs.readFileSync(file,'utf8'));
const claim=s.claim_meanings.IdentityClaim;
claim.owner_acceptance.decision_id='notice-owner-decision-v2';
claim.owner_acceptance.subject.version=claim.business_meaning.version;
claim.owner_acceptance.subject.digest=profileEngine.dataDigest(claim.business_meaning);
fs.writeFileSync(file,JSON.stringify(s,null,2)+'\n');
JS
npx --no-install alchlang profile check project.json
npx --no-install alchlang profile generate project.json --out generated-revised
npx --no-install alchlang profile verify project.json --out generated-revised
```

For real work, record the actual owner's decision, rather than interpreting this example script as approval. Changing business behavior also requires revising the proposition/Rule/Mapping/Operation and their explicit correspondence. Formal claims remain unproved.

## Author or choose a different profile

The installed node-http-api-prefix-v2 profile uses /api/ routes, a different body limit and api/index.mjs dispatcher placement through the same registered mechanisms. [Profile package authoring](PROFILE-PACKAGES.md) gives the exact recipe to create that package yourself without compiler changes. Its Request example uses /api/receiveNotice and imports generated/api/index.mjs. A selected package hash is an integrity check; each new profile needs qualification against its declared behavior.

## Open Questions

The final frozen qualification matrix and release envelope are tracked by the successor release process. For this business-only self-service profile, persistence, messaging, protected access, arbitrary business expressions, new mechanism families, cross-source application linking and ontology-carrier ingestion require separate supported extensions. The source-backed Commerce candidate covers selected effects, but its protected runtime still lacks a public credential-to-actor adapter. Local hosting, TDE, EVF and publication remain deferred.
