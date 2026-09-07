# Development contract

Generate EPUB XHTML, Kindle HTML, and print-ready Markdown front matter from one form.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.1.0 improvement session

Validate publishing fields and XHTML, add reusable publisher profiles and section ordering, and export direct XHTML/HTML/Markdown files.

Use `--format xhtml`, `html`, or `md` for direct documents instead of a report wrapper. `--profile publisher.json` loads local defaults for imprint, rights, isbn and author; explicit book input wins. `section_order` must list every available section exactly once (title, copyright, plus dedication/imprint when supplied). XHTML is checked for well-formed XML, not EPUB/store certification. Review prompts identify a defaulted rights statement or missing identifier; they do not determine legal sufficiency or identifier requirements. No publisher lookup or submission occurs.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
