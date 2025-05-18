# PyFinder

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Ruff](https://img.shields.io/badge/style-ruff-%23cc66cc.svg?logo=ruff&logoColor=white)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)

An **Information Retrieval S25 Project**

---

## 📚 Table of Contents

- [📌 Contributors](#-contributors)
- [💼 Requirements](#-requirements)
- [🚀 Before You Start](#-before-you-start)
- [⚡ Quick Start](#-quick-start)
  - [🛠️ Setup](#️-setup)
  - [🏗️ Production](#️-production)
  - [🧪 Development](#-development)
- [🗂️ Repository Structure](#️-repository-structure)
- [📬 Contact](#-contact)

---

## 📌 Contributors

- Dmitry Beresnev — [d.beresnev@innopolis.university](mailto:d.beresnev@innopolis.university)
- Vsevolod Klyushev — [v.klyushev@innopolis.university](mailto:v.klyushev@innopolis.university)
- Nikita Yaneev — [n.yaneev@innopolis.university](mailto:n.yaneev@innopolis.university)

---

## 💼 Requirements

- ✅ Tested on **Windows 11** and **Fedora Linux**
- 🐍 Requires **Python 3.12**
- 📦 All dependencies are listed in [`pyproject.toml`](./pyproject.toml)

---

## 🚀 Before You Start

Install all dependencies using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Enable pre-commit hooks for auto-formatting/linting:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

> \[!IMPORTANT]
> 📄 We **highly recommend** reading [`about.md`](./about.md) to understand the workflow

---

## ⚡ Quick Start

### 🛠️ Setup

> \[!IMPORTANT]
> Make sure that you have installed all the python dependencies (check [🚀 Before You Start](#-before-you-start) for details)

Setup project using script:

- **Windows**:

  ```powershell
  ./setup.bat
  ```

- **Linux**:

  ```bash
  bash ./setup.sh
  ```

> \[!NOTE]
> Do not worry: sometimes script takes a while to initialize

> \[!WARNING]
> When setting up using script, you can not pass any flags. For flag description run: `uv run ./src/setup.py -h`

Or run corresponding python script:

```bash
uv run ./src/setup.py
```

### 🏗️ Production

Start everything together:

- **Windows**:

  ```powershell
  ./run_prod.bat
  ```

- **Linux**:

  ```bash
  bash ./run_prod.sh
  ```

Or start frontend/backend separately:

- **Backend**:

  ```bash
  uv run fastapi run
  ```

- **Frontend**:

  ```bash
  cd frontend
  yarn build
  yarn start
  ```

---

### 🧪 Development

Start everything together:

- **Windows**:

  ```powershell
  ./run_dev.bat
  ```

- **Linux**:

  ```bash
  bash ./run_dev.sh
  ```

Or start frontend/backend separately:

- **Backend**:

  ```bash
  uv run fastapi dev
  ```

- **Frontend**:

  ```bash
  cd frontend
  yarn dev
  ```

---

## 🗂️ Repository Structure

```text
.
├── data/                          # Data used in project
│   ├── bad_words/
│   │   └── bad_words.txt          # List of inappropriate words
│   │
│   ├── evaluation/                # Evaluation results and metrics
│   │   ├── general_metrics.json
│   │   ├── indexer_responses.json
│   │   ├── llm_metrics.json
│   │   ├── llm_responses.json
│   │   └── queries.json
│   │
│   ├── index_directory/          # Indexes and related metadata
│   │   ├── document_lengths.json
│   │   ├── document_word_count.json
│   │   ├── documents.json
│   │   └── index.json
│   │
│   ├── llm_tree_index/           # LLM-related tree index
│   │   ├── builder.json
│   │   └── tree.pkl
│   │
│   ├── scrapped/                 # Raw scraped web data
│   │   └── index_1_1.json        # Information about scrapped data
│   │
│   └── spell_directory/          # Spellcheck-related files
│       ├── counter.json
│       ├── settings.json
│       └── .gitignore
│
├── frontend/                  # Next.js frontend application
│
├── pictures/                  # Images, graphs, plots
│
├── src/                       # Main source code
│   ├── notebooks/             # Jupyter notebooks
│   │   ├── bert_indexer.ipynb
│   │   ├── content_filter.ipynb
│   │   ├── evaluate.ipynb     # For metrics evaluation
│   │   ├── inverted_index.ipynb
│   │   ├── scrapper.ipynb
│   │   ├── spellcheck.ipynb
│   │   └── w2v_indexer.ipynb
│   │
│   ├── bloom.py                # Bad words filter
│   ├── inverted_index.py
│   ├── llm_indexer.py
│   ├── pipeline.py             # Complete pipelines
│   ├── rag_local.py            # RAG with local models
│   ├── rag.py                  # RAG with API
│   ├── scrapper.py             # Data scrapper
│   ├── setup.py                # Main setup file
│   ├── spellcheck.py           # Norvig spell checker
│   ├── utils.py
│   └── w2v_indexer.py          # Unsuccessful Word2Vec
│
├── .env                       # Environment variables
├── .env.example               # Example environment template
├── .gitignore
├── .pre-commit-config.yaml    # Pre-commit hooks config
├── .python-version
├── about.md                   # Project description
├── main.py                    # FastAPI backend application
├── presentation.pdf           # Project presentation
├── pyproject.toml             # Dependency and tool config
├── uv.lock
└── README.md                  # Project documentation (this file)
```

---

## 📬 Contact

If you have any questions, feel free to reach out via the university emails listed above.
