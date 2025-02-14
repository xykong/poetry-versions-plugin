import re

from cleo.events import console_events
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.console.application import Application
from poetry.console.commands.version import VersionCommand
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry

from poetry_versions_plugin import PLUGIN_NAME
from poetry_versions_plugin.services import get_git_info, update_pyproject, update_py_file
from poetry_versions_plugin.services import update_readme, commit_local_changes
from poetry_versions_plugin.utils import pyproject_get, wrap_write_line


class VersionsPlugin(Plugin):

    def activate(self, poetry: Poetry, io: IO):
        io.write_line(f'<b>{PLUGIN_NAME}</b>: activate init', Verbosity.VERBOSE)

        io.write_line(f'<b>{PLUGIN_NAME}</b>: activate finished', Verbosity.VERBOSE)


def write_line(message: str, verbosity: Verbosity = Verbosity.VERBOSE):
    """
    This function is a placeholder for @wrap_write_line decorator.
    It helps for pycharm or pylint to recognize the function.
    It is replaced by the actual implementation in wrap_write_line.
    """
    print(message, verbosity)


# noinspection PyUnusedLocal
class VersionsApplicationPlugin(ApplicationPlugin):
    def __init__(self):
        super().__init__()
        self.current_version = None
        self.git_info = None
        self.new_version = None

    def activate(self, application: Application):
        # noinspection PyTypeChecker
        application.event_dispatcher.add_listener(console_events.COMMAND, self.before_version_command)
        # noinspection PyTypeChecker
        application.event_dispatcher.add_listener(console_events.TERMINATE, self.after_version_command)

    def before_version_command(
            self,
            event: ConsoleCommandEvent,
            event_name: str,
            dispatcher: EventDispatcher  # noqa
    ) -> None:
        io = event.io
        io.write_line(f'<b>{PLUGIN_NAME}</b>: before_version_command {event_name} init', Verbosity.VERBOSE)

        if not isinstance(event.command, VersionCommand):
            return

        # noinspection PyUnresolvedReferences
        self.current_version = event.command.poetry.package.version.text
        self.git_info = get_git_info(version=self.current_version)

        io.write_line(f'<b>{PLUGIN_NAME}</b>: before_version_command {event_name} finished', Verbosity.VERBOSE)

    @wrap_write_line
    def after_version_command(
            self,
            event: ConsoleCommandEvent,
            event_name: str,  # noqa
            dispatcher: EventDispatcher  # noqa
    ) -> None:
        write_line('init')

        if not isinstance(event.command, VersionCommand):
            write_line('not a version command, skip')
            return

        # Check if a version argument is provided
        version_argument = event.io.input.argument("version")
        if not version_argument:
            write_line('No version bump specified, skipping updates.')
            return

        # noinspection PyUnresolvedReferences
        pyproject = event.command.poetry.pyproject
        self.new_version = str(pyproject.data["tool"]["poetry"]["version"])

        write_line('start processing')

        dry_run = event.command.option('dry-run')
        short = event.command.option('short')

        # 获取 Git 信息
        if not self.git_info:
            write_line('git information get failed')
            return

        self.git_info['version'] = self.new_version

        allow_dirty = pyproject_get(pyproject, 'tool.versions.settings.allow_dirty', False)
        updated = ['pyproject.toml']
        update_pyproject(self.git_info, pyproject, write_line, dry_run)

        files = pyproject_get(pyproject, 'tool.versions.settings.filename', [])
        for file in files:
            if file.endswith('.py'):
                update_py_file(file, self.git_info, write_line, dry_run)
                write_line(f'update python file {file}')
                updated.append(file)
            elif file == 'README.md':
                # 更新 README.md 文件
                update_readme(file, self.git_info, dry_run)
                updated.append(file)

        commit = pyproject_get(pyproject, 'tool.versions.settings.commit', False)
        commit_on_argument = pyproject_get(pyproject, 'tool.versions.settings.commit_on_argument', [])
        commit_on_branches = pyproject_get(pyproject, 'tool.versions.settings.commit_on_branches', [])

        current_branch = self.git_info['branch']
        branch_match = any(re.match(branch_pattern, current_branch) for branch_pattern in commit_on_branches)

        if commit and (version_argument in commit_on_argument or version_argument == self.new_version) and branch_match:
            commit_message = pyproject_get(pyproject, 'tool.versions.settings.commit_message',
                                           "Bump version: {current_version} → {new_version}")

            if dry_run:
                write_line('dry-run mode, skip commit to local git repository')
            else:

                if self.git_info['is_dirty'] and not allow_dirty:
                    write_line(f'git information {self.git_info}, repo is dirty, abort processing')
                    return

                commit_local_changes(pyproject.file.path.parent, commit_message.format(
                    current_version=self.current_version,
                    new_version=self.new_version
                ))

            write_line('commit to local git repository: ' + commit_message.format(
                current_version=self.current_version,
                new_version=self.new_version
            ))
        else:
            if not branch_match:
                write_line(
                    f'Current branch {current_branch} does not match commit_on_branches patterns, skipping commit.'
                )

        write_line(f'the new version has been updated: {self.git_info}')

        write_line(f"versions updated of {', '.join(updated)}", Verbosity.VERBOSE if short else Verbosity.NORMAL)

        write_line('finished')
