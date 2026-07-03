#!/usr/bin/env python3
"""Prepare UAE Golden Visa documents for portal upload."""

from __future__ import annotations

import argparse
from pathlib import Path

from golden_visa.config import load_config
from golden_visa.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Golden Visa upload documents.")
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config.yaml",
        help="Path to case-specific config (default: config.yaml)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    results = run_pipeline(config)

    print(f"Prepared documents in {config.ready}:")
    for name, size_kb in results:
        print(f"  {name:55s} {size_kb:7.1f} KB")


if __name__ == "__main__":
    main()
