import os
import re
import string
from collections import Counter, defaultdict
from pathlib import Path

from nltk.corpus import stopwords
from tqdm import tqdm

from src.utils import from_current_file, load_json, remove_path, save_json


class NorvigSpellCorrector:
    letters = "abcdefghijklmnopqrstuvwxyz"
    _stop_words = set(stopwords.words("english"))

    def __init__(
        self,
        spell_dir: Path = from_current_file("../data/spell_directory"),
        documents_dir: Path = from_current_file(
            "../data/scrapped/class_data_function__1_1"
        ),
        max_edits: int = 2,
        save_distances: bool = False,
        force: bool = False,
    ):
        self._max_edits = max_edits
        self.save_distances = save_distances

        self._spell_dir = spell_dir
        self._documents_dir = documents_dir

        self._counter_path = os.path.join(self._spell_dir, "counter.json")
        self._settings_path = os.path.join(self._spell_dir, "settings.json")

        if force or not os.path.exists(self._spell_dir):
            remove_path(self._spell_dir)
            print("Spell index is not found, creating new...")
            os.mkdir(path=self._spell_dir)
            self.build_index()
            print("Complete!")

        self.load_index()

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def filter_stopwords(self, words: list[str]) -> list[str]:
        return [word for word in words if word not in self._stop_words]

    def generate_edits(self, word: str) -> set[str]:
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in self.letters]
        inserts = [L + c + R for L, R in splits for c in self.letters]
        return set(deletes + transposes + replaces + inserts)

    def build_index(self):
        # Words counter
        words_counter = Counter(
            self.filter_stopwords(
                self.tokenize(
                    " ".join(
                        [
                            re.sub(
                                r"[^\x00-\x7F]+",
                                " ",
                                open(str(path), encoding="utf-8")
                                .read()
                                .lower()
                                .replace("\n", " "),
                            )
                            for path in Path(self._documents_dir).rglob("*.txt")
                        ]
                    )
                )
            )
        )
        save_json(self._counter_path, words_counter)
        settings = {"total": words_counter.total(), "max_edits": self._max_edits}
        save_json(self._settings_path, settings)

        if self.save_distances:
            edit_dicts = [defaultdict(set) for _ in range(self._max_edits)]
            for word in tqdm(words_counter):
                edits = {word}
                for i in range(self._max_edits):
                    temp_edits: set[str] = set()
                    for w in edits:
                        temp_edits.update(self.generate_edits(w))
                        edit_dicts[i][w].add(word)
                    edits = temp_edits

            for idx in range(self._max_edits):
                save_json(
                    os.path.join(self._spell_dir, f"distance{idx + 1}"), edit_dicts[idx]
                )

    def load_index(self):
        self.settings = load_json(self._settings_path)
        if self.save_distances and self.settings["max_edits"] != self._max_edits:
            raise RuntimeError("'max_edits' does not match!")
        self.total_sum = self.settings["total"]
        self.words_counter = Counter(load_json(self._counter_path))

        if self.save_distances:
            self.distance_dicts = []
            for idx in range(self._max_edits):
                self.distance_dicts.append(
                    load_json(os.path.join(self._spell_dir, f"distance{idx + 1}"))
                )

    def word_probability(self, word: str) -> float:
        return self.words_counter[word] / self.total_sum

    def filter_known(self, words: list[str] | set[str]) -> set[str]:
        return set(w for w in words if w in self.words_counter)

    def _word_candidates_saved(self, word: str) -> list[str]:
        if self.save_distances:
            return self._word_candidates_saved(word)
        for i in range(self._max_edits):
            knowns = self.distance_dicts[i].get(word, None)
            if knowns is not None:
                return knowns
        return [word]

    def word_candidates(self, word: str) -> list[str]:
        if self.save_distances:
            return self._word_candidates_saved(word)

        edits = {word}
        for _ in range(self._max_edits):
            current_edits: set[str] = set()
            for w in edits:
                current_edits.update(self.generate_edits(w))
            knowns = self.filter_known(current_edits)
            if len(knowns) > 0:
                return list(knowns)
            edits = current_edits
        return [word]

    def spell_correction_word(self, word: str) -> str:
        if word in self.words_counter:
            return word
        return max(self.word_candidates(word), key=self.word_probability)

    def spell_correction(self, text: str, skip_stop_words: bool = False) -> str:
        tokens = self.tokenize(text.lower())
        if len(tokens) == 1:
            return self.spell_correction_word(tokens[0])
        corrected = ""
        for token in tokens:
            if token in string.punctuation:
                if len(corrected) > 0 and corrected[-1] == " ":
                    corrected = corrected[:-1]
                corrected = corrected + token + " "
                continue
            if token in self._stop_words:
                if skip_stop_words:
                    continue
                corrected = corrected + token + " "
                continue
            corrected = corrected + self.spell_correction_word(token) + " "
        return corrected.strip()
