# textual-web

Textual Web is an application to publish [Textual](https://github.com/Textualize/textual) apps and terminals on the web.

Currently in a **prototype** stage (pre-beta), but available for testing.

## Getting Started

Textual Web is a Python application. But you don't need to be a Python developer to run it.

The easiest way to install Textual Web it is via [pipx](https://pypa.github.io/pipx/).
Once you have pipx installed, run the following command:

```python
pipx install textual-web
```

You will now have the `textual-web` command on your path.

## Run a test

To see what Textual Web does, run the following at the command line:

```bash
textual-web
```

You should see something like the following:

<img width="1002" alt="Screenshot 2023-08-22 at 09 41 08" src="https://github.com/Textualize/textual-web/assets/554369/cc61edf8-0396-4dbc-b3b6-5573986143cd">

Click the blue link to launch the example Textual app (you may need to hold cmd or ctrl on some terminals).
Or copy the link to your browser if your terminal doesn't support links.

You should see something like this in your browser:

<img width="1058" alt="Screenshot 2023-08-22 at 09 41 35" src="https://github.com/Textualize/textual-web/assets/554369/654f670b-a90c-46e6-89df-ed3a7daabf4a">

You are seeing a simple Textual application.
This app is running on your machine, but is available via a public URL.
You could send that to anyone with internet access, and they would see the same thing.

Hit ctrl+C in the terminal to stop serving the welcome application.

## Serving a terminal

Textual Web can also serve your terminal. For quick access add the `-t` switch:

```bash
textual-web -t
```

This will generate another URL, which will present you with your terminal in your browser:

<img width="1058" alt="Screenshot 2023-08-22 at 09 42 23" src="https://github.com/Textualize/textual-web/assets/554369/1f3b0138-e724-4c90-a335-830717455c19">

When you server a terminal in this way it will generate a new random URL, but note that it is public so don't share it with anyone that you wouldn't trust to have access to yout machine!
