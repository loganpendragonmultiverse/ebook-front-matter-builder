import json
from xml.etree import ElementTree

import pytest

from ebook_front_matter_builder.cli import main
from ebook_front_matter_builder.core import analyze


def test_profile_sections_direct_outputs_and_xml(tmp_path) -> None:
    data = {
        "title": "A & B",
        "author": "Writer",
        "year": 2026,
        "dedication": "For friends",
        "section_order": ["title", "imprint", "dedication", "copyright"],
    }
    profile = {
        "imprint": "Local Press",
        "rights": "Example rights text",
        "isbn": "Example identifier",
    }
    report = analyze({**data, "profile": profile})
    assert report["review_prompts"] == []
    assert report["sections"] == 4
    ElementTree.fromstring(report["epub_xhtml"])
    assert report["print_markdown"].index("Local Press") < report["print_markdown"].index(
        "For friends"
    )
    source, publisher = tmp_path / "input.json", tmp_path / "profile.json"
    source.write_text(json.dumps(data))
    publisher.write_text(json.dumps(profile))
    for extension, field in (
        ("xhtml", "epub_xhtml"),
        ("html", "kindle_html"),
        ("md", "print_markdown"),
    ):
        output = tmp_path / f"front.{extension}"
        assert (
            main(
                [
                    str(source),
                    "--profile",
                    str(publisher),
                    "--format",
                    extension,
                    "--output",
                    str(output),
                ]
            )
            == 0
        )
        assert output.read_text() == report[field]


@pytest.mark.parametrize(
    "patch",
    [
        {"title": []},
        {"year": True},
        {"year": 10000},
        {"rights": "bad\x00"},
        {"profile": []},
        {"profile": {"unknown": "bad"}},
        {"section_order": ["title", "title"]},
        {"title": "\ufffe"},
    ],
)
def test_invalid_publishing_fields(patch) -> None:
    with pytest.raises((ValueError, TypeError)):
        analyze({"title": "A", "author": "B", "year": 2026, **patch})
