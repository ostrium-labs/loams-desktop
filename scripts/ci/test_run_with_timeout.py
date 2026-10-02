from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TimeoutTests(unittest.TestCase):
    def run_command(self, source):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name('run-with-timeout.py')),
                 '--timeout', '2', '--diagnostics', directory,
                 sys.executable, '-u', '-c', source],
                capture_output=True, text=True, timeout=30,
            )
            logs = list(Path(directory).glob('*.log'))
            return result, ''.join(path.read_text() for path in logs)

    def test_preserves_success_and_failure(self):
        result, _ = self.run_command("print('PASS')")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS', result.stdout)
        result, _ = self.run_command("raise SystemExit(7)")
        self.assertEqual(result.returncode, 7)

    def test_hang_fails_and_retains_output(self):
        result, logs = self.run_command("import time; print('before hang'); time.sleep(60)")
        self.assertEqual(result.returncode, 124, result.stderr)
        self.assertIn('before hang', logs)
        self.assertIn('timed out', result.stderr)


if __name__ == '__main__':
    unittest.main()
