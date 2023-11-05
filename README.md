# textual-web

Textual Web publishes [Textual](https://github.com/Textualize/textual) apps and terminals on the web.

Currently in a beta phase &mdash; help us test!

[Hacker News discussion](https://news.ycombinator.com/item?id=37418424)

## Getting Started

Textual Web is a Python application, but you don't need to be a Python developer to run it.

The easiest way to install Textual Web is via [pipx](https://pypa.github.io/pipx/).
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

<img width="1002" alt="Screenshot 2023-09-06 at 10 11 07" src="https://github.com/Textualize/textual-web/assets/554369/b8c6b043-57c8-4781-addf-165696f3d404">


Click the blue links to launch the example Textual apps (you may need to hold cmd or ctrl on some terminals).
Or copy the link to your browser if your terminal doesn't support links.

You should see something like this in your browser:

<img width="1058" alt="Screenshot 2023-08-22 at 09 41 35" src="https://github.com/Textualize/textual-web/assets/554369/93f70177-7b3c-4840-8265-4d8ec96c5ebc">

<img width="1188" alt="Screenshot 2023-09-06 at 10 10 01" src="https://github.com/Textualize/textual-web/assets/554369/eaed134a-5fcc-40f6-8252-55cf93c84d60">

These Textual apps are running on your machine, but have public URLs.
You could send the URLs to anyone with internet access, and they would see the same thing.

Hit ctrl+C in the terminal to stop serving the welcome application.

## Serving a terminal

Textual Web can also serve your terminal. For quick access add the `-t` switch:

```bash
textual-web -t
```

This will generate another URL, which will present you with your terminal in your browser:


<img width="1058" alt="Screenshot 2023-08-22 at 09 42 23" src="https://github.com/Textualize/textual-web/assets/554369/99b10778-2183-4cce-9154-052a80cf6c34">


When you serve a terminal in this way it will generate a random public URL.

> [!WARNING]
> Don't share this with anyone you wouldn't trust to have access to your machine.


## Configuration

Textual Web can serve multiple [Textual](https://github.com/Textualize/textual) apps and terminals (as many as you like).

To demonstrate this, [install Textual](https://textual.textualize.io/getting_started/) and clone the repository.
Navigate to the `textual/examples` directory and add the following TOML file:

```toml
[app.Calculator]
command = "python calculator.py"

[app.Dictionary]
command = "python dictionary.py"
```

The name is unimportant, but let's say you called it "serve.toml".
Use the `--config` switch to load the new configuration:

```bash
textual-web --config serve.toml
```

You should now get 3 links, one for each of the sections in the configuration:


<img width="1145" alt="Screenshot 2023-08-22 at 10 37 59" src="https://github.com/Textualize/textual-web/assets/554369/81b966de-e95a-4672-83b9-b95c2029b942">


Click any of the links to serve the respective app:


<img width="1131" alt="Screenshot 2023-08-22 at 10 42 25" src="https://github.com/Textualize/textual-web/assets/554369/d25f3061-bc98-48b9-b4d0-1bab61d401b1">

### Slugs

Textual Web will derive the slug (text in the URL) from the name of the app.
You can also set it explicitly with the slug parameter.

```toml
[app.Calculator]
command = "python calculator.py"
slug = "calc"
```

### Terminal configuration

> [!NOTE]
> Terminals currently work on macOS and Linux only. Windows support is planned for a future update.

You can also add terminals to the configuration file, in a similar way.

```toml
[terminal.Terminal]
```

This will launch a terminal with your current shell.
You can also add a `command` value to run a command other than your shell.
For instance, let's say we want to serve the `htop` command.
We could add the following to the configuration:

```toml
[terminal.HTOP]
command = "htop"
```

## Accounts

In previous examples, the URLs  all contained a random string of digits which will change from run to run.
If you want to create a permanent URL you will need to create an account.

To create an account, run the following command:


```bash
textual-web --signup
```

This will bring up a dialog in your terminal that looks something like this:


<img width="1145" alt="Screenshot 2023-08-22 at 09 43 03" src="https://github.com/Textualize/textual-web/assets/554369/9601eee1-7733-4e8a-a401-78402cfd1cca">


If you fill in that dialog, it will create an account for you and generate a file called "ganglion.toml".
At the top of that file you will see a section like the following:

```toml
[account]
api_key = "JSKK234LLNWEDSSD"
```

You can add that to your configuration file, or edit "ganglion.toml" with your apps / terminals.
Run it as you did previously:

```bash
textual-web --config ganglion.toml
```

Now the URLs generated by `textual-web` will contain your account slug in the first part of the path.
The account slug won't change, so you will get the same URLs from one run to the next.

## Debugging

For a little more visibility on what is going on "under the hood", set the `DEBUG` environment variable:

```
DEBUG=1 textual-web --config ganglion.toml
```

Note this may generate a lot of output, and it may even slow your apps down.

## Known problems

You may encounter a glitch with apps that have a lot of colors.
This is a bug in an upstream library, which we are expecting a fix for soon.

The experience on mobile may vary.
On iPhone Textual apps are quite usable, but other systems may have a few issues.
We should be able to improve the mobile exprience in future updates.

## What's next?

The goal of this project is to turn Textual apps into fully featured web applications.

Currently serving Textual apps and terminals appears very similar.
In fact, if you serve a terminal and then launch a Textual app, it will work just fine in the browser.
Under the hood, however, Textual apps are served using a custom protocol.
This protocol will be used to expose web application features to the Textual app.

For example, a Textual app might generate a file (say a CSV with a server report).
If you run that in the terminal, the file would be saved in your working directory.
But in a Textual app it would be served and saved in your Downloads folder, like a regular web app.

In the future, other web APIs can be exposed to Textual apps in a similar way.

Also planned for the near future is *sessions*.
Currently, if you close the browser tab it will also close the Textual app.
In the future you will be able to close a tab and later resume where you left off.
This will also allow us to upgrade servers without kicking anyone off.

## Help us test

Currently testing is being coordinated via our [Discord server](https://discord.com/invite/Enf6Z3qhVr).
Join us if you would like to participate.
