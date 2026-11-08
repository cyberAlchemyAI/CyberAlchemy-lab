# SWU-FMT-008 Readiness Closeout Receipt

Timestamp: 2026-06-16T21:53:00Z
Result: pass-with-residue

## Validation Commands

```bash
while IFS= read -r md; do
  bash tools/check_markdown_links.sh "$md"
done < <(find projects/domainspec-v2/research/alloy-tla-modeling -name '*.md' -type f | sort)
```

Result:

```text
all tower markdown links resolve
```

```bash
git status --short projects/domainspec-v2/research/alloy-tla-modeling .formal-tools
```

Result:

```text
?? projects/domainspec-v2/research/alloy-tla-modeling/
```

Interpretation: the tower itself is new/untracked in this parent checkout; `.formal-tools/` does not appear in scoped status and remains local-only.

## Receipt Inventory

```text
invoke-plan/run-results/alloy/order-fulfillment-commands.md
invoke-plan/run-results/alloy/order-fulfillment-exec.md
invoke-plan/run-results/alloy/order-fulfillment-output/receipt.json
invoke-plan/run-results/alloy/order-fulfillment-output/showCompleteSaga-solution-0.json
invoke-plan/run-results/alloy/order-fulfillment-summary.md
invoke-plan/run-results/fixtures/swu-fmt-007-fixture-validation.md
invoke-plan/run-results/tla/order-fulfillment-sany.md
invoke-plan/run-results/tla/order-fulfillment-summary.md
invoke-plan/run-results/tla/order-fulfillment-tlc-safety.md
invoke-plan/run-results/toolchain/ToolchainSmoke.cfg
invoke-plan/run-results/toolchain/ToolchainSmoke.tla
invoke-plan/run-results/toolchain/alloy-6.2.0.local.sha256
invoke-plan/run-results/toolchain/swu-fmt-001-smoke-clean.md
invoke-plan/run-results/toolchain/swu-fmt-001-smoke.md
invoke-plan/run-results/toolchain/swu-fmt-003-wrapper-validation.md
invoke-plan/run-results/toolchain/swu-fmt-004-policy-validation.md
invoke-plan/run-results/toolchain/toolchain-receipt.md
```

## Readiness Verdict

- Local executable surface: ready.
- Alloy bounded graph validation: pass in scope 8 after reserved-word syntax repair.
- TLA+ temporal validation: counterexample captured for `FreshnessSafety`.
- Fixture contract: ready for review.
- Canonical proof/validator readiness: not ready; requires TLA freshness repair and generator/integration decisions.
