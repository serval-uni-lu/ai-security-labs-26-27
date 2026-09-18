"""Checks that preparing a lab preserves student work and starter notebooks."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_lab.py"
SPEC = importlib.util.spec_from_file_location("prepare_lab", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrepareLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name)
        self.starter = self.lab / "01_exercise.ipynb"
        self.original = b'{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}\n'
        self.starter.write_bytes(self.original)

    def test_copy_preserves_starter_and_notebook_content(self):
        copies = MODULE.prepare_lab(self.lab, "Ada", "Lovelace")
        self.assertEqual(copies, [self.lab / "01_exercise__submission_Ada_Lovelace.ipynb"])
        self.assertEqual(copies[0].read_bytes(), self.original)
        self.assertEqual(self.starter.read_bytes(), self.original)

    def test_rerun_preserves_work_even_after_starter_update(self):
        copy = MODULE.prepare_lab(self.lab, "Ada", "Lovelace")[0]
        copy.write_bytes(b"student answers")
        self.starter.write_bytes(b"updated teacher notebook")
        copies = MODULE.prepare_lab(self.lab, "Ada", "Lovelace")
        self.assertEqual(copies, [copy])
        self.assertEqual(copy.read_bytes(), b"student answers")
        self.assertEqual(len(list(self.lab.glob("*.ipynb"))), 2)

    def test_multiple_notebooks_and_existing_other_student_copy(self):
        second = self.lab / "02_exercise.ipynb"
        second.write_bytes(self.original)
        other = self.lab / "01_exercise__submission_Grace_Hopper.ipynb"
        other.write_bytes(b"other work")
        copies = MODULE.prepare_lab(self.lab, "Ada", "Lovelace")
        self.assertEqual(len(copies), 2)
        self.assertEqual(other.read_bytes(), b"other work")

    def test_missing_or_invalid_identity_creates_nothing(self):
        for first, family in [("", "Lovelace"), ("Ada", " "), ("../", "Lovelace")]:
            with self.subTest(first=first, family=family):
                with self.assertRaises(ValueError):
                    MODULE.prepare_lab(self.lab, first, family)
        self.assertEqual(list(self.lab.glob("*.ipynb")), [self.starter])

    def test_unicode_spaces_and_path_characters_stay_in_lab(self):
        copy = MODULE.prepare_lab(self.lab, "  Jose\u0301 / Anne  ", "O'Neil\\de Silva")[0]
        self.assertEqual(copy.name, "01_exercise__submission_José-Anne_O-Neil-de-Silva.ipynb")
        self.assertEqual(copy.parent, self.lab)

    def test_existing_symlink_is_not_followed_or_overwritten(self):
        target = self.lab / "answers.txt"
        target.write_bytes(b"student answers")
        copy = self.lab / "01_exercise__submission_Ada_Lovelace.ipynb"
        copy.symlink_to(target)
        MODULE.prepare_lab(self.lab, "Ada", "Lovelace")
        self.assertTrue(copy.is_symlink())
        self.assertEqual(target.read_bytes(), b"student answers")

    def test_no_templates_and_overlong_names_fail(self):
        with self.assertRaises(ValueError):
            MODULE.prepare_lab(self.lab, "A" * 250, "Lovelace")
        self.starter.unlink()
        with self.assertRaises(ValueError):
            MODULE.prepare_lab(self.lab, "Ada", "Lovelace")


if __name__ == "__main__":
    unittest.main()
