import numpy as np
from sklearn.neighbors import BallTree
from transformers import AutoTokenizer, AutoModel
import torch

class BERTEmbedder:
    def __init__(self, model_name="sentence-transformers/stsb-bert-base", device=None):
        self.device = device or 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        self.do_lower_case = getattr(self.tokenizer, 'do_lower_case', False)

    def text_to_embedding(self, texts, pooling='mean', normalize=False):
        is_single = isinstance(texts, str)
        texts = [texts] if is_single else texts
        
        inputs = self.tokenizer(
            texts,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        if pooling == 'mean':
            mask = inputs['attention_mask'].unsqueeze(-1)
            embeddings = (outputs.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        elif pooling == 'cls':
            embeddings = outputs.last_hidden_state[:, 0, :]
        else:
            raise ValueError("Invalid pooling method")
            
        if normalize:
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            
        return embeddings.cpu().numpy()[0] if is_single else embeddings.cpu().numpy()


class BERTBallTree:
    def __init__(self, embedder=None, metric='euclidean', leaf_size=40):
        """
        Initialize the BERT Ball Tree.
        
        Args:
            embedder: Pre-initialized BERTEmbedder instance
            metric: Distance metric for BallTree ('euclidean', 'cosine', etc.)
            leaf_size: Affects the speed of queries and memory usage
        """
        self.embedder = embedder or BERTEmbedder()
        self.metric = metric
        self.leaf_size = leaf_size
        self.tree = None
        self.texts = None
    
    def build_tree(self, texts):
        """
        Build the Ball Tree from a list of texts.
        
        Args:
            texts: List of strings to index
        """
        self.texts = np.array(texts)  # Store the original texts
        embeddings = self.embedder.text_to_embedding(texts, pooling='mean', normalize=True)
        self.tree = BallTree(embeddings, metric=self.metric, leaf_size=self.leaf_size)
    
    def query(self, query_text, k=5, return_distances=False):
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
        if self.tree is None:
            raise ValueError("Ball Tree has not been built yet. Call build_tree() first.")
            
        # Get embedding for the query text
        query_embedding = self.embedder.text_to_embedding(
            query_text, pooling='mean', normalize=True
        ).reshape(1, -1)
        
        # Query the tree
        distances, indices = self.tree.query(query_embedding, k=k)
        
        # Get the corresponding texts
        results = self.texts[indices[0]]
        
        if return_distances:
            return results, distances[0]
        return results
    
    def save_tree(self, filepath):
        """Save the Ball Tree and associated data to disk."""
        import joblib
        data = {
            'texts': self.texts,
            'tree': self.tree,
            'metric': self.metric,
            'leaf_size': self.leaf_size
        }
        joblib.dump(data, filepath)
    
    @classmethod
    def load_tree(cls, filepath, embedder=None):
        """Load a saved Ball Tree from disk."""
        import joblib
        data = joblib.load(filepath)
        instance = cls(embedder=embedder, metric=data['metric'], leaf_size=data['leaf_size'])
        instance.texts = data['texts']
        instance.tree = data['tree']
        return instance
