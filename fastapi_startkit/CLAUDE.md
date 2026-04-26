# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important

**Do not modify framework code unless explicitly necessary.** This is a foundational framework used by downstream applications. Changes to core abstractions (Container, Application, Model, Provider, Facades) can have broad breaking effects.

## Commands

```bash
# Install dependencies
uv sync

# Build
uv build

# Run all tests
uv run pytest src/fastapi_startkit/tests/ -v

# Run a single test file
uv run pytest src/fastapi_startkit/tests/configurations/test_config_merge.py -v

# Run a single test function
uv run pytest src/fastapi_startkit/tests/configurations/test_config_merge.py::TestConfiguration::test_merge_with_dict -v
```

Tests run with `asyncio_mode = "auto"` (configured in `pyproject.toml`), so all tests are async-capable by default.

## Architecture

This is a **FastAPI application framework** providing IoC, configuration, ORM, logging, and CLI tooling. It wraps FastAPI and adds a Laravel/Masonite-inspired structure.

### Application Lifecycle

1. `Application(base_path)` initializes the service container and singleton
2. `.load_environment()` loads `.env` + `.env.{APP_ENV}` (auto-detects `.env.testing` under pytest)
3. `.configure_paths()` sets config/storage paths
4. `.register_providers()` → `.load_providers()` (two-phase boot)
5. `app.fastapi` is lazy-loaded; HTTP routes delegate to the FastAPI instance

### Service Container (`container/container.py`)

Central IoC container. Core API:
- `bind(key, value)` — register a binding
- `make(key)` — resolve a binding
- `resolve(obj)` — auto-wire a callable by inspecting its type-hinted parameters

Hooks (`on_bind`, `on_make`, `on_resolve`) allow intercepting container operations. `collect('Auth*')` returns all bindings matching a wildcard.

### Configuration (`configuration/`)

#### 1. Defining config with dataclasses

The recommended approach is to define config as a dataclass, with each field sourced from an environment variable via `env()`:

```python
from dataclasses import dataclass, field
from fastapi_startkit.environment import env

@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: env('REDIS_HOST'))
    port: int = field(default_factory=lambda: env('REDIS_PORT'))
    db: int   = field(default_factory=lambda: env('REDIS_DB'))
    options: dict = field(default_factory=lambda: {
        'decode_responses': True
    })
```

`env()` reads from the currently loaded environment, so calling `RedisConfig()` before and after `app.load_environment()` will produce different values.

#### 2. Accessing config anywhere

Because each field is a `default_factory`, instantiating the dataclass at any point will reflect the current environment:

```python
RedisConfig().host     # reads REDIS_HOST from the active .env
RedisConfig().port     # reads REDIS_PORT
RedisConfig().options  # static default dict
```

No injection or container lookup is required for simple access.

#### 3. Environment-specific `.env` loading

`app.load_environment()` applies a two-step merge:

1. Loads `.env` as the base.
2. If an environment is set (e.g. `production`), loads `.env.production` on top, overriding matching keys.

```
.env              ← always loaded first (base/defaults)
.env.testing      ← loaded when APP_ENV=testing (or under pytest)
.env.production   ← loaded when APP_ENV=production
```

Set the environment in code before loading:

```python
app.set_environment('testing')
app.load_environment()
```

Example — `.env` has `REDIS_HOST=host.default`; `.env.testing` has `REDIS_HOST=host.testing`. After `load_environment()`, `RedisConfig().host` returns `host.testing`.

#### 4. Setting the environment via the CLI (`artisan`)

Prefer passing `--env` on the command line over hardcoding it:

```bash
uv run artisan --env=production   # loads .env + .env.production
uv run artisan --env=testing      # loads .env + .env.testing
uv run artisan                    # loads .env only
```

The `artisan` entry point at the project root bootstraps the application and delegates to `app.handle_command()`.

#### 5. Registering config in the container (optional)

For runtime overrides or dotted-key access to nested values, register a config instance with the container:

```python
config = app.make('config')
config.set('redis', RedisConfig())
```

Then access it from anywhere via the `Config` facade:

```python
from fastapi_startkit.facades import Config

Config.get('redis.host')     # 'host.testing'
Config.get('redis.options')  # {'decode_responses': True}
```

This is most useful when you need to change config at runtime or share nested config across services. Direct instantiation (`RedisConfig().host`) is simpler for read-only access.

`Configuration.merge_with()` allows packages to inject their own config defaults.

### Provider Pattern (`providers/`)

Providers are the standard way to register services. Each provider has two phases:
- `register()` — bind things into the container
- `boot()` — run after all providers are registered (safe to resolve dependencies here)

### ORM (`masoniteorm/`)

An async-first fork of Masonite ORM built on SQLAlchemy async. Key points:
- All DB operations are `async`/`await`
- `Model` base class auto-pluralizes table names via `inflection`
- `created_at`/`updated_at` are managed automatically as `pendulum` Carbon objects
- Relationships (`HasOne`, `HasMany`, `BelongsTo`, `BelongsToMany`, `HasOneThrough`) are defined as class attributes
- `AsyncQueryBuilder` provides the chainable query interface

### Facades (`facades/`)

Static-like access to container-resolved services (e.g., `Config.get()`, `Auth.user()`). Each facade has a corresponding `.pyi` stub file for IDE type support. Facades resolve from the Application singleton — they require a booted Application to function.

### Console (`console.py`, `commands/`, `masoniteorm/commands/`)

CLI is built on [Cleo](https://github.com/python-poetry/cleo). `ConsoleApplication` wraps Cleo and auto-registers commands. Database commands (migrate, seed, make:model, etc.) live in `masoniteorm/commands/`.

## Key Dependencies

| Package | Purpose |
|---|---|
| `fastapi[standard]` | HTTP framework (lazily imported) |
| `sqlalchemy[asyncio]` | Async ORM backend |
| `pendulum` | Datetime/timezone (used as Carbon) |
| `cleo` | CLI commands |
| `dotty-dict` | Nested dict access via dotted keys |
| `inflection` | Table name pluralization |
| `asyncpg` / `aiomysql` / `aiosqlite` | DB drivers |
