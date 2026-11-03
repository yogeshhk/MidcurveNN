"""Reverse the moves recorded in 08_moves_done.csv (newest first).

    python 08_rollback.py --dry-run     # print what would move, check sources/destinations, change nothing
    python 08_rollback.py               # perform the moves back

Scope and limits:
  - It restores LOCATIONS only (new_path -> old_path). Edits made to file contents during the reorganisation
    (imports, path arithmetic, run.py, READMEs, .gitignore) are not undone here; use git to restore those.
  - Files created inside a moved folder after the move (for example enhanced/, README.md, notebook.ipynb) travel
    with the folder. Empty directories that were removed (models/, runs/, runs_smoke/, testing/, ...) are re-created
    by the move itself. Nothing is deleted.
  - Stops at the first conflict (destination already exists or source missing) and reports it.
"""
import argparse
import csv
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
DONE = os.path.join(HERE, "08_moves_done.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    with open(DONE, newline="") as f:
        rows = list(csv.DictReader(f))
    print("%d recorded moves; %s" % (len(rows), "DRY RUN" if a.dry_run else "EXECUTING"))
    problems = 0
    for r in reversed(rows):
        new = os.path.join(SRC, r["new_path"])
        old = os.path.join(SRC, r["old_path"])
        if not os.path.exists(new):
            print("CONFLICT source missing:", r["new_path"])
            problems += 1
            if not a.dry_run:
                break
            continue
        if os.path.exists(old):
            print("CONFLICT destination exists:", r["old_path"])
            problems += 1
            if not a.dry_run:
                break
            continue
        print("%s -> %s" % (r["new_path"], r["old_path"]))
        if not a.dry_run:
            os.makedirs(os.path.dirname(old), exist_ok=True)
            shutil.move(new, old)
    print("done; conflicts: %d" % problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
