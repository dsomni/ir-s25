# Information Retrieval S25 Project

by Dmitry Beresnev / <d.beresnev@innopolis.university>, Vsevolod Klyushev / <v.klyushev@innopolis.university> and Nikita Yaneev / <n.yaneev@innopolis.university>

## Projects description

TBW

## Requirements

Code was tested on Windows 11, Python 3.12

All the requirement packages are listed in the file `pyproject.toml`

## Before start

We recommend using [uv](https://docs.astral.sh/uv/) for project setup and management.
You can start with `uv sync`.

Optionally, you can run `bash setup_precommit.sh` to setup pre-commit hook for GitHub for code formatting using [ruff](https://docs.astral.sh/ruff/).

## Start

### Production

`uv run fastapi run`
`cd frontend`
`yarn build`
`yarn start`

Or, alternatively:
`./run_prod.bat` for Windows
`bash ./run_prod.sh` for Linux

### Development

`uv run fastapi dev`
`yarn dev`

Or, alternatively:
`./run_dev.bat` for Windows
`bash ./run_dev.sh` for Linux

## Repository structure

```text
├── data                 # Data used in project
├───── scrapped          # Dirty scrapped data
|
├── src                  # Source notebooks and scripts
├───── ...
|
├── .python-version
├── pyproject.toml       # Formatter and linter settings
├── README.md            # The top-level README
|
├── setup_precommit.sh   # Script for creating pre-commit GitHub hook
|
└── uv.lock              # Information about uv environment
```

## References

TBW

## Contacts

In case of any questions you can contact us via university emails listed at the beginning
