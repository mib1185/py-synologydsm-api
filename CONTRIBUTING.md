# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT license](https://opensource.org/licenses/MIT) and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code](https://github.com/mib1185/py-synologydsm-api)
- [Documentation](https://github.com/mib1185/py-synologydsm-api#readme)
- [Issue Tracker](https://github.com/mib1185/py-synologydsm-api/issues)

## How to report a bug

Report bugs on the [Issue Tracker](https://github.com/mib1185/py-synologydsm-api/issues).

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to request a feature

Request features on the [Issue Tracker](https://github.com/mib1185/py-synologydsm-api/issues).

## How to set up your development environment

This project use a [Visual Studio Code Dev Container](https://code.visualstudio.com/docs/devcontainers/containers).
This approach will create a preconfigured development environment with all the tools you need.

## How to test the project

Unit tests are located in the `tests` directory, and are written using the [pytest](https://pytest.readthedocs.io/) testing framework.
Run the full test suite:

```bash
$ pytest tests
```

There is also a Visual Studio Code task available to run the full test suite.

## How to submit changes

Open a [pull request](https://github.com/mib1185/py-synologydsm-api/pulls) to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The test suite must pass without errors and warnings.
- Include unit tests. This project maintains 100% code coverage.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before commiting your change, pre-commit as a Git hook is installed within the [Visual Studio Code Dev Container](https://code.visualstudio.com/docs/devcontainers/containers).

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.
