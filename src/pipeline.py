import typing

from src.inverted_index import InvertedIndex
from src.llm_indexer import LlmTreeIndexer
from src.rag import RetrievalAugmentedGeneration
from src.spellcheck import NorvigSpellCorrector

PipelineOutput = tuple[
    str, list[tuple[str, float]]
]  # (spell correction, [(doc path, score)])

ApiModel = typing.Literal[
    "qwen-2-72b",
    "qwen-2.5-coder-32b",
    # "mixtral-small-24b",
    "gpt-4o",
    "wizardlm-2-7b",
    "wizardlm-2-8x22b",
    "dolphin-2.6",
    "dolphin-2.9",
    "glm-4",
    "evil",
    "command-r",
]

Indexer = typing.Literal["llm_tree_idx", "inverted_idx"]


class IndexerPipeline:
    _available_indexers: list[Indexer] = list(typing.get_args(Indexer))

    def __init__(self) -> None:
        self.indexer = InvertedIndex()
        self.llm_indexer = LlmTreeIndexer()
        self.corrector = NorvigSpellCorrector()

    def index(self, query: str, indexer: Indexer, k: int = 10) -> PipelineOutput:
        corrected_query = self.corrector.spell_correction(query)
        if indexer == "llm_tree_idx":
            scored_docs = self.llm_indexer.find(corrected_query, k=k)
        elif indexer == "inverted_idx":
            scored_docs = self.indexer.find(corrected_query, k=k)
        else:
            raise RuntimeError(f"Unknown indexer '{indexer}'")

        return (corrected_query, scored_docs)

    @property
    def available_indexers(self) -> list[Indexer]:
        return self._available_indexers


class RAGPipeline:
    _available_api_models: list[ApiModel] = list(typing.get_args(ApiModel))

    def __init__(self) -> None:
        self.rag = RetrievalAugmentedGeneration()
        self.indexer = IndexerPipeline()

    def request(
        self,
        query: str,
        model: ApiModel,
        k: int,
        indexer: Indexer,
    ):
        _, scored_docs = self.indexer.index(query, indexer, k=k)
        return self.rag.generate_stream(query, model, scored_docs)

    @property
    def available_models(self) -> list[ApiModel]:
        return self._available_api_models
