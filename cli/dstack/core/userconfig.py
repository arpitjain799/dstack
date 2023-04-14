from typing import Optional

from pydantic import BaseModel

from dstack.core.repo import RepoRef


class RepoUserConfig(BaseModel):
    repo_id: str
    repo_user_id: str = "default"
    ssh_key_path: Optional[str] = None

    @property
    def repo_ref(self) -> RepoRef:
        return RepoRef(repo_id=self.repo_id, repo_user_id=self.repo_user_id)
