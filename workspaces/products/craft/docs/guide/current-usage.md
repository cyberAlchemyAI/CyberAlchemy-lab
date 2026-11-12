# Use Craft today: application examples and source checks

Craft has working local components, but it is not yet one command that turns any idea into a finished application. Start with the behavior you want to describe, then choose the component and profile that support that behavior.

## 1. Describe the decision or behavior

Write a small expected outcome before choosing a tool. In the Customer Success example, an account with 8 active seats out of 10 and two recorded activity values gets a score of 95. With no open escalation, the authored policy suggests `Renew`. Specify who owns that policy, which account edition is being reviewed, and what result should be saved. A model can check the declared structure, but it cannot decide whether this is the right policy for a real business.

Read the [plain-language concepts](../reference/concepts.md) if Product, Rule, Operation, or evidence are unfamiliar. The [capability catalog](../../product/capabilities/README.md) records what each area proposes and its limits.

## 2. Choose a supported source path

AlchLang is the language used to author the business behavior in the Customer Success application. Its `.alch` source and the selected implementation profiles have separate jobs; [AlchLang in Craft](alchlang.md) shows the exact files and a short policy excerpt.

| Path | Use it for | Read first |
| --- | --- | --- |
| Typed model (JSON graph) | Concepts, relationships, and model checks. | [Modeling capability](../../product/capabilities/modeling/README.md) |
| AlchLang application source | Supported business declarations with separately selected generation profiles. | [AlchLang overview](../../implementation/alchlang/README.md) and [generic applications](../../implementation/alchlang/docs/GENERIC-APPLICATIONS.md) |

These paths have different source formats and commands. A profile selects an implementation route for supported meaning; it does not decide business facts or make an unsupported feature work. If the capability or profile does not cover the behavior, record the gap rather than changing the intended meaning to make a check pass.

The [Customer Success business source](../../implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) and [application selection](../../implementation/cli/examples/technical-profile-source/customer-success-example/example-project.json) show one concrete AlchLang path. The [Craft guide](../../COMPLETE-GUIDE.md) follows that application, Contract Workbench, and a simpler ReviewDesk approval API.

## 3. Build and check the local workspace

This is a **repository contributor workflow**. It builds and checks the relocated Craft source and ontology. It does not generate or run the Customer Success or ReviewDesk application. For the small application exercise, use the [ReviewDesk Rule starter](alchlang.md#start-with-one-rule) through either its checkout-local or installed-package path.

From the Lab repository root on the configured Linux environment, use the canonical Product path:

```sh
node workspaces/products/craft/implementation/run.mjs build
node workspaces/products/craft/implementation/run.mjs check
```

`build` prepares the imported local source. `check` runs the focused relocation and ontology checks described in the [implementation guide](../../implementation/README.md). For the wider set, `node workspaces/products/craft/implementation/run.mjs verify` writes a report and currently includes known failures and pending cases in the test derivation suite. Consult the [current report](../../work/outcomes/current-verification/broader-qualification.json) before interpreting its result.

## 4. Read the result at its actual scope

A valid source file means its declared form passed a check. Generated code needs its own verification. A local runtime test says something about the tested inputs and environment. None of these alone establishes live provider behavior, production readiness, or approval to deploy.

The [ontology application](../../ontology/application/README.md) can read the prepared native source model and produce local views. Named Craft consumer views still need their qualified reading adapter. Use the component's own CLI or API for a specific journey, and check its acceptance and exclusions before depending on the result.

[Back to the Craft overview](../README.md)

