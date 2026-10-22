import importlib.util
import pathlib
import unittest
from importlib.machinery import SourceFileLoader

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "gh-push"
SPEC = importlib.util.spec_from_loader("gh_push", SourceFileLoader("gh_push", str(SCRIPT)))
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ParseStatusTests(unittest.TestCase):
    def test_parses_staged_unstaged_untracked_and_spaces(self):
        raw = b" M unstaged file.py\0M  staged.py\0?? new file.txt\0"
        got = MODULE.parse_porcelain(raw)
        by_path = {item.path: item for item in got}
        self.assertTrue(by_path["staged.py"].staged)
        self.assertFalse(by_path["unstaged file.py"].staged)
        self.assertTrue(by_path["new file.txt"].untracked)

    def test_skips_second_rename_path(self):
        raw = b"R  renamed.py\0old name.py\0 M keep.py\0"
        got = MODULE.parse_porcelain(raw)
        self.assertEqual({item.path for item in got}, {"renamed.py", "keep.py"})

    def test_conflict_detection(self):
        self.assertTrue(MODULE.Change("UU", "conflict.txt").conflicted)
        self.assertTrue(MODULE.Change("AA", "conflict.txt").conflicted)
        self.assertFalse(MODULE.Change(" M", "normal.txt").conflicted)

    def test_control_characters_are_visible(self):
        self.assertEqual(MODULE.safe_path("a\nb\t"), "a\\x0ab\\x09")


if __name__ == "__main__":
    unittest.main()
