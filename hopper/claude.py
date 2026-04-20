# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 sol pbc

"""Claude Code wrapper for hopper."""

import json
import logging
import os
import shlex
from pathlib import Path

from hopper.tmux import new_window, select_window

logger = logging.getLogger(__name__)

CLAUDE_JSON = Path.home() / ".claude.json"


def ensure_workspace_trusted(directory: str) -> None:
    """Pre-trust a directory in Claude Code's workspace trust store.

    Claude Code stores trust state in ~/.claude.json under
    projects.<path>.hasTrustDialogAccepted. It walks parent directories
    when checking, so trusting a parent covers subdirectories.
    """
    directory = os.path.realpath(directory)

    try:
        data = json.loads(CLAUDE_JSON.read_text()) if CLAUDE_JSON.exists() else {}
    except (json.JSONDecodeError, OSError):
        data = {}

    projects = data.setdefault("projects", {})
    entry = projects.setdefault(directory, {})

    if entry.get("hasTrustDialogAccepted"):
        return

    entry["hasTrustDialogAccepted"] = True
    entry["isTrusted"] = True

    tmp = CLAUDE_JSON.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2) + "\n")
        os.replace(tmp, CLAUDE_JSON)
        logger.debug(f"Trusted workspace: {directory}")
    except OSError as e:
        logger.warning(f"Failed to write workspace trust: {e}")
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def spawn_claude(
    lode_id: str,
    project_path: str | None = None,
    foreground: bool = False,
) -> str | None:
    """Spawn Claude via hopper in a new tmux window.

    Args:
        lode_id: The hopper lode ID.
        project_path: Working directory for the Claude session.
        foreground: If True, switch to the new window. Defaults to staying in current window.

    Returns:
        The tmux pane ID on success, None on failure.
    """
    path = os.environ.get("PATH", "/usr/bin:/bin")
    # Run through /bin/sh so PATH and || work regardless of tmux's default shell
    fail = "echo 'Failed. Press Enter to close.'; read"
    inner = f"export PATH={shlex.quote(path)}; hop process {lode_id} || {{ {fail}; }}"
    command = f"/bin/sh -c {shlex.quote(inner)}"
    return new_window(command, cwd=project_path, background=not foreground)


def switch_to_pane(pane_id: str) -> bool:
    """Switch to the tmux window containing the given pane.

    Args:
        pane_id: The tmux pane ID to switch to (e.g., "%1").

    Returns:
        True if successfully switched, False otherwise.
    """
    return select_window(pane_id)
