import os
import shutil
from pathlib import Path

import requests
from pybloom_live import ScalableBloomFilter

from src.utils import from_current_file


def fetch_words(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    return []


def sanitize_wordlist(words):
    return sorted({w.strip().lower() for w in words if w.strip()})


class BloomModerator:
    def __init__(
        self,
        words_dir: Path = from_current_file("../data/bad_words"),
        force: bool = False,
        filename: str = "bad_words.txt",
        phrase_length: int = 5,
    ):
        self.filter = ScalableBloomFilter(
            initial_capacity=5000,
            error_rate=0.001,
            mode=ScalableBloomFilter.LARGE_SET_GROWTH,
        )
        self.filename = filename
        self.phrase_length = phrase_length

        self._words_dir = words_dir
        self._words_path = os.path.join(self._words_dir, filename)

        if force or not os.path.exists(self._words_path):
            print("Bad words is not found, creating new...")
            if force:
                try:
                    shutil.rmtree(self._words_dir)
                except FileNotFoundError:
                    pass
            os.makedirs(self._words_dir, exist_ok=True)
            self._build()
            print("Complete!")

        self._load_words()

    def _build(self):
        google_en = requests.get(
            "https://raw.githubusercontent.com/coffee-and-fun/google-profanity-words/main/data/en.txt"
        ).text.splitlines()
        ldnoobw_en = requests.get(
            "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en"
        ).text.splitlines()
        ldnoobw_rus = requests.get(
            "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/ru"
        ).text.splitlines()
        with open(self._words_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sanitize_wordlist(google_en + ldnoobw_en + ldnoobw_rus)))

    def _load_words(self):
        with open(self._words_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                self.filter.add(line)
                if "_" in line:
                    self.filter.add(line.replace("_", " "))

    def check_text(self, text: str) -> tuple[str, bool]:
        words = text.lower().split()

        for word in words:
            if word in self.filter:
                return (word, True)

        for i in range(len(words)):
            for j in range(1, self.phrase_length + 1):
                if i + j > len(words):
                    continue
                phrase = " ".join(words[i : i + j])
                if phrase in self.filter:
                    return (phrase, True)
        return ("", False)
