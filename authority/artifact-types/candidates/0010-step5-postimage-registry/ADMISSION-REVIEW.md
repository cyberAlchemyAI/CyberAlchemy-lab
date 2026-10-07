<!-- GENERATED FILE: canonical data is admission-manifest.json. -->

# Complete Artifact Type model — collective admission review

- Proposed decision: `CAL-DECISION-0069-COMPLETE-ARTIFACT-TYPE-MODEL-ADMISSION`
- Artifact Types to admit: `53`
- Existing ready candidates: `17`
- Repaired candidates: `5`
- Immutable successors: `9`
- New endpoint carriers: `22`
- Predecessors transitioning to historical: `9`
- Excluded candidate records: `8`
- Authority effect before approval: `none`

## Exact admission set

### Existing Ready Candidate

| Artifact Type | Version | Artifact digest | Predecessor |
| --- | --- | --- | --- |
| `cal.artifact-type.artifact-type-request/v1` | `1.0.0-candidate.2` | `cdebf56d2b2e074cdb06b6d744f7b9a8628501910410f064cf2bcf784503cae8` | `—` |
| `cal.artifact-type.canonical-package-manifest/v1` | `1.0.0-candidate.2` | `df3d8d8180416271d3dc7659f3fefaa697b15b85fe2dcda059037c39ace3c771` | `—` |
| `cal.artifact-type.context-request/v1` | `1.0.0-candidate.2` | `170576d368329b6e2603fa2949494363e809508288a4ec42bb26fe427c8a338f` | `—` |
| `cal.artifact-type.context-view/v1` | `1.0.0-candidate.2` | `d912c6b47059f786f366230de4189d00d7a7d075adadb85393f6a46a222fb841` | `—` |
| `cal.artifact-type.context/v1` | `1.0.0-candidate.2` | `0d77654bef3c8dc96144fa210df55bc4876c82f2e52e042d98ee9dd3759ad94c` | `—` |
| `cal.artifact-type.experiment-design/v1` | `1.0.0-candidate.2` | `abc7e7d4e0e73d27be98129c4feb8fd3e5b58d26a0167bc3710f0319f95ea8be` | `—` |
| `cal.artifact-type.experiment-run/v1` | `1.0.0-candidate.2` | `f2bbfb9f9a62cd72764ce5c504eda3cc3e050da476b9ea5f06ff41529a9bac8b` | `—` |
| `cal.artifact-type.finding/v1` | `1.0.0-candidate.2` | `754ae78686ce548a1d15f53c9431818d4ede004fc21f1d4ef095d7a54b86a6d4` | `—` |
| `cal.artifact-type.identity-claim/v1` | `1.0.0-candidate.2` | `c6f51fe4adc69d646236f410986fd40a40851d86e876d350cbea8c9c46e34bc4` | `—` |
| `cal.artifact-type.observation/v1` | `1.0.0-candidate.2` | `9c52f8b4395f5532393bb76189580bf4849394cd17c1411adf45711862932d45` | `—` |
| `cal.artifact-type.ontology/v1` | `1.0.0-candidate.2` | `aab97b1389fc103d1c0b3e837474d6e85a357daae86797686b0f54a586cfb206` | `—` |
| `cal.artifact-type.person-reference/v1` | `1.0.0-candidate.2` | `aafc2b7894a675ea650fb044f9aebff126a21b545b26b247cb8dcefe928060ea` | `—` |
| `cal.artifact-type.repository-migration-manifest/v1` | `1.0.0-candidate.1` | `7be737ec03d54084cd88bbadaac09fcdc14126c42a63d2bc6c47e866bc067b65` | `—` |
| `cal.artifact-type.role-assignment/v1` | `1.0.0-candidate.2` | `6006dd6a6bdb465fabe2576bbf05da4934888bf8b6fcd74f37aed5165f748a41` | `—` |
| `cal.artifact-type.role/v1` | `1.0.0-candidate.2` | `57d530b5a56b750c4833ec156abffd56d4f1d1a3d8a80999a14fcc496533a03f` | `—` |
| `cal.artifact-type.team-membership/v1` | `1.0.0-candidate.2` | `887d560f6b98ff2bf400fdcbcbf9b8fe612926997ea30eca1f89811e29a651b4` | `—` |
| `cal.artifact-type.team/v1` | `1.0.0-candidate.2` | `545d872000d08466b02416f5cfc05b358d737370b90c4fe59f35ee9c1c6da099` | `—` |

