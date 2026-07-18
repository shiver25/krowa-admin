#!/bin/sh

case "$-" in
    *i*)
        if [ -x /usr/bin/krowa-admin ]; then
            /usr/bin/krowa-admin --summary || true
        fi
        ;;
esac
