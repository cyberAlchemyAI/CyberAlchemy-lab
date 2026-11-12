# Shared capability and local instance

Meaning: reusable behavior and its particular application have different owners and lifecycles.

Evidence: [Craft implementation bindings](../../../../workspaces/products/craft/implementation/bindings.json) and [ontology application](../../../../workspaces/products/craft/ontology/application/README.md) connect local records/source to shared components without copying their installations.

Use: describe Project-management behavior across Product/contracts/architecture/implementation/docs, while `project/` carries the workspace's particular coordinating identity. Shared semantic definitions remain exact references.

Failure to avoid: treating a directory copy as a new Project identity or as admission of the copied capability.
