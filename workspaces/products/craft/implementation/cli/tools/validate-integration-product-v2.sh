#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cli_root="$(cd "${script_dir}/.." && pwd)"
repo_root="$(git -C "${cli_root}" rev-parse --show-toplevel)"
project="projects/domainspec-v2/impl/cli"
scratch="$(mktemp -d "${cli_root}/.integration-product-v2.XXXXXX")"

cleanup() {
  case "${scratch}" in
    "${cli_root}"/.integration-product-v2.*) find "${scratch}" -depth -delete 2>/dev/null || true ;;
    *) return 70 ;;
  esac
}
trap cleanup EXIT

relative="${scratch#${cli_root}/}"
node_env="${repo_root}/toolchains/node-typescript/bin/node-env"

"${node_env}" run --project "${project}" -- node --import tsx --test \
  test/system-integration/kernel-v2.test.ts \
  test/system-integration/persistence-v2.test.ts \
  test/system-integration/messaging-v2.test.ts \
  test/system-integration/external-api-v2.test.ts \
  test/system-integration/observation-v2.test.ts \
  test/system-integration/integration-project-layout-v1.test.ts \
  test/system-integration/generation-v2.test.ts \
  test/system-integration/product-v2.test.ts \
  test/system-integration/public-api-v2.test.ts

for language in typescript python rust; do
  "${node_env}" run --project "${project}" -- node --import tsx tools/materialize-integration-generation-v2.ts "${language}" "${relative}/${language}"
done

"${node_env}" run --project "${project}" -- tsc -p "${relative}/typescript/tsconfig.json" --pretty false
python3 -m compileall -q "${scratch}/python"
CARGO_TARGET_DIR="${scratch}/cargo-target" cargo check --quiet --offline --manifest-path "${scratch}/rust/Cargo.toml"

test -f "${scratch}/typescript/.domainspec/integrations/semantic-manifest.json"
cmp "${scratch}/typescript/.domainspec/integrations/semantic-manifest.json" "${scratch}/python/.domainspec/integrations/semantic-manifest.json"
cmp "${scratch}/typescript/.domainspec/integrations/semantic-manifest.json" "${scratch}/rust/.domainspec/integrations/semantic-manifest.json"

printf '%s\n' '{"schema_version":"domainspec.integration-product-validation/v2","result":"pass","languages":["typescript","python","rust"],"temporary_outputs_disposed_on_exit":true,"authority_effect":"none"}'
