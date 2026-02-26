from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


EXTENSION_MAP = {
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".csv": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".mp4": "Videos",
    ".mov": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".ipynb": "Code",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
}


TRAINING_SAMPLES = [
    ("resume cv profile portfolio", "Documents"),
    ("invoice bill receipt payment tax", "Finance"),
    ("notes assignment lesson homework lecture", "Study"),
    ("screenshot photo wallpaper image", "Images"),
    ("movie clip recording trailer", "Videos"),
    ("script source notebook project code", "Code"),
    ("backup archive bundle package", "Archives"),
]


@dataclass
class OrganizationResult:
    moved: list[tuple[Path, Path]]
    duplicates: list[Path]
    skipped: list[Path]


class FilenameClassifier:
    def __init__(self) -> None:
        self.label_tokens: dict[str, Counter[str]] = defaultdict(Counter)
        for text, label in TRAINING_SAMPLES:
            self.label_tokens[label].update(tokenize(text))

    def predict(self, filename: str) -> str:
        tokens = tokenize(Path(filename).stem)
        if not tokens:
            return "Others"
        best_label = "Others"
        best_score = 0
        for label, vocab in self.label_tokens.items():
            score = sum(vocab[t] for t in tokens)
            if score > best_score:
                best_score = score
                best_label = label
        return best_label if best_score > 0 else "Others"


def tokenize(text: str) -> list[str]:
    return [t for t in re.sub(r"[^a-z0-9]+", " ", text.lower()).split() if t]


def normalize_text(text: str) -> str:
    return " ".join(tokenize(text))


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def classify_file(path: Path, classifier: FilenameClassifier | None = None) -> str:
    ext_category = EXTENSION_MAP.get(path.suffix.lower())
    if ext_category:
        return ext_category
    if classifier:
        return classifier.predict(path.name)
    return "Others"


def smart_name(path: Path) -> str:
    stem = normalize_text(path.stem).replace(" ", "_") or "file"
    return f"{stem}{path.suffix.lower()}"


def ensure_unique(destination: Path) -> Path:
    if not destination.exists():
        return destination
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return destination.with_stem(f"{destination.stem}_{timestamp}")


def discover_files(folder: Path) -> Iterable[Path]:
    for p in folder.iterdir():
        if p.is_file():
            yield p


def organize_folder(folder: Path, classifier: FilenameClassifier | None = None) -> OrganizationResult:
    folder = folder.expanduser().resolve()
    hashes: dict[str, Path] = {}
    moved: list[tuple[Path, Path]] = []
    duplicates: list[Path] = []
    skipped: list[Path] = []

    managed_dirs = {"Documents", "Images", "Videos", "Code", "Archives", "Finance", "Study", "Others", "Duplicates"}

    for path in discover_files(folder):
        if path.name.startswith(".organizer_history"):
            continue
        file_hash = sha256(path)
        if file_hash in hashes:
            dup_dir = folder / "Duplicates"
            dup_dir.mkdir(exist_ok=True)
            destination = ensure_unique(dup_dir / path.name)
            shutil.move(str(path), str(destination))
            duplicates.append(destination)
            moved.append((path, destination))
            continue

        hashes[file_hash] = path
        category = classify_file(path, classifier)
        if category not in managed_dirs:
            category = "Others"
        destination_dir = folder / category
        destination_dir.mkdir(exist_ok=True)

        renamed = smart_name(path)
        destination = ensure_unique(destination_dir / renamed)
        if destination.resolve() == path.resolve():
            skipped.append(path)
            continue

        shutil.move(str(path), str(destination))
        moved.append((path, destination))

    _save_history(folder, moved)
    return OrganizationResult(moved=moved, duplicates=duplicates, skipped=skipped)


def _history_file(folder: Path) -> Path:
    return folder / ".organizer_history.json"


def _save_history(folder: Path, moves: list[tuple[Path, Path]]) -> None:
    history_path = _history_file(folder)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "moves": [{"src": str(src), "dst": str(dst)} for src, dst in moves],
    }
    entries = []
    if history_path.exists():
        entries = json.loads(history_path.read_text())
    entries.append(entry)
    history_path.write_text(json.dumps(entries, indent=2))


def undo_last(folder: Path) -> int:
    history_path = _history_file(folder)
    if not history_path.exists():
        return 0

    entries = json.loads(history_path.read_text())
    if not entries:
        return 0

    last = entries.pop()
    reverted = 0
    for move in reversed(last.get("moves", [])):
        dst = Path(move["dst"])
        src = Path(move["src"])
        if dst.exists() and not src.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(src))
            reverted += 1

    history_path.write_text(json.dumps(entries, indent=2))
    return reverted


def _tfidf_vectors(texts: list[str]) -> tuple[list[dict[str, float]], dict[str, float]]:
    tokenized = [tokenize(t) for t in texts]
    df = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    n_docs = len(texts)
    idf = {term: math.log((1 + n_docs) / (1 + freq)) + 1 for term, freq in df.items()}

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        vec = {term: (count / max_tf) * idf.get(term, 1.0) for term, count in tf.items()}
        vectors.append(vec)
    return vectors, idf


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a).intersection(b)
    dot = sum(a[k] * b[k] for k in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def semantic_search(folder: Path, query: str, top_k: int = 5) -> list[tuple[Path, float]]:
    files = [p for p in folder.rglob("*") if p.is_file() and not p.name.startswith(".organizer_history")]
    if not files:
        return []

    corpus = [normalize_text(p.stem) for p in files]
    vectors, idf = _tfidf_vectors(corpus)

    q_tokens = tokenize(query)
    q_tf = Counter(q_tokens)
    max_tf = max(q_tf.values()) if q_tf else 1
    q_vec = {term: (count / max_tf) * idf.get(term, 1.0) for term, count in q_tf.items()}

    scored = [(path, _cosine(q_vec, vec)) for path, vec in zip(files, vectors)]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(p, s) for p, s in scored[:top_k] if s > 0]


def monitor(folder: Path, interval_s: int = 5) -> None:
    classifier = FilenameClassifier()
    print(f"Monitoring {folder} every {interval_s}s. Press Ctrl+C to stop.")
    try:
        while True:
            result = organize_folder(folder, classifier)
            if result.moved:
                print(f"Organized {len(result.moved)} files at {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("Stopped monitoring.")
