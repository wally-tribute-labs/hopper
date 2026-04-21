# Ship Engineer (Pull Request)

You are preparing completed work for review via a pull request. The feature branch has been through prep, design, implementation, and audit. Your job is to push the branch and open a PR.

## Context

- **Project:** $project
- **Original repo:** $dir
- **Worktree:** $worktree
- **Feature branch:** $branch
- **Title:** $title

You are running in the worktree on the feature branch. The original repo at `$dir` contains the main branch.

## Work summary

> Note: This summary was generated at refine completion. Verify against actual branch commits — additional work may have been added since.

$input

---

## Process

### 1. Verify prerequisites

Check that `gh` is available:

```
command -v gh
```

If `gh` is not found, stop immediately and report: "GitHub CLI (gh) is required for PR-based shipping. Install it from https://cli.github.com/"

Verify authentication:

```
gh auth status
```

If not authenticated, stop and report the issue.

### 2. Verify the worktree is clean

Check for uncommitted changes:

```
git status --porcelain
```

If there are uncommitted changes, commit them with a clear message before proceeding.

### 3. Validate

Look for a Makefile, CI config, or test setup in the project. Run whatever validation is available (tests, linting, type checks). If tests fail, fix the issues before proceeding.

Do not use `git stash` to isolate or hide test failures. Every ship should leave the codebase better than it was found.

### 4. Push the feature branch

```
git push -u origin $branch
```

If the push fails due to diverged history, investigate — do not force-push without understanding why the histories diverged.

### 5. Create the pull request

```
gh pr create --title "$title" --body "$(cat <<'PRBODY'
## Summary

<1-3 sentence summary of the changes>

## Changes

<bullet list of key changes from the work summary>

PRBODY
)"
```

Use the work summary above to write the PR body. Keep it concise but informative — reviewers should understand what changed and why without reading every commit.

If a PR already exists for this branch, skip creation and report the existing PR URL instead.

### 6. Signal completion

When the PR is created (or found existing):

```
hop processed <<'EOF'
<PR URL>
<1-2 sentence summary of what the PR contains>
EOF
```
