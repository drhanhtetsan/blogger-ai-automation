from __future__ import annotations

import argparse
import json

from .config import load_settings
from .job_runner import run_batch, sync_comments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WordPress AI automation runner")
    parser.add_argument("--env", default="dev", help="Environment name (dev or prod)")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Generate and publish posts from topic queue")
    sub.add_parser("sync-comments", help="Sync WordPress comments to CSV")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_settings(environment=args.env)
    if args.command == "run":
        summary = run_batch(settings)
        print(json.dumps(summary))
        return 0

    if args.command == "sync-comments":
        total = sync_comments(settings)
        print(json.dumps({"synced_comments": total}))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
