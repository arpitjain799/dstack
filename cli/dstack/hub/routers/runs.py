from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from dstack.core.job import JobStatus
from dstack.core.repo import RepoRef
from dstack.core.run import RunHead
from dstack.hub.models import RunsList
from dstack.hub.routers.cache import get_backend
from dstack.hub.routers.util import get_project
from dstack.hub.security.permissions import ProjectMember

router = APIRouter(prefix="/api/project", tags=["runs"], dependencies=[Depends(ProjectMember())])


@router.post(
    "/{project_name}/runs/create",
    response_model=str,
    response_class=PlainTextResponse,
)
async def create_run(project_name: str, repo: RepoRef) -> str:
    project = await get_project(project_name=project_name)
    backend = get_backend(project, repo)
    run_name = backend.create_run()
    return run_name


@router.post(
    "/{project_name}/runs/list",
    response_model=List[RunHead],
)
async def list_run(project_name: str, body: RunsList):
    project = await get_project(project_name=project_name)
    backend = get_backend(project, body.repo)
    run_name = backend.list_run_heads(
        run_name=body.run_name,
        include_request_heads=body.include_request_heads,
        interrupted_job_new_status=JobStatus.PENDING,
    )
    return run_name
