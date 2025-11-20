#!/bin/bash

set -a
source $HOME/$PROJECT_PATH/.env
set +a

cd $HOME/$PROJECT_PATH 
$HOME/.local/bin/uv run src/worker.py "$@"
