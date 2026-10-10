# Contributing

Thanks for your interest in the Montis coaching engine.

## Questions and bugs

Open an issue. Say what you ran (for example `python report.py --range weekly --direct`), what you expected and what happened. Leave out your API key and any personal data, and attach only the parts of a report that show the problem.

Security problems go through [SECURITY.md](SECURITY.md), not public issues.

## Changes

1. Fork the repository and create a branch.
2. Set up Python as in [docs/RUN_LOCALLY.md](docs/RUN_LOCALLY.md).
3. Make your change and keep it focused on one thing.
4. Run the tests:

   ```bash
   python -m unittest discover -s tests
   ```

5. Run a report with your own data to check it still works:

   ```bash
   python report.py --range weekly --direct
   ```

6. Open a pull request that explains what changed and why.

Coaching thresholds, keywords and windows live in `coaching_cheat_sheet.py`. Please change them there rather than hard-coding values elsewhere, and cite the source (a paper or a coaching reference) for any change to how a metric is calculated.

## Licence

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE) of this repository.
