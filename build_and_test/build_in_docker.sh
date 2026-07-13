#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
    pwd
)"

PROJECT_ROOT="$(
    cd -- "$SCRIPT_DIR/.."
    pwd
)"

DIST_DIR="$PROJECT_ROOT/dist"
VERSION="${VERSION:-0.2.0}"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

for packager in deb rpm; do
    docker run --rm \
        --env VERSION="$VERSION" \
        --volume "$PROJECT_ROOT:/work:Z" \
        --workdir /work \
        goreleaser/nfpm:v2.47.0 \
        package \
        --config /work/nfpm.yaml \
        --packager "$packager" \
        --target /work/dist
done
