# Github Actions

GitHub Actions utilized in this project:

- [Pylint](https://pypi.org/project/pylint/)
- [CodeQL Analysis](https://github.com/github/codeql-action)

**Pylint** - Static code analysis

    # run locally
    pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # run locally without adding pylint to PATH
    python -m pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # Or generate default pylint config file:
    pylint --generate-rcfile > ./.pylintrc

**CodeQL Analysis** - Semantic code analysis engine
