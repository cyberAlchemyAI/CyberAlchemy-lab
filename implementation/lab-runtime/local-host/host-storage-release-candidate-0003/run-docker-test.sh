#!/bin/sh
set -eu
case "${1:-}" in
  --run) ;;
  *) echo 'NO_DOCKER_EFFECT: pass --run for disposable no-host-bind test' >&2; exit 3 ;;
esac
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
image='sha256:543d0cf66f0f85411e42e35adfbfb4a7171de325a3047c34b0b23674189eacfe'
tar -C "$script_dir" -cf - release.py runtime-pins.json docker_active_gate.py docker_test.py | \
  docker run --rm -i --network none --read-only --tmpfs /var/lib:rw,nosuid,nodev,mode=0755 \
    --tmpfs /usr/local/libexec:rw,nosuid,nodev,mode=0755 --pids-limit 32 --memory 128m \
    --cap-drop ALL --cap-add SETUID --cap-add SETGID --security-opt no-new-privileges \
    --user 0:0 --entrypoint sh "$image" -c \
    'set -eu; mkdir -m 0700 /usr/local/libexec/cal-host-storage-release-0003; tar --no-same-owner -xf - -C /usr/local/libexec/cal-host-storage-release-0003; chmod 0500 /usr/local/libexec/cal-host-storage-release-0003/release.py; chmod 0400 /usr/local/libexec/cal-host-storage-release-0003/runtime-pins.json; /usr/bin/python3.14 -I -B -S - < /usr/local/libexec/cal-host-storage-release-0003/docker_active_gate.py; python3 -B /usr/local/libexec/cal-host-storage-release-0003/docker_test.py'
tar -C "$script_dir" -cf - install_code.py release.py runtime-pins.json docker_install_test.py | \
  docker run --rm -i --network none --read-only --tmpfs /tmp:rw,nosuid,nodev,mode=0700 \
    --tmpfs /usr/local/libexec:rw,nosuid,nodev,mode=0755 --pids-limit 32 --memory 128m \
    --cap-drop ALL --security-opt no-new-privileges --user 0:0 --entrypoint sh "$image" -c \
    'set -eu; mkdir -m 0700 /tmp/candidate; tar --no-same-owner -xf - -C /tmp/candidate; /usr/bin/python3.14 -I -B -S /tmp/candidate/docker_install_test.py'
