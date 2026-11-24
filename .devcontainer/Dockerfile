FROM mcr.microsoft.com/vscode/devcontainers/python:3.14

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

# the uv cache and the workspace live on different filesystems, so hardlinks are not possible
ENV UV_LINK_MODE=copy

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
