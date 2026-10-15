from xml.etree import ElementTree

import pytest

from ebook_front_matter_builder.core import analyze


def test_roles_unicode_order_and_escaping():
    credits = [
        {"role": "translator", "name": "Zoë <Z>"},
        {"role": "author", "name": "李 & Co"},
        {"role": "editor", "name": "Éditor"},
        {"role": "author", "name": "Second"},
        {"role": "illustrator", "name": "Artist"},
    ]
    report = analyze({"title": "Book", "year": 2026, "credits": credits})
    for key in ("epub_xhtml", "kindle_html", "print_markdown"):
        output = report[key]
        assert output.index("Translator:") < output.index("Author:") < output.index("Editor:")
        assert "Illustrator: Artist" in output
    assert "Zoë &lt;Z&gt;" in report["epub_xhtml"]
    assert "李 &amp; Co, Second" in report["epub_xhtml"]
    ElementTree.fromstring(report["epub_xhtml"])


def test_legacy_profile_and_section_order():
    base = {"title": "Book", "year": 2026, "author": "Original"}
    legacy = analyze(base)
    assert "<p>Original</p>" in legacy["epub_xhtml"]
    report = analyze(
        {
            "title": "Book",
            "year": 2026,
            "profile": {"author": "Profile Author", "imprint": "Press"},
            "credits": [{"role": "author", "name": "Title Author"}],
            "section_order": ["copyright", "imprint", "title"],
        }
    )
    assert report["section_order"] == ["copyright", "imprint", "title"]
    assert "2026 Profile Author" in report["print_markdown"]
    assert "Author: Title Author" in report["print_markdown"]
    assert report["sections"] == 3


@pytest.mark.parametrize(
    "credits",
    [
        [],
        {},
        [None],
        [{"role": "unknown", "name": "A"}],
        [{"role": [], "name": "A"}],
        [{"role": "author", "name": ""}],
        [{"role": "author", "name": 1}],
        [{"role": "author", "name": "bad\x00"}],
        [{"role": "author", "name": "\ufffe"}],
        [{"role": "author", "name": "A", "extra": 1}],
    ],
)
def test_invalid_credits(credits):
    with pytest.raises((ValueError, TypeError)):
        analyze({"title": "Book", "year": 2026, "author": "A", "credits": credits})


def test_credit_without_author_needs_copyright_byline():
    with pytest.raises(ValueError, match="author"):
        analyze({"title": "Book", "year": 2026, "credits": [{"role": "editor", "name": "E"}]})
