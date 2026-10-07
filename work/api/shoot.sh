#!/usr/bin/env bash
# Full-page screenshots of the running app with headless Edge.  Usage: shoot.sh <out.png> "<url query>" [width] [height]
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
OUT="$1"; Q="$2"; W="${3:-1440}"; H="${4:-3600}"; PAGE="${5:-engine.html}"
"$EDGE" --headless=new --disable-gpu --hide-scrollbars --window-size="$W,$H" --virtual-time-budget=15000 \
  --screenshot="$OUT" "http://localhost:8770/$PAGE?$Q" >/dev/null 2>&1
echo "saved $OUT"
