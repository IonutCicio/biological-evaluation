#!/bin/bash

set -a
source $HOME/biological-evaluation/.env
set +a

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin
export LD_LIBRARY_PATH=$HOME/.local/lib:

cd $HOME/$PROJECT_PATH 
$HOME/.local/bin/uv run src/optimizer.py "$@"

# TODO: script to submit jobs with sbatch, instead of doing it manually each time
