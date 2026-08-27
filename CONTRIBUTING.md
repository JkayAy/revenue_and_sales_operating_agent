# Contributing

Thanks for your interest in PipelinePilot. This started as a portfolio build with an emphasis on verified, testable claims, and issues and pull requests are welcome.

## Getting started

Fork and clone the repo, then follow the Quick start section in the README (Docker or local, in-memory mode). Before opening a pull request, run the test suite locally: `pytest` and `python -m eval` (the golden-eval harness).

## Making changes

Keep changes focused and describe what changed and why in the pull request. Match the existing code style, which is enforced by `ruff`. Add or update tests for new behavior rather than removing existing coverage, and if your change affects real HubSpot/CRM integration, do not commit live API keys or tokens — the mock client and shadow mode should remain the default.

## Pull requests

Reference any related issue, confirm that GitHub Actions CI passes on your branch, and describe how you tested the change locally, including whether MOCK_TOOLS/shadow_mode were left at their defaults.

## Reporting issues

Please include steps to reproduce, expected versus actual behavior, and any relevant logs or error messages. If the issue concerns a specific claim in the README's evidence table, note which row it relates to.

## Code of conduct

Be respectful and constructive. This is an actively maintained portfolio project, so response times may vary.
