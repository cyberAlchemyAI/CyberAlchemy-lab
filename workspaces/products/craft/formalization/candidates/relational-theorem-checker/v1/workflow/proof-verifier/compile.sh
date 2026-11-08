#!/runtime/bash
set -u
# Writable scratch exists only in the sized namespace tmpfs.
/toolchain/bin/lean -j1 -o /tmp/Submitted.olean /source/Submitted.lean > /tmp/compiler.log 2>&1
status=$?
/runtime/cat /tmp/compiler.log >&2
if [ "$status" -ne 0 ]; then exit "$status"; fi
parts=(Submitted.olean)
if [ -f /tmp/Submitted.olean.server ]; then parts+=(Submitted.olean.server); fi
if [ -f /tmp/Submitted.olean.private ]; then parts+=(Submitted.olean.private); fi
/runtime/tar -C /tmp -cf - "${parts[@]}"
