#!/bin/bash

set -a
source .env
set +a

declare -a surrogate_types=("prf" "lightgbm")
# declare -a acq_types=("mesmo" "usemo" "parego" "ehvi")
declare -a acq_types=("mesmo")
# declare -a acq_optimizers=("local_random" "random_scipy" "scipy_global" "cma_es")
declare -a acq_optimizers=("local_random")

rm -f experiments/*-dist_1.env

for surrogate_type in "${surrogate_types[@]}"; do
    for acq_type in "${acq_types[@]}"; do
        for acq_optimizer in "${acq_optimizers[@]}"; do
            filename="experiments/$surrogate_type-$acq_type-$acq_optimizer-dist_1.env"
            cat experiments/.env > $filename
            echo "SURROGATE_TYPE=\"$surrogate_type\"" >> $filename
            echo "ACQ_TYPE=\"$acq_type\"" >> $filename
            echo "ACQ_OPTIMIZER_TYPE=\"$acq_optimizer\"" >> $filename
        done
    done
done

# for dotenv in experiments/*-dist_1.env; do
#     echo $dotenv
#     uv run src/orchestrator.py --env $dotenv > $dotenv.log 2>&1
# done
