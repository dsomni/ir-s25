import asyncio
import json
import os
from time import time

from g4f.client import AsyncClient

from src.embeddingV2 import BERTBallTree
from src.utils import from_current_file, load


class RAG:
    folder_path = from_current_file("../data/scrapped/class_data_function__1_1")

    def __init__(self):
        self.client = AsyncClient()
        self.ball_tree = BERTBallTree()
        self.timeout: float = 60.0

    def generate_stream(self, question: str, model: str, k: int = 10):
        start = time()
        docs_scores, context = self._retrieve_docs(question, k)
        prompt = (
            "You're a Python expert. Suppose all the documentation information you know is provided in context section. "
            "Answer on the question as usual but take technical information only from context. "
            'If there is no answer in the context, say, "I can\'t find the answer in the Python documentation"\n'
            "Highlight cited passages or provide “show sources” toggles ONLY FROM CONTEXT\n"
            "NO PYTHON CODE EXAMPLES!\n"
            "NO PROMPT REPETITION IN ANSWER!\n"
            "NO EXAMPLES!\n"
            "NO ADDITIONAL EXPLANATIONS!\n"
            'If question is unrealated to python documentation, just answer "Question is unrelated"\n'
            "\nContext:\n"
            f"{'\n\n'.join([f'{idx + 1}. {c}' for idx, c in enumerate(context)])}\n"
            f"\nQuestion: {question}\n"
            f"\nResponse (with reference to the source [1-{k}]):\n"
        )
        messages = [{"role": "user", "content": prompt, "additional_data": []}]

        yield (
            json.dumps(
                {
                    "type": "proposals",
                    "data": [{"document": x[0], "score": x[1]} for x in docs_scores],
                }
            )
            + "\n\n"
        )

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                verbose=False,
                silent=True,
                max_tokens=500,
            )

            try:
                while True:
                    chunk = loop.run_until_complete(
                        asyncio.wait_for(response.__anext__(), timeout=self.timeout)
                    )

                    if chunk.choices[0].delta.content:
                        yield (
                            json.dumps(
                                {"type": "chunk", "data": chunk.choices[0].delta.content}
                            )
                            + "\n\n"
                        )
            except asyncio.TimeoutError:
                print("Timed out waiting for next item.")
            except StopAsyncIteration:
                print("Generator finished.")
            finally:
                loop.run_until_complete(response.aclose())
                loop.close()

        except BaseException as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

        yield (
            json.dumps({"type": "complete", "data": {"elapsed": time() - start}}) + "\n\n"
        )

    def _retrieve_docs(self, query_m: str, k):
        docs_scores = self.ball_tree.find(query_m, k=k)

        contents = []

        for name, _ in docs_scores:
            content = load(os.path.join(self.folder_path, name + ".txt"))

            contents.append(name + "\n" + content)

        return docs_scores, contents
