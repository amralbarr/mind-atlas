#!/usr/bin/env python3
"""
Docker-service watcher: automatically runs link_sweep.py whenever a markdown
file is added or modified anywhere under the handbook -- no LLM/agent call
needed to trigger it.

- New file under concepts/ or overviews/ (a brand-new concept/overview doc):
    1. link_sweep.py --apply --file <path>      (link its own body against
                                                  every pre-existing concept)
    2. link_sweep.py --apply --term "<alias>"   for every alias on its H1
       (retroactively links every pre-existing file's bare mentions of it,
       now that a target finally exists for them)
- Modified existing file (anywhere in the scanned tree):
    link_sweep.py --apply --file <path>         (links any new bare mentions
                                                  the edit just introduced)
- Retitled concept file (its own H1 aliases changed): treated like a new
  file, but only for the alias(es) that are actually new.

Self-write-safe: link_sweep.py only ever wraps existing plain text in
`[text](url)` -- it never rewrites or removes anything else -- so its own
write can itself be observed as a later "modified" event. Each path's
content hash is recorded immediately after a sweep finishes writing it; an
incoming event for that path is skipped once its hash matches what's
recorded, instead of re-running the sweep in a loop.

Debounced per path (default 2s of quiet) so one editor save -- which can
fire several raw filesystem events -- triggers exactly one sweep.

Uses watchdog's PollingObserver rather than the native OS observer: a
Docker Desktop bind-mount on macOS does not always forward native
inotify/FSEvents reliably, and correctness here matters more than shaving
the few-second poll interval. Only SCAN_DIRS (the same tree link_sweep.py
itself scans) is watched -- not the whole mounted volume -- which keeps
each poll cycle's directory walk small and permanently avoids watching
scripts/link_sweep_report.md, link_sweep.py's own output file.
"""
import hashlib
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

sys.path.insert(0, str(Path(__file__).resolve().parent))
from link_sweep import ROOT, INDEX_DIRS, SCAN_DIRS, SCAN_EXTRA_FILES, build_index, extract_aliases  # noqa: E402

DEBOUNCE_SECONDS = float(os.environ.get("LINK_SWEEP_DEBOUNCE", "3.0"))
POLL_INTERVAL = float(os.environ.get("LINK_SWEEP_POLL_INTERVAL", "3.0"))
SCRIPT = str(Path(__file__).resolve().parent / "link_sweep.py")
REPAIR_SCRIPT = str(Path(__file__).resolve().parent / "link_repair.py")

# `scripts/` is deliberately never watched: it holds link_sweep.py's own
# report file (link_sweep_report.md), which gets rewritten on every sweep --
# watching it would make the watcher react to its own output. Scanning is
# restricted to exactly SCAN_DIRS + SCAN_EXTRA_FILES (the same tree
# link_sweep.py itself scans) instead of the whole mounted volume, which
# also keeps every poll cycle's directory walk small.
IGNORE_DIR_NAMES = {".git", "node_modules", "scripts"}
WATCH_TARGETS = [ROOT / d for d in SCAN_DIRS if (ROOT / d).exists()]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watch-and-link] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIR_NAMES for part in path.parts)


def is_indexed_dir(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in INDEX_DIRS


def content_hash(path: Path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, IsADirectoryError):
        return None


class State:
    def __init__(self):
        self.lock = threading.Lock()
        _, file_to_terms = build_index()
        self.known_aliases = {p.resolve(): set(a) for p, a in file_to_terms.items()}
        self.last_hash = {}
        self.timers = {}


state = State()


def run_sweep(extra_args):
    cmd = [sys.executable, SCRIPT, "--apply"] + extra_args
    log.info("running: %s", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    for line in (result.stdout + result.stderr).splitlines():
        log.info("  %s", line)


def run_repair(rel_path):
    # Fixes an EXISTING link whose relative path is wrong (e.g. written as
    # if the file were one directory level shallower/deeper than it
    # actually is) -- link_sweep.py never touches these, since it only
    # ever adds a NEW link to previously-bare text. Only auto-repairs when
    # exactly one file in the vault matches the broken link's basename;
    # anything ambiguous is left alone and only reported.
    cmd = [sys.executable, REPAIR_SCRIPT, "--apply", "--file", rel_path]
    log.info("running: %s", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    for line in (result.stdout + result.stderr).splitlines():
        log.info("  %s", line)


def process(path: Path):
    path = path.resolve()
    if is_ignored(path) or not path.is_file() or path.suffix != ".md":
        return

    new_hash = content_hash(path)
    if new_hash is None:
        return

    with state.lock:
        if state.last_hash.get(path) == new_hash:
            return  # nothing changed since our own last write (or no real change at all)

    rel = path.relative_to(ROOT)
    log.info("processing %s", rel)

    run_repair(str(rel))
    run_sweep(["--file", str(rel)])

    if is_indexed_dir(path):
        new_aliases = set(extract_aliases(path))
        with state.lock:
            old_aliases = state.known_aliases.get(path, set())
        fresh = new_aliases - old_aliases
        for alias in sorted(fresh):
            log.info("new/changed alias on %s -- backfilling other files for %r", rel, alias)
            run_sweep(["--term", alias])
        with state.lock:
            state.known_aliases[path] = new_aliases

    with state.lock:
        state.last_hash[path] = content_hash(path)  # re-read: the sweep may have just changed it


def schedule(path: Path):
    path = path.resolve()
    if is_ignored(path):
        return
    with state.lock:
        existing = state.timers.get(path)
        if existing:
            existing.cancel()
        t = threading.Timer(DEBOUNCE_SECONDS, process, args=(path,))
        t.daemon = True
        state.timers[path] = t
        t.start()


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            schedule(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            schedule(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory and str(event.dest_path).endswith(".md"):
            schedule(Path(event.dest_path))


def main():
    log.info("watching %d director(ies) + %d top-level file(s) under %s "
              "(debounce=%ss, poll=%ss)",
              len(WATCH_TARGETS), len(SCAN_EXTRA_FILES), ROOT, DEBOUNCE_SECONDS, POLL_INTERVAL)
    observer = PollingObserver(timeout=POLL_INTERVAL)
    handler = Handler()
    for target in WATCH_TARGETS:
        observer.schedule(handler, str(target), recursive=True)
    if SCAN_EXTRA_FILES:
        # Non-recursive watch on ROOT itself just to catch top-level files
        # like README.md, without re-descending into scripts/ or anything
        # else not already covered by WATCH_TARGETS.
        observer.schedule(handler, str(ROOT), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
