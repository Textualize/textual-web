import io
from pathlib import Path
from textual import on
from textual.app import App, ComposeResult
from textual.events import DeliveryComplete
from textual.widgets import Button, Input, Label


class ScreenshotApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Button("screenshot: no filename or mime", id="button-1")
        yield Button("screenshot: screenshot.svg / open in browser", id="button-2")
        yield Button("screenshot: screenshot.svg / download", id="button-3")
        yield Button(
            "screenshot: screenshot.svg / open in browser / plaintext mime",
            id="button-4",
        )
        yield Label("Deliver custom file:")
        yield Input(id="custom-path-input", placeholder="Path to file...")

    @on(Button.Pressed, selector="#button-1")
    def on_button_pressed(self) -> None:
        screenshot_string = self.export_screenshot()
        string_io = io.StringIO(screenshot_string)
        self.deliver_text(string_io)

    @on(Button.Pressed, selector="#button-2")
    def on_button_pressed_2(self) -> None:
        screenshot_string = self.export_screenshot()
        string_io = io.StringIO(screenshot_string)
        self.deliver_text(
            string_io, save_filename="screenshot.svg", open_method="browser"
        )

    @on(Button.Pressed, selector="#button-3")
    def on_button_pressed_3(self) -> None:
        screenshot_string = self.export_screenshot()
        string_io = io.StringIO(screenshot_string)
        self.deliver_text(
            string_io, save_filename="screenshot.svg", open_method="download"
        )

    @on(Button.Pressed, selector="#button-4")
    def on_button_pressed_4(self) -> None:
        screenshot_string = self.export_screenshot()
        string_io = io.StringIO(screenshot_string)
        self.deliver_text(
            string_io,
            save_filename="screenshot.svg",
            open_method="browser",
            mime_type="text/plain",
        )

    @on(DeliveryComplete)
    def on_delivery_complete(self, event: DeliveryComplete) -> None:
        self.notify(title="Download complete", message=event.key)

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        path = Path(event.value)
        if path.exists():
            self.deliver_binary(path)
        else:
            self.notify(
                title="Invalid path",
                message="The path does not exist.",
                severity="error",
            )


app = ScreenshotApp()
if __name__ == "__main__":
    app.run()
