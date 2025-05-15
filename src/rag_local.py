import json
import os
import time
from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from src.rag import get_prompt
from src.utils import from_current_file, load


class RetrievalAugmentedGenerationLocal:
    folder_path = from_current_file("../data/scrapped/class_data_function__1_1")
    max_tokens: int = 256

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def generate_stream(
        self, query: str, model_name: str, scored_docs: list[tuple[str, float]]
    ):
        start = time.time()
        source_names = [x for x, _ in scored_docs]
        sources = self._retrieve_docs(source_names)

        prompt = get_prompt(query, sources)

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
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            model.eval()

            model = model.to(self.device)

            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(self.device)

            streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)

            generation_kwargs = {
                "input_ids": input_ids,
                "streamer": streamer,
                "max_new_tokens": self.max_tokens,
                "pad_token_id": tokenizer.eos_token_id,
            }

            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            for new_token in streamer:
                yield (json.dumps({"type": "chunk", "data": new_token}) + "\n\n")

        except BaseException as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

        yield (json.dumps({"type": "complete", "data": time.time() - start}) + "\n\n")

    def _retrieve_docs(self, source_names: list[str]) -> list[str]:
        contents = []

        for name in source_names:
            content = load(os.path.join(self.folder_path, name + ".txt"))

            contents.append(name + "\n" + content)

        return contents
