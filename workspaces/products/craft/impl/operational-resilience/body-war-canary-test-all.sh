#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../.." && pwd)"
node_bin="/home/vrondelli/.nvm/versions/node/v22.13.0/bin/node"
tsc="$repo_root/projects/domainspec-v2/impl/node_modules/typescript/bin/tsc"
loader="$repo_root/projects/domainspec-v2/impl/node_modules/tsx/dist/loader.mjs"

"$node_bin" "$tsc" --project "$script_dir/tsconfig.json" --noEmit
"$node_bin" --import "$loader" --test \
  "$script_dir/test/body-war-runtime-snapshot.test.ts" \
  "$script_dir/test/body-war-runtime-projection.test.ts" \
  "$script_dir/test/body-war-canary-gateway-state.test.ts" \
  "$script_dir/test/body-war-canary-gateway-router.test.ts" \
  "$script_dir/test/body-war-canary-gateway-metrics.test.ts" \
  "$script_dir/test/body-war-canary-gateway-server.test.ts"

python3 "$script_dir/body-war-canary-validate-contracts.py"
for pattern in \
  test_body_war_canary_workload.py \
  test_body_war_canary_evaluator.py \
  test_body_war_canary_recovery.py \
  test_body_war_canary_rollback.py \
  test_body_war_canary_observer.py \
  test_body_war_canary_evidence.py \
  test_body_war_canary_tabletop.py
do
  (cd "$script_dir" && python3 -m unittest discover -s test -p "$pattern")
done
python3 "$script_dir/body-war-canary-validate-static.py"

printf 'BODY_WAR_CANARY_NO_EFFECT_SUITE=pass\n'
printf 'DOCKER_EXECUTED=false\nNETWORK_ACCESSED=false\nAUTHORITY_EFFECT=none\n'
