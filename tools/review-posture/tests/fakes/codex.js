#!/usr/bin/env bash
# FAKE codex "js entrypoint". Deliberately a bash script, not JavaScript: the fake `node`
# beside it just runs it. Nothing here touches a network or a model.
# Mirrors the real surface this repo uses: `--version`, and
# `exec -m <id> [...] -o <out> - < <prompt>`.
set -u
[ "${1:-}" = "--version" ] && { echo "codex-cli 0.0.0-fake"; exit 0; }
exec "$FAKE_CLI_BODY" codex "$@"
