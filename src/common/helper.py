import sys
from pathlib import Path

def get_resource_path(relative_path: Path | str) -> Path:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys,"_MEIPASS"):
        base_path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        main_file = sys.modules["__main__"].__file__
        base_path = Path(main_file or ".").resolve().parent

    return base_path / relative_path
