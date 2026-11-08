<!-- GENERATED FILE: edit the adjacent canonical JSON and run the carrier generator. -->

# Craft Product identity graph

- Graph: `CAL-IDENTITY-GRAPH-CRAFT-V1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Nodes

- `CA2-PRODUCT-CYBERALCHEMY` — `product`
- `CA2-PRODUCT-CRAFT` — `product`
- `CA2-PROJECT-CRAFT` — `project`
- `CAV2-D20` — `method`
- `CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION` — `goal`

## Relations

- `CAL-REL-CYBERALCHEMY-CONTAINS-CRAFT`: `CA2-PRODUCT-CYBERALCHEMY` — **contains_product** → `CA2-PRODUCT-CRAFT`
- `CAL-REL-CRAFT-COORDINATED-BY-PROJECT`: `CA2-PRODUCT-CRAFT` — **coordinated_by** → `CA2-PROJECT-CRAFT`
- `CAL-REL-CRAFT-EMBODIES-METHOD`: `CA2-PRODUCT-CRAFT` — **embodies_method** → `CAV2-D20`
- `CAL-REL-CRAFT-PROJECT-USES-METHOD`: `CA2-PROJECT-CRAFT` — **uses_method** → `CAV2-D20`
- `CAL-REL-CRAFT-PROJECT-PURSUES-FOUNDATION-GOAL`: `CA2-PROJECT-CRAFT` — **pursues_goal** → `CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION`

## Accountability

- Graph owner: `role:identity-graph-owner`
- Challenge route: `role:identity-graph-owner`

## Semantic definitions

- `cal.definition.identity-relation@1.0.0-candidate.1`
- `cal.definition.identity-carrier@1.0.0-candidate.1`
- `cal.definition.product@1.0.0-candidate.1`
- `CAV2-D60@1.0.0-candidate.1`
- `CAV2-D32@1.0.0-candidate.1`
- `CAV2-D59@1.0.0-candidate.1`

## Evidence

- `CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-DECISION`
- `CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-PROJECT`
- `CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-GOAL`
- `CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1`

## Claim ceiling

Candidate identity graph only. Endpoint resolution and relation validity do not admit endpoints or relations, transfer authority, infer a Bounded Context, prove Goal achievement, or establish implementation or runtime conformance.
