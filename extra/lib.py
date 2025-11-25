from typing import TypeAlias

import psycopg

import pyslurm

JobId: TypeAlias = int


def submit_job(
    pg_connection: psycopg.Connection,
    job_description: pyslurm.JobSubmitDescription,
) -> JobId:
    job_id = job_description.submit()

    pg_cursor: psycopg.Cursor = pg_connection.cursor()
    with pg_connection.transaction():
        pass

    return job_id
