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


docker run --rm \
    --volume "$PROJECT_ROOT/dist:/pkg:ro,Z" \
    debian:13-slim \
    bash -euxo pipefail -c '
        apt-get update
        apt-get install -y /pkg/*.deb

        test -x /usr/bin/krowa-admin
        test -f /etc/krowa-admin/config.yaml

        python3 -m compileall -q /usr/lib/krowa-admin \
            /usr/lib/krowa-admin/service-status.py \
            /usr/lib/krowa-admin/formatting.py

        dpkg -L krowa-admin

        output="$(/usr/bin/krowa-admin)"
        grep -q "KROWA ADMIN" <<< "$output"
    '
