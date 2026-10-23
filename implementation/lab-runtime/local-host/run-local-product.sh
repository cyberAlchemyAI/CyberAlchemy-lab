#!/usr/bin/env bash
set -euo pipefail

# Disposable local product proof. The two fixture profiles exercise the
# Source→Reader→Mapper→Context chain and the Work journey; this is not the
# protected Source8 or original-role qualification.
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
LAB_LOCAL_IMAGE="cyberalchemy-lab-local-host:local-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
export LAB_LOCAL_IMAGE
build_context="$(mktemp -d /tmp/cal-local-product-context-XXXXXX)"
export LAB_LOCAL_BUILD_CONTEXT="$build_context"

cleanup() {
    local result=$?
    trap - EXIT
    if ! docker image rm -- "$LAB_LOCAL_IMAGE" >/dev/null; then
        if (( result == 0 )); then result=1; fi
    fi
    rm -rf -- "$build_context"
    exit "$result"
}
trap cleanup EXIT

# Stage only the pinned public source closure. No checkout mount enters either
# container, and the package verifier checks image bytes before each run.
python3 -B "$here/package_runtime.py" --context "$build_context"
python3 -B "$here/verify_package.py" --verify-context "$build_context"
# The unique tag prevents concurrent invocations from replacing each other's
# image between build and run.
docker compose -f "$build_context/compose.yaml" build --no-cache lab-fixture
docker compose -f "$build_context/compose.yaml" run --rm --no-deps --pull never chain-fixture
docker compose -f "$build_context/compose.yaml" run --rm --no-deps --pull never lab-fixture
