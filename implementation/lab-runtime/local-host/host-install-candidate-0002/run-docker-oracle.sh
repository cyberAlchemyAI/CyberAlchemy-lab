#!/bin/sh
set -eu
case "${1:-}" in
  --run) ;;
  *) echo 'NO_DOCKER_EFFECT: pass --run for disposable no-host-mount oracle' >&2; exit 3 ;;
esac
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
image='sha256:ca4f3f0cbb2dc39759b701f1306602d820a06a7ca50562561f4d9cf8f2182f8d'
exec docker run --rm -i --network none --read-only --tmpfs /tmp:rw,nosuid,nodev,mode=1777 \
  --pids-limit 32 --memory 128m --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID \
  --security-opt no-new-privileges --user 0:0 --entrypoint python3 "$image" - \
  < "$script_dir/docker_parent_oracle.py"
