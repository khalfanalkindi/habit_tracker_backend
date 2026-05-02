#!/usr/bin/env bash
# Run db/init_tables.sql against Railway (or any) MySQL — no secrets in this file.
#
# Option A — set Railway-style vars (from MySQL plugin → Variables):
#   export MYSQLHOST=... MYSQLPORT=3306 MYSQLUSER=root MYSQLPASSWORD='...' MYSQLDATABASE=railway
#   ./scripts/run_init_tables.sh
#
# Option B — password prompt (safer than putting -p on the command line):
#   export MYSQLHOST=... MYSQLPORT=... MYSQLUSER=root MYSQLDATABASE=railway
#   ./scripts/run_init_tables.sh --prompt
#
# Requires: mysql client (brew install mysql-client on macOS; add to PATH).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SQL_FILE="$ROOT/db/init_tables.sql"

prompt=0
[[ "${1:-}" == "--prompt" ]] && prompt=1

: "${MYSQLHOST:?Set MYSQLHOST}"
: "${MYSQLPORT:?Set MYSQLPORT}"
: "${MYSQLUSER:?Set MYSQLUSER}"
: "${MYSQLDATABASE:?Set MYSQLDATABASE}"

if [[ "$prompt" -eq 1 ]]; then
  exec mysql -h"$MYSQLHOST" -P"$MYSQLPORT" -u"$MYSQLUSER" -p "$MYSQLDATABASE" <"$SQL_FILE"
else
  : "${MYSQLPASSWORD:?Set MYSQLPASSWORD or use --prompt}"
  exec mysql -h"$MYSQLHOST" -P"$MYSQLPORT" -u"$MYSQLUSER" -p"$MYSQLPASSWORD" "$MYSQLDATABASE" <"$SQL_FILE"
fi
