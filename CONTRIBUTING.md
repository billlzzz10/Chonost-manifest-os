# Contributing to Chonost Manuscript OS

Thank you for your interest in improving Chonost Manuscript OS. The project is still evolving, so thoughtful pull requests that clarify intent and keep the codebase approachable are highly appreciated.

## Development Workflow
1. **Fork and clone** the repository.
2. **Create a branch** using `feature/<short-description>` or `fix/<short-description>`.
3. **Install dependencies** following `docs/ENV_SETUP_GUIDE.md` and verify that the backend and frontend start locally.
4. **Write tests** for any behaviour changes.
5. **Run the test suite** (`python -m pytest` inside `services/api-server`).
6. **Open a pull request** with a clear summary, screenshots for UI changes, and test results.

## Coding Standards
- **Python**: Format with `black`, type-check with `mypy`, and keep imports sorted (`isort` or the tooling of your choice).
- **TypeScript/React**: Run `npm run lint` from `craft-ide`. Follow modern React patterns (function components, hooks) and co-locate component docs where helpful.
- **Commits**: Prefer small, focused commits. Reference issues when applicable (`Fixes #123`).

## Testing Guidelines
- `python -m pytest` covers current backend behaviour.
- Add fast unit tests for new logic; integration and E2E coverage can live under `services/testing` as it grows.
- For frontend contributions, include Storybook examples or screencasts when practical.

## Documentation
- Update relevant files in `docs/` when altering architecture, setup, or API behaviour.
- Keep `README.md` aligned with real capabilities. If something is experimental, label it clearly.

## Communication
- Use GitHub Discussions or issues for design proposals.
- Draft pull requests are welcome when you need early feedback.

By contributing you agree to the MIT license that covers this repository.

