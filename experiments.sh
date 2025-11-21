#!/bin/bash

set -a
source .env
set +a

declare -a surrogate_types=("prf" "lightgbm")
declare -a acq_types=("mesmo" "usemo" "parego")
declare -a acq_optimizers=("local_random" "random_scipy" "scipy_global" "cma_es")

for surrogate_type in "${surrogate_types[@]}"; do
    for acq_type in "${acq_types[@]}"; do
        for acq_optimizer in "${acq_optimizers[@]}"; do
            filename="experiments/$surrogate_type_$acq_type_$acq_optimizer-2.env"
            cat experiments/plain.env > $filename
            echo "SURROGATE_TYPE=\"$surrogate_type\"" >> $filename
            echo "ACQ_TYPE=\"$acq_type\"" >> $filename
            echo "ACQ_OPTIMIZER_TYPE=\"$acq_optimizer\"" >> $filename
        done
    done
done

for file in experiments/*-2.env; do
    uv run src/orchestrator.py -e "$file" > $file.log 2>&1
done
