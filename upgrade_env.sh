#!/bin/bash

if [ $# -eq 1 ]; then
    uv lock --upgrade-package "$1"
else
    uv lock --upgrade
fi
uv sync --all-extras --dev