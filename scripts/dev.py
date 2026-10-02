"""Start the review window for development: install, serve the frontend, open the window.

    uv run poe dev [-- anonymize-ui options]      # Vite hot reload + real window
    uv run poe dev --built [-- options]           # build the page once, open it

Everything after `--` goes to `anonymize-ui`, e.g. `-- some.pdf --lang cs --ner`.
`--debug` is always on in the hot-reload mode (web inspector, debug logging; the
log holds document text, so use only synthetic documents).
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

FRONTEND = Path(__file__).resolve().parent.parent / "packages" / "ui" / "frontend"
# Must match `server` in vite.config.ts (strictPort, so it never moves).
VITE_HOST, VITE_PORT = "127.0.0.1", 5173
VITE_STARTUP_SECONDS = 30


def main(argv: list[str] | None = None) -> int:
    """Prepare the frontend and open the window; returns the window's exit code."""
    parser = argparse.ArgumentParser(description="Start the review window for development.")
    parser.add_argument("--built", action="store_true", help="build the page and open that")
    parser.add_argument(
        "--no-install", action="store_true", help="skip npm ci even if the lockfile changed"
    )
    parser.add_argument("window_args", nargs="*", help="passed to anonymize-ui")
    args, rest = parser.parse_known_args(argv)
    window_args = [*rest, *args.window_args]

    npm = shutil.which("npm")
    if npm is None:
        print("dev: npm not found; install Node.js to build the frontend", file=sys.stderr)
        return 1
    if not args.no_install:
        install_frontend_dependencies(npm)

    from anonymizer.ui.app import main as open_window

    if args.built:
        run([npm, "run", "build"])
        return open_window(window_args)

    server = start_vite(npm)
    try:
        wait_for_vite(server)
        return open_window(
            ["--dev-server", f"http://{VITE_HOST}:{VITE_PORT}", "--debug", *window_args]
        )
    finally:
        stop(server)


def run(command: list[str]) -> None:
    """Run a command in the frontend folder, failing if it does."""
    subprocess.run(command, cwd=FRONTEND, check=True)


def install_frontend_dependencies(npm: str) -> None:
    """Run `npm ci` when node_modules is missing or older than the lockfile."""
    marker = FRONTEND / "node_modules" / ".package-lock.json"
    lockfile = FRONTEND / "package-lock.json"
    if marker.is_file() and marker.stat().st_mtime >= lockfile.stat().st_mtime:
        return
    run([npm, "ci"])


def start_vite(npm: str) -> subprocess.Popen[bytes]:
    """Start the Vite dev server in the background."""
    if port_open():
        raise SystemExit(f"dev: port {VITE_PORT} is taken; stop the running Vite server first")
    # Own process group, so stopping it also stops Vite, which npm starts as a child.
    return subprocess.Popen([npm, "run", "dev"], cwd=FRONTEND, start_new_session=os.name == "posix")


def port_open() -> bool:
    """Whether something already listens on the Vite port."""
    with socket.socket() as probe:
        probe.settimeout(0.3)
        return probe.connect_ex((VITE_HOST, VITE_PORT)) == 0


def wait_for_vite(server: subprocess.Popen[bytes]) -> None:
    """Block until Vite answers, or exit if it dies or takes too long."""
    deadline = time.monotonic() + VITE_STARTUP_SECONDS
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise SystemExit("dev: Vite exited before it was ready")
        if port_open():
            return
        time.sleep(0.2)
    raise SystemExit(f"dev: Vite did not answer on port {VITE_PORT} within {VITE_STARTUP_SECONDS}s")


def stop(server: subprocess.Popen[bytes]) -> None:
    """Stop Vite and the processes npm started for it."""
    if server.poll() is not None:
        return
    if os.name == "posix":
        os.killpg(server.pid, signal.SIGTERM)
    else:
        server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
