import unittest

import stactools.nalcms


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.nalcms.__version__)
