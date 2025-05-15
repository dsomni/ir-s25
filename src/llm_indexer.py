import os
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import List

import joblib
import numpy as np
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import BallTree

from src.utils import from_current_file, load_json, save_json

STOP_WORDS = set(stopwords.words("english"))


class LlmEmbeddingBuilder:
    def __init__(
        self,
        index_dir: Path = from_current_file("../data/llm_tree_index"),
        documents_dir: Path = from_current_file(
            "../data/scrapped/class_data_function__1_1"
        ),
        force: bool = False,
        model_name: str = "all-MiniLM-L6-v2",
        common_word_threshold: float = 0.5,
    ):
        self._index_dir = index_dir
        self._documents_dir = documents_dir

        self.model_name = model_name
        self.common_word_threshold = common_word_threshold
        self.model = SentenceTransformer(self.model_name)

        self.common_words = set()

        self._builder_path = os.path.join(self._index_dir, "builder.json")

        if force or not os.path.exists(self._builder_path):
            print("Builder is not found, creating new...")
            if force:
                try:
                    shutil.rmtree(self._index_dir)
                except FileNotFoundError:
                    pass
            os.makedirs(self._index_dir, exist_ok=True)
            self.build()
            print("Complete!")
        else:
            self.load()

    def build(self):
        docs = self._load_docs()
        self._build_embeddings(docs)
        self.save()

    def _load_docs(self) -> list[str]:
        sentences = []
        self.documents = []
        for document_id, filename in enumerate(os.listdir(self._documents_dir)):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(self._documents_dir, filename), "r", encoding="utf-8"
                ) as f:
                    text = f.read()
                    self.documents.append(filename[:-4])
                    sentences.append(f"{filename[:-4]}\n\n{text}")

        return sentences

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9_]+", " ", text)
        return text.split()

    def _preprocess(self, docs: List[str]) -> List[str]:
        tokenized_docs = []
        word_counts = Counter()

        for doc in docs:
            tokens = self._tokenize(doc)
            tokenized_docs.append(tokens)
            word_counts.update(set(tokens))

        doc_count = len(docs)
        self.common_words = {
            word
            for word, freq in word_counts.items()
            if freq / doc_count > self.common_word_threshold
        }

        cleaned_docs = []
        for tokens in tokenized_docs:
            filtered = [
                t for t in tokens if t not in STOP_WORDS and t not in self.common_words
            ]
            cleaned_docs.append(" ".join(filtered))

        return cleaned_docs

    def _build_embeddings(self, docs: List[str]):
        self.cleaned_documents = self._preprocess(docs)
        self.embeddings = self.model.encode(
            self.cleaned_documents, show_progress_bar=True
        )

    def embed_query(self, query: str) -> np.ndarray:
        tokens = self._tokenize(query)
        filtered = [
            t for t in tokens if t not in STOP_WORDS and t not in self.common_words
        ]
        cleaned = " ".join(filtered)
        return self.model.encode([cleaned])

    def save(self):
        metadata = {
            "common_words": list(self.common_words),
            "common_word_threshold": self.common_word_threshold,
            "model_name": self.model_name,
            "documents": self.documents,
        }
        save_json(self._builder_path, metadata)

    def load(self):
        metadata = load_json(self._builder_path)

        self.common_words = set(metadata["common_words"])
        self.common_word_threshold = metadata["common_word_threshold"]
        self.model_name = metadata["model_name"]
        self.documents = metadata["documents"]
        self.model = SentenceTransformer(self.model_name)


class LlmTreeIndexer:
    def __init__(
        self,
        index_dir: Path = from_current_file("../data/llm_tree_index"),
        documents_dir: Path = from_current_file(
            "../data/scrapped/class_data_function__1_1"
        ),
        force: bool = False,
    ):
        self._index_dir = index_dir
        self._documents_dir = documents_dir
        self.embedding_builder = LlmEmbeddingBuilder(
            self._index_dir, self._documents_dir, force=force
        )

        self._tree_path = os.path.join(self._index_dir, "tree.pkl")

        if force or not os.path.exists(self._tree_path):
            print("Tree is not found, creating new...")
            if force:
                try:
                    shutil.rmtree(self._index_dir)
                except FileNotFoundError:
                    pass
            os.makedirs(self._index_dir, exist_ok=True)
            self.build_tree()
            print("Complete!")
        else:
            self.load()

    def build_tree(self):
        if self.embedding_builder.embeddings is None:
            raise ValueError("Embeddings not built or loaded.")
        self.tree = BallTree(self.embedding_builder.embeddings, metric="euclidean")
        self.save()

    def save(self):
        if self.tree is None:
            raise ValueError("BallTree not built.")
        joblib.dump(self.tree, self._tree_path)

    def load(self):
        self.tree = joblib.load(self._tree_path)

    def find(self, query: str, k: int = 5):
        if self.tree is None:
            raise ValueError("BallTree not built or loaded.")
        query_embedding = self.embedding_builder.embed_query(query)
        dist, ind = self.tree.query(query_embedding, k=k)
        return [
            (self.embedding_builder.documents[i], dist[0][j])
            for j, i in enumerate(ind[0])
        ]
