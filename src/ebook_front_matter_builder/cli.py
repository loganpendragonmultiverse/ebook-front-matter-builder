from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic, reviewable report from explicit JSON input."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument(
        "--format", choices=("markdown", "json", "xhtml", "html", "md"), default="markdown"
    )
    parser.add_argument("--profile", type=Path, help="Local publisher profile JSON")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if args.profile:
            if not isinstance(data, dict):
                raise ValueError("input must be a JSON object")
            data["profile"] = json.loads(args.profile.read_text(encoding="utf-8"))
        report = analyze(data)
        if args.format in {"xhtml", "html", "md"}:
            rendered = report[
                {"xhtml": "epub_xhtml", "html": "kindle_html", "md": "print_markdown"}[args.format]
            ]
        else:
            rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
