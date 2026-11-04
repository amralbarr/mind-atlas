#!/usr/bin/env python3
"""
Host-native companion to watch_and_link.py's Docker container: watches the
engineering/ vault for changes and, once things go quiet, commits and
pushes to GitHub -- using your real SSH agent / osxkeychain credential
helper already configured on this machine. Deliberately NOT run inside
Docker: an unattended container holding live push access to a GitHub
account is a meaningfully different (and worse) trust boundary than a
script running as you, on your own Mac, through your own already-trusted
git config.

Runs independently of the Docker linking watcher -- the two don't talk to
each other directly. This script's debounce window is set longer than the
Docker watcher's own debounce + sweep time, so by the time this script
commits, the linking pass has already finished and settled on disk.

Scope is deliberately narrow: `git add` only ever touches the engineering/
subtree, never the whole repo -- this repository also holds unrelated
personal directories (job-hunter-data/, marketing/, personal/, etc.) that
must never be swept into an automatic commit this script makes.

Usage:
    python3 git_sync.py                  # run in the foreground
    python3 git_sync.py --once           # one commit+push pass, then exit
"""
import argparse
import logging
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINEERING_ROOT = SCRIPT_DIR.parent          # .../engineering-handbook/engineering
REPO_ROOT = ENGINEERING_ROOT.parent           # .../engineering-handbook  (has .git)
TRACKED_SUBPATH = "engineering"               # only this subtree is ever staged

DEBOUNCE_SECONDS = 10.0  # intentionally longer than watch_and_link.py's own
                          # debounce (3s) + typical sweep runtime, so this
                          # only fires after the linking pass has settled
IGNORE_DIR_NAMES = {".git", "node_modules"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [git-sync] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, **kw)


def git_sync_once():
    status = run(["git", "status", "--porcelain", "--", TRACKED_SUBPATH])
    if status.returncode != 0:
        log.error("git status failed: %s", status.stderr.strip())
        return
    changed = [l for l in status.stdout.splitlines() if l.strip()]
    if not changed:
        log.info("no changes under %s/ -- nothing to commit", TRACKED_SUBPATH)
        return

    log.info("%d changed path(s) under %s/", len(changed), TRACKED_SUBPATH)

    add = run(["git", "add", "--", TRACKED_SUBPATH])
    if add.returncode != 0:
        log.error("git add failed: %s", add.stderr.strip())
        return

    files = [l[3:] for l in changed][:5]
    suffix = f" (+{len(changed) - 5} more)" if len(changed) > 5 else ""
    message = f"auto-sync: {', '.join(files)}{suffix}\n\n{datetime.now().isoformat(timespec='seconds')}"

    commit = run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        log.error("git commit failed: %s", commit.stderr.strip())
        return
    log.info("committed: %s", commit.stdout.strip().splitlines()[0] if commit.stdout else "ok")

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() or "main"
    push = run(["git", "push", "origin", branch])
    if push.returncode != 0:
        log.error("git push failed (commit was still made locally): %s", push.stderr.strip())
        return
    log.info("pushed to origin/%s", branch)


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.timer = None


state = State()


def schedule():
    with state.lock:
        if state.timer:
            state.timer.cancel()
        state.timer = threading.Timer(DEBOUNCE_SECONDS, git_sync_once)
        state.timer.daemon = True
        state.timer.start()


def is_ignored(path_str: str) -> bool:
    parts = Path(path_str).parts
    return any(p in IGNORE_DIR_NAMES for p in parts)


class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        if is_ignored(event.src_path):
            return
        schedule()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Run a single commit+push pass and exit.")
    args = ap.parse_args()

    if args.once:
        git_sync_once()
        return

    log.info("watching %s for changes (debounce=%ss), committing to repo at %s",
              ENGINEERING_ROOT, DEBOUNCE_SECONDS, REPO_ROOT)
    observer = Observer()
    observer.schedule(Handler(), str(ENGINEERING_ROOT), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
