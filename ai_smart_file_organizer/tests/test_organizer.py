from pathlib import Path

from ai_smart_file_organizer.organizer import FilenameClassifier, organize_folder, semantic_search, undo_last


def write_file(path: Path, content: str) -> None:
    path.write_text(content)


def test_organize_duplicate_and_categories(tmp_path: Path) -> None:
    write_file(tmp_path / "resume_nishit_final.pdf", "resume")
    write_file(tmp_path / "family.jpg", "img")
    write_file(tmp_path / "copy1.txt", "same")
    write_file(tmp_path / "copy2.txt", "same")

    result = organize_folder(tmp_path, FilenameClassifier())

    assert len(result.moved) == 4
    assert (tmp_path / "Documents").exists()
    assert (tmp_path / "Images").exists()
    assert (tmp_path / "Duplicates").exists()


def test_search_and_undo(tmp_path: Path) -> None:
    write_file(tmp_path / "resume_nishit_final.pdf", "resume")
    organize_folder(tmp_path, FilenameClassifier())

    hits = semantic_search(tmp_path, "show my resume", top_k=3)
    assert hits

    reverted = undo_last(tmp_path)
    assert reverted >= 1
    assert (tmp_path / "resume_nishit_final.pdf").exists()
