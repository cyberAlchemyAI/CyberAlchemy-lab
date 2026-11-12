# Use Define to prepare a meaning for review

Define helps a Work describe a term, its boundaries, and the evidence behind it. It produces a candidate package. The Lab's owner review decides whether that meaning becomes authoritative.

## 1. Open the current CLI

From the repository root:

```bash
CLI=./workspaces/products/define/define
"$CLI" doctor
"$CLI" --help
```

`doctor` checks the selected implementation and its local context. The [Define workspace](../../../workspaces/products/define/README.md) explains the current implementation and its limits.

## 2. See the shape of a request

```bash
"$CLI" example --output /tmp/define-example
```

This creates a request and source evidence for a User Journey Definition. It does not choose a Project or Work for you. To use the request in an actual session, select your Project and Work context, then use `import-request` with those explicit inputs. Run `"$CLI" --help` for the required arguments.

## 3. Prepare and inspect a candidate

After a session has enough source evidence, `request` writes its current request and `prepare` creates a candidate package. Use `inspect --package DIRECTORY` to examine that exact package. `confirm` records an observation bound to the inspected package and request; it does not grant owner approval.

The [AlchLang implementation guide](../../../workspaces/products/define/implementation/cli/alchlang/README.md) describes the current command and verification surface. The [semantic preparation guide](../../../workspaces/products/define/implementation/cli/alchlang/preparation/README.md) explains questions, discovery, field contributions, revision and handoff.

## 4. Hand the meaning to Lab review

A candidate package is one input to a Lab Definition. Follow [Prepare a definition for review](prepare-definition.md) to align its formal meaning, plain explanation, domain context, boundaries, source evidence and owner.


## 5. Place the Definition in its owning workspace

Define materializes a portable package. Shared Lab placement gives that output its workspace home. Create a placement request:

    {
      "package": "/absolute/path/to/verified/define-package",
      "workspace": "product/craft"
    }

Run the shared candidate-placement workflow first with --dry-run, then without it to write the files:

    node implementation/lab-workflows/definition-catalog/cli.mjs --file placement.json --dry-run
    node implementation/lab-workflows/definition-catalog/cli.mjs --file placement.json

The checked path is authority/definitions/<readable-definition-name>/<version>/ inside that workspace, for example workspaces/products/craft/authority/definitions/craft-method/1.0.0-candidate.2/. It contains definition.json, generated DEFINITION.md, field-lineage.json and evidence.json. Shared definitions use the same layout at the Lab root. Stable IDs stay inside records; names lead the folder and human index.

Known definitions use the selected maintenance-home mapping. The workflow materializes through Define again, checks the actual selected workspace and original meaning, and refuses altered owners, unsafe paths or conflicting existing versions. It does not admit the candidate, publish a canonical registry successor or activate a runtime. See [shared placement](../../../implementation/lab-workflows/definition-catalog/README.md).
