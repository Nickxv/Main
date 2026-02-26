from __future__ import annotations

import argparse
from pathlib import Path

from ai_smart_file_organizer.organizer import FilenameClassifier, monitor, organize_folder, semantic_search, undo_last


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Smart File Organizer")
    parser.add_argument("folder", type=Path, help="Folder to organize/search")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("organize", help="Organize files once")

    monitor_parser = sub.add_parser("monitor", help="Continuously monitor and organize")
    monitor_parser.add_argument("--interval", type=int, default=5)

    search_parser = sub.add_parser("search", help="Semantic search by filename meaning")
    search_parser.add_argument("query", type=str)
    search_parser.add_argument("--top-k", type=int, default=5)

    sub.add_parser("undo", help="Undo the last organization run")

    args = parser.parse_args()

    folder = args.folder.expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)

    if args.command == "organize":
        clf = FilenameClassifier()
        result = organize_folder(folder, clf)
        print(f"Moved: {len(result.moved)}, duplicates: {len(result.duplicates)}, skipped: {len(result.skipped)}")
    elif args.command == "search":
        results = semantic_search(folder, args.query, args.top_k)
        if not results:
            print("No matches found.")
            return
        for path, score in results:
            print(f"{score:.3f} - {path}")
    elif args.command == "undo":
        count = undo_last(folder)
        print(f"Reverted {count} file moves")
    elif args.command == "monitor":
        monitor(folder, args.interval)


if __name__ == "__main__":
    main()