### Repaired Candidate

| Artifact Type | Version | Artifact digest | Predecessor |
| --- | --- | --- | --- |
| `cal.artifact-type.context-profile/v1` | `1.0.0-candidate.3` | `ce4bb03b0cfa4f269d5425719f97d845da1e4899beb4bd92fddb2d8a6df9fd87` | `—` |
| `cal.artifact-type.measurement-method/v1` | `1.0.0-candidate.3` | `96a25b42ea259e7175136b25dd96be2b26208dd5e1d622f76b84827fb5cb87f1` | `—` |
| `cal.artifact-type.measurement-result/v1` | `1.0.0-candidate.3` | `cc349602cdb6cfb2d03998c4f64678392c4fb5e680399cb77ba176ed96996c26` | `—` |
| `cal.artifact-type.model-instance-binding/v1` | `1.0.0-candidate.3` | `83dc3cf80216ad16aa0862aa7aa5be980058f10bd5633064cc0a3f73ac5c18ce` | `—` |
| `cal.artifact-type.ontology-package/v1` | `1.0.0-candidate.2` | `2c8219548391e8afef50e5da32f20a45b23af36849232d796d142f67b7aa181e` | `—` |

### Immutable Successor

| Artifact Type | Version | Artifact digest | Predecessor |
| --- | --- | --- | --- |
| `cal.artifact-type.artifact-type/v3` | `3.0.0-candidate.1` | `7ae4cad15fe1669fbb81294a711095e6fb77cda28817009f23124f506b2b37eb` | `cal.artifact-type.artifact-type/v2` |
| `cal.artifact-type.bounded-context/v3` | `3.0.0-candidate.1` | `3bea2dc969e68e54bf7d6fd64af1e2a103df9a45882d35e8ec6e3dfbf459e3ee` | `cal.artifact-type.bounded-context/v2` |
| `cal.artifact-type.capability-instance/v2` | `2.0.0-candidate.1` | `8292e9c86e578a4022909aea6886de343f18051a61dfe3465f19db9cd6c1c8a5` | `cal.artifact-type.capability-instance/v1` |
| `cal.artifact-type.capability-realization-binding/v2` | `2.0.0-candidate.1` | `4f08e93d861c78fe4d39ea674260446c56ebe4e4eec79768ad318ad21e076732` | `cal.artifact-type.capability-realization-binding/v1` |
| `cal.artifact-type.context-lineage-record/v2` | `2.0.0-candidate.1` | `ee0ce42f54d2d72a8a0f73fd6475b90ccda35a2d1981cf8daf5d6376e693ce77` | `cal.artifact-type.context-lineage-record/v1` |
| `cal.artifact-type.context-map/v3` | `3.0.0-candidate.1` | `0069e71aa6e243f62835f249bea1eb3ff2c29c294ee0b7588b92cc850bbc9cbb` | `cal.artifact-type.context-map/v2` |
| `cal.artifact-type.context-migration-manifest/v2` | `2.0.0-candidate.1` | `2e8f6270b161c42cf1c583991fa2de4194b118497aadaa43d1d72b6394063460` | `cal.artifact-type.context-migration-manifest/v1` |
| `cal.artifact-type.definition/v2` | `2.0.0-candidate.1` | `f863bd4b09a28c5ca3e82e9008ddc837c1186bad9f35fe9e5cde4ea2ccfac5f7` | `cal.artifact-type.definition/v1` |
| `cal.artifact-type.ubiquitous-language/v2` | `2.0.0-candidate.1` | `d52fdc3dcc393386c5925e1f6de00756b47c9f1f3b9be95e89f29832a7895275` | `cal.artifact-type.ubiquitous-language/v1` |

