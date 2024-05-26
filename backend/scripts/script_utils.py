import os
import sys


def setup_path() -> None:
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, main_path)
