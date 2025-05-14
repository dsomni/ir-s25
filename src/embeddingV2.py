import os
import shutil

import torch
from sklearn.neighbors import BallTree
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from src.utils import from_current_file


class BERTEmbedder:
    def __init__(self, model_name="sentence-transformers/msmarco-bert-base-dot-v5"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.do_lower_case = getattr(self.tokenizer, "do_lower_case", False)

    def text_to_embedding(self, texts, pooling="mean", normalize=False):
        is_single = isinstance(texts, str)
        texts = [texts] if is_single else texts

        inputs = self.tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        if pooling == "mean":
            mask = inputs["attention_mask"].unsqueeze(-1)
            embeddings = (outputs.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(
                min=1e-9
            )
        elif pooling == "cls":
            embeddings = outputs.last_hidden_state[:, 0, :]
        else:
            raise ValueError("Invalid pooling method")

        if normalize:
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().numpy()[0] if is_single else embeddings.cpu().numpy()


def batch(iterable, batch_size):
    all_batches = []
    current_batch = []

    for item in iterable:
        current_batch.append(item)
        if len(current_batch) == batch_size:
            all_batches.append(current_batch)
            current_batch = []

    if current_batch:  # Add the last partial batch
        all_batches.append(current_batch)

    return all_batches


class BERTBallTree:
    def __init__(
        self,
        index_dir: str = "../data/embedding_directory",
        documents_dir: str = "../data/scrapped/class_data_function__1_1",
        metric="euclidean",
        leaf_size=1,
        tree_name="tree",
        force=False,
    ):
        self._index_dir = from_current_file(index_dir)
        self._documents_dir = from_current_file(documents_dir)
        self.embedder = BERTEmbedder()
        self.metric = metric
        self.leaf_size = leaf_size
        self.tree = None
        self.tree_name = tree_name
        self.documents: dict[int, str] = {}

        if force or not os.path.exists(self._index_dir):
            print("Tree is not found, creating new...")
            if force:
                try:
                    shutil.rmtree(self._index_dir)
                except FileNotFoundError:
                    pass
            os.mkdir(path=self._index_dir)
            self.build_tree()
            print("Complete!")

        self.load_tree()

    def build_tree(self):
        sentences = []
        for document_id, filename in enumerate(os.listdir(self._documents_dir)):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(self._documents_dir, filename), "r", encoding="utf-8"
                ) as f:
                    text = f.read()
                    self.documents[document_id] = filename[:-4]
                    sentences.append(text)

        embeddings = []
        for b in tqdm(batch(sentences, 64)):
            batch_embeddings = self.embedder.text_to_embedding(
                b, pooling="mean", normalize=True
            )
            embeddings.extend(batch_embeddings)
        self.tree = BallTree(embeddings, metric=self.metric, leaf_size=self.leaf_size)
        self.save_tree()

    def find(self, query_text, k=10, return_distances=True):
        """
        Query the Ball Tree for nearest neighbors.

        Args:
            query_text: The query text string
            k: Number of nearest neighbors to return
            return_distances: Whether to return distances along with results

        Returns:
            If return_distances is False: list of nearest texts
            If return_distances is True: tuple of (texts, distances)
        """
        # Get embedding for the query text
        query_embedding = self.embedder.text_to_embedding(
            query_text, pooling="mean", normalize=True
        ).reshape(1, -1)

        # Query the tree
        distances, indices = self.tree.query(query_embedding, k=k)

        # Get the corresponding texts
        results = []
        for indice in indices[0]:
            results.append(self.documents[indice])

        if return_distances:
            return results, distances[0]
        return results

    def save_tree(self):
        """Save the Ball Tree and associated data to disk."""
        import joblib

        data = {
            "tree": self.tree,
            "documents": self.documents,
        }
        joblib.dump(data, os.path.join(self._index_dir, self.tree_name))

    def load_tree(self):
        """Load a saved Ball Tree from disk."""
        import joblib

        data = joblib.load(os.path.join(self._index_dir, self.tree_name))
        self.tree = data["tree"]
        self.documents = data["documents"]
