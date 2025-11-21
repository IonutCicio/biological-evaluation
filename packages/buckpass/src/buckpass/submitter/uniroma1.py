import os
import subprocess

from typing_extensions import override

from buckpass.core import OpenBoxTaskId, SlurmJobId
from buckpass.core.submitter import Submitter


class Uniroma1Submitter(Submitter[OpenBoxTaskId, SlurmJobId]):
    @override
    def submit(self, args: OpenBoxTaskId) -> SlurmJobId:
        job_name = "_".join(
            reversed(args.replace("-t ", "").replace("-e ", "").split())
        )

        completed_process = subprocess.run(
            [
                "/usr/bin/ssh",
                "-i",
                "~/.ssh/Uniroma1Cluster",
                f"{os.getenv('CLUSTER_USER')}@{os.getenv('FRONTEND_HOST')}",
                f'""ssh submitter \\\\"sbatch -J {job_name} /home/{os.getenv("CLUSTER_USER")}/{os.getenv("PROJECT_PATH")}/src/job.sh {args}\\\\" ""',
            ],
            check=False,
            capture_output=True,
        )

        stdout: str = completed_process.stdout.decode()
        stderr: str = completed_process.stderr.decode()
        print(stdout, stderr, sep="\n")

        # `sbatch` prints "Submitted batch job 781422" to stdout
        return "".join(filter(str.isnumeric, stdout))
