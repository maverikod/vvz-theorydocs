"""
Minimal package sanity test.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import theorydocs


def test_version() -> None:
    """Package is importable and has __version__."""
    assert hasattr(theorydocs, "__version__")
    assert theorydocs.__version__ == "0.1.0"
