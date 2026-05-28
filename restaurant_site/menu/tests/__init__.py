import os
import unittest


def load_tests(loader, standard_tests, pattern):
    """Discover only test_*.py modules (skip ``models`` name clash with menu.models)."""
    start_dir = os.path.dirname(__file__)
    top_level = os.path.dirname(os.path.dirname(__file__))
    discovered = loader.discover(
        start_dir=start_dir,
        pattern='test_*.py',
        top_level_dir=top_level,
    )
    return discovered
