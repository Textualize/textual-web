from textual.app import App, ComposeResult
from textual.widgets import Pretty

import os


class TerminalEnv(App):
    def compose(self) -> ComposeResult:
        yield Pretty(dict(os.environ))


if __name__ == "__main__":
    TerminalEnv().run()
