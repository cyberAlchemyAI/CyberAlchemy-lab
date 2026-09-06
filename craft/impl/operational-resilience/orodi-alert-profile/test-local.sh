#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
profile_dir="$repo_root/projects/domainspec-v2/impl/operational-resilience/orodi-alert-profile"
domainspec_dir="$repo_root/projects/domainspec-v2/development/operational-resilience-observability-deployment-integration/operator-interface/alert-profile/domainspec"
node_bin="/home/vrondelli/.nvm/versions/node/v22.13.0/bin/node"
tsx_cli="$repo_root/projects/domainspec-v2/impl/node_modules/tsx/dist/cli.mjs"
export TMPDIR=/tmp

"$node_bin" "$tsx_cli" "$profile_dir/test.ts"
"$node_bin" "$tsx_cli" "$profile_dir/cli.ts" render
"$node_bin" "$tsx_cli" "$profile_dir/cli.ts" check
"$node_bin" "$tsx_cli" "$domainspec_dir/scripts/build.ts" --emit-json >/tmp/orodi-alert-profile-build.json
python3 -B "$repo_root/projects/domainspec-v2/development/operational-resilience-observability-deployment-integration/operator-interface/alert-profile/scripts/validate.py"

mode="${1:---profile-only}"
if [[ "$mode" == "--profile-only" ]]; then
  exit 0
fi
if [[ "$mode" != "--operator-test" ]]; then
  echo "usage: $0 [--profile-only|--operator-test]" >&2
  exit 2
fi
exec "$repo_root/projects/domainspec-v2/impl/operational-resilience/body-war-canary-local-test.sh" --operator-test
