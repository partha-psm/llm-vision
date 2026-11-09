import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pymupdf
from PIL import Image

from llm_vision.cli import main
from llm_vision.recognition import DEFAULT_MODEL, analyze_image, analyze_pdf


class AnalyzeRecognitionTests(unittest.TestCase):
    def test_sends_image_to_default_model_and_returns_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "sample.png"
            Image.new("RGB", (2, 2), color="white").save(image_path)

            with patch(
                "llm_vision.recognition.ollama.generate",
                return_value=SimpleNamespace(response="  detected text  "),
            ) as generate:
                result = analyze_image(image_path)

        self.assertEqual(result, "detected text")
        self.assertEqual(generate.call_args.kwargs["model"], DEFAULT_MODEL)
        self.assertEqual(
            generate.call_args.kwargs["images"],
            [str(image_path.resolve())],
        )

    def test_rejects_missing_image(self) -> None:
        with self.assertRaises(FileNotFoundError):
            analyze_image("/no/such/image.png")

    def test_rejects_invalid_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "not-an-image.png"
            image_path.write_text("not an image")

            with self.assertRaises(ValueError):
                analyze_image(image_path)

    def test_analyzes_each_pdf_page_and_labels_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "sample.pdf"
            document = pymupdf.open()
            document.new_page()
            document.new_page()
            document.save(pdf_path)
            document.close()

            with patch(
                "llm_vision.recognition.ollama.generate",
                side_effect=[
                    SimpleNamespace(response="first page"),
                    SimpleNamespace(response="second page"),
                ],
            ) as generate:
                result = analyze_pdf(pdf_path)

        self.assertEqual(result, "Page 1:\nfirst page\n\nPage 2:\nsecond page")
        self.assertEqual(generate.call_count, 2)
        for call in generate.call_args_list:
            self.assertIsInstance(call.kwargs["images"][0], bytes)

    def test_rejects_invalid_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "not-a-pdf.pdf"
            pdf_path.write_text("not a PDF")

            with self.assertRaises(ValueError):
                analyze_pdf(pdf_path)

    def test_cli_routes_pdf_to_pdf_analyzer(self) -> None:
        with patch("llm_vision.cli.analyze_pdf", return_value="Page 1: result") as analyze:
            with patch("builtins.print"):
                result = main(["document.PDF"])

        self.assertEqual(result, 0)
        analyze.assert_called_once_with("document.PDF", model=DEFAULT_MODEL)


if __name__ == "__main__":
    unittest.main()
