#!/bin/sh
set -e
# node_modules live in a Docker volume; sync when package-lock.json changes (host bind-mount).
STAMP=/app/node_modules/.rajniti-lock-hash
if [ -f package-lock.json ]; then
    HASH=$(sha256sum package-lock.json | awk '{print $1}')
    OLD=$(cat "$STAMP" 2>/dev/null || echo "")
    if [ "$HASH" != "$OLD" ] || [ ! -d node_modules/next-auth ] || [ ! -d node_modules/next ]; then
        echo "rajniti web: installing or syncing dependencies (npm ci)…"
        npm ci
        echo "$HASH" > "$STAMP"
    fi
else
    if [ ! -d node_modules/next ]; then
        npm install
    fi
fi
exec "$@"
