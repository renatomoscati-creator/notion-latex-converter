# Notion LaTeX Converter

A local tool that converts typed math, formulas, and images into Notion-compatible LaTeX with one-click copy.

## Setup

1. **Python 3.11+** required
2. Create a virtual environment:
   ```bash
   python -m venv venv && source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
5. Run:
   ```bash
   streamlit run app.py
   ```
6. Open `http://localhost:8501`

## Usage

| Tab | What it does |
|-----|-------------|
| **Text / Formula** | Type natural language or a formula, click Convert |
| **Image Upload** | Upload PNG/JPG of a printed or handwritten math expression |
| **Paste from Clipboard** | Paste a screenshot directly from your clipboard |

- Toggle **Block** (`$$ ... $$`) vs **Inline** (`\( ... \)`) output format
- Use the **copy icon** on the LaTeX output box to copy to clipboard
- Paste directly into a Notion equation block
- Edit the output in the text area before copying if needed
- A **⚠️ low confidence warning** appears when the result may be inaccurate

## Architecture

```
app.py                    # Streamlit UI (no business logic)
converter/
  llm_client.py           # Anthropic API calls (text + vision)
  normalizer.py           # Notion LaTeX compatibility rules
  image_processor.py      # Pillow image preprocessing
  confidence.py           # Output quality scoring
tests/                    # pytest test suite (40 tests)
```

## Running Tests

```bash
pytest tests/ -v
```
