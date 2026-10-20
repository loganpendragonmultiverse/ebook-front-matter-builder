# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Validate publishing fields and XHTML, add reusable publisher profiles and section ordering, and export direct XHTML/HTML/Markdown files.

## 1.2.1 acceptance

Run the full formatting, lint, strict typing, coverage and build checks above.
`tests/test_gold_validation.py` covers malformed input, successful fresh outputs,
existing files, dangling links where supported, and unchanged input bytes.
Install both built distributions outside the source tree and rerun the complete
suite against the installed package. Confirm all four handoff documents and the
license are present in the wheel/source distribution; exercise the installed CLI.
