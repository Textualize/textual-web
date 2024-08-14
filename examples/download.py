import io
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button


class ScreenshotApp(App[None]):
    BINDINGS = [Binding("s", "deliver_screenshot", "Screenshot")]

    def compose(self) -> ComposeResult:
        yield Button("Hello, World!")

    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        self.action_deliver_screenshot()

    def action_deliver_screenshot(self) -> None:
        screenshot_string = self.export_screenshot()
        string_io = io.StringIO(screenshot_string)
        self.deliver_text(string_io)


app = ScreenshotApp()
if __name__ == "__main__":
    app.run()
