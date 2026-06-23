# Monte Carlo Risk Model

Simulate thousands of possible portfolio paths using historical return distributions. Calculate drawdown probabilities and tail risk. This is how quant firms evaluate strategies before deploying real capital. Built with numpy and matplotlib.

## Quickstart

```bash
make bootstrap   # install package + dev extras, run pytest
make test        # run pytest with coverage
make lint        # ruff check + format check + mypy
make format      # auto-fix lint and format
make docker-build   # build the container image (optional)
make docker-smoke   # smoke-check the container image
```

Requires **Python 3.12+**. The bootstrap target works without Docker; container
images are built only via `make docker-build`.

## Notes

1. Educational / example project.
2. Shipped as a single Docker image (`make docker-build && make docker-smoke`).
3. Uses bundled mock data.
4. Pure Python (numpy + matplotlib).
5. Hexagonal architecture — domain isolated from transport and infrastructure.