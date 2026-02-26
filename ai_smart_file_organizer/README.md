# AI Smart File Organizer

An AI-powered organizer for messy `Downloads`/`Desktop` folders.

## Features

### Core
- Extension-based categorization (`Documents`, `Images`, `Videos`, `Code`, `Archives`)
- Automatic folder creation and file moves
- Duplicate detection using SHA-256 hash
- Search utility

### Advanced
- Filename AI classifier (keyword-trained lightweight model)
- Smart auto-renaming to clean file names
- Semantic search (cosine similarity over vectorized filename text)
- Undo last organization run
- Real-time monitoring mode

## Install

```bash
cd ai_smart_file_organizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m ai_smart_file_organizer.cli ~/Downloads organize
python -m ai_smart_file_organizer.cli ~/Downloads search "show my resume"
python -m ai_smart_file_organizer.cli ~/Downloads undo
python -m ai_smart_file_organizer.cli ~/Downloads monitor --interval 10
```

## Architecture

1. Rule-based classifier by extension.
2. ML fallback classifier for names with unknown extensions.
3. Duplicate detector via SHA-256.
4. Operation history for undo.
5. Semantic retrieval using TF-IDF vectors.
