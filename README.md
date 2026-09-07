# Ebook Front-Matter Builder

[![CI](https://github.com/loganpendragonmultiverse/ebook-front-matter-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/ebook-front-matter-builder/actions/workflows/ci.yml)

Generate EPUB XHTML, Kindle HTML, and print-ready Markdown front matter from one form. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
ebook-front-matter examples/sample.json
ebook-front-matter examples/sample.json --format json --output report.json
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

The builder creates front-matter fragments, not a complete EPUB or print interior. Publishers remain responsible for identifiers, rights, validation, and house style.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.1.0: reviewed improvements

Validate publishing fields and XHTML, add reusable publisher profiles and section ordering, and export direct XHTML/HTML/Markdown files.

```bash
ebook-front-matter examples/sample.json --format xhtml --output front.xhtml
```

Use `--format xhtml`, `html`, or `md` for direct documents instead of a report wrapper. `--profile publisher.json` loads local defaults for imprint, rights, isbn and author; explicit book input wins. `section_order` must list every available section exactly once (title, copyright, plus dedication/imprint when supplied). XHTML is checked for well-formed XML, not EPUB/store certification. Review prompts identify a defaulted rights statement or missing identifier; they do not determine legal sufficiency or identifier requirements. No publisher lookup or submission occurs.
