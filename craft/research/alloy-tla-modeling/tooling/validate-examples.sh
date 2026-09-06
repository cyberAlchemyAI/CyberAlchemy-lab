#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TOWER_ROOT="projects/domainspec-v2/research/alloy-tla-modeling"
RUN_RESULTS="$TOWER_ROOT/invoke-plan/run-results"
TLA_SPEC="$TOWER_ROOT/examples/OrderFulfillmentSaga.tla"
ALLOY_SPEC="$TOWER_ROOT/examples/OrderFulfillmentSaga.alloy"

"$SCRIPT_DIR/run-tla-check.sh" --receipt "$RUN_RESULTS/tla/order-fulfillment-sany.md" --sany "$TLA_SPEC"
"$SCRIPT_DIR/run-alloy-check.sh" --receipt "$RUN_RESULTS/alloy/order-fulfillment-commands.md" commands "$ALLOY_SPEC"
