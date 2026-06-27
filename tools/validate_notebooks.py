#!/usr/bin/env python3
"""Execute every workshop notebook without modifying the distributed copies."""

from __future__ import annotations

import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]


def execute_notebook(path_string: str) -> tuple[str, float]:
    path = Path(path_string)
    started = time.monotonic()
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    client.execute()
    return str(path.relative_to(ROOT)), time.monotonic() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    notebooks = sorted(ROOT.glob("session-*/notebooks/*.ipynb"))
    failures: list[tuple[str, str]] = []

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(execute_notebook, str(path)): path for path in notebooks}
        for future in as_completed(pending):
            path = pending[future]
            try:
                relative, seconds = future.result()
                print(f"PASS  {relative}  {seconds:.1f}s", flush=True)
            except Exception as exc:
                failures.append((str(path.relative_to(ROOT)), repr(exc)))
                print(f"FAIL  {path.relative_to(ROOT)}  {exc!r}", flush=True)

    if failures:
        print("\nFailures:")
        for path, error in failures:
            print(f"- {path}: {error}")
        raise SystemExit(1)
    print(f"\nAll {len(notebooks)} notebooks executed successfully.")


if __name__ == "__main__":
    main()
