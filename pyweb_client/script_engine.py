import code
import sys
import types
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


@dataclass
class Script:
    content: str
    dependencies: List[str]


class ScriptEngineException(Exception):
    pass


class InvalidScriptException(ScriptEngineException):
    pass


class IScriptEngine(ABC):

    @abstractmethod
    def run_script(self, script: Script) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate_script(self, script: Script) -> None:
        """
        :throws: InvalidScriptException
        """
        raise NotImplementedError


class PyWebScriptEngine(IScriptEngine):

    def run_script(self, script: Script) -> None:
        pass

    def validate_script(self, script: Script) -> None:
        pass


class PyWebInterpreter:
    def __init__(self, client: 'PyWebClient'):
        self.banner = "Welcome to the PyWeb REPL"
        self.exit_message = "Thanks for using PyWeb"
        self.file_name = "PyWeb Console"
        self.client = client
        self.__init_pyweb_env()
        self.console = code.InteractiveConsole(self.env, filename=self.file_name)

    def open_console(self) -> None:
        try:
            self.console.interact(banner=self.banner, exitmsg=self.exit_message)
        except Exception as e:
            import logging
            logging.getLogger().error(msg=str(e))

    def __init_pyweb_env(self) -> None:
        # Create virtual pyweb module
        pyweb_module = types.ModuleType("pyweb")
        pyweb_module.Window = self.client.window
        pyweb_module.Document = self.client.window.document
        
        # Make it importable by scripts
        sys.modules["pyweb"] = pyweb_module

        self.env: dict = {
            "pyweb": pyweb_module,
            "console": self.client.window.console
        }
