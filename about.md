# PyFinder

PyFinder is a useful app that allows you to fast search relevant Python documentation files for built-in modules!

PyFinder has several modes:
- **Search Mode** - Allows you to find useful documentation by keywords and phrases, basing its answer on one of indexing approaches (**Inverted Index** or **LLM embedding + Ball Tree**)
- **Chat Mode (Retrieval-Augmented Generation)** - With help of selected LLM model, you can get all necessary information in our chat section! 

## Technology stack

**Backend:**

- Python 3.12 - main programming language
- FastAPI - backend framework
- NLTK - library for words processing
- sckit-learn - library with various metrics and algorithms (e.g. Ball Tree)
- PyTorch - part of main toolkit for working with neural networks and GPU calculations
- transformers - library for importing and usage different LLMs
- g4f - free API for hosted LLMs (e.g. evil, command-r, qwen)
- pybloom-live - data structure, which helps to filter bad words

**Frontend:**

- NextJS - main frontend language

**Models:**

- Hosted LLMs (e.g. evil, command-r, qwen)
- "sentence-transformers/all-MiniLM-L6-v2" - for embeddings generation

## System Design
<p align="center">
  <img src=./pictures/Flow_PyFinder.png/>
</p>

### Workflows:

1. Frontend ➔ Bloom: Content filtering of incoming query before passing to RAG
2. Frontend ➔ Norwig: Pass query through Norvig spell corrector
3. Frontend ➔ Scrapped Data: Access the information about scrapped documents
4. Bloom ➔ RAG: Pass query to RAG pipeline 
5. RAG ➔ Norvig: Pass query to Norvig Spell Corrector
6. Norvig ➔ Indexer: Pass corrected query to indexer to get relevant documents 
7. Indexer ➔ Scrapped Data: Retrieve relevant documents
8. RAG ➔ LLM API: Insert query and retrieved documents in prompt for LLM model and get its answer 

## Components:

### Bloom

