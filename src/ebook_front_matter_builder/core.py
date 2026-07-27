from __future__ import annotations

import json
from html import escape
from typing import Any

PROJECT = "ebook-front-matter-builder"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _front_matter(data: dict[str, Any]) -> dict[str, Any]:
    title = str(_require(data, "title"))
    author = str(_require(data, "author"))
    year = int(_require(data, "year"))
    rights = str(data.get("rights", "All rights reserved."))
    dedication = str(data.get("dedication", "")).strip()
    isbn = str(data.get("isbn", "")).strip()
    copyright_text = f"Copyright © {year} {author}. {rights}" + (f" ISBN {isbn}." if isbn else "")
    xhtml_sections = [
        f'<section epub:type="titlepage"><h1>{escape(title)}</h1><p>{escape(author)}</p></section>',
        f'<section epub:type="copyright-page"><p>{escape(copyright_text)}</p></section>',
    ]
    if dedication:
        xhtml_sections.append(
            f'<section epub:type="dedication"><p>{escape(dedication)}</p></section>'
        )
    xhtml = (
        '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><body>'
        + "".join(xhtml_sections)
        + "</body></html>"
    )
    kindle = (
        f"<h1>{escape(title)}</h1><p>{escape(author)}</p><hr><p>{escape(copyright_text)}</p>"
        + (f"<p><em>{escape(dedication)}</em></p>" if dedication else "")
    )
    print_text = f"# {title}\n\n{author}\n\n---\n\n{copyright_text}\n" + (
        f"\n---\n\n_{dedication}_\n" if dedication else ""
    )
    return {
        "epub_xhtml": xhtml,
        "kindle_html": kindle,
        "print_markdown": print_text,
        "sections": 2 + bool(dedication),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_front_matter(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
