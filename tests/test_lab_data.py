"""Ensure failed downloads cannot become cached datasets."""

import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


SCRIPT = Path(__file__).resolve().parents[1] / "src/01_environment_setup/lab_data.py"
SPEC = importlib.util.spec_from_file_location("lab_data", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LabDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)
        self.directory_patch = patch.object(MODULE, "DATA_DIR", self.cache)
        self.directory_patch.start()
        self.addCleanup(self.directory_patch.stop)
        self.content = b"charged_off,issue_d\n0,2014-01-01\n1,2016-01-01\n"
        self.digest = hashlib.sha256(self.content).hexdigest()
        self.path = self.cache / "lcld_v2.csv"

    def test_download_and_reuse_valid_cache(self):
        with patch.object(MODULE, "urlopen", return_value=io.BytesIO(self.content)) as download:
            result = MODULE.ensure_file(self.path.name, self.digest)
            self.assertEqual(result.read_bytes(), self.content)
            self.assertEqual(MODULE.ensure_file(self.path.name, self.digest), result)
            download.assert_called_once()
        self.assertEqual(list(self.cache.iterdir()), [self.path])

    def test_cached_sharepoint_error_is_repaired(self):
        self.path.write_bytes(b"404 FILE NOT FOUND")
        with patch.object(MODULE, "urlopen", return_value=io.BytesIO(self.content)):
            MODULE.ensure_file(self.path.name, self.digest)
        self.assertEqual(self.path.read_bytes(), self.content)

    def test_http_error_does_not_create_cached_csv(self):
        error = HTTPError("https://example.invalid/data.csv", 404, "Not found", {}, None)
        with patch.object(MODULE, "urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Could not download"):
                MODULE.ensure_file(self.path.name, self.digest)
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_success_status_with_invalid_body_keeps_previous_file(self):
        previous = b"404 FILE NOT FOUND"
        self.path.write_bytes(previous)
        with patch.object(MODULE, "urlopen", return_value=io.BytesIO(b"<html>Sign in</html>")):
            with self.assertRaisesRegex(RuntimeError, "checksum"):
                MODULE.ensure_file(self.path.name, self.digest)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(self.cache.iterdir()), [self.path])

    def test_interrupted_download_does_not_leave_partial_file(self):
        with patch.object(MODULE, "urlopen") as download:
            download.return_value.__enter__.return_value.read.side_effect = [
                b"charged_off,issue_d\n", OSError("connection interrupted")
            ]
            with self.assertRaisesRegex(RuntimeError, "connection interrupted"):
                MODULE.ensure_file(self.path.name, self.digest)
        self.assertEqual(list(self.cache.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
