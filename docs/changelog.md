# Changelog

All notable changes to `pypresscart` are recorded here. This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] — 2026-04-18

Housekeeping release. No runtime behavior changes.

### Changed
- Project URLs in `pyproject.toml` (and therefore the **Project links** sidebar on PyPI) now point at the new owner `pypresscart/py-presscart`. 0.1.0 still shipped with the original `annjawn/py-presscart` URLs baked into its metadata; GitHub redirects preserve them, but 0.1.1 is the first release published under the canonical URLs.
- Docs site moved from `www.anjanbiswas.dev/py-presscart/` to <https://pypresscart.github.io/py-presscart/> as a side-effect of the repo transfer to the new `pypresscart` GitHub org.
- README now documents the full release procedure end-to-end and notes that `main` is protected (CI must pass, no direct pushes, force-pushes and deletions denied).

## [0.1.0] — Initial release

Initial public release.

### Added
- `PresscartClient` with composable resource services: `auth`, `outlets`, `products`, `orders`, `order_items`, `profiles`, `campaigns`, `articles`, `files`, `folders`.
- Full coverage of the Presscart API as of release date (40+ endpoints).
- Pydantic models for every request and response shape.
- Dual-mode I/O: accept and return either Pydantic models or `dict`s, controllable per-call (`as_json=`) or at the client level (`response_mode=`).
- Typed exception hierarchy with `BadRequestError`, `ValidationError`, `AuthenticationError`, `PermissionError`, `NotFoundError`, `RateLimitError`, `ServerError`, and `PresscartTransportError`.
- Automatic exponential-backoff retry on 429/5xx/network errors, honoring `Retry-After`.
- Context-manager lifecycle.
- Typed throughout (`py.typed` shipped; mypy-strict clean).

### Dependencies
- Runtime: `pydantic>=2.7,<3`, `requests>=2.31,<3`.
- Python 3.10+.

[Unreleased]: https://github.com/pypresscart/py-presscart/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.1
[0.1.0]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.0
