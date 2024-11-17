from cleo.events import console_events
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.console.application import Application
from poetry.console.commands.command import Command
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


class VersionsCommand(Command):
    name = "versions"

    def handle(self) -> int:
        self.line("My command")
        self.io.write_line(str(self.poetry.package.version))

        # pretty_json = json.dumps(self.poetry.pyproject.data, indent=4, ensure_ascii=False)
        # self.io.write_line(pretty_json)

        self.io.write_line(str(self.poetry.pyproject.data))

        self.io.write_line(str(self.poetry.pyproject.data["tool"]["versions"]))

        return 0


def write_line(message: str, verbosity: Verbosity = Verbosity.VERBOSE):
    print(message, verbosity)


class VersionsApplicationPlugin(ApplicationPlugin):
    def __init__(self):
        super().__init__()
        self.current_version = None
        self.new_version = None

    def activate(self, application: Application):
        application.command_loader.register_factory("versions", VersionsCommand)

        # noinspection PyTypeChecker
        application.event_dispatcher.add_listener(console_events.COMMAND, self.before_version_command)
        # noinspection PyTypeChecker
        application.event_dispatcher.add_listener(console_events.TERMINATE, self.after_version_command)

    def before_version_command(
            self,
            event: ConsoleCommandEvent,
            event_name: str,
            dispatcher: EventDispatcher
    ) -> None:
        io = event.io
        io.write_line(f'<b>{PLUGIN_NAME}</b>: before_version_command {event_name} init', Verbosity.VERBOSE)

        if not isinstance(event.command, VersionCommand):
            return

        # noinspection PyUnresolvedReferences
        self.current_version = event.command.poetry.package.version.text

        io.write_line(f'<b>{PLUGIN_NAME}</b>: before_version_command {event_name} finished', Verbosity.VERBOSE)

    @wrap_write_line
    def after_version_command(
            self,
            event: ConsoleCommandEvent,
            event_name: str,
            dispatcher: EventDispatcher
    ) -> None:
        write_line('init')

        if not isinstance(event.command, VersionCommand):
            return

        # noinspection PyUnresolvedReferences
        pyproject = event.command.poetry.pyproject

        # noinspection PyUnresolvedReferences
        self.new_version = str(pyproject.data["tool"]["poetry"]["version"])

        write_line('start processing')

        # 获取 Git 信息
        info = get_git_info(version=self.new_version)
        if not info:
            write_line('Git information get failed')
            return

        allow_dirty = pyproject_get(pyproject, 'tool.versions.settings.allow_dirty', False)
        if info['is_dirty'] and not allow_dirty:
            write_line(f'Git information is dirty, abort processing')
            return

        updated = ['pyproject.toml']
        update_pyproject(info, pyproject, event.io)

        files = pyproject_get(pyproject, 'tool.versions.settings.filename', [])
        for file in files:
            if file.endswith('.py'):
                update_py_file(file, info)
                write_line(f'update python file {file}')
                updated.append(file)
            elif file == 'README.md':
                # 更新 README.md 文件
                update_readme(file, info)
                updated.append(file)

        commit = pyproject_get(pyproject, 'tool.versions.settings.commit', False)
        commit_on = pyproject_get(pyproject, 'tool.versions.settings.commit_on', [])
        argument = event.command.argument("version")
        if commit and argument in commit_on:
            commit_message = pyproject_get(pyproject, 'tool.versions.settings.commit_message',
                                           "Bump version: {current_version} → {new_version}")

            commit_local_changes(pyproject.file.parent, commit_message.format(
                current_version=self.current_version,
                new_version=self.new_version
            ))

            write_line('commit to local git repoistory: ' + commit_message.format(
                current_version=self.current_version,
                new_version=self.new_version
            ))

        write_line(f'The new version has been updated: {info}')

        write_line(f"Versions updated of {', '.join(updated)}", Verbosity.NORMAL)

        write_line('finished')
