"""Tests for the dependency-free stable-release metadata guard."""

from tools.release import verify_release_metadata as release


def _configure_metadata(monkeypatch, tmp_path, version: str, changelog: str) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[project]\n"
        f'version = "{version}"\n',
        encoding="utf-8",
    )
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(changelog, encoding="utf-8")
    monkeypatch.setattr(release, "PYPROJECT", pyproject)
    monkeypatch.setattr(release, "CHANGELOG", changelog_path)


def test_final_version_and_matching_tag_are_accepted(monkeypatch, tmp_path):
    _configure_metadata(monkeypatch, tmp_path, "0.2.0", "## 0.2.0 — Released\n")

    assert release.validate("v0.2.0") == []


def test_development_version_is_rejected(monkeypatch, tmp_path):
    _configure_metadata(monkeypatch, tmp_path, "0.2.0.dev0", "## 0.2.0.dev0 — Unreleased\n")

    errors = release.validate("v0.2.0.dev0")

    assert any("not a final" in error for error in errors)


def test_tag_and_changelog_mismatches_are_rejected(monkeypatch, tmp_path):
    _configure_metadata(monkeypatch, tmp_path, "0.2.0", "## 0.1.0 — Released\n")

    errors = release.validate("v0.2.1")

    assert any("does not match" in error for error in errors)
    assert any("CHANGELOG" in error for error in errors)
