# llm-vision

Recognize objects and extract text from images and PDF pages using the Gemma 4
E2B vision model through Ollama.

## Project layout

```text
.
├── pyproject.toml
├── src/
│   └── llm_vision/
└── tests/
```

Application code belongs in `src/llm_vision/`; tests belong in `tests/`.

## Setup

1. Install and start [Ollama](https://ollama.com/).
2. Download the vision model:

   ```sh
   ollama pull gemma4:e2b
   ```

3. Install this package in the project's virtual environment:

   ```sh
   python -m pip install -e .
   ```

## Use

Analyze an image with the default `gemma4:e2b` model:

```sh
llm-vision path/to/image.jpg
```

Analyze every page of a PDF:

```sh
llm-vision path/to/document.pdf
```

Or specify a different Ollama vision model:

```sh
llm-vision path/to/document.pdf --model gemma4:e2b
```

PDF pages are rendered locally and analyzed one at a time. Results are labeled
by page. The program reports visible objects and their relationships, followed
by readable text transcribed from the image or page. Ollama must be running and
the selected model must already be available locally.

## Test

```sh
python -m unittest discover -s tests
```
