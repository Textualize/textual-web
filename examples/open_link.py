from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button


class OpenLink(App[None]):
    """Demonstrates opening a URL in the same tab or a new tab."""

    def compose(self) -> ComposeResult:
        yield Button("Visit the Textual docs", id="open-link-same-tab")
        yield Button("Visit the Textual docs in a new tab", id="open-link-new-tab")

    @on(Button.Pressed)
    def open_link(self, event: Button.Pressed) -> None:
        """Open the URL in the same tab or a new tab depending on which button was pressed."""
        self.open_url(
            "https://textual.textualize.io",
            new_tab=event.button.id == "open-link-new-tab",
        )


app = OpenLink()
if __name__ == "__main__":
    app.run()
