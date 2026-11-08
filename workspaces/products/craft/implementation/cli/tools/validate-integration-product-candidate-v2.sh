#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cli_root="$(cd "${script_dir}/.." && pwd)"
repo_root="$(git -C "${cli_root}" rev-parse --show-toplevel)"
candidate="${1:-${repo_root}/projects/domainspec-v2/development/integration-reconciliation/v1/candidate/INTEGRATION-PRODUCT-CANDIDATE.v2.json}"

verify_external() {
  local expected="$1"
  local target="$2"
  test -f "${target}"
  test "$(sha256sum "${target}" | cut -d ' ' -f 1)" = "${expected}"
}

verify_external "cc93b59b68cbb016fdab6b0b4a476e69d1e0e6df99df1d94ca1c48fb7ff16c2a" "/home/vrondelli/projects/cyberAlchemy-v2/define/candidates/domainspec-integration/DOMAINSPEC-INTEGRATION-DEFINITION-PACK.v1-candidate.json"
verify_external "e18da2faa859905c28a49b70e13622f3a0c9efc330dacb31c67c839686881b0f" "/home/vrondelli/projects/cyberAlchemy-v2/goals/plans/domainspec-integration-reconciliation/PLAN.md"
verify_external "f5940fef74c69baeee445723dcdca180a3668ef7c4eb8b1d84e5fce22a345ebe" "/home/vrondelli/projects/cyberAlchemy-v2/goals/plans/domainspec-integration-reconciliation/RECONCILIATION-MATRIX.v1-candidate.json"

case "$(realpath -m "${candidate}")" in
  "${repo_root}"/*) ;;
  *) printf 'Candidate must be inside %s\n' "${repo_root}" >&2; exit 2 ;;
esac

candidate_relative="$(realpath --relative-to="${cli_root}" "${candidate}")"
"${repo_root}/toolchains/node-typescript/bin/node-env" run --project projects/domainspec-v2/impl/cli -- \
  node --import tsx tools/validate-integration-product-candidate-v2.ts "${candidate_relative}"
