#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
profile=${1:-smoke}

python3 "$root_dir/validate.py" --self-test
cargo test --manifest-path "$root_dir/Cargo.toml"

case "$profile" in
  smoke)
    nodes=1000
    queries=120
    repetitions=2
    ;;
  medium)
    nodes=10000
    queries=600
    repetitions=5
    ;;
  large)
    nodes=100000
    queries=600
    repetitions=5
    ;;
  *)
    printf 'unknown profile: %s\n' "$profile" >&2
    exit 2
    ;;
esac

mkdir -p "$root_dir/evidence"
output="$root_dir/evidence/${profile}.jsonl"
cargo run --release --manifest-path "$root_dir/Cargo.toml" -- \
  --nodes "$nodes" \
  --edges-per-node 4 \
  --queries "$queries" \
  --repetitions "$repetitions" \
  --seed 65 \
  --output "$output"
python3 "$root_dir/validate.py" "$output"
printf 'benchmark evidence appended to %s\n' "$output"
