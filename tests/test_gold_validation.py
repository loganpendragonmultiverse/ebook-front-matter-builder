import json

import pytest

from ebook_front_matter_builder.cli import main
from ebook_front_matter_builder.core import analyze


def test_fresh_outputs_and_input_preservation(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(
        json.dumps({"title": "Harbor", "author": "Writer", "year": 2026}), encoding="utf-8"
    )
    before = source.read_bytes()
    output = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["project"] == "ebook-front-matter-builder"
    assert source.read_bytes() == before
    assert main([str(source), "--output", str(output)]) == 2
    assert "error:" in capsys.readouterr().err
    assert json.loads(output.read_text(encoding="utf-8"))["project"] == "ebook-front-matter-builder"
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_bytes() == before


def test_dangling_output_link_is_not_followed(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(
        json.dumps({"title": "Harbor", "author": "Writer", "year": 2026}), encoding="utf-8"
    )
    target = tmp_path / "must-not-be-created.txt"
    link = tmp_path / "report.json"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("creating symbolic links is not available to this user")
    assert main([str(source), "--output", str(link)]) == 2
    assert "error:" in capsys.readouterr().err
    assert link.is_symlink() and not target.exists()


def test_cli_io_and_json_errors(tmp_path, capsys):
    source = tmp_path / "bad.json"
    for contents in [b"{", b"\xff"]:
        source.write_bytes(contents)
        assert main([str(source)]) == 2
        assert "error:" in capsys.readouterr().err
    assert main([str(tmp_path / "missing.json")]) == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("field", ["title", "author"])
@pytest.mark.parametrize("value", ["   ", 42, True, {}, ["name"]])
def test_invalid_required_text_is_actionable(field, value, tmp_path, capsys):
    data = {"title": "Harbor", "author": "Writer", "year": 2026, field: value}
    with pytest.raises(ValueError, match=field):
        analyze(data)
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(source)]) == 2
    error = capsys.readouterr().err
    assert field in error and "Traceback" not in error


def test_invalid_profile_root_is_actionable(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text("[]", encoding="utf-8")
    profile = tmp_path / "profile.json"
    profile.write_text("{}", encoding="utf-8")
    assert main([str(source), "--profile", str(profile)]) == 2
    assert "JSON object" in capsys.readouterr().err


def test_default_rights_and_explicit_unicode_text():
    report = analyze({"title": " Harbor ", "author": " Writer ", "year": 2026})
    assert " Harbor " in report["print_markdown"]
    assert len(report["review_prompts"]) == 2
