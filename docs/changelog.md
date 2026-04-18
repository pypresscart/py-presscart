# Changelog

All notable changes to `pypresscart` are recorded here. This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/annjawn/py-presscart/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/annjawn/py-presscart/releases/tag/v0.1.0
