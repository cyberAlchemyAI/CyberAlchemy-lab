# Craft

Craft is a Lab subset whose Product, Project, Work, Authority and Ontology follow the Lab model. Current functional source and work definitions are imported; only the selected current verification reports are retained.

- [Product](product/README.md)
- [Project](project/README.md)
- [Work](work/README.md)
- [Authority](authority/README.md)
- [Ontology](ontology/README.md)
- [Architecture](architecture/README.md)
- [Implementation](implementation/README.md)
- [Documentation](docs/README.md)


Start with the [implementation guide](implementation/README.md) to build or check the relocated Craft, or read the [current work](work/CURRENT.json). Product capability proposals retain their candidate standing.

## Existing Lab entry points

The relocated implementation is selected explicitly through `node craft/implementation/run.mjs`. The existing [runtime binding](RUNTIME.json), [runtime validator](validate-runtime.mjs), [legacy implementation](impl) and [formalization](formalization) remain accessible. No global consumer switch or production activation has run.

## Open questions

Production providers and broader runtime qualification remain separate from the local journey. [Ontology source reconciliation](ontology/sources/reconciliation.json) checks the current reviewed functional source selections. Body War is a [reference application](work/experiments/body-war-reference/README.md).

## Workspace location

Canonical Product home: workspaces/products/craft/. Product coordination and Work stay here. Shared operations remain at the Lab root implementation/. Legacy locations are compatibility links, not additional copies. Native definition/admission standing is unchanged.
