import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from checks.documentation import load_documentation_entries


class DocumentationParserTests(unittest.TestCase):
    def test_missing_config_file_returns_no_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.conf"

            self.assertEqual(load_documentation_entries(path), [])

    def test_empty_config_file_returns_no_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "docs.conf"
            path.write_text("", encoding="utf-8")

            self.assertEqual(load_documentation_entries(path), [])

    def test_empty_lines_and_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text("documentation", encoding="utf-8")
            config = root / "docs.conf"
            config.write_text(
                f"\n# comment\n   # indented comment\nOverview | {document}\n",
                encoding="utf-8",
            )

            self.assertEqual(
                load_documentation_entries(config),
                [("Overview", str(document))],
            )

    def test_invalid_entries_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text("documentation", encoding="utf-8")
            config = root / "docs.conf"
            config.write_text(
                "Missing separator\n"
                " | /tmp/documentation.md\n"
                "Overview | \n"
                "Too | many | separators\n"
                "Relative | README.md\n"
                f"Valid | {document}\n",
                encoding="utf-8",
            )

            self.assertEqual(
                load_documentation_entries(config),
                [("Valid", str(document))],
            )

    def test_nonexistent_documentation_paths_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.md"
            config = root / "docs.conf"
            config.write_text(f"Missing | {missing}\n", encoding="utf-8")

            self.assertEqual(load_documentation_entries(config), [])

    def test_document_does_not_need_to_be_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text("documentation", encoding="utf-8")
            document.chmod(0o000)
            config = root / "docs.conf"
            config.write_text(f"Overview | {document}\n", encoding="utf-8")

            self.assertEqual(
                load_documentation_entries(config),
                [("Overview", str(document))],
            )

    def test_inaccessible_path_does_not_hide_valid_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            inaccessible = Path("/restricted/documentation.md")
            config = root / "docs.conf"
            config.write_text(
                f"Overview | {document}\nRestricted | {inaccessible}\n",
                encoding="utf-8",
            )

            def check_file(path):
                if path == inaccessible:
                    raise PermissionError("permission denied")
                return path == document

            with patch(
                "checks.documentation.Path.is_file",
                autospec=True,
                side_effect=check_file,
            ):
                self.assertEqual(
                    load_documentation_entries(config),
                    [("Overview", str(document))],
                )


if __name__ == "__main__":
    unittest.main()
