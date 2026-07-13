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
    fedora:44 \
    bash -euxo pipefail -c '
        dnf install -y /pkg/*.rpm

        test -x /usr/bin/krowa-admin
        test -f /etc/krowa-admin/config.yaml

        python3 -m compileall -q /usr/lib/krowa-admin \
            /usr/lib/krowa-admin/service-status.py \
            /usr/lib/krowa-admin/formatting.py

        rpm -ql krowa-admin

        output="$(/usr/bin/krowa-admin)"
        grep -q "KROWA ADMIN" <<< "$output"
    '
