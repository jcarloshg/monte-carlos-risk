# Task 007 — Portfolio YAML + Inline Parser

**Epic:** epic-002-portfolio-declare-and-validate-holdings
**Layer:** Infrastructure
**Sprint:** 02
**Depends on:** task-006
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Translates user input (YAML file path or inline string) into a `Portfolio` aggregate. The parser lives in `infrastructure/` because PyYAML is a third-party I/O library, forbidden in `domain/` per ADR-001. Traces to Stories 2.1, 2.3.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a YAML file `p.yaml` with `holdings: [{ticker: AAPL, weight: 0.4}, {ticker: MSFT, weight: 0.3}, {ticker: GOOG, weight: 0.3}]`, When I call `YamlPortfolioParser.from_path(Path("p.yaml"))`, Then a `Portfolio` aggregate is returned with the expected holdings.
- [ ] **Scenario 2 (Sad Path):** Given a YAML file with malformed YAML (e.g., a tab indentation), When I call `from_path`, Then `PortfolioYamlParseError` is raised with the line number from PyYAML's error in the context dict.
- [ ] **Scenario 3 (Inline Happy Path):** Given `'AAPL:0.4,MSFT:0.3,GOOG:0.3'`, When I call `InlinePortfolioParser.from_string(s)`, Then a `Portfolio` aggregate is returned with the expected holdings.
- [ ] **Scenario 4 (Inline Sad Path):** Given `'AAPL:0.4,MSFT:0.3'` (sum 0.7), When I call `InlinePortfolioParser.from_string`, Then `WeightsSumMustEqualOne` is raised (the aggregate's invariant catches it; parser is pass-through).
- [ ] **Edge Case (Mandatory):** If the YAML file path does not exist, `PortfolioFileNotFound` is raised with the absolute path in the context dict. The CLI's error envelope maps this to `error_code = "portfolio_file_not_found"` (already in `cli-contract.yaml`).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The `validate-portfolio` use case (`task-008`) — this task only adds the parsers.
- The CLI command (`task-009`) — this task only adds the infrastructure adapters.

## Deliverables

- `src/monte_carlo_risk/infrastructure/filesystem/yaml_portfolio_parser.py` — `class YamlPortfolioParser` with `from_path(path: Path) -> Portfolio` and `from_string(yaml_text: str) -> Portfolio`. Uses PyYAML `safe_load`. Validates the loaded dict against the schema fields from `cli-contract.yaml` §`portfolio_schema` before constructing the aggregate.
- `src/monte_carlo_risk/infrastructure/filesystem/inline_portfolio_parser.py` — `class InlinePortfolioParser` with `from_string(text: str) -> Portfolio`. Splits on `,`, then on `:`, validates ticker pattern and weight range, then constructs the aggregate (which enforces the sum invariant).
- `tests/unit/infrastructure/filesystem/test_yaml_portfolio_parser.py`
- `tests/unit/infrastructure/filesystem/test_inline_portfolio_parser.py`
- New `pyproject.toml` dependency: `pyyaml>=6.0`.
