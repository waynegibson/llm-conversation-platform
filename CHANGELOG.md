# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- GitHub Actions CI workflow for pull requests and `main` pushes with pre-commit, lint, and test gates

### Changed

- CI triggers optimized to reduce noise (branch strategy and docs/metadata ignores)
- Branch protection settings-as-code now require the `lint-and-test` status check before merge

## [0.1.0] - 2026-04-29

### Added

- FastAPI service for conversation and message persistence
- PostgreSQL-backed data model with Alembic migrations
- Ollama-backed streaming and non-streaming chat endpoints
- Structured logging, Prometheus metrics, and container hardening
- Ruff, pytest, and pre-commit quality gates
- Release process documentation in the README
- Annotated Git tag targets in the Makefile
- Repository settings as code via `.github/settings.yml`
