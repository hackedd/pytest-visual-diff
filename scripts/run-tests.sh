#!/usr/bin/env bash
set -e
[[ -n "$HEADLESS" ]] && headless="--headless"
pytest tests/ --driver ${DRIVER:-Chrome} $headless
