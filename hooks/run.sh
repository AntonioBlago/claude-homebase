#!/bin/sh
# Launcher for Context Guard. Finds a working Python 3.8+ (python3, python, py) and runs context_guard.py with the
# hook input on stdin. If no Python is installed, it stays silent and exits 0, so a session never breaks.
case "$0" in
  */*) here=${0%/*} ;;
  *) here=${0%\\*} ;;
esac
for py in python3 python py; do
  if "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" </dev/null >/dev/null 2>&1; then
    "$py" "$here/context_guard.py" "$@"
    exit 0
  fi
done
exit 0
