<!-- Generated from fixtures/valid/source.json. Do not edit. -->

# Owner-selected source fixture

- Source: `cal.source.ontology-as-product-demo`
- Package target: `cal.ontology-package.ontology-as-product-demo`
- Domain: `ontology-as-product-demonstration`
- Owner: `role:ontology-product-owner`
- Authority effect: `none`

## Selected meaning

- `demo.product` — A Product whose typed-meaning capability produces governed ontology packages.
- `demo.product-ontology` — A descriptive ontology scaffold representing Product meaning.
- `demo.output` — The minimum durable source-bound Product output.

## Relations

- `demo.product-ontology-represents-product`: `demo.product-ontology` --`represents`→ `demo.product`
- `demo.product-produces-output`: `demo.product` --`produces-through-capability`→ `demo.output`
