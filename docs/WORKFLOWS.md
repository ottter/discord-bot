# Workflows

What runs in GitHub Actions, and why it's there.

## Pylint & Test

`.github/workflows/pylint_test.yml` — runs on every push to main and every PR.

Two checks, across Python 3.11, 3.12 and 3.13:

**Pylint** scores the code against `.pylintrc`. The job fails below `fail-under=8.0`,
so a stray warning won't block a merge but a real mess will. To run it yourself:

    python -m pylint --rcfile ./.pylintrc $(git ls-files '*.py')

**Extension check** (`scripts/check_extensions.py`) builds the bot, runs its
`setup_hook()`, and fails if any cog didn't load. Pylint only reads the code — this
actually imports every module and registers the slash commands, so it catches import
errors, bad decorators, duplicate command names, and discord.py breaking changes on an
upgrade.

It needs no token. `setup_hook()` does all the local work; `bot.start()` is the only
part that logs in, and this never calls it. That also means it can't test anything
requiring a live connection — permissions, or whether a command actually replies.

Worth knowing: `main.load_extensions` logs a failed cog and keeps going, so the bot
still starts with a broken module and just quietly drops its commands. The script
asserts that every file it expected actually loaded, rather than trusting the exit code.

    python scripts/check_extensions.py

## Docker

`.github/workflows/docker.yml` — builds the image, and publishes it when appropriate.

| Trigger | Builds | Pushes |
| --- | --- | --- |
| Pull request | yes | no |
| Push to main | yes | `latest`, `sha-<commit>` |
| Tag `v1.2.3` | yes | `1.2.3`, `1.2`, `sha-<commit>` |

Pull requests build without logging in, so a broken Dockerfile gets caught before it
merges and no credentials exist in that run. PRs only trigger it when something that
affects the image changes — the Dockerfile, requirements, or the bot source.

There's no PAT to manage. It authenticates with the `GITHUB_TOKEN` that Actions issues
per run, which is why the job asks for `packages: write`. It also attaches build
provenance, so an image can be traced back to the commit and run that produced it.

Every build gets an immutable `sha-<commit>` tag. That's the one to pin to in a
deployment if you want to be able to roll back — `latest` moves under you.

To cut a release:

    git tag v1.2.3 && git push origin v1.2.3

## CodeQL

`.github/workflows/codeql_analysis.yml` — GitHub's static analysis for security bugs.
Runs on pushes to main, on PRs, and on a schedule (Thursdays, 00:38 UTC) so newly
published vulnerability patterns get applied to code that hasn't changed.

Results land in the repo's Security tab.

## Dependabot

`.github/dependabot.yml` — not a workflow, but it opens PRs like one.

Weekly checks for pip packages, GitHub Actions, and the Docker base image. `discord.py`
is pinned exactly, which is the right call for reproducible deploys but means it goes
stale silently — this is what surfaces a new release. Those PRs run through the checks
above like any other, so an update that breaks a cog fails before you merge it.
