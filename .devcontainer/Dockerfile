FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.9

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install test requirements
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && python -m pip install \
        nox \
        nox-poetry \
        pylint \
        pre-commit \
        pre-commit-hooks \
        black \
        darglint \
        flake8 \
        flake8-bandit \
        flake8-bugbear \
        flake8-docstrings \
        flake8-rst-docstrings \
        pep8-naming \
        reorder-python-imports

WORKDIR /workspaces

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
