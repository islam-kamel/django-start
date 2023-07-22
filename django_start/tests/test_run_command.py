import platform
import unittest
from django_start.utils.helpers import run_command


class TestRunCommand(unittest.TestCase):

    def test_run_command(self):
        result = run_command("python --version")
        self.assertIn(result.stdout.strip().split()[-1], platform.python_version())
        self.assertEqual(result.returncode, 0)

    def test_run_command_exception(self):
        result = run_command("python --version1")
        self.assertGreaterEqual(result.returncode, 1)
        self.assertIsNotNone(result.stderr)