### New Endpoint Carrier

| Artifact Type | Version | Artifact digest | Predecessor |
| --- | --- | --- | --- |
| `cal.artifact-type.authority-claim/v1` | `1.0.0-candidate.1` | `811021f95a04e358b1f5ebb73e9ce5cbcf29340b130eebf243bcdfc736c7255c` | `—` |
| `cal.artifact-type.constitution/v1` | `1.0.0-candidate.1` | `b08ac8f81478d3061ce080087d11ebfb35713285b51b237051da9bf60ad4f901` | `—` |
| `cal.artifact-type.contract/v1` | `1.0.0-candidate.1` | `4b0c2003d824160182a54fbf8af4e29517702ab7a984ccee08f44642daed3d80` | `—` |
| `cal.artifact-type.decision-scope/v1` | `1.0.0-candidate.1` | `d482163b5b1b68b768cf2c2e0faf748160182600310058cbb8a2025ee46d457f` | `—` |
| `cal.artifact-type.decision/v1` | `1.0.0-candidate.1` | `18a36d5ac65ca35459d125397386aff444499ad1945032bcb6721d0ace4ab92f` | `—` |
| `cal.artifact-type.effect/v1` | `1.0.0-candidate.1` | `813aa2d35a092537570e468b557e55495c86379fb83f55ddccdc95474e7e2cb0` | `—` |
| `cal.artifact-type.evaluation/v1` | `1.0.0-candidate.1` | `fa12e46e685436a5c0c860d6534780fa9e1029daadfc2199fb8f519a834f66be` | `—` |
| `cal.artifact-type.evidence-set/v1` | `1.0.0-candidate.1` | `1ab42ade4ceafa26d5bc14cffa01e89fabd0bbc678b665b5fc344074b24ba87b` | `—` |
| `cal.artifact-type.generated-output/v1` | `1.0.0-candidate.1` | `0c0ab1f806eedc754f619d079efdd4e1ce8eb7805bc2fc3fd899db7f4da6652a` | `—` |
| `cal.artifact-type.governed-model/v1` | `1.0.0-candidate.1` | `2bff00386e9b232645387edc4de6e46ab30dd62a4c37d7a846266507b2298e13` | `—` |
| `cal.artifact-type.hypothesis/v1` | `1.0.0-candidate.1` | `5c4bd9d984f1d73b42af2b877006b7abb0d02752ebacbba38ac0339c767ec21c` | `—` |
| `cal.artifact-type.implementation/v1` | `1.0.0-candidate.1` | `bc2033e5af8600085f7c19fbbd8707dde274dd9c6803adb0b14ca7f56c10d298` | `—` |
| `cal.artifact-type.ontology-node/v1` | `1.0.0-candidate.1` | `8e280634307a45177467392052619da9363c15c0fc86f2285f1633ed79ab51cf` | `—` |
| `cal.artifact-type.person/v1` | `1.0.0-candidate.1` | `20f8cea940300cb3c268fd9454b610d15e502d72c4488c05a25ad7c753b39ef4` | `—` |
| `cal.artifact-type.policy/v1` | `1.0.0-candidate.1` | `92729ed29dc913a1dafd7f1c79576577bcc76af2953d728ed64ef6f127d553d1` | `—` |
| `cal.artifact-type.relation-kind/v2` | `2.0.0-candidate.1` | `dc770c1aa54655eba289a18c8ba4e7f3bbeb0d7886b328a42667d26dcbc4eb4e` | `—` |
| `cal.artifact-type.responsibility/v1` | `1.0.0-candidate.1` | `3a3b2c0abb03c302f2f93a8ed5779f9f853ae4017ffcbeff0c25f8b1f67180d2` | `—` |
| `cal.artifact-type.review/v1` | `1.0.0-candidate.1` | `676385f67759798f51eff82e8d8123199565b7077d1a03822b7f5a87ee077d13` | `—` |
| `cal.artifact-type.schema/v1` | `1.0.0-candidate.1` | `7b6b2598a6274b572271940caa1fbdc565ac7b984c031605b2bdaaa62f166291` | `—` |
| `cal.artifact-type.source/v1` | `1.0.0-candidate.1` | `4deb1c7964a25daa683dafcdab037c5bbfc5011a32f37e30ba1314c0120995c6` | `—` |
| `cal.artifact-type.typed-relation/v2` | `2.0.0-candidate.1` | `a58d5dd90624239a51dadb859efe8c6864ce25b86ec1ee4dfd7ea936af50b66d` | `—` |
| `cal.artifact-type.work/v1` | `1.0.0-candidate.1` | `215e161bb7dbc2914bc5ae8a237a20619f017324ee1d2c77d8e8104ce3445590` | `—` |

