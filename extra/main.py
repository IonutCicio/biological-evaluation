import psycopg
from lib import submit_job
import pyslurm
from psycopg.rows import TupleRow

from blackbox import GREEN_BEANS

HOST = "database"
DBNAME = "openbox"
USER = "postgres"
PASSWORD = "postgres"

PG_CONNECTION_INFO = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DBNAME}"


def main() -> None:
    with psycopg.connect(PG_CONNECTION_INFO) as pg_connection:
        GREEN_BEANS.register(pg_connection)

    job_description: pyslurm.JobSubmitDescription = (
        pyslurm.JobSubmitDescription(
            name=GREEN_BEANS.name,
            cpus_per_task=1,
            script="/data/job.sh",
            script_args="",
        )
    )

    job_id: int = submit_job(job_description)


if __name__ == "__main__":
    main()
