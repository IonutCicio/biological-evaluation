import argparse
import datetime
import json
import os
import time

import psycopg
import pyslurm


def main() -> None:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("params")
    args = parser.parse_args()
    params: dict[str, float] = json.loads(args.params)

    # parser.add_argument('filename')           # positional argument
    # parser.add_argument('-c', '--count')      # option that takes a value
    # parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
    # print(args.filename, args.count, args.verbose)
    job_id = os.getenv("SLURM_JOB_ID")
    assert job_id
    job_id = int(job_id)

    conn = psycopg.connect(
        dbname="openbox", user="postgres", password="postgres", host="database"
    )
    postgres_cursor = conn.cursor()

    postgres_cursor.execute(
        """ 
        BEGIN TRANSACTION;
        SET CONSTRAINTS ALL DEFERRED;

        UPDATE Job
        SET start_time = %(start_time)s
        WHERE job_id = %(job_id)s;

        COMMIT;
        """,
        {
            "job_id": job_id,
            "start_time": datetime.datetime.fromtimestamp(
                pyslurm.Job.load(job_id).start_time
            ),
        },
    )

    time.sleep(1)

    postgres_cursor.execute(
        """ 
        BEGIN TRANSACTION;
        SET CONSTRAINTS ALL DEFERRED;

        UPDATE Job
        SET 
            end_time = %(end_time)s,
            result = %(result)s
        WHERE job_id = %(job_id)s;

        COMMIT;
        """,
        {
            "job_id": job_id,
            "end_time": datetime.datetime.fromtimestamp(
                pyslurm.Job.load(job_id).end_time
            )
            or datetime.datetime.now(),
            "result": sum(params.values()),
        },
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exception:
        print(exception)


# print("before simulation", flush=True)
# print("after simulation, yay", flush=True)
# cur = conn.cursor()
# cur.execute("SELECT * FROM information_schema.tables")
# records = cur.fetchall()
# for record in records:
# print(1)
# print(record, flush=True)

# try:
# except Exception as e:
#     print("ok")
#     print(e)
