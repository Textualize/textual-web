import re
import unicodedata

from rich.console import RenderableType


from textual import on
from textual.app import App, ComposeResult
from textual import events
from textual.containers import Vertical, Container
from textual.renderables.bar import Bar
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Input, Button, LoadingIndicator
from textual.screen import Screen


class Form(Container):
    DEFAULT_CSS = """
    Form {
        color: $text;
        width: auto;
        height: auto;        
        background: $boost;
        
        padding: 1 2;        
    }

    Form .title {
        color: $text;
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
        width: 100%;        
    }

    Form Button {
        width: 100%;
        margin: 2 1 0 1;
    }
    LoadingIndicator {
        width: 100%;
        height: 3 !important;
        margin: 2 1 0 1;        
        display: none;
    }
    Form:disabled Button {
        display: none;
    }
    Form:disabled LoadingIndicator {
        display: block;
    }
    """


class FormField(Container):
    DEFAULT_CSS = """
    FormField {
        layout: horizontal;
        height: auto;        
        width: 80;
        margin: 1 0;
        
    }
    FormField Input {
        border: tall transparent;
    
    }
    Form:disabled FormField Label{
        opacity:0.5;
    }
    FormField:focus-within > Label {
        color: $text;
    }

    FormField > Label {
        width: 1fr;
        margin: 1 2;
        text-align: right;
        color: $text-muted;
    }

    FormField .group PasswordStrength {
        margin: 0 1 0 1;
        color: $text-muted;
    }

    FormField > Input, FormField > Select {
        width: 2fr;
    }
    
    
    FormField Vertical.group {
        height: auto;
        width: 2fr;        
    }

    FormField Vertical.group Input {
        width: 100%;        
    }

    """


class PasswordStrength(Widget):
    DEFAULT_CSS = """
    PasswordStrength {
        margin: 1;
        height: 1;
    }
    PasswordStrength > .password-strength--highlight {
        color: $error;
       
    }
    PasswordStrength > .password-strength--back {
        color: $foreground 10%;
    }

    PasswordStrength > .password-strength--success {
        color: $success;
    }
    """
    COMPONENT_CLASSES = {
        "password-strength--highlight",
        "password-strength--back",
        "password-strength--success",
    }
    password = reactive("")

    def render(self) -> RenderableType:
        if self.password:
            steps = 8
            progress = len(self.password) / steps
            if progress >= 1:
                highlight_style = self.get_component_rich_style(
                    "password-strength--success"
                )
            else:
                highlight_style = self.get_component_rich_style(
                    "password-strength--highlight"
                )
            back_style = self.get_component_rich_style("password-strength--back")
            return Bar(
                highlight_range=(0, progress * self.size.width),
                width=None,
                background_style=back_style,
                highlight_style=highlight_style,
            )
        else:
            return "Minimum 8 character, no common words"


def slugify(value: str, allow_unicode=False) -> str:
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class SignupScreen(Screen):
    def compose(self) -> ComposeResult:
        with Form():
            yield Label("Textual-web Signup", classes="title")
            with FormField():
                yield Label("Your name*")
                yield Input(id="name")
            with FormField():
                yield Label("Account slug*")
                yield Input(id="org-name", placeholder="Identifier used in URLs")
            with FormField():
                yield Label("Email*")
                yield Input(id="email")
            with FormField():
                yield Label("Password*")
                with Vertical(classes="group"):
                    yield Input(password=True, id="password")
                    yield PasswordStrength()
            with FormField():
                yield Label("Password (again)")
                yield Input(password=True, id="password-check")
            yield Button("Signup", variant="primary", id="signup")
            yield LoadingIndicator()

    @on(Button.Pressed, "#signup")
    def signup(self):
        self.disabled = True

    @on(Input.Changed, "#password")
    def input_changed(self, event: Input.Changed):
        self.query_one(PasswordStrength).password = event.input.value

    @on(events.DescendantBlur, "#password-check")
    def password_check(self, event: Input.Changed) -> None:
        password = self.query_one("#password", Input).value
        if password:
            password_check = self.query_one("#password-check", Input).value
            if password != password_check:
                self.notify("Passwords do not match", severity="error")

    @on(events.DescendantFocus, "#org-name")
    def update_org_name(self) -> None:
        org_name = self.query_one("#org-name", Input).value
        if not org_name:
            name = self.query_one("#name", Input).value
            self.query_one("#org-name", Input).insert_text_at_cursor(slugify(name))


class SignUpApp(App):
    CSS_PATH = "signup.tcss"

    def on_ready(self) -> None:
        self.push_screen(SignupScreen())


if __name__ == "__main__":
    app = SignUpApp()
    app.run()
