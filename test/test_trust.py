# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 sol pbc

"""Tests for workspace trust functionality."""

import json

from hopper.claude import ensure_workspace_trusted


class TestEnsureWorkspaceTrusted:
    def test_creates_claude_json_if_missing(self, tmp_path, monkeypatch):
        """Creates ~/.claude.json with trust entry when it doesn't exist."""
        claude_json = tmp_path / ".claude.json"
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        target = str(tmp_path / "my-project")
        ensure_workspace_trusted(target)

        data = json.loads(claude_json.read_text())
        assert data["projects"][target]["hasTrustDialogAccepted"] is True
        assert data["projects"][target]["isTrusted"] is True

    def test_preserves_existing_data(self, tmp_path, monkeypatch):
        """Preserves existing entries in ~/.claude.json."""
        claude_json = tmp_path / ".claude.json"
        existing = {
            "env": {"MAX_THINKING_TOKENS": "10000"},
            "projects": {"/other/project": {"hasTrustDialogAccepted": True}},
        }
        claude_json.write_text(json.dumps(existing))
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        target = str(tmp_path / "new-project")
        ensure_workspace_trusted(target)

        data = json.loads(claude_json.read_text())
        assert data["env"]["MAX_THINKING_TOKENS"] == "10000"
        assert data["projects"]["/other/project"]["hasTrustDialogAccepted"] is True
        assert data["projects"][target]["hasTrustDialogAccepted"] is True

    def test_skips_if_already_trusted(self, tmp_path, monkeypatch):
        """No-ops if the directory is already trusted."""
        claude_json = tmp_path / ".claude.json"
        target = str(tmp_path / "project")
        existing = {"projects": {target: {"hasTrustDialogAccepted": True}}}
        claude_json.write_text(json.dumps(existing))
        mtime_before = claude_json.stat().st_mtime_ns
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        ensure_workspace_trusted(target)

        assert claude_json.stat().st_mtime_ns == mtime_before

    def test_handles_corrupt_json(self, tmp_path, monkeypatch):
        """Recovers from corrupt ~/.claude.json by starting fresh."""
        claude_json = tmp_path / ".claude.json"
        claude_json.write_text("{invalid json")
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        target = str(tmp_path / "project")
        ensure_workspace_trusted(target)

        data = json.loads(claude_json.read_text())
        assert data["projects"][target]["hasTrustDialogAccepted"] is True

    def test_resolves_symlinks(self, tmp_path, monkeypatch):
        """Resolves symlinks to the real path."""
        claude_json = tmp_path / ".claude.json"
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        real_dir = tmp_path / "real-project"
        real_dir.mkdir()
        link = tmp_path / "link-project"
        link.symlink_to(real_dir)

        ensure_workspace_trusted(str(link))

        data = json.loads(claude_json.read_text())
        assert str(real_dir) in data["projects"]
        assert str(link) not in data["projects"]

    def test_no_tmp_file_left_on_success(self, tmp_path, monkeypatch):
        """Temp file is cleaned up after successful write."""
        claude_json = tmp_path / ".claude.json"
        monkeypatch.setattr("hopper.claude.CLAUDE_JSON", claude_json)

        ensure_workspace_trusted(str(tmp_path / "project"))

        assert not (tmp_path / ".claude.json.tmp").exists()
