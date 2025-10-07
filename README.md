# The Compass Community App

This is the Webapp and Discord Bot for the [Compass Community](https://thecompass.diy) Discord server.


## Note

This repository is a community project to extend the features of the Compass Community Discord server with extra features and  has nothing to do with the Compass App created by Angelo for the Compass Program.


## Features

### Accountability management

The bot can automatically (or on command) create accountability setting and check in threads.

Additionally, it can detect accountability check-ins and count points for every completed accountability.


## Permissions

The following section describes what permissions the bot needs and why.

- Message Intent (Allowed to read messages)
  - Needed for accountability tracking
- Manage Threads and Posts
  - Needed for accountability thread management

- Send Messages and Create Posts
  - Needed for accountability announcements and thread creation
<!-- - Read messages in threads
  - Needed for accountability tracking -->
- Embed Links
  - Needed for accountability commands


## Development Setup

This projects primary development system is using nix and/or direnv.

If you use direnv, allow the project once to be ready for development:

```bash
cd compass
direnv allow    # do once after cloning
```

When using VSCode or Jetbrains IDEA, you can use the respective direnv plugins for full IntelliSense support.

If you don't use direnv, you can use nix directly to enter the dev environment:

```bash
cd compass
nix develop
```

Before running, it is required to create the static configuration file. By default, this file is looked for in `data/config.json`, but this can be changed with arguments. Create such a file according to the following template and adjust all required parameters (the ones with ... are required):

```json
{
    "discord_bot_token": "...",
    "discord_guild_id": ...,
    "discord_client_id": "",
    "discord_client_secret": "",
    "discord_redirect_url": "http://localhost:3000/callback",

    "web_host": "localhost",
    "web_port": 3000,
    
    "accountability_channel_id": ...
}
```

The first time the project is set up, a virtual environment is created (in `.venv`) and the compass-app project is installed into it (editable).
This way you can simply launch the bot as such:

```bash
compass_app
```

This is equivalent to the following:

```bash
python -m compass_app.main
```

See commandline arguments using the help flag:

```bash
compass_app --help
```


## Contribution

If you are part of the Compass Community and want to help with development, feel free to contribute to the project by creating issues, PRs or discussing ideas for new features in the dedicated Compass Bot Development club (`explain-your-problem > [CLUB] Compass Bot`) on the Compass discord server.