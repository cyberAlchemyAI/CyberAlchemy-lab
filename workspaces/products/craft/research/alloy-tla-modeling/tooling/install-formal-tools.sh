#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/formal-tools-common.sh
source "$SCRIPT_DIR/lib/formal-tools-common.sh"

JRE_URL="https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz"
JRE_SHA256="adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75"
JRE_ARCHIVE="${FORMAL_TOOLS_HOME}/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz"
JRE_DIR="${FORMAL_TOOLS_HOME}/jre/jdk-17.0.19+10-jre"

TLA_URL="https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar"
TLA_SHA1="bee4a54f3ee3d4afc347c3240ec2d9e93b075104"

ALLOY_URL="https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar"

download_if_missing() {
  local url="$1"
  local dest="$2"
  mkdir -p "$(dirname "$(formal_abs "$dest")")"
  if [[ ! -f "$(formal_abs "$dest")" ]]; then
    curl -fL --retry 3 -o "$(formal_abs "$dest")" "$url"
  fi
}

cd "$FORMAL_PROJECT_ROOT"
mkdir -p "$FORMAL_TOOLS_HOME"/{downloads,tla,alloy,jre}

download_if_missing "$JRE_URL" "$JRE_ARCHIVE"
printf '%s  %s\n' "$JRE_SHA256" "$JRE_ARCHIVE" | sha256sum -c -
if [[ ! -d "$JRE_DIR" ]]; then
  tar -xzf "$JRE_ARCHIVE" -C "${FORMAL_TOOLS_HOME}/jre"
fi
ln -sfn "$(basename "$JRE_DIR")" "${FORMAL_TOOLS_HOME}/jre/current"

download_if_missing "$TLA_URL" "$TLA_TOOLS_JAR"
printf '%s  %s\n' "$TLA_SHA1" "$TLA_TOOLS_JAR" | sha1sum -c -

download_if_missing "$ALLOY_URL" "$ALLOY_JAR"
sha256sum "$ALLOY_JAR" > "$(dirname "$ALLOY_JAR")/alloy-6.2.0.local.sha256"

printf 'Installed formal tools under %s\n' "$FORMAL_TOOLS_HOME"
"$(formal_abs "$JAVA_BIN")" -version
