# gh-push

A small keyboard-driven terminal UI for staging Git changes, creating commits, fetching, and pushing the current branch. It uses Python 3's standard library and the Git command-line client—no Python packages to install.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/Mandrusian/misc-os-tools/main/gh-push/install.sh | sh
```

This installs gh-push into `~/.local/bin`, or `$XDG_BIN_HOME` when set. Make sure that directory is on your `PATH`.

Requirements: Python 3, Git, and an interactive terminal. GitHub authentication is handled by your existing Git credential helper or SSH setup.

## Use

Run it from inside a repository, or pass a path explicitly:

```sh
gh-push
gh-push -C ~/src/my-project
```

## Keys

| Key | Action |
|---|---|
| `↑` / `↓`, `j` / `k` | Select a changed file |
| `Space` | Stage an unstaged file, or unstage a staged file |
| `d` | Show the selected file's diff |
| `a` | Confirm and stage all changes (`git add -A`) |
| `c` | Enter a commit message and commit staged changes |
| `p` | Confirm and push the current branch |
| `f` | Fetch from configured remotes |
| `l` | Show recent commits |
| `r` | Refresh status |
| `q` / `Esc` | Quit |

## Safety notes

- It never force-pushes and does not automatically pull, rebase, or merge.
- Pushing sends commits only. Unstaged and uncommitted changes are not included.
- Stage/unstage works at whole-file level. Unstaging a partially staged file removes its partial staging while leaving the working-tree edits intact.
- Files with unresolved merge conflicts cannot be staged through the UI; resolve them in an editor first.
- Commit, push, and fetch run with the terminal attached, so Git hooks and SSH credential prompts can work normally.
- If the current branch has no upstream, the first push targets `origin` (or the first configured remote) and sets the upstream.

The tool works with Git repositories in general; a GitHub remote is not mandatory. Review the diff before committing and confirm the destination before pushing.
