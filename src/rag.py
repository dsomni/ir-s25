import asyncio
import json
import os
import time

from g4f.client import AsyncClient

from src.utils import from_current_file, load


def get_prompt(query: str, sources: list[str]) -> str:
    return (
        "### Role\n"
        "You are a Python documentation assistant. Your knowledge is strictly limited to the provided context.\n\n"
        "### Instructions\n"
        "1. Answer Requirements:\n"
        "   - Provide a concise answer based only on the context.\n"
        "   - End your response with: `References: [X, Y]` (document indices where the answer is found).\n\n"
        "2. If the answer is missing:\n"
        '   - Say: "I can\'t find the answer in the Python documentation."\n\n'
        "3. If the question is unrelated to Python:\n"
        '   - Respond: "Question is unrelated."\n\n'
        "4. Strict Prohibitions:\n"
        "   - No repetition of the prompt.\n"
        "   - No extra explanations beyond the context.\n"
        "   - No unsourced information.\n\n"
        "5. Citations:\n"
        '   - Highlight key phrases only from the context (or use "show sources" if needed).\n\n'
        "### Context\n"
        f"{'\n\n'.join([f'{idx + 1}. {c}' for idx, c in enumerate(sources)])}\n\n"
        "### Question\n"
        f"{query}\n\n"
        "### Response Format\n"
        "[Your answer here.]\n"
        "References: [X, Y]"
    )


class RetrievalAugmentedGeneration:
    folder_path = from_current_file("../data/scrapped/class_data_function__1_1")
    response_timeout_seconds: float = 30.0

    def __init__(self):
        self.client = AsyncClient()

    def generate_stream(
        self, query: str, model: str, scored_docs: list[tuple[str, float]]
    ):
        start = time.time()
        source_names = [x for x, _ in scored_docs]
        sources = self._retrieve_docs(source_names)

        prompt = get_prompt(query, sources)
        messages = [{"role": "user", "content": prompt, "additional_data": []}]

        yield (
            json.dumps(
                {
                    "type": "proposals",
                    "data": [{"document": x[0], "score": x[1]} for x in scored_docs],
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

            delay = 0.05
            max_iters = int(self.response_timeout_seconds // delay)
            try:
                for _ in range(max_iters):
                    chunk = loop.run_until_complete(
                        asyncio.wait_for(
                            response.__anext__(),  # type: ignore
                            timeout=self.response_timeout_seconds,
                        )
                    )

                    if chunk.choices[0].delta.content:
                        yield (
                            json.dumps(
                                {"type": "chunk", "data": chunk.choices[0].delta.content}
                            )
                            + "\n\n"
                        )
                    time.sleep(delay)
            except asyncio.TimeoutError as e:
                raise TimeoutError("Timed out waiting for the model response") from e
            except StopAsyncIteration:
                # Generator finished
                pass
            finally:
                loop.run_until_complete(response.aclose())  # type: ignore
                loop.close()

        except BaseException as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

        yield (json.dumps({"type": "complete", "data": time.time() - start}) + "\n\n")

    def _retrieve_docs(self, source_names: list[str]) -> list[str]:
        contents = []

        for name in source_names:
            content = load(os.path.join(self.folder_path, name + ".txt"))

            contents.append(name + "\n" + content)

        return contents
