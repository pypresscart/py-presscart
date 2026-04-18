# Installation

## Requirements

- Python **3.10** or newer
- A Presscart API token (starts with `pc_`) — see [Authentication and Scopes](authentication-and-scopes.md)

## With uv (recommended)

```bash
uv add pypresscart
```

## With pip

```bash
pip install pypresscart
```

## With Poetry

```bash
poetry add pypresscart
```

## Verify

```bash
python -c "from pypresscart import PresscartClient, __version__; print(__version__)"
```

## Runtime dependencies

`pypresscart` installs only two runtime dependencies:

| Package | Why |
|---|---|
| [`requests`](https://requests.readthedocs.io/) | HTTP transport |
| [`pydantic`](https://docs.pydantic.dev/) (v2) | Request/response models |

Everything else — testing, linting, typing — is in the `dev` dependency group and not installed by users.

## Upgrading

```bash
uv add --upgrade pypresscart
# or
pip install --upgrade pypresscart
```

Always check the [Changelog](changelog.md) before upgrading across minor versions.

## Uninstall

```bash
uv remove pypresscart
# or
pip uninstall pypresscart
```
