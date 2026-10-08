"""Load the lab's LCLD files from Hugging Face instead of retired SharePoint links."""

import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen

from mlc.datasets.dataset import CsvDataSource
from mlc.datasets.dataset_factory import get_dataset as mlc_get_dataset


REVISION = "49cb6c10f28d17d6e9b70ccac27a7cf6e8a563c8"
BASE_URL = (
    "https://huggingface.co/datasets/serval-uni-lu/tabularbench/resolve/"
    + REVISION + "/lcld_v2/"
)
DATA_DIR = Path(__file__).resolve().parent / "data" / "mlc" / "lcld_v2"
FILES = {
    "lcld_v2.csv": "7fb27e2dc60555bc4f6d8d1a47cec44add5f740c9070ad82f3d8702451a19bd1",
    "lcld_v2_metadata.csv": "342cafb84f54d1458f231fabeb2ac9352674133826e4c53273f0a213adcc3ee6",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_file(filename, expected_hash):
    path = DATA_DIR / filename
    if path.is_file() and sha256(path) == expected_hash:
        return path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Downloading {} from Hugging Face...".format(filename), flush=True)
    temporary_path = None
    try:
        # Download to a separate file: errors and interrupted downloads must not
        # become a cached CSV, as they did in the original mlc downloader.
        with tempfile.NamedTemporaryFile(dir=DATA_DIR, suffix=".part", delete=False) as output:
            temporary_path = Path(output.name)
            with urlopen(BASE_URL + filename, timeout=60) as response:
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    output.write(chunk)
        if sha256(temporary_path) != expected_hash:
            raise ValueError("Downloaded file does not match the expected SHA-256 checksum.")
        temporary_path.replace(path)
    except (OSError, ValueError) as error:
        raise RuntimeError(
            "Could not download {}. Check your internet connection and retry. {}"
            .format(filename, error)
        ) from error
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return path


def get_dataset(name="lcld_v2_iid"):
    """Return the original mlc dataset with verified local data and metadata."""
    if name != "lcld_v2_iid":
        raise ValueError("This lab loader supports only lcld_v2_iid.")
    paths = {filename: ensure_file(filename, digest) for filename, digest in FILES.items()}
    dataset = mlc_get_dataset(name)
    dataset.data_source = CsvDataSource(str(paths["lcld_v2.csv"]))
    dataset.metadata_source = CsvDataSource(str(paths["lcld_v2_metadata.csv"]))
    return dataset


if __name__ == "__main__":
    get_dataset()
    print("LCLD data and metadata are ready. Restart the notebook kernel and run the cells again.")
