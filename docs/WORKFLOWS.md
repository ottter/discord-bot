# Workflows

What runs in GitHub Actions, and why.

## Pylint & Test

`.github/workflows/pylint_test.yml` — every PR, on Python 3.14 to match the Dockerfile.
Pushes to main and tags run it too, through the Docker workflow.

**Pylint** scores against `.pylintrc` and fails below 9.0, so a stray warning won't
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

Pushes run the Pylint & Test workflow first and only build if it passes. PRs skip
that step because the Pylint workflow already runs on them.

PRs build without logging in, so a broken Dockerfile fails before it merges and no
credentials exist in that run. They only trigger on changes that affect the image.

No PAT to manage: it uses the `GITHUB_TOKEN` Actions issues per run, which is what the
`packages: write` permission is for. Builds also get provenance attestation, so an image
traces back to the commit that produced it.

Every build is scanned with Trivy before it's pushed. It fails on HIGH or CRITICAL CVEs
that have a fix available, and results land in the Security tab. To accept a CVE you've
checked, add its ID to a `.trivyignore`.

Pin deployments to `sha-<commit>` if you want to roll back. `latest` moves under you.

To release:

    git tag v1.2.3 && git push origin v1.2.3

## CodeQL

`.github/workflows/codeql_analysis.yml` — GitHub's security scanner. Runs Thursdays at
00:38 UTC, or by hand from the Actions tab. Results show up under the Security tab.

## Dependabot

`.github/dependabot.yml` — not a workflow, but it opens PRs like one.

Weekly checks on pip packages, Actions, and the Docker base image. Pinning `discord.py`
is right for reproducible deploys but hides new releases; this surfaces them. Pip and
Actions updates are each grouped into one PR a week. The PRs run the checks above, so
an update that breaks a cog fails before you merge it.
