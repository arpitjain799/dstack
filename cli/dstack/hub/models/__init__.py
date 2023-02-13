from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from dstack.core.job import Job
from dstack.core.repo import LocalRepoData, RepoAddress


class Hub(BaseModel):
    name: str
    backend: str
    config: str


class HubInfo(BaseModel):
    name: str
    backend: str


class UserInfo(BaseModel):
    user_name: str


class AddTagRun(BaseModel):
    repo_address: RepoAddress
    tag_name: str
    run_name: str
    run_jobs: List[Job]


class AddTagPath(BaseModel):
    repo_data: LocalRepoData
    tag_name: str
    local_dirs: List[str]


class StopRunners(BaseModel):
    repo_address: RepoAddress
    job_id: str
    abort: bool


class ReposUpdate(BaseModel):
    repo_address: RepoAddress
    last_run_at: int


class RunsList(BaseModel):
    repo_address: RepoAddress
    run_name: Optional[str]
    include_request_heads: Optional[bool]


class JobsGet(BaseModel):
    repo_address: RepoAddress
    job_id: str
