#!/bin/bash

set -a
source .env
set +a

docker exec -it biological-evaluation-mongo-1 mongoexport \
    -u $MONGO_INITDB_ROOT_USERNAME \
    -p $MONGO_INITDB_ROOT_PASSWORD \
    --authenticationDatabase "admin" \
    --collection runhistory --db=$MONGO_INITDB_DATABASE \
    --type="json" \
    --jsonArray \
    --quiet > data.json
