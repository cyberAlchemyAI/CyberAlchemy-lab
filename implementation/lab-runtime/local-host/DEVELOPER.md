# Develop the local Lab runtime

The [implementation stream](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/IMPLEMENTATION-STREAM-20261022.md) is the task order; the [engineering state](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/engineering-state.json) is the current local progress record. A passed fixture demonstration is a starting point, while the native 34-operation and protected-source work is still being implemented.

## Reproduce the packaged product

From the repository root, run `implementation/lab-runtime/local-host/run-local-product.sh`. The [operator walkthrough](../../../docs/lab/runtime/tutorials/local-docker-product.md) gives prerequisites, expected output and refusal diagnostics. The launcher stages only files selected by [`source-manifest.json`](source-manifest.json) and checked by [`package-release.json`](package-release.json). [`package_runtime.py`](package_runtime.py) creates the temporary context; [`verify_package.py`](verify_package.py) rechecks every image input at container startup. Do not add an undeclared host file or mount to make a local run pass: add the needed byte to a new selected package revision and test its mutation behavior.

The two fixture programs are [`chain-fixture/chain.py`](chain-fixture/chain.py) and [`../local-product/run.py`](../local-product/run.py). The first creates a disposable signed Source and maps a bounded Context. The second creates a temporary local Work store, exercises review, signed apply, retry, fresh-process replay and cleanup. Both are fixture-authority tests; they are not the native Source8 issuer or the developing composite API.

The [34-operation contract index](../../../docs/lab/runtime/reference/api/README.md) is generated from one hash-pinned public catalog. It describes declared behavior and explicitly marks current qualification pending. Its [generator and verification command](t21-doc-reference-0001/README.md) check all bound schemas and page bytes.

The current [API40 host walkthrough](../../../docs/lab/runtime/tutorials/current-local-composite.md) runs the selected Base, Action and Governance branches plus Craft/AlchLang generated behavior on this WSL checkout. Its [entrypoint](t06-api40-rebind-0001/README.md) uses an absolute host installation and is not yet a portable Docker closure. The [T25 candidate package](t25-local-candidate-0001/README.md) contains the separately runnable Docker fixture context, the exact original public-input archive, and twelve selected API40 controls. Its deterministic archive is discarded after each build; clean extraction can be verified without modifying the checkout. The [T20 candidate privacy check](t20-candidate-package-privacy-0001/README.md) scans its selected public bytes. These checks do not substitute for the remaining API40 installation and operation tests.

## Run focused checks

The package and staging tests can run without rebuilding Docker:

```bash
python3 -B -m unittest -q implementation/lab-runtime/local-host/test_package_runtime.py
python3 -O -B -m unittest -q implementation/lab-runtime/local-host/test_package_runtime.py
```

Use the individual task package README for a changed runtime component, then rerun that component's positive and causal-negative tests on its exact selected source/profile. The [progress record](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/ENGINEERING-PROGRESS-20261022.md) links currently observed checks and remaining gaps. Run the local state checker after changing a task result:

```bash
python3 -B docs/plans/0011-lab-runtime-completion/runs/0001-execution/check_engineering_state.py
```

Versioned API candidates and their source/profile manifests are independent selections. A passing check against one version does not qualify a later candidate. Keep failed receipts for diagnosis, use new successor paths when changing a frozen selection, and report exact effects and unresolved operations rather than inferring completion from catalog membership.
