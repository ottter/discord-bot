# Modules

All of these are loaded in by the `load_extensions()` function in `~/main.py`

## Admin

| COMMAND       | ACTION                            | SUBCOMMAND(S)             | EXAMPLES         |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|------------------|
| unload        | Unloads/disables selected extension group. <br />It is based off of the class that individual commands are in and not the command itself.<br /> I.e.  `unload` is a member of the `admin` extension. To unload this command, you need to do `.unload admin` (not recommended)                                                                 | * <br /> {module}         | .unload *        |
| reload        | Same as unload, but it attempts to restart the extension after unloading.     | * <br /> {module}         | .reload people   |
| load          | Attempts to load a disabled extension.                                        | * <br /> {module}         | .load xkcd       |
| change_prefix | Changes the default prefix the bot will use in respective server.             | {single symbol character} | .change_prefix ? |
| admin         | DMs the verified admin this list of admin commands                            | n/a                       | .admin           |
| shutdown      | Shuts down the bot. Will have to be manually restarted through hosting method | n/a                       | .shutdown        |

## Help

## People

## xkcd

## custom-command
