#!/bin/sh
set -ex
ldconfig
exec python3 -m vllm.entrypoints.openai.api_server