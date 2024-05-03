#!/usr/bin/env bash
set -ex
./build.sh
source .venv/bin/activate
exec python src/main.py $@