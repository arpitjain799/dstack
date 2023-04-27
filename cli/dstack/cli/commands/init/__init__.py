from argparse import Namespace
from pathlib import Path
from typing import Optional

import giturlparse

from dstack.api.repos import get_local_repo_credentials
from dstack.cli.commands import BasicCommand
from dstack.cli.common import check_backend, check_config, check_git, check_init, console
from dstack.cli.config import config, get_hub_client
from dstack.core.repo import RemoteRepo
from dstack.core.userconfig import RepoUserConfig


class InitCommand(BasicCommand):
    NAME = "init"
    DESCRIPTION = "Authorize dstack to access the current Git repo"

    def __init__(self, parser):
        super(InitCommand, self).__init__(parser)

    def register(self):
        self._parser.add_argument(
            "--project",
            type=str,
            help="Hub project to execute the command",
            default=None,
        )
        self._parser.add_argument(
            "-t",
            "--token",
            metavar="OAUTH_TOKEN",
            help="An authentication token for Git",
            type=str,
            dest="gh_token",
        )
        self._parser.add_argument(
            "--git-identity",
            metavar="SSH_PRIVATE_KEY",
            help="A path to the private SSH key file for non-public repositories",
            type=str,
            dest="git_identity_file",
        )
        self._parser.add_argument(
            "--ssh-identity",
            metavar="SSH_PRIVATE_KEY",
            help="A path to the private SSH key file for SSH tunneling",
            type=str,
            dest="ssh_identity_file",
        )

    @check_config
    @check_git
    @check_backend
    @check_init
    def _command(self, args: Namespace):
        repo = RemoteRepo(local_repo_dir=Path.cwd())
        repo_credentials = get_local_repo_credentials(
            repo_data=repo.repo_data,
            identity_file=args.git_identity_file,
            oauth_token=args.gh_token,
            original_hostname=giturlparse.parse(repo.repo_url).resource,
        )
        config.save_repo_user_config(
            RepoUserConfig(
                repo_id=repo.repo_ref.repo_id,
                repo_user_id=repo.repo_ref.repo_user_id,
                ssh_key_path=get_ssh_keypair(args.ssh_identity_file),
            )
        )
        hub_client = get_hub_client(project_name=args.project)
        hub_client.save_repo_credentials(repo_credentials)
        status = (
            "[yellow]WARNING[/]"
            if config.repo_user_config.ssh_key_path is None
            else "[green]OK[/]"
        )
        console.print(f"{status}")
        if config.repo_user_config.ssh_key_path is None:
            console.print(
                f"[red]SSH is not enabled. To enable it, make sure `{args.ssh_identity_file or '~/.ssh/id_rsa'}` exists or call `dstack init --ssh-identity PATH`[/]"
            )


def get_ssh_keypair(key_path: Optional[str], default: str = "~/.ssh/id_rsa") -> Optional[str]:
    """Returns path to the private key if keypair exists"""
    key_path = Path(key_path or default).expanduser().resolve()
    pub_key = (
        key_path if key_path.suffix == ".pub" else key_path.with_suffix(key_path.suffix + ".pub")
    )
    private_key = pub_key.with_suffix("")
    if pub_key.exists() and private_key.exists():
        return str(private_key)
