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
from poetry_versions_plugin.services import get_git_info, update_pyproject, update_py_file, update_readme


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


class VersionsApplicationPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        application.command_loader.register_factory("versions", VersionsCommand)

        # noinspection PyTypeChecker
        # application.event_dispatcher.add_listener(console_events.COMMAND, self.event_hander)
        # noinspection PyTypeChecker
        application.event_dispatcher.add_listener(console_events.TERMINATE, self.event_hander)

    @staticmethod
    def event_hander(
            event: ConsoleCommandEvent,
            event_name: str,
            dispatcher: EventDispatcher
    ) -> None:

        io = event.io
        # noinspection PyUnresolvedReferences
        pyproject = event.command.poetry.pyproject

        io.write_line(f'<b>{PLUGIN_NAME}</b>: event_hander {event_name} init', Verbosity.VERBOSE)

        if not isinstance(event.command, VersionCommand):
            return

        io.write_line(f'<b>{PLUGIN_NAME}</b>: event_hander {event_name} start processing', Verbosity.VERBOSE)

        # 获取 Git 信息
        info = get_git_info()

        updated = ['pyproject.toml']
        update_pyproject(info, pyproject, io)

        files = pyproject.data.get('tool', {}).get('versions', {}).get('files', {}).get('filename', {})
        for file in files:
            if file.endswith('.py'):
                update_py_file(file, info)
                io.write_line(f'<b>{PLUGIN_NAME}</b>: event_hander {event_name} update python file {file}',
                              Verbosity.VERBOSE)
                updated.append(file)
            elif file == 'README.md':
                # 更新 README.md 文件
                update_readme(file, info)
                updated.append(file)

        io.write_line(f'<b>{PLUGIN_NAME}</b>: event_hander {event_name} The new version has been updated: {info}',
                      Verbosity.VERBOSE)

        io.write_line(f"Versions updated of {', '.join(updated)}", Verbosity.NORMAL)

        io.write_line(f'<b>{PLUGIN_NAME}</b>: event_hander {event_name} finished', Verbosity.VERBOSE)
