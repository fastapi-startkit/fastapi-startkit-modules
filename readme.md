## Setup

After cloning, activate the git hooks:

```sh
git config core.hooksPath .githooks
```

This enables the pre-commit hook that runs `ruff check --fix` on the core package before every commit.