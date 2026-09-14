import os
import unittest
from unittest import mock

from web import __main__ as web_main


class _FakeApp:
    def __init__(self):
        self.run_calls = []

    def run(self, **kwargs):
        self.run_calls.append(kwargs)


class TestWebEntrypoint(unittest.TestCase):
    def test_main_defaults_to_localhost(self):
        fake_app = _FakeApp()
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(web_main, "create_app", return_value=fake_app):
                web_main.main()

        self.assertEqual(len(fake_app.run_calls), 1)
        self.assertEqual(fake_app.run_calls[0]["host"], "127.0.0.1")
        self.assertEqual(fake_app.run_calls[0]["port"], 8765)
        self.assertFalse(fake_app.run_calls[0]["debug"])


if __name__ == "__main__":
    unittest.main()
