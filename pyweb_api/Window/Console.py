class Console:
    def __init__(self, write_to_console):
        self.write_to_console = write_to_console

    def _args_to_str(self, args_tuple) -> str:
        return " ".join([str(a) for a in args_tuple])

    def log(self, *args):
        msg = self._args_to_str(args)
        print(msg)
        self.write_to_console("log", msg)

    def error(self, *args):
        msg = self._args_to_str(args)
        print("---ERROR:", msg)
        self.write_to_console("error", msg)

    def warn(self, *args):
        msg = self._args_to_str(args)
        print("---WARN:", msg)
        self.write_to_console("warn", msg)
