from dstack.cli.commands.config import ConfigCommand
from dstack.cli.commands.cp import CpCommand
from dstack.cli.commands.hub import HubCommand
from dstack.cli.commands.init import InitCommand
from dstack.cli.commands.logs import LogCommand
from dstack.cli.commands.ls import LsCommand
from dstack.cli.commands.prune import PruneCommand
from dstack.cli.commands.ps import PSCommand
from dstack.cli.commands.rm import RMCommand
from dstack.cli.commands.run import RunCommand
from dstack.cli.commands.secrets import SecretCommand
from dstack.cli.commands.stop import StopCommand
from dstack.cli.commands.tags import TAGCommand

commands_classes = [
    ConfigCommand,
    CpCommand,
    InitCommand,
    LogCommand,
    LsCommand,
    PruneCommand,
    PSCommand,
    RMCommand,
    RunCommand,
    SecretCommand,
    StopCommand,
    TAGCommand,
    HubCommand,
]


def cli_initialize(parser):
    commands = [cls(parser=parser) for cls in commands_classes]
    for command in commands:
        command.register()
