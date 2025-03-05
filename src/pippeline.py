from src.indexer import Indexer
from src.spellcheck import NorvigSpellCorrector

PipelineOutput = tuple[
    str, list[tuple[str, float]]
]  # (spell correction, [(doc path, score)])


class Pipeline:
    def __init__(self) -> None:
        self.indexer = Indexer()
        self.corrector = NorvigSpellCorrector()

    def __call__(self, query: str) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        scored_docs = self.indexer.find(corrected_query)

        return (corrected_query, scored_docs)
