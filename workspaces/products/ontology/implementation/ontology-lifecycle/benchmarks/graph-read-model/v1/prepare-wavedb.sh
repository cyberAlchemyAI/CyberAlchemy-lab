#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
expected_commit=9c87530e948e414e077fae4f86262a9439905875
wavedb_source=${WAVEDB_SOURCE:?set WAVEDB_SOURCE to an external WaveDB checkout}

actual_commit=$(git -C "$wavedb_source" rev-parse HEAD)
if [[ "$actual_commit" != "$expected_commit" ]]; then
  printf 'WaveDB commit mismatch: expected %s, got %s\n' "$expected_commit" "$actual_commit" >&2
  exit 3
fi
if [[ ! -f "$wavedb_source/LICENSE" && ! -f "$wavedb_source/LICENSE.md" ]]; then
  printf 'evaluation warning: no WaveDB root/core license file at %s; adoption remains blocked\n' "$expected_commit" >&2
fi
cmake_bin=${CMAKE_BIN:-cmake}
if ! command -v "$cmake_bin" >/dev/null 2>&1 && [[ ! -x "$cmake_bin" ]]; then
  printf 'not_evaluable: cmake is unavailable\n' >&2
  exit 5
fi

build_dir=${WAVEDB_BUILD_DIR:-"$wavedb_source/build-cav2-read-model-benchmark"}
"$cmake_bin" -S "$wavedb_source" -B "$build_dir" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTS=ON \
  -DBUILD_BENCHMARKS=OFF \
  -DBUILD_EXAMPLES=OFF
"$cmake_bin" --build "$build_dir" --parallel 2 --target test_graph test_graph_parser test_graph_schema
ctest_bin=${CTEST_BIN:-ctest}
"$ctest_bin" --test-dir "$build_dir" --output-on-failure \
  -R '^(test_graph|test_graph_parser|test_graph_schema)$'

driver_bin=${WAVEDB_DRIVER_BIN:-"$build_dir/cav2-wavedb-benchmark-driver"}
cc -O3 -DNDEBUG -I "$wavedb_source/src" \
  -I "$wavedb_source/deps/libcbor/src" \
  -I "$build_dir/deps/libcbor/src" \
  -I "$build_dir/deps/libcbor" \
  -I "$wavedb_source/deps/xxhash" \
  -I "$wavedb_source/deps/hashmap/include" \
  "$root_dir/wavedb/benchmark_driver.c" \
  "$build_dir/libwavedb.a" \
  -latomic "$build_dir/libxxhash.a" \
  "$build_dir/deps/libcbor/src/libcbor.a" \
  "$build_dir/libhashmap.a" -lcrypto -lpthread -lm \
  -o "$driver_bin"

printf 'WaveDB graph prerequisites and benchmark driver passed build: %s\n' "$driver_bin"
