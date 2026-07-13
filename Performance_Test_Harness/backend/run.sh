#!/bin/bash
set -e

# Java runtime used to launch the load-test engine (Amazon Corretto on EC2).
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-17-amazon-corretto.x86_64}"

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"

cd "$(dirname "$0")"

python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT"
