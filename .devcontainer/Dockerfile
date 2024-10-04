FROM mcr.microsoft.com/vscode/devcontainers/python:3.9-bookworm

# install test requirements
COPY requirements*.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements_dev.txt \
   && rm -rf /tmp/pip-tmp

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
