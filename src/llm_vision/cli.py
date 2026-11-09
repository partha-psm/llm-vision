"""Command-line interface for image recognition and OCR."""

import argparse
import sys
from collections.abc import Sequence

import ollama

from llm_vision.recognition import DEFAULT_MODEL, analyze_image, analyze_pdf


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recognize objects and transcribe text in an image or PDF using Ollama."
    )
    parser.add_argument("file", help="Path to the image or PDF to analyze")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama vision model to use (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args(argv)

    try:
        analyze = analyze_pdf if args.file.lower().endswith(".pdf") else analyze_image
        print(analyze(args.file, model=args.model))
    except (FileNotFoundError, ValueError, ollama.ResponseError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0
