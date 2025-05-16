# Information Retrieval S25 Project

## Contributors

Dmitry Beresnev / <d.beresnev@innopolis.university>,

Vsevolod Klyushev / <v.klyushev@innopolis.university>

Nikita Yaneev / <n.yaneev@innopolis.university>

## Requirements

Code was tested on Windows 11 and Fedora Linux, Python 3.12

All the requirement packages are listed in the file `pyproject.toml`

## Before start

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Optionally setup pre-commit hook:

```bash
uv run pre-commit install
```

and test it:

```bash
uv run pre-commit run --all-files
```

We also highly recommend reading report to fully understand context and purpose of some files and folders.

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
