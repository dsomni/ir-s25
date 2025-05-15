# Information Retrieval S25 Project

## Contributors

Dmitry Beresnev / <d.beresnev@innopolis.university>,

Vsevolod Klyushev / <v.klyushev@innopolis.university>

Nikita Yaneev / <n.yaneev@innopolis.university>

## Projects description

TBW

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

## Project Description
The project is a web application for intelligent search of Python documentation, 
combining three different approaches:

1. **Inverted Index** 
2. **Embedding search** 
3. **Generative approach** 


The system allows you to:
- Quickly find relevant documentation sections
- Compare the results of different search methods
- Receive extended explanations using language models

Key Features:

| Approach         |       Technologies       |                                             Advantages                                              |
|------------------|:------------------------:|:---------------------------------------------------------------------------------------------------:|
| Inverted index   |     k-grams, TF-IDF      |                                 High speed, exact matching of terms                                 |
| Embedding Search |    Embedding via LLM     |                                 Robust to synonyms and paraphrases                                  |
| RAG              | API, Prompt Engineering  | Ability to synthesize multiple sources Provides extended explanations beyond simple keyword matches |


## Inverted Index

We build a classical inverted index on the scraped documentation:

- K-grams tokenizer: Splits text into overlapping k-character sequences to 
support fuzzy matching and fast lookups.

- TF-IDF weighting: Assigns higher scores to terms that are important within 
a document but rare across the corpus.

- Query processing: Splits the request into k-grams and gets the
necessary documents for each k-gram. Computing TF-IDF


## Embedding Search

To capture semantic similarity, we use embeddings:

- Embedding extraction: We use a pre-trained LLM embedding endpoint to
convert each documentation section into a fixed-length vector.

- Ball Tree index: All embeddings are stored in a Ball Tree structure 
for efficient nearest-neighbor search in high-dimensional space.

- Query embeddings: A user's natural language query is embedded using
the same model, then matched in the Ball Tree to find semantically 
similar sections.


## Generative Search

We further enhance results with a Retrieval-Augmented Generation pipeline:

- Retrieve candidates: Use the Embedding Search (Ball Tree) to fetch the top-n
relevant sections.

- Construct prompt: Combine retrieved text with a task-specific
prompt template.

- LLM API call: Send the prompt to an LLM (e.g., Evil, command-r, qwen) via API.

- Generate answer: The model returns a synthesized, context-rich 
explanation incorporating the retrieved snippets.
## Technology stack

**Backend:**

- Python 3.12
- FastAPI
- NLTK
- sckit-learn
- PyTorch
- transformers

**Frontend:**

- NextJS

**Models:**

- ...
- ...
- ...




## References

TBW

## Contacts

In case of any questions you can contact us via university emails listed at the beginning
