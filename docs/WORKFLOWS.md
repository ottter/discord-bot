# Workflows

What runs in GitHub Actions, and why.

## Pylint & Test

`.github/workflows/pylint_test.yml` — every push to main and every PR, on Python 3.11,
3.12 and 3.13.

**Pylint** scores against `.pylintrc` and fails below 8.0, so a stray warning won't
block a merge but a real mess will:

    python -m pylint --rcfile ./.pylintrc $(git ls-files '*.py')

**Extension check** imports every cog and registers the slash commands, which pylint
can't do by reading the code. It catches import errors, bad decorators, duplicate
command names, and discord.py breaking on an upgrade:

    python scripts/check_extensions.py

No token needed — `setup_hook()` is all local, and `bot.start()` is the only part that
logs in. So it can't test anything needing a live connection, like permissions or
whether a command actually replies.

It checks what registered rather than watching for a crash, because `load_extensions`
logs a broken cog and keeps going — the bot starts fine and just quietly drops those
commands.

## Docker

`.github/workflows/docker.yml` — builds the image, publishes it when it should.

| Trigger | Builds | Pushes |
| --- | --- | --- |
| Pull request | yes | no |
| Push to main | yes | `latest`, `sha-<commit>` |
| Tag `v1.2.3` | yes | `1.2.3`, `1.2`, `sha-<commit>` |

PRs build without logging in, so a broken Dockerfile fails before it merges and no
credentials exist in that run. They only trigger on changes that affect the image.

No PAT to manage: it uses the `GITHUB_TOKEN` Actions issues per run, which is what the
`packages: write` permission is for. Builds also get provenance attestation, so an image
traces back to the commit that produced it.

Pin deployments to `sha-<commit>` if you want to roll back. `latest` moves under you.

To release:

    git tag v1.2.3 && git push origin v1.2.3

## CodeQL

`.github/workflows/codeql_analysis.yml` — GitHub's security scanner. Pushes to main,
PRs, and Thursdays at 00:38 UTC, so new vulnerability patterns reach code that hasn't
changed. Results show up under the Security tab.

## Dependabot

`.github/dependabot.yml` — not a workflow, but it opens PRs like one.

Weekly checks on pip packages, Actions, and the Docker base image. Pinning `discord.py`
is right for reproducible deploys but hides new releases; this surfaces them. The PRs
run the checks above, so an update that breaks a cog fails before you merge it.
