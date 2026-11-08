# Semantic refusal codes

These finite codes preserve the exact original rejection meanings without including a body value, schema excerpt, locator or chained exception. `SEMANTIC_DEPENDENCY_REFUSED` covers bounded reader/body-parser refusals; `SEMANTIC_UNEXPECTED_REFUSAL` covers all other ordinary exceptions. Process interrupts are not intercepted. This is ordinary rendered-error containment, not isolation from Python exception-object introspection.

| Code | Meaning |
|---|---|
| `SEMANTIC_F071A4957C89` | ELIGIBILITY_FULL_BINDING |
| `SEMANTIC_1D47E39B98BE` | JSON pointer required |
| `SEMANTIC_28E8FB3044E6` | POLICY_FULL_BINDING |
| `SEMANTIC_CE58DB7F62A6` | SEMANTIC_CLOSED_FIELDS |
| `SEMANTIC_AA97C81D15F3` | SEMANTIC_SCHEMA_ORIGIN |
| `SEMANTIC_F99D2922CE3B` | SEMANTIC_SELECTION_TYPE |
| `SEMANTIC_75FFF1B92CE5` | SEMANTIC_SELECTOR_UNRESOLVED |
| `SEMANTIC_0C63A8A8F3C4` | SEMANTIC_STATES |
| `SEMANTIC_232341430741` | Typed Relation contract omitted |
| `SEMANTIC_3382342FBEF1` | actual original schema refused |
| `SEMANTIC_1E2DEBD2D896` | actual protected reader/independent graph anchor required |
| `SEMANTIC_D52F39E117FA` | actual qualifier contract refused |
| `SEMANTIC_4053CD4B5F06` | actual semantic dependency cycle |
| `SEMANTIC_0D0C8BDD5BC9` | captured fragment/type/schema binding differs |
| `SEMANTIC_1EF43F7B0C46` | carrier discriminator differs |
| `SEMANTIC_A512037DE979` | carrier is not exact original current lookup |
| `SEMANTIC_3965BF28015E` | closed context selection required |
| `SEMANTIC_A4EA647ECCEA` | current-context reference omitted |
| `SEMANTIC_2B3A7B252184` | declared identity absent |
| `SEMANTIC_6EB9C3B518B5` | declared nested/reference/items slot omitted or added |
| `SEMANTIC_D8A6777C7E53` | declared reference location/disposition differs |
| `SEMANTIC_28FD381DE58C` | declared wildcard on scalar |
| `SEMANTIC_4DCF1A17C768` | descriptor discriminator differs |
| `SEMANTIC_988C0B197084` | descriptor instance schema digest differs |
| `SEMANTIC_A7CB2F009822` | descriptor kind differs |
| `SEMANTIC_179480CF84B6` | duplicate carrier profile |
| `SEMANTIC_B1DEDC2A0A78` | duplicate reference disposition |
| `SEMANTIC_F224E155853E` | duplicate relation contract |
| `SEMANTIC_7AA02B159FC9` | duplicate schema document path |
| `SEMANTIC_EF7FD7F7E726` | duplicate semantic identity |
| `SEMANTIC_72B95D958BB0` | eligibility contains omitted/additional subjects |
| `SEMANTIC_BF5F349959A8` | eligibility source/profile/cut differs |
| `SEMANTIC_CB77ECEC2AC3` | eligible version omitted |
| `SEMANTIC_44DAA609B1D1` | embedded declaration contract differs |
| `SEMANTIC_A3A5DCB22666` | exact captured declaration required |
| `SEMANTIC_E2DB1C3AD720` | exact current Relation Kind proof differs |
| `SEMANTIC_C8B433ACD8A3` | exact descriptor role/pair differs |
| `SEMANTIC_E4C76D07BC33` | exact native subject body/carrier/version/kind provenance differs |
| `SEMANTIC_21F53133DD48` | exact original declaration fragment omitted/substituted/duplicated |
| `SEMANTIC_109ABE5011EA` | exact proof reference omitted |
| `SEMANTIC_7563CDDC5C64` | external schema retrieval forbidden |
| `SEMANTIC_D90520981D8A` | graph source/profile/cut differs |
| `SEMANTIC_4C39BFB25462` | graph version/effect differs |
| `SEMANTIC_4C37FE4031BD` | historical/withdrawn carrier not eligible |
| `SEMANTIC_6111E30653EE` | independent eligibility pin differs |
| `SEMANTIC_16A8C94A490A` | independent graph anchor mutated |
| `SEMANTIC_B623CC50487F` | independent graph policy pin differs |
| `SEMANTIC_479D22BD4174` | invalid schema node |
| `SEMANTIC_9587B0C2FDE6` | native category/carrier semantic kind mismatch |
| `SEMANTIC_705844C34112` | native registered fragment/category differs |
| `SEMANTIC_7A7DD313128E` | native registered version identity differs |
| `SEMANTIC_DB2E81B7DDE5` | native supported identity absent |
| `SEMANTIC_6BB3E4E5D6CE` | native version must qualify exact identity |
| `SEMANTIC_563570281209` | non-object relation_refs requires explicit original carrier contract |
| `SEMANTIC_F051108927D0` | original Relation Kind omitted |
| `SEMANTIC_6D9F97FC8F63` | original closed role lists required |
| `SEMANTIC_F5A5BDB05199` | original declaration body provenance differs |
| `SEMANTIC_EBFACFC3659B` | original declaration proof omitted |
| `SEMANTIC_4A7B59205105` | original declaration schema selector differs |
| `SEMANTIC_50E2D7B76F28` | original descriptor digest differs |
| `SEMANTIC_ACA8075B9F5F` | original global endpoint pair differs |
| `SEMANTIC_FD20A17E079A` | original kernel identity origin required |
| `SEMANTIC_4FC94845EA00` | original native identity fallback semantics differ |
| `SEMANTIC_C860ECE00B56` | original native identity function semantics differ |
| `SEMANTIC_89D14DE71BB1` | original native registered-fragment/identity operation source differs |
| `SEMANTIC_91191692FEE4` | original qualifier reference omitted/added |
| `SEMANTIC_456223C7058A` | original schema bytes differ |
| `SEMANTIC_21F7BF92BB2C` | pattern reference coverage requires explicit original key selector |
| `SEMANTIC_27F9215EBABE` | proof duplicate/kind spoof |
| `SEMANTIC_09242D9522E0` | qualifier original selector/disposition differs |
| `SEMANTIC_A80E90C8A6D6` | recursive reference coverage requires explicit bounded contract |
| `SEMANTIC_44DDF5233871` | reference path incompatible with validated instance |
| `SEMANTIC_5A311BAB6980` | reference scalar required |
| `SEMANTIC_4C8C0943D8C5` | registry selector is not exact admitted contract |
| `SEMANTIC_CAFE88924C04` | schema dependency outside closed documents |
| `SEMANTIC_8052BFB14FB9` | schema path escape |
| `SEMANTIC_0EE6341DC86A` | self identity differs |
| `SEMANTIC_687AB8328A4A` | semantic dependency omitted |
| `SEMANTIC_AE9ED3EB0F87` | semantic edges duplicated/omitted/substituted |
| `SEMANTIC_BA10063ADABF` | semantic node disconnected from selected roots |
| `SEMANTIC_C145E01967B6` | semantic node omitted/kind spoofed |
| `SEMANTIC_1C86C050B85E` | semantic relation endpoint absent/kind differs |
| `SEMANTIC_C4294C0040E1` | subject is not selected eligible-current version |
| `SEMANTIC_021891B9B460` | typed endpoint current version/kind differs |
| `SEMANTIC_53CAD01618DC` | typed endpoint omitted |
| `SEMANTIC_5BCBFAD9834A` | typed endpoint pair differs |
| `SEMANTIC_923CCCB1E9A9` | unique selected graph roots required |
| `SEMANTIC_A640F767BB8E` | unknown native category |
| `SEMANTIC_D1BB8ABD9A54` | unselected carrier type |
| `SEMANTIC_4E90BA2E96E6` | unselected native instance fragment |
| `SEMANTIC_BE2DB8663E65` | unselected original schema |
