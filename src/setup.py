import argparse
import os
import sys

import nltk

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from bloom import BloomModerator
from llm_indexer import LlmTreeIndexer
from src.inverted_index import InvertedIndex
from src.scrapper import ModulesIndex, ModulesScrapper
from src.spellcheck import NorvigSpellCorrector
from src.utils import load, save


def setup_project(force: bool, skip_scrap: bool):
    # Loading nltk data
    print("Start loading NLTK data...")
    nltk.download("stopwords")
    nltk.download("punkt_tab")
    print("Successfully loaded NLTK data!\n")

    # Scrap the data
    if not skip_scrap:
        print("Start scrapping...")
        modules_index = ModulesIndex()
        scrapper = ModulesScrapper(modules_index)
        scrapper.load(force=force)
        print("Successfully finished scrapping!\n")

    # Setup spell corrector
    print("Building spell corrector...")
    NorvigSpellCorrector(force=force)
    print("Successfully built spell corrector!\n")

    # Setup Bloom Filter
    print("Building Bloom Filter...")
    BloomModerator(force=force)
    print("Successfully built Bloom Filter!\n")

    # Setup Inverted Index
    print("Building Inverted Index...")
    InvertedIndex(force=force)
    print("Successfully built Inverted Index!\n")

    # Setup LLM Tree
    print("Building LLM Tree...")
    LlmTreeIndexer(force=force)
    print("Successfully built LLM Tree!\n")

    # Create sample .env
    if not os.path.exists(".env"):
        print("Creating sample .env file...")
        save(".env", load(".env.example"))
        print("Successfully created .env file...")

    print("Done!")


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Setup project")

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="rewrite existing data if already exists (default: False)",
    )

    parser.add_argument(
        "-s",
        "--skip-scrap",
        default=False,
        action=argparse.BooleanOptionalAction,
        dest="skip_scrap",
        help="should skip scrapping phase (default: False)",
    )

    namespace = parser.parse_args()
    (force, skip_scrap) = (namespace.force, namespace.skip_scrap)

    setup_project(force, skip_scrap)
