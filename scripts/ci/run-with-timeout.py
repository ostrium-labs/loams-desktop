#!/usr/bin/env python3
"""Bound a native test's execution separately from its Cargo build."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--diagnostics', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.timeout <= 0 or not args.command:
        parser.error('a positive timeout and command are required')
    args.diagnostics.mkdir(parents=True, exist_ok=True)
    log_path = args.diagnostics / 'test-output.log'
    with log_path.open('w+') as log:
        process = subprocess.Popen(args.command, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f'test PID {process.pid} timed out after {args.timeout}s', file=sys.stderr)
            try:
                with (args.diagnostics / 'processes.log').open('w') as diagnostics:
                    subprocess.run(['ps', '-axo', 'pid,ppid,stat,comm'], stdout=diagnostics,
                                   stderr=subprocess.STDOUT, timeout=5, check=False)
                if sys.platform == 'darwin':
                    subprocess.run(['/usr/bin/sample', str(process.pid), '3', '-file',
                                    str(args.diagnostics / 'sample.log')],
                                   timeout=8, check=False)
            except (OSError, subprocess.TimeoutExpired) as error:
                print(f'could not finish process diagnostics: {error}', file=sys.stderr)
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
            code = 124
        log.seek(0)
        sys.stdout.write(log.read())
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    raise SystemExit(main())
