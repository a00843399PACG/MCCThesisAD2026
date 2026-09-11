#!/bin/sh
# Compiles the minimal build A1* into bin/. No external dependencies, no build tool.
set -e
cd "$(dirname "$0")"
rm -rf bin
mkdir -p bin
find src -name '*.java' -print0 | xargs -0 javac -encoding UTF-8 -d bin
echo "compiled into bin/ (main class: Run)"
