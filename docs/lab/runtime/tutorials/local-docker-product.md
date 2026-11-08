# Run the local Docker Lab

This walkthrough runs the current **disposable fixture product** on a WSL host. It exercises a signed Source → Reader → Mapper → Context chain and a separate Work review/apply/replay journey. It does not start the developing 34-operation composite API or use protected Source8 credentials.

## Prerequisites

- Work from the CyberAlchemy-lab repository root.
- Have Python 3, Docker Engine, and Docker Compose available to your WSL user. The build needs network access to fetch its digest-pinned base image and locked wheels; the fixture containers have no network.
- Allow time for a clean image build. The [observed setup cycles](../../../../implementation/lab-runtime/local-host/t28-local-docker-setup-0001/RESULT-v2.json) took 879.772 and 812.143 seconds on this host. These are observations, not a promised duration.

Check the tools, then run the product:

```bash
python3 --version
docker compose version
docker info --format '{{.ServerVersion}}'
implementation/lab-runtime/local-host/run-local-product.sh
```

The launcher creates a unique image tag and temporary build context, verifies its pinned public inputs, builds without a layer cache, and runs two short-lived containers. It removes its image tag and build context on exit. It does not mount the checkout, create a persistent volume, expose a port, or write a Lab transaction into `authority/`.

Successful output includes both `CyberAlchemy Lab — local Source → Reader → Mapper → Context fixture: PASS` and `CyberAlchemy Lab — local Work journey: PASS`. The chain reports 15 mapped nodes, 10 edges and 25 Context references. The Work journey reports local proposal review, altered-signature refusal, committed local sequence, exact retry, fresh-process replay and disposal of its temporary key and store. The [retained local run](../../../../implementation/lab-runtime/local-host/working/t07-contained-package-20261022/RELEASE-v3.json) observed both journeys and cleanup; the [independent review](../../../../implementation/lab-runtime/local-host/working/t07-contained-independent-review-0003/REVIEW.md) checked that bounded result.

The [23 October WSL rerun](../../../../implementation/lab-runtime/local-host/working/LOCAL-PRODUCT-ACCEPTANCE-20261023-0008.md) also exited zero for both journeys. Its unique image and container names were absent after cleanup. A [live Docker inspection](../../../../implementation/lab-runtime/local-host/t18-local-docker-security-20261023/README.md) recorded the Work container's non-root, no-network and read-only isolation settings while it was running.

The same two journeys also passed from a clean extraction of the exact [T25 candidate archive](../../../../implementation/lab-runtime/local-host/t25-local-candidate-0001/README.md). To repeat that slower archive smoke with a unique owned Docker project, run `python3 -B implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/run_docker.py` from the repository root. Its [latest retained receipt](../../../../implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/RUN-DOCKER-0003.json) records exit zero and the required PASS marker for both journeys, with selected containers, volumes, networks and image absent before and after. This archive still contains only the Docker fixture, not the complete API40 installed runtime.

To run the **installed public fixture package** from a fresh private root, use the pinned installer and Docker launcher:

```bash
lab_install=$(mktemp -d "$HOME/cal-lab-install.XXXXXX")
lab_result=$(mktemp -d "$HOME/cal-lab-result.XXXXXX")
python3 -B implementation/lab-runtime/local-host/t25-runtime-installer-0004/install.py install "$lab_install"
python3 -B implementation/lab-runtime/local-host/t25-runtime-docker-runner-0002/run_installed_fixture.py 97ed982c6f7826ca861af552a26c1b245016b5cf0cea0f96d34f924835c72d21 "$lab_install" "$lab_result"
cat "$lab_result/RESULT.json"
```

The installer publishes 810 selected public files and a seven-file status guard; its cold replay precedes the Docker build. The launcher then verifies the installed fixture context, builds a unique image, runs both journeys, records each phase log under `$lab_result`, and removes its image. The [observed installed run](../../../../implementation/lab-runtime/local-host/t25-runtime-docker-runner-0002/working-docker-0002/RESULT.json) and [independent review](../../../../implementation/lab-runtime/local-host/working/t25-runtime-installer-independent-review-0001/REVIEW-0007.md) passed that exact fixture slice. The installed archive does not yet contain the full integrated API Service or portable WSL ABI closure.

## If a command refuses

- A failed `docker info` means the daemon is unavailable to this WSL user. Start the Docker integration or daemon for this host, then rerun the preflight. The product command has not started.
- `PACKAGE_REFUSED:...` comes from the source/build-input verifier. It means a selected file, file mode, epoch inventory or staged image input differs from the release pin. Inspect the named file and the [package release pin](../../../../implementation/lab-runtime/local-host/package-release.json); use a clean checkout of the intended cut rather than editing a manifest to silence the refusal.
- A Docker build error should be resolved from the build output and the pinned [Dockerfile](../../../../implementation/lab-runtime/local-host/Dockerfile) and [wheel lock](../../../../implementation/lab-runtime/local-host/requirements.lock). A failed build is not a successful runtime test.
- A fixture failure is reported by the chain or Work runner. Keep the error and selected cut for diagnosis. The launcher owns its image tag and temporary context cleanup; check `docker ps -a` before removing anything manually, so unrelated containers are preserved.

The [single implementation stream](../../../plans/0011-lab-runtime-completion/runs/0001-execution/IMPLEMENTATION-STREAM-20261022.md) and [engineering progress](../../../plans/0011-lab-runtime-completion/runs/0001-execution/ENGINEERING-PROGRESS-20261022.md) show which deeper runtime behaviors are still being built. Fixture success is a useful smoke test, not evidence that the protected Source8 run, all 34 operations, human usefulness, or canonical release has passed.
