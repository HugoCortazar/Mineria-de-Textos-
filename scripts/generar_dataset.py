"""Regenera el corpus desde Wikipedia y publica los dos CSV en una carpeta local."""

import argparse
import logging
from pathlib import Path

from esperanto_nlp.dataset import DATASET_CSV, SOURCES_CSV, collect_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=Path.cwd())
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    data, sources = collect_dataset()
    args.salida.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.salida / DATASET_CSV, sep=";", index=False, encoding="utf-8")
    sources.to_csv(args.salida / SOURCES_CSV, sep=";", index=False, encoding="utf-8")
    print(data["class"].value_counts().sort_index().to_string())
    print(f"Total: {len(data)} párrafos de {sources['article_id'].nunique()} artículos.")


if __name__ == "__main__":
    main()
