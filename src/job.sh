#!/bin/bash

set -a
source $HOME/biological-evaluation/.env
set +a

cd $HOME/$PROJECT_PATH 
$HOME/.local/bin/uv run src/worker.py "$@"
