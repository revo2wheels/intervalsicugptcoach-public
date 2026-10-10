# Security

## Reporting a problem

Please report security problems privately. Don't open a public issue.

Use GitHub's private reporting: on this repository, open **Security → Report a vulnerability**. Include what you found, how to reproduce it, and what it could expose. You'll get a reply as soon as possible, and we'll agree a fix before anything is made public.

## Your keys

- Your Intervals.icu API key (`ICU_API_KEY`) or OAuth token (`ICU_OAUTH`) gives access to your Intervals.icu account. Set it in your terminal, as [docs/RUN_LOCALLY.md](docs/RUN_LOCALLY.md) shows, and never commit or share it.
- If a key has been exposed, generate a new one in Intervals.icu → Settings → Developer Settings. The old one then stops working.

## What the engine does with your data

When you run it yourself (`report.py --direct`), the engine reads your Intervals.icu data with your own key and writes reports to the `reports` folder on your computer. It sends nothing to Montis and never changes anything in Intervals.icu.

The hosted Montis service uses its own private keys, which are not part of this repository.
