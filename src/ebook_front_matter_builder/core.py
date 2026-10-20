from __future__ import annotations

import json
from html import escape
from typing import Any
from xml.etree import ElementTree

PROJECT = "ebook-front-matter-builder"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _front_matter(data: dict[str, Any]) -> dict[str, Any]:
    profile = data.get("profile", {})
    if not isinstance(profile, dict) or any(
        key not in {"imprint", "rights", "isbn", "author"} for key in profile
    ):
        raise ValueError("profile supports imprint, rights, isbn and author only")
    data = {**profile, **data}
    title = _require(data, "title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be non-empty text")
    credits = data.get("credits")
    if credits is not None:
        if not isinstance(credits, list) or not credits:
            raise ValueError("credits must be a nonempty array")
        for index, credit in enumerate(credits):
            if not isinstance(credit, dict) or set(credit) != {"role", "name"}:
                raise ValueError(f"credits[{index}] requires role and name")
            if credit["role"] not in ("author", "editor", "translator", "illustrator"):
                raise ValueError(f"credits[{index}].role is unsupported")
            name = credit["name"]
            if (
                not isinstance(name, str)
                or not name.strip()
                or any(ord(char) < 32 and char not in "\t\n\r" for char in name)
            ):
                raise ValueError(f"credits[{index}].name must be XML-compatible text")
    if "author" not in data and credits:
        data["author"] = ", ".join(c["name"] for c in credits if c["role"] == "author")
    author = _require(data, "author")
    if not isinstance(author, str) or not author.strip():
        raise ValueError("author must be non-empty text")
    credit_lines = [f"{c['role'].title()}: {c['name']}" for c in credits] if credits else [author]
    credit_html = "".join(f"<p>{escape(line)}</p>" for line in credit_lines)
    year = _require(data, "year")
    if not isinstance(year, int) or isinstance(year, bool) or not 1 <= year <= 9999:
        raise ValueError("year must be an integer from 1 through 9999")
    for field in ("title", "author", "rights", "dedication", "isbn", "imprint"):
        value = data.get(field, "")
        if not isinstance(value, str) or any(
            ord(char) < 32 and char not in "\t\n\r" for char in value
        ):
            raise ValueError(f"{field} must be XML-compatible text")
    rights = data.get("rights", "All rights reserved.")
    dedication = data.get("dedication", "").strip()
    isbn = data.get("isbn", "").strip()
    imprint = data.get("imprint", "").strip()
    copyright_text = f"Copyright © {year} {author}. {rights}" + (f" ISBN {isbn}." if isbn else "")
    xhtml_sections = {
        "title": f'<section epub:type="titlepage"><h1>{escape(title)}</h1>{credit_html}</section>',
        "copyright": f'<section epub:type="copyright-page"><p>{escape(copyright_text)}</p></section>',
    }
    if dedication:
        xhtml_sections["dedication"] = (
            f'<section epub:type="dedication"><p>{escape(dedication)}</p></section>'
        )
    if imprint:
        xhtml_sections["imprint"] = f"<section><h2>Imprint</h2><p>{escape(imprint)}</p></section>"
    order = data.get("section_order", list(xhtml_sections))
    if (
        not isinstance(order, list)
        or not all(isinstance(key, str) for key in order)
        or len(order) != len(set(order))
        or set(order) != set(xhtml_sections)
    ):
        raise ValueError("section_order must list each available section exactly once")
    xhtml = (
        '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>'
        + escape(title)
        + "</title></head><body>"
        + "".join(xhtml_sections[key] for key in order)
        + "</body></html>"
    )
    try:
        ElementTree.fromstring(xhtml)
    except ElementTree.ParseError as exc:
        raise ValueError("input contains characters invalid in XHTML") from exc
    kindle = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'
        + escape(title)
        + "</title><body>"
        + "".join(
            xhtml_sections[key]
            .replace(' epub:type="titlepage"', "")
            .replace(' epub:type="copyright-page"', "")
            .replace(' epub:type="dedication"', "")
            for key in order
        )
        + "</body></html>"
    )
    markdown = {
        "title": f"# {title}\n\n" + "\n\n".join(credit_lines),
        "copyright": copyright_text,
        "dedication": dedication,
        "imprint": imprint,
    }
    print_text = "\n\n---\n\n".join(markdown[key] for key in order) + "\n"
    return {
        "epub_xhtml": xhtml,
        "kindle_html": kindle,
        "print_markdown": print_text,
        "sections": len(order),
        "section_order": order,
        "xhtml_well_formed": True,
        "review_prompts": (
            ["Confirm the default rights statement before publishing."]
            if not data.get("rights")
            else []
        )
        + (["No identifier supplied; confirm whether this edition needs one."] if not isbn else []),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be a JSON object")
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
