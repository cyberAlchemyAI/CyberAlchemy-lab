[Documentation home](../../README.md)

# Product

<a id="def-cal-definition-product"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Product

The continuing offering that promises value to participants. Particular projects and implementations serve it while retaining their own identities.

**When it applies**

When identifying the enduring promise of value around which capabilities and work are organized.

**Record formats**

[Product identity · v2](type-cal-artifact-type-product-identity-v2.md#type-cal-artifact-type-product-identity-v2)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The customer-data platform promises continuing value through export capabilities.

**Common mistake**

Identifying the temporary repair Project as the Product.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Product is the enduring thing that promises value. Projects organize work around it, and methods help build it, but neither is the Product itself.

## Exact governing statement

A Product is a durable identity-bearing boundary for a coherent purpose and promise of value. It may be coordinated by Projects, embody Methods, contain Product Features and Capabilities, and have many realizations, but none of those relations merges their identities or transfers their authority.

````
Product(p) = (identity, purpose, value_promise, lineage, owner_route); related(p,x) does not imply p = x.
````

- A shared name, owner, path, or relation does not collapse Product with another identity.
- Product placement does not create a Bounded Context.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.product@1.0.0-candidate.1

**Content fingerprint · SHA-256**

19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:product-definition",
  "applicability": "A durable identity that owns a coherent promise of value, purpose, and product meaning across the projects and realizations used to develop it.",
  "exclusions": [
    "A Project that coordinates work.",
    "A Method used to build systems.",
    "A Product Feature, Product Capability, repository, package, directory, Bounded Context, or implementation."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
