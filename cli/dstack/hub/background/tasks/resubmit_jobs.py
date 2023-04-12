import asyncio
from typing import List

from dstack.core.job import JobStatus
from dstack.core.repo import RepoRef
from dstack.hub.db.models import Project
from dstack.hub.repository.projects import ProjectManager
from dstack.hub.routers.cache import get_backend
from dstack.utils.common import get_milliseconds_since_epoch

RESUBMISSION_INTERVAL = 60


async def resubmit_jobs():
    projects = await ProjectManager.list()
    await asyncio.get_running_loop().run_in_executor(None, _resubmit_projects_jobs, projects)


def _resubmit_projects_jobs(projects: List[Project]):
    for project in projects:
        _resubmit_project_jobs(project)


def _resubmit_project_jobs(project: Project):
    curr_time = get_milliseconds_since_epoch()
    unbound_backend = get_backend(project, repo=None)
    for repo_head in unbound_backend.list_repo_heads():
        backend = get_backend(project, RepoRef(repo_id=repo_head.name, repo_user_id="default"))
        run_heads = backend.list_run_heads(
            run_name=None,
            include_request_heads=True,
            interrupted_job_new_status=JobStatus.PENDING,
        )
        for run_head in run_heads:
            job_heads = backend.list_job_heads(run_name=run_head.run_name)
            for job_head in job_heads:
                if (
                    job_head.status == JobStatus.PENDING
                    and curr_time - job_head.submitted_at > RESUBMISSION_INTERVAL * 1000
                ):
                    job = backend.get_job(job_head.job_id)
                    backend.resubmit_job(
                        job=job,
                        failed_to_start_job_new_status=JobStatus.PENDING,
                    )
