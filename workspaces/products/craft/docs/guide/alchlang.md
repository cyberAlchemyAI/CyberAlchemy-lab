# AlchLang in Craft

The [step-by-step Craft guide](../../COMPLETE-GUIDE.md) introduces the meta types and follows one Customer Success application from source to result. This page is the follow-on AlchLang guide: a small runnable Rule, the files around Customer Success, and the command paths for different supported source families.

If you want to write the smallest possible source first, use the ReviewDesk Rule below. For more declaration forms, continue to the [syntax reference](../reference/alchlang-syntax.md) and [profiles and profile creation](alchlang-profiles.md).

## Start with one Rule

The [ReviewDesk starter](../../implementation/alchlang/examples/generic-rule/README.md) has a two-field request and one Rule. This is its complete `business.alch` source:

```alch
module ReviewDesk version 1

value-object Request:
  verified Bool
  flagged Bool

rule IsVerified:
  input request Request
  expression request.verified
```

The Rule returns `true` when `verified` is true and `false` otherwise. Changing `flagged` does not change this Rule. The example's `profile.json` selects a Node generator and exact execution limits. Its exercise runs the generated module with true, false, and malformed inputs.

**Run from this checkout.** From the Lab repository root in the configured Linux environment, build the local source once using the [implementation guide](../../implementation/README.md). Then run the built source CLI against a fresh copy of the example:

```sh
REPO="$PWD"
node workspaces/products/craft/implementation/run.mjs build
RUN=$(mktemp -d)
cp -R "$REPO/workspaces/products/craft/implementation/alchlang/examples/generic-rule/." "$RUN/"
ALCHLANG_DOMAINSPEC_PACKAGE_ROOT="$REPO/workspaces/products/craft/implementation/cli" \
  node "$REPO/workspaces/products/craft/implementation/alchlang/dist/generic-composition-cli.js" \
  generate --source "$RUN/business.alch" --profile "$RUN/profile.json" \
  --rule ReviewDesk.IsVerified --out "$RUN/generated" --accept-local-review local-rule > "$RUN/generation.json"
(cd "$RUN" && node exercise.mjs generated)
```

The exercise prints true and false outcomes and rejects a wrong input type. `$RUN` retains the copied inputs, generated module, and result for inspection. Use a new output directory for another generation. The local review label records acceptance of this captured input; it is not a real user identity or runtime permission.

For an **installed-package exercise** in a separate consumer project, use Linux x64, Node 26.8.1, and matching AlchLang and Core package archives. The [starter README](../../implementation/alchlang/examples/generic-rule/README.md) has the install, copy, generate, and exercise commands. The archives are a local candidate supplied by their owner; [the CLI overview](../../implementation/alchlang/README.md#install-a-local-candidate-and-run-it) records package identities and distribution status.

## See it in Customer Success

The [Customer Success source](../../implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) declares an account snapshot, the `HealthScore` calculation, a `SuggestedAction` policy, a protected account read, and a `ReviewRenewal` operation. This is the actual policy excerpt:

```alch
policy SuggestedAction:
  input account AccountSnapshot
  result RenewalAction
  ordered-cases:
    escalated when account.openEscalations > 0 -> Support()
    underused when account.activeSeats * 2 < account.licensedSeats -> Adoption()
    otherwise -> Renewal()
```

The cases are checked in order. An open escalation selects `SupportReview`; low adoption selects `AdoptionReview`; otherwise the policy selects `Renew`. `Support`, `Adoption`, and `Renewal` are calculations declared in the same source. The policy returns a suggested action. A separate protected operation reads the stored account, checks the review request against that account, and saves a permitted human review.

## What goes in which file?

| File | Responsibility |
| --- | --- |
| [business.alch](../../implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) | Business types, rules, calculations, policy, mappings, queries, operations, and protected entries. |
| [selected-profile.json](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/selected-profile.json) | Supported application mechanisms, including the selected Node target, SQLite transaction behavior, and Auth binding. |
| [http-profile.json](../../implementation/cli/examples/technical-profile-source/customer-success-example/contracts/http-profile.json) | Checked GET and POST routes and response mappings. |
| [example-project.json](../../implementation/cli/examples/technical-profile-source/customer-success-example/example-project.json) | A readable list of the existing source and profile arguments for this example; it is not a new compiler project syntax. |

The connected example also has [business role source](../../implementation/cli/examples/technical-profile-source/customer-success-example/business-roles.alch) and [cited-context source](../../implementation/cli/examples/technical-profile-source/customer-success-example/cited-context.alch). They select existing Entry roles and map a released answer into the review context. They do not replace the business rules in `business.alch`.

## From source to evidence

1. **Author:** Write the business meaning in the `.alch` source and choose profiles that explicitly support it.
2. **Check and generate:** Use the command family for that source and profile. The compiler rejects unsupported declarations or selections and produces candidate artifacts for supported ones.
3. **Exercise the result:** Run the generated application with its required Auth, storage, and other runtime inputs. Keep the exact test inputs and observations.
4. **Read the limit:** A successful source check establishes well-formed supported input. A generated module needs separate verification, and a local behavior test covers only its tested environment and inputs.

## Choose the command path

AlchLang has multiple implemented command paths. Their source and profile formats are not interchangeable. Select the path that matches your application before copying syntax or commands.

| Command path | Use it for | Detailed guide |
| --- | --- | --- |
| `alchlang-generic generate` | Generic `module ... version ...` business source and explicit capability profile. | [Installed generic examples](../../implementation/alchlang/docs/GENERIC-APPLICATIONS.md) and [Core generic guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md) |
| `alchlang profile check-source` / `compile-source` | A reusable technical profile written in AlchLang plus a JSON envelope. | [Technical profile source](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md) |
| `alchlang profile generate-source` | Join a compiled technical source selection to a separately checked business application. | [Protected service example](../../implementation/cli/docs/TECHNICAL-PROFILE-SOURCE.md#use-the-generated-artifact) |
| `alchlang profile check` / `plan` / `generate` / `verify` | Declarative application or service package and checked project. | [Profile generation](../../implementation/alchlang/docs/PROFILE-GENERATION.md) |
| `alchlang business ...` | A narrower finite business-authoring path with v3 technical packages and an exact review decision. | [Business authoring tutorial](../../implementation/cli/docs/BUSINESS-AUTHORING.md) |
| `alchlang check` / `build` | Existing `application-v1` and compatibility carriers. Their `domain`/`owner` grammar differs from generic `module` source. | [Compatibility language reference](../../implementation/alchlang/docs/LANGUAGE.md) |

The installed candidate archives and the working source checkout do not necessarily expose identical features. Confirm the chosen tool pair and its `--help` output before using a source-profile or application-input command. The [AlchLang CLI overview](../../implementation/alchlang/README.md) records the installed candidate and companion.

The [Craft application guide](../../COMPLETE-GUIDE.md) follows Customer Success, Contract Workbench, and the larger ReviewDesk API. The [syntax reference](../reference/alchlang-syntax.md) explains the declarations in those examples; the [profile guide](alchlang-profiles.md) starts with the ReviewDesk profile before introducing advanced profile families.
