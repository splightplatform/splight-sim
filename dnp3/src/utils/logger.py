from datetime import datetime
import os


class Logger:
    def __init__(self, module: str = "NONE"):
        self._module = module
        self._debug = os.getenv("DEBUG") is not None

    def _print(self, level: str, *args):
        print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}|{self._module}|{level}] ", *args)

    def log(self, *args):
        self._print("LOG", *args)

    def success(self, *args):
        self._print("SUCCESS", *args)

    def error(self, *args):
        self._print("ERROR", *args)

    def debug(self, *args):
        if self._debug:
            self._print("DEBUG", *args)
