from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from .api import create_app
from .config import Settings
from .evaluations import run_fixture_evaluation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enterprise RAG Evals command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)
    eval_parser = subparsers.add_parser("eval", help="run the versioned fixture evaluation")
    eval_parser.add_argument("--output", type=Path, default=None)
    serve_parser = subparsers.add_parser("serve", help="run the FastAPI service")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "eval":
        report = run_fixture_evaluation(Settings.from_env())
        payload = report.model_dump(mode="json")
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + "\n", encoding="utf-8")
        print(serialized)
        return 0 if report.passed else 1
    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
