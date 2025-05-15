import math
import os
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import nltk
from nltk.corpus import stopwords

from src.utils import from_current_file, load_json, round_float, save_json

nltk.download("stopwords")
nltk.download("punkt_tab")


def compute_levenshtein_distance(w1: str, w2: str) -> int:
    if len(w1) < len(w2):
        return compute_levenshtein_distance(w2, w1)

    if len(w2) == 0:
        return len(w1)

    previous_row = range(len(w2) + 1)

    for i, letter1 in enumerate(w1):
        current_row = [i + 1]
        for j, letter2 in enumerate(w2):
            add = previous_row[j + 1] + 1
            delete = current_row[j] + 1
            change = previous_row[j] + (letter1 != letter2)
            current_row.append(min(add, delete, change))

        previous_row = current_row

    return previous_row[-1]


class InvertedIndex:
    _stop_words = set(stopwords.words("english"))

    def __init__(
        self,
        index_dir: Path = from_current_file("../data/index_directory"),
        documents_dir: Path = from_current_file(
            "../data/scrapped/class_data_function__1_1"
        ),
        max_distance: int = 3,
        force: bool = False,
    ):
        self._index_dir = index_dir
        self._documents_dir = documents_dir
        self.max_distance = max_distance

        self._index_path = os.path.join(self._index_dir, "index.json")
        self._doc_word_count_path = os.path.join(
            self._index_dir, "document_word_count.json"
        )
        self._doc_id_path = os.path.join(self._index_dir, "documents.json")
        self._doc_len_path = os.path.join(self._index_dir, "document_lengths.json")

        self.index = defaultdict(set)  # {word : set(document id)}
        self.document_word_count = defaultdict(Counter)  # {document id -> word -> count}
        self.documents: dict[int, str] = {}  # {id: document title}
        self.document_lengths: dict[int, int] = {}  # doc_id -> total words in document

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
        for index_word in self.index:
            distance = compute_levenshtein_distance(word, index_word)
            if distance <= self.max_distance:
                matches.add(
                    (index_word, 1 / (1 + distance))
                )  # add inverse distance factor
        return matches

    def build_index(self):
        for document_id, filename in enumerate(os.listdir(self._documents_dir)):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(self._documents_dir, filename), "r", encoding="utf-8"
                ) as f:
                    text = f.read()
                    self.documents[document_id] = filename[:-4]
                    words = self._tokenize(text)
                    self.document_lengths[document_id] = len(words)

                    for word in words:
                        self.index[word].add(document_id)
                        self.document_word_count[document_id][word] += 1

        save_json(self._index_path, {k: list(v) for k, v in self.index.items()})
        save_json(self._doc_word_count_path, self.document_word_count)
        save_json(self._doc_id_path, self.documents)
        save_json(self._doc_len_path, self.document_lengths)

    def load_index(self):
        self.index = {k: set(v) for k, v in load_json(self._index_path).items()}
        self.document_word_count = {
            int(k): v for k, v in load_json(self._doc_word_count_path).items()
        }
        self.documents = {int(k): v for k, v in load_json(self._doc_id_path).items()}
        self.document_lengths = {
            int(k): v for k, v in load_json(self._doc_len_path).items()
        }

    def find(self, query: str, k: int = 10) -> list:
        query_words = self._tokenize(query)
        document_scores = Counter()
        total_documents = len(self.documents)

        for word in query_words:
            matching_words = self._get_similar_words(word) | {(word, 1)}

            for match, distance_coef in matching_words:
                if match in self.index:
                    doc_freq = len(self.index[match])
                    idf = math.log(total_documents / (1 + doc_freq))

                    for doc_id in self.index[match]:
                        tf = (
                            self.document_word_count[doc_id][match]
                            / self.document_lengths[doc_id]
                        )
                        document_scores[doc_id] += tf * idf * distance_coef  # type: ignore

        ranked_docs = sorted(document_scores.items(), key=lambda x: -x[1])[:k]
        return [
            (self.documents[doc_id], round_float(score, 5))
            for doc_id, score in ranked_docs
        ]
