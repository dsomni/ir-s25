from src.embedding import Word2VecIndexer
from src.indexer import Indexer
from src.spellcheck import NorvigSpellCorrector

PipelineOutput = tuple[
    str, list[tuple[str, float]]
]  # (spell correction, [(doc path, score)])


class Pipeline:
    def __init__(self) -> None:
        self.indexer = Indexer()
        self.W2Vindexer = Word2VecIndexer()
        self.corrector = NorvigSpellCorrector()

    def inverted_index(self, query: str) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        scored_docs = self.indexer.find(corrected_query)

        return (corrected_query, scored_docs)

    def w2v(self, query: str) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        scored_docs = self.W2Vindexer.find(corrected_query)

        return (corrected_query, scored_docs)