**1. Bad Word List Aggregation**  
The system builds its lexicon by combining multiple authoritative sources:  
- [Google's profanity word list](https://github.com/coffee-and-fun/google-profanity-words/tree/main)
- [LDNOOBW's English bad words](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/en)
- [LDNOOBW's Russian bad words](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/ru)

These are fetched via HTTP requests, merged, sanitized (lowercased, deduplicated), and stored locally.

**2. Efficient Storage with Bloom Filters**  
For high-performance checking, we use a probabilistic data structure that:  
- Initializes with 5,000 word capacity (ScalableBloomFilter from `pybloom_live`)  
- Maintains 0.1% false positive rate
- Automatically expands for large vocabularies
- Stores both original words and phrase variants

**3. Content Moderation Logic**  
When checking text, the system:  
1. Checks individual words against the filter  
2. Examines word sequences up to `phrase_length` (default=5)  
3. Returns the first match found with:  
   - The offending word/phrase  
   - Boolean confirmation  

**Key Features**  
- Automatic cache rebuilding (`force=True`)  
- Multi-language support (English/Russian)  
- Space-efficient storage via bloom filters  
- Configurable phrase detection length  

### Norvig

**1. Text Preprocessing Pipeline**  
Firstly, using `nltk` and `re`, we clean both our scraped data and incoming queries by:
- Removing stopwords (via `filter_stopwords()`)
- Tokenizing text into lowercase words (via `tokenize()`)
- Stripping non-ASCII characters during index building

**2. Building the Language Model**  
Based on the cleaned documents, we:
- Count word frequencies across all documents
- Calculate each word's probability (occurrence/total words)
- Optionally precompute edit-distance relationships when `save_distances=True`

**3. Generating Spelling Suggestions**  
For any misspelled word, we:
- Generate all possible edits within `max_edits` (default=2) using:
  - Deletions (`acess → access`)
  - Transpositions (`acess → acess`)
  - Replacements (`acess → accss`)
  - Insertions (`acess → access`)
- Filter candidates to only known vocabulary words
- Return the most frequent valid candidate

**4. Query Processing**  
When correcting text, we:
- Preserve punctuation positioning
- Optionally skip stopword correction
- Handle single-word inputs efficiently

**Key Optimizations**  
- Edit dictionaries are precomputed (`save_distances`) for faster lookup
- Stopword filtering reduces noise in frequency counts
- Configurable edit distance balances accuracy/speed

### Indexer (Inverted Index Search)

We use an **inverted index** to efficiently search through Python documentation files. The system leverages `nltk` to remove English stop words during indexing and query processing, focusing only on meaningful terms.

**1. Indexing**  
We build an inverted index that maps each word to the documents containing it
For each document, we store:
- Word counts (for TF calculation)
- Total document length (for normalization)
- Document titles

**2. Search**
Queries are tokenized and stop words are removed 
We use **Levenshtein distance** (with configurable max distance) to find similar words
Results are ranked using TF-IDF scoring, weighted by:
    - Term frequency in document
    - Inverse document frequency
    - Similarity score ${1}\over{(1 + distance)}$

**3. Fuzzy matching**:
- When a word isn't found exactly, we match similar words within the allowed edit distance
- Each match contributes to the score, weighted by its similarity to the query term

### Indexer (LLM Embeddings + Ball Tree Search)

We use **LLM embeddings** to convert text into dense vector representations and a **Ball Tree** data structure for efficient nearest-neighbor search. The system leverages `sentence-transformers/all-MiniLM-L6-v2` to generate high-quality embeddings that capture semantic meaning.

**1. Embedding Generation**:
  - We use LLM to convert text into embeddings
  - Supports `mean` pooling or `cls` token pooling
**2. Indexing**:
  - Documents are processed in batches for efficiency 
  - Embeddings are stored in a Ball Tree for fast similarity search
**3. Search**:
  - Query text is embedded using the same LLM model
  - The Ball Tree finds the k-nearest neighbors in embedding space
  - Returns either document names or (documents + distances)

The system is particularly effective for:
- Finding semantically similar Python documentation
- Handling paraphrased queries
- Discovering related functions/classes based on description

### RAG

**1. Context-Aware Prompt Engineering**  
The system uses a structured prompt template that:
- Restricts answers to provided Python documentation only
- Requires citation of source documents
- Prohibits code examples or unsourced information
- Formats responses with clear references

**2. Dual-Mode Operation**  
The assistant supports both synchronous and asynchronous workflows:
- **Streaming mode**: For real-time responses with progress updates
  - Yields proposals, content chunks, and timing data
  - Enforces 30-second timeout for model responses
- **Batch mode**: For direct question-answer pairs
  - Returns complete responses with error handling

**3. Document Retrieval**  
When processing queries:
1. Fetches relevant documentation files from local storage
2. Combines them with the query into a structured prompt
3. Tracks source documents for proper attribution

**4. AI Response Handling**  
The system carefully manages LLM interactions by:
- Using both async/sync clients for flexibility
- Implementing chunked streaming with rate limiting
- Providing full error handling and timeout protection
- Maintaining strict separation between docs and generation

**Key Features**  
- Strict Python-only responses with citations
- Real-time streaming with JSON-formatted outputs
- Configurable timeout protection
- Dual client architecture for different use cases

## Key challenges and solutions
Tried w2v was bad

Local model has pure performance or too heavy for our machines

Find free api for LLMs


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

## Key Features:

| Approach         |       Technologies       |                                             Advantages                                              |
|------------------|:------------------------:|:---------------------------------------------------------------------------------------------------:|
| Inverted index   |     Inverted Index & Levenshtein distance      |                                 High speed, exact matching of terms                                 |
| Embedding Search |    Embedding via LLM & Ball Tree     |                                 Robust to synonyms and paraphrases                                  |
| RAG              | API, Prompt Engineering  | Ability to synthesize multiple sources Provides extended explanations beyond simple keyword matches. Answer with only relevant to question information |
