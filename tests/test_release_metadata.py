"""Tests for the dependency-free stable-release metadata guard."""

from tools.release import verify_release_metadata as release


def _configure_metadata(
    monkeypatch,
    tmp_path,
    version: str,
    changelog: str,
    *,
    meson_version: str | None = None,
    with_release_notes: bool = True,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[project]\n"
        f'version = "{version}"\n',
        encoding="utf-8",
    )
    meson_build = tmp_path / "meson.build"
    meson_build.write_text(
        "project(\n"
        "  'pyspharm-ng',\n"
        f"  version: '{meson_version or version}',\n"
        ")\n",
        encoding="utf-8",
    )
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(changelog, encoding="utf-8")
    release_notes_directory = tmp_path / "docs" / "releases"
    if with_release_notes:
        release_notes_directory.mkdir(parents=True)
        (release_notes_directory / f"{version}.md").write_text(
            f"# {version}\n", encoding="utf-8"
        )
    monkeypatch.setattr(release, "PYPROJECT", pyproject)
    monkeypatch.setattr(release, "MESON_BUILD", meson_build)
    monkeypatch.setattr(release, "CHANGELOG", changelog_path)
    monkeypatch.setattr(release, "RELEASE_NOTES_DIRECTORY", release_notes_directory)


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


def test_missing_release_notes_are_rejected(monkeypatch, tmp_path):
    _configure_metadata(
        monkeypatch,
        tmp_path,
        "0.2.0",
        "## 0.2.0 — Released\n",
        with_release_notes=False,
    )

    errors = release.validate("v0.2.0")

    assert any("missing versioned release notes" in error for error in errors)


def test_mismatched_meson_version_is_rejected(monkeypatch, tmp_path):
    _configure_metadata(
        monkeypatch,
        tmp_path,
        "0.2.0",
        "## 0.2.0 — Released\n",
        meson_version="0.1.9",
    )

    errors = release.validate("v0.2.0")

    assert any("meson.build project version" in error for error in errors)
