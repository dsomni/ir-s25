import os
import re
import shutil

import numpy as np
from annoy import AnnoyIndex
from gensim.models import Word2Vec
from nltk.corpus import stopwords

from src.utils import from_current_file, load_json, round_float, save_json


class Word2VecIndexer:
    _stop_words = set(stopwords.words("english"))

    def __init__(
        self,
        index_dir: str = "../data/embedding_directory",
        documents_dir: str = "../data/scrapped/class_data_function__1_1",
        top_similar: int = 10,
        force: bool = False,
    ):
        self._index_dir = from_current_file(index_dir)
        self._documents_dir = from_current_file(documents_dir)
        self.top_similar = top_similar

        self._word2vec_model_path = os.path.join(self._index_dir, "word2vec.model")
        self._annoy_index_path = os.path.join(self._index_dir, "doc_embeddings.ann")
        self.doc_embeddings: dict[int, np.ndarray] = {}  # Document ID -> embedding
        self.annoy_index: AnnoyIndex = None  # Annoy index for document embeddings
        self._doc_id_path = os.path.join(self._index_dir, "documents.json")
        self.documents: dict[int, str] = {}

        self.model: Word2Vec = None

        if force or not os.path.exists(self._index_dir):
            print("Index is not found, creating new...")
            if force:
                try:
                    shutil.rmtree(self._index_dir)
                except FileNotFoundError:
                    pass
            os.mkdir(path=self._index_dir)
            self.build_index()
            print("Complete!")

        self.load_index()

    def _tokenize(self, text: str) -> list[str]:
        return [w for w in re.findall(r"\w+", text.lower()) if w not in self._stop_words]

    def _get_similar_words(self, word: str) -> set[tuple[str, float]]:
        matches = set()
        if self.model and word in self.model.wv:
            for similar_word, similarity in self.model.wv.most_similar(
                word, topn=self.top_similar, indexer=self.annoy_indexer
            ):
                if similar_word in self.index:
                    matches.add((similar_word, similarity))
        return matches

    def build_index(self):
        sentences = []
        for document_id, filename in enumerate(os.listdir(self._documents_dir)):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(self._documents_dir, filename), "r", encoding="utf-8"
                ) as f:
                    text = f.read()
                    self.documents[document_id] = filename[:-4]
                    words = self._tokenize(text)
                    sentences.append(words)

        self.model = Word2Vec(
            sentences=sentences,
            min_count=1,
        )
        vector_size = self.model.vector_size

        self.doc_embeddings = {
            doc_id: np.mean(
                [self.model.wv[word] for word in words if word in self.model.wv], axis=0
            )
            for doc_id, words in enumerate(sentences)
        }

        # self.doc_embeddings = {}
        # for doc_id, words in tqdm(enumerate(sentences)):
        #     self.doc_embeddings[doc_id] = np.mean([
        #         self.model.wv[word]
        #         for word in words
        #         if word in self.model.wv
        #     ], axis=0)

        # Build Annoy index for documents
        self.annoy_index = AnnoyIndex(vector_size, "angular")
        for doc_id, embedding in self.doc_embeddings.items():
            self.annoy_index.add_item(doc_id, embedding)
        self.annoy_index.build(n_trees=1000)
        self.annoy_index.save(self._annoy_index_path)

        # Persist model and index
        self.model.save(self._word2vec_model_path)

        save_json(self._doc_id_path, self.documents)

    def load_index(self):
        self.documents = {int(k): v for k, v in load_json(self._doc_id_path).items()}
        self.model = Word2Vec.load(self._word2vec_model_path)
        vector_size = self.model.vector_size
        self.annoy_index = AnnoyIndex(vector_size, "angular")
        self.annoy_index.load(self._annoy_index_path)

    def find(self, query: str, top_k: int = 10) -> list:
        query_words = self._tokenize(query)
        query_vectors = [
            self.model.wv[word] for word in query_words if word in self.model.wv
        ]

        if not query_vectors:
            return []

        # Average word vectors for query embedding
        query_embedding = np.mean(query_vectors, axis=0)

        # Find similar documents using Annoy
        doc_ids, distances = self.annoy_index.get_nns_by_vector(
            query_embedding, top_k, include_distances=True
        )

        # Convert angular distances to cosine similarities
        results = []
        for doc_id, distance in zip(doc_ids, distances):
            cosine_sim = 1 - (distance**2) / 2  # Convert angular distance to cosine
            results.append((doc_id, cosine_sim))

        return [
            (self.documents[doc_id], round_float(score, 5))
            for doc_id, score in sorted(results, key=lambda x: -x[1])
        ]
