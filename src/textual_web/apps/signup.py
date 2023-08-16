import re
import unicodedata

import httpx
from rich.console import RenderableType


from textual import on
from textual import work
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
        layout: grid;
        grid-size: 2;
        grid-columns: auto 50;
        grid_rows: auto;  
        grid-gutter: 1;        
    }

    Form .title {
        color: $text;
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
        width: 100%;    
        column-span: 2;    
    }

    Form Button {
        width: 100%;
        margin: 1 1 0 0;
        column-span: 2;
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
        column-span: 2;
        padding-bottom: 1;
    }

    Form Label {
        width: 100%;        
        text-align: right;
        padding: 1 0 0 1;
    }

    Form .group {
        height: auto;    
        width: 100%;     
    }

    Form .group > * {
       padding: 0 1;
       color: $text-muted;
    }

    Form Input {
        border: tall transparent;
    }


    
    """


class PasswordStrength(Widget):
    DEFAULT_CSS = """
    PasswordStrength {        
        height: 1;
        padding-left: 0;
        padding-top: 0;
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
            return "Minimum 8 characters, no common words"


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


class SignupInput(Vertical):
    DEFAULT_CSS = """
    
    SignupInput {
        width: 100%;
        height: auto;
    }
    """


class ErrorLabel(Label):
    DEFAULT_CSS = """
    SignupScreen ErrorLabel {
        color: $error;
        text-align: left !important;
        padding-left: 1;
        padding-top: 0;
        display: none;
    }
    SignupScreen ErrorLabel.-show-error  {
        display: block;
    }
    """


class SignupScreen(Screen):
    def compose(self) -> ComposeResult:
        with Form():
            yield Label("Textual-web Signup", classes="title")

            yield Label("Your name*")
            with SignupInput(id="name"):
                yield Input()
                yield ErrorLabel()

            yield Label("Account slug*")
            with SignupInput(id="account_slug"):
                yield Input(placeholder="Identifier used in URLs")
                yield ErrorLabel()

            yield Label("Email*")
            with SignupInput(id="email"):
                yield Input()
                yield ErrorLabel()

            yield Label("Password*")
            with SignupInput(id="password"):
                with Vertical(classes="group"):
                    yield Input(password=True)
                    yield PasswordStrength()
                yield ErrorLabel()

            yield Label("Password (again)")
            with SignupInput(id="password_check"):
                yield Input(password=True)
                yield ErrorLabel()

            yield Button("Signup", variant="primary", id="signup")
            yield LoadingIndicator()

    @on(Button.Pressed, "#signup")
    def signup(self):
        self.disabled = True
        data = {
            input.id: input.query_one(Input).value for input in self.query(SignupInput)
        }
        self.send_signup(data)

    @work
    async def send_signup(self, data: dict[str, str]) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8080/api/signup/", data=data
                )
                result = response.json()

        except Exception as error:
            self.notify("Unable to reach server", severity="error")
            self.log(error)
            return
        finally:
            self.disabled = False

        self.notify("There are errors in the form. Please try again.")
        self.query_one(Form).add_class("-show-errors")

        for error_label in self.query(ErrorLabel):
            error_label.update("")
            error_label.remove_class("-show-error")

        for error in result:
            if error["loc"]:
                error_label = self.query_one(
                    f"#{error['loc'][0]} ErrorLabel", ErrorLabel
                )
                error_label.add_class("-show-error")
                error_label.update(error["ctx"].get("error", error["msg"]))
            else:
                self.notify(
                    error["ctx"].get("error", error["msg"]), severity="error", timeout=5
                )
        self.app.log(result)

    @on(Input.Changed, "#password Input")
    def input_changed(self, event: Input.Changed):
        self.query_one(PasswordStrength).password = event.input.value

    @on(events.DescendantBlur, "#password_check")
    def password_check(self, event: Input.Changed) -> None:
        password = self.query_one("#password", Input).value
        if password:
            password_check = self.query_one("#password-check", Input).value
            if password != password_check:
                self.notify("Passwords do not match", severity="error")

    @on(events.DescendantFocus, "#account_slug Input")
    def update_account_slug(self) -> None:
        org_name = self.query_one("#account_slug Input", Input).value
        if not org_name:
            name = self.query_one("#name Input", Input).value
            self.query_one("#account_slug Input", Input).insert_text_at_cursor(
                slugify(name)
            )


class SignUpApp(App):
    CSS_PATH = "signup.tcss"

    def on_ready(self) -> None:
        self.push_screen(SignupScreen())


if __name__ == "__main__":
    app = SignUpApp()
    app.run()
