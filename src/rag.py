import json
import os

from g4f.client import Client

from src.embeddingV2 import BERTBallTree
from utils import load


class RAG:
    folder_path = "../data/scrapped/class_data_function__1_1"

    def __init__(self):
        self.client = Client()
        self.ball_tree = BERTBallTree()

    def generate_stream(self, question: str, model: str, k: int = 10):
        res, context = self._retrive_docs(question, k)
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
        messages = [{"role": "user", "content": prompt}]

        yield (
            json.dumps(
                {
                    "type": "proposals",
                    "data": [{"document": x[0], "score": x[1]} for x in res],
                }
            )
            + "\n\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                verbose=False,
                max_tokens=500,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield (
                        json.dumps(
                            {"type": "chunk", "data": chunk.choices[0].delta.content}
                        )
                        + "\n\n"
                    )
        except BaseException as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

        yield json.dumps({"type": "complete", "data": {"elapsed": time}}) + "\n\n"

    def _retrive_docs(self, query_m: str, k):
        results, distances = self.ball_tree.find(query_m, k, return_distances=True)
        print(results, distances)

        contents = []

        for name in results:
            content = load(os.path.join(self.folder_path, name + ".txt"))

            contents.append(name + "\n" + content)

        return [results, distances], contents
