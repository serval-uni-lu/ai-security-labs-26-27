"""Create named notebook copies using LAB_FIRST_NAME and LAB_FAMILY_NAME."""

import os
from pathlib import Path
import re
import sys
import unicodedata


SUBMISSION_MARKER = "__submission_"


def filename_name(value):
    """Keep Unicode letters and digits, using hyphens between name parts."""
    normalized = unicodedata.normalize("NFC", value.strip())
    safe = "".join(char if char.isalnum() else "-" for char in normalized)
    return re.sub("-+", "-", safe).strip("-")


def prepare_lab(lab, first_name, family_name):
    first = filename_name(first_name)
    family = filename_name(family_name)
    if not first or not family:
        raise ValueError(
            "Fill in LAB_FIRST_NAME and LAB_FAMILY_NAME in the repository's .env "
            "file, save it, and run the preparation command again. "
            "Each name must contain at least one letter or digit."
        )

    templates = sorted(
        path for path in lab.glob("*.ipynb")
        if SUBMISSION_MARKER not in path.stem and path.is_file()
    )
    if not templates:
        raise ValueError("No starter notebooks found in this lab folder.")

    copies = [
        (template, template.with_name(
            "{}{}{}_{}.ipynb".format(template.stem, SUBMISSION_MARKER, first, family)
        ))
        for template in templates
    ]
    if any(len(copy.name.encode("utf-8")) > 240 for _, copy in copies):
        raise ValueError("The submission filename is too long; shorten the names in .env.")

    for template, copy in copies:
        content = template.read_bytes()
        try:
            # Exclusive creation also protects existing files and symlinks.
            with copy.open("xb") as output:
                output.write(content)
        except FileExistsError:
            print("Keeping existing work: {}".format(copy.name))
        else:
            print("Created: {}".format(copy.name))
    return [copy for _, copy in copies]


def main():
    lab = Path.cwd().resolve()
    root = Path(__file__).resolve().parent.parent
    if lab.parent != root / "src":
        print("Run this command from a lab folder, such as src/01_environment_setup.",
              file=sys.stderr)
        return 1
    try:
        prepare_lab(lab, os.environ.get("LAB_FIRST_NAME", ""),
                    os.environ.get("LAB_FAMILY_NAME", ""))
    except (ValueError, OSError) as error:
        print("Could not prepare lab: {}".format(error), file=sys.stderr)
        return 1
    print("Open the named submission notebook(s) in VS Code and work in those files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
