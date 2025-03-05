import os

import nltk

from src.utils import from_current_file

nltk.download("stopwords")
nltk.download("punkt_tab")


class Indexer:
    def __init__(
        self,
        index_dir: str = "../data/index_directory",
        documents_dir: str = "../data/scrapped/class_data_function__1_1",
    ):
        self._index_dir = from_current_file(index_dir)
        self._documents_dir = from_current_file(documents_dir)

        if not os.path.exists(self._documents_dir):
            print("Index is not found, creating new...")
            os.mkdir(path=self._documents_dir)
            self.build_index()
            print("Complete!")

        self.load_index()

    def find(self, query: str) -> list[tuple[str, float]]:
        return [(query, 0.0)]

    def build_index(self):
        pass

    def load_index(self):
        pass
