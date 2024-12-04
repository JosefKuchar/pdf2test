# PDF to Test

Create tests from lecture PDF slides using Google Gemini LLM

## Output format

The output format is a JSON file with the following structure:

```json
[
  {
    "question": "What is the capital of France?",
    "correct": ["Paris"],
    "incorrect": ["London", "Berlin", "Madrid"]
  },
  ...
]
```

## Prerequisites

- Python
- `requirements.txt` packages
- Gemini API key - create `.env` file with `KEY=your_key`

## Usage

```
python pdf2test.py --help
```
