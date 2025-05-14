from src.embeddingV2 import BERTBallTree
from src.indexer import Indexer
from src.rag import RAG
from src.spellcheck import NorvigSpellCorrector

PipelineOutput = tuple[
    str, list[tuple[str, float]]
]  # (spell correction, [(doc path, score)])


class Pipeline:
    def __init__(self) -> None:
        self.indexer = Indexer()
        self.BallTree = BERTBallTree()
        self.corrector = NorvigSpellCorrector()

    def inverted_index(self, query: str) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        scored_docs = self.indexer.find(corrected_query)

        return (corrected_query, scored_docs)

    def ball_tree(self, query: str) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        scored_docs = self.BallTree.find(corrected_query)

        return (corrected_query, scored_docs)


class RAGPipeline:
    def __init__(self) -> None:
        self.RAG = RAG()
        self.corrector = NorvigSpellCorrector()

    def request(self, query, model, k):
        corrected_query = self.corrector.spell_correction(query)
        return self.RAG.generate_stream(corrected_query, model, k)
