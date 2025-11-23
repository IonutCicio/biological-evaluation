#!/bin/bash

# Build reactome.sif image to run container
build_reactome_sif=false 

# Run on HPC cluster with slurm + singularity
# Requires reactome.sif image to be built (./reactome.sh -b)
run_reactome_sif_with_slurm_interactive=false 

# Run reactome container locally with Docker
run_reactome_locally_with_docker=false 

# Run a query using cypher-shell within a running container
exec_cypher_query=false

# Run query with a srun job and save results (requires cypher file)
submit_job=false

# Run query with a sbatch job and save results (requries cypher file)
submit_batch_job=false

# File containing the cypher query (requires cypher file)
cypher_filename=''

# File in which to store a job logs (requires logs file)
logs_filename=''

# File in which to store the results of a query (requires out file)
stdout_filename=''

# Job id to wait before launching the next batch job
jobid_to_wait_for=''

while getopts bc:dj:l:o:q:sw: option; do
    case $option in
        b) build_reactome_sif=true;;
        s) run_reactome_sif_with_slurm_interactive=true;;
        d) run_reactome_locally_with_docker=true;;

        c) exec_cypher_query=true; cypher_filename="$OPTARG";;
        j) submit_job=true; cypher_filename="$OPTARG";;
        q) submit_batch_job=true; cypher_filename="$OPTARG";;
        w) jobid_to_wait_for="$OPTARG";;

        l) logs_filename="$OPTARG";;
        o) stdout_filename="$OPTARG";;
    esac
done

if $build_reactome_sif; then
    singularity build --sandbox reactome.sif docker://public.ecr.aws/reactome/graphdb:latest
fi

if $run_reactome_sif_with_slurm_interactive; then
    srun --pty singularity shell --writable reactome.sif 
fi

if $run_reactome_locally_with_docker; then
    docker run -p 7474:7474 -p 7687:7687 -e NEO4J_dbms_memory_heap_maxSize=1g public.ecr.aws/reactome/graphdb:latest
fi


exec_query() {
    cypher-shell --debug -u neo4j -p neo4j --format verbose "$1"
}

exec_query_file() {
    cypher-shell --debug -u neo4j -p neo4j --format verbose --file $1 
}

if $exec_cypher_query; then 
    basename="$(basename $cypher_filename '.cypher')"

    if [ -z "$logs_filename" ]; then 
        logs_filename="./logs/$basename.log"
    fi

    {
        time {
            touch /var/lib/neo4j/logs/neo4j.log
            cp ./neo4j.conf /var/lib/neo4j/conf/neo4j.conf

            neo4j start
            neo4j status

            iteration=1
            while ! (echo > /dev/tcp/localhost/7687) 2>/dev/null; do 
                sleep 1; 
                echo "[$(printf "%3d" $iteration)]"
                iteration=$((iteration + 1))
            done
        }
    } 2> $logs_filename 

    { 
        if [ -z "$stdout_filename" ]; then 
            stdout_filename="./logs/$basename.out"
        fi

        time exec_query_file $cypher_filename > $stdout_filename 
    } 2>> $logs_filename 
fi

if $submit_job; then
    args=( "-c $cypher_filename" )
    
    if [ -n "$stdout_filename" ]; then 
        args+=( "-o $stdout_filename" ) 
    fi

    if [ -n "$logs_filename" ]; then 
        args+=( "-l $logs_filename" ) 
    fi

    basename="$(basename $cypher_filename '.cypher')"
    srun -J "reactome_$basename" --partition multicore --mem 131072 singularity run --writable reactome.sif ./reactome.sh "${args[@]}"
fi

if $submit_batch_job; then
    args=( "-c $cypher_filename" )
    
    if [ -n "$stdout_filename" ]; then 
        args+=( "-o $stdout_filename" ) 
    fi

    if [ -n "$logs_filename" ]; then 
        args+=( "-l $logs_filename" ) 
    fi

    echo $cypher_filename
    basename="$(basename $cypher_filename '.cypher')"
    echo "#!/bin/bash" > temp.job
    echo "singularity run --writable reactome.sif ./reactome.sh ${args[@]}" >> temp.job
    chmod +x temp.job

    sbatch_args=()
    if [ -n "$jobid_to_wait_for" ]; then
        sbatch_args+=( "-w $jobid_to_wait_for" )
    fi

    sbatch -J "reactome_$basename" --partition multicore --mem 196608 temp.job "${sbatch_args[@]}"
fi