## Excluded records

| Artifact Type | Path | Reason |
| --- | --- | --- |
| `cal.artifact-type.artifact-type-registry/v1` | `authority/artifact-types/artifact-type-registry/v1/artifact.json` | `candidate-lineage-predecessor-preserved` |
| `cal.artifact-type.artifact-type-registry/v1` | `authority/artifact-types/artifact-type-registry/v1/candidates/0002-executable-surface/artifact.json` | `obsolete-candidate-predecessor` |
| `cal.artifact-type.artifact-type-request/v1` | `authority/artifact-types/artifact-type-request/v1/artifact.json` | `candidate-lineage-predecessor-preserved` |
| `cal.artifact-type.artifact-type/v1` | `authority/artifact-types/artifact-type/v1/candidates/0002-ctx01-registration/artifact.json` | `obsolete-candidate-predecessor` |
| `cal.artifact-type.canonical-package-manifest/v1` | `authority/artifact-types/canonical-package-manifest/v1/artifact.json` | `candidate-lineage-predecessor-preserved` |
| `cal.artifact-type.definition/v1` | `authority/artifact-types/definition/v1/artifact.json` | `same-version-non-effective-duplicate` |
| `cal.artifact-type.relation-kind/v1` | `authority/artifact-types/relation-kind/v1/artifact.json` | `superseded-before-admission` |
| `cal.artifact-type.typed-relation/v1` | `authority/artifact-types/typed-relation/v1/artifact.json` | `superseded-before-admission` |

## Realistic integrated examples

### implementation-realizes-capability

Implementation/v1 carries executable realization identity; Product Capability carries promised product behavior; Capability Realization Binding/v2 records the governed association; relation.realizes remains a separate candidate Relation Kind.

### person-reference-identifies-person

Person Reference/v1 is a durable reference record; Person/v1 is the human identity endpoint; relation.asserts-identity-of remains a separately governed connection.

### typed-relation-in-ontology

Typed Relation/v2 carries one exact connection instance with explicit endpoint kinds, revisions, and closed qualifiers; Relation Kind/v2 carries the full semantic-axis contract; Ontology Node/v1 carries a node; Ontology/v1 carries the governed graph context.

## Decision boundary

- Admit only the exact artifact and schema bytes listed in entries.
- Transition only the nine exact predecessor contracts named by successor entries from admitted-current to admitted-historical.
- Create or replace one current_by_identity mapping per admitted entry.
- Preserve every excluded candidate record and every unrelated admitted contract.
- Generate and admit a new Registry/v2 postimage after the transaction; preserve prior registry snapshots.
- Do not admit an ordinary artifact instance, Relation Kind, Typed Relation, ontology assertion, consumer, implementation, or runtime.

## Claim ceiling

This review manifest binds 53 exact Artifact Type candidate postimages and nine predecessor transitions. It has authority effect none and does not admit any bytes, instance, relation, ontology assertion, consumer, implementation, or runtime.
