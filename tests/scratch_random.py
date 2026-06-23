import code
from types import CodeType
import io
import sys

original_stdin = sys.stdin

sys.stdin = io.StringIO("n = 11 + 2\nprint(n)")

# Define a custom namespace (variables and functions pre-loaded for the user)
custom_env = {
    "secret_number": 42,
    "greet": lambda name: f"Hello, {name}!",
}

# Create and start the interactive console
console = code.InteractiveConsole(custom_env, filename="pyweb-console")
console.runcode(sys.stdin.read())
