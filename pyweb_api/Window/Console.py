class Console:
    def __init__(self, write_to_console):
        self.write_to_console = write_to_console

    def log(self, *args):
        print(self._args_to_str(args))
        self.write_to_console("log", self._args_to_str(args))

    def error(self, *args):
        print("---ERROR:", self._args_to_str(args))
        self.write_to_console("error", self._args_to_str(args))

    def warn(self, *args):
        print("---WARN:", self._args_to_str(args))
        self.write_to_console("warn", self._args_to_str(args))

    def _args_to_str(*args):
        return " ".join([str(a) for a in args])
