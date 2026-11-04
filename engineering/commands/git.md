# Git & GitHub Commands

The everyday Git commands worth having memorized, plus the GitHub CLI (`gh`) commands that avoid switching to the browser. See [Git & GitHub Basics](../guides/git/git-github-basics.md) for the underlying concepts (working tree/staging/commit model, branching) this cheatsheet assumes.

## Setup & Configuration

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --list                          # show all config
```

## Everyday Workflow

```bash
git status                                 # what's changed, what's staged
git diff                                   # unstaged changes
git diff --staged                          # staged changes, not yet committed

git add <file>                             # stage a specific file
git add -p                                 # stage interactively, hunk by hunk
git add -u                                 # stage modifications/deletions, not new files

git commit -m "message"
git commit --amend                         # rewrite the most recent, NOT-YET-PUSHED commit

git push
git push -u origin <branch>                # first push of a new branch, sets upstream
git pull                                   # fetch + merge in one step
git fetch                                  # download remote changes without merging
```

## Branching

```bash
git branch                                 # list local branches
git branch -a                              # list local + remote branches
git checkout -b <new-branch>               # create and switch
git switch <branch>                        # switch (newer, clearer alternative to checkout)
git branch -d <branch>                     # delete a merged branch
git branch -D <branch>                     # force-delete an unmerged branch
```

## Inspecting History

```bash
git log --oneline --graph --all            # compact visual history across branches
git log -p <file>                          # full diff history for one file
git blame <file>                           # who last changed each line, and when
git show <commit-hash>                     # full diff of one commit
```

## Undoing Things

| Situation | Command |
|---|---|
| Discard unstaged changes to a file | `git restore <file>` |
| Unstage a file (keep the edits) | `git restore --staged <file>` |
| Undo the last commit, keep the changes staged | `git reset --soft HEAD~1` |
| Undo the last commit, discard the changes | `git reset --hard HEAD~1` (destructive) |
| Revert a commit that's already pushed | `git revert <commit-hash>` (safe — adds a new commit undoing it) |
| Recover a branch/commit you think you lost | `git reflog` (shows every HEAD movement, including "deleted" ones) |

`reset --hard` and `checkout -- <file>` discard work with no undo — always run `git status` first if there's any doubt about what's uncommitted.

## Stashing

```bash
git stash                                  # shelve uncommitted changes
git stash -u                               # also stash untracked files
git stash list
git stash pop                              # reapply the most recent stash and remove it
git stash apply                            # reapply without removing it from the stash list
```

## Merging & Rebasing

```bash
git merge <branch>                         # merge <branch> into the current branch
git rebase <branch>                        # replay current branch's commits on top of <branch>
git rebase -i HEAD~3                       # interactively edit/squash the last 3 commits

# During a conflict:
git status                                 # see which files need resolving
# ...edit the conflicted files...
git add <file>
git rebase --continue                      # or: git merge --continue
git rebase --abort                         # bail out entirely, back to pre-rebase state
```

See [Idempotency & Race Conditions](../concepts/programming/fundamentals/idempotency-and-race-conditions.md) for why `rebase` rewrites history (and is therefore unsafe on a branch others have already pulled) while `merge` doesn't.

## Remotes

```bash
git remote -v                              # list remotes and their URLs
git remote add origin <url>
git remote set-url origin <new-url>
```

## GitHub CLI (`gh`)

```bash
gh auth login                              # authenticate once per machine

gh repo clone owner/repo
gh repo create my-repo --public --source=. --push

gh pr create --title "..." --body "..."
gh pr list
gh pr view <number> --web                  # open a PR in the browser
gh pr checkout <number>                    # check out a PR's branch locally
gh pr merge <number> --squash

gh issue create --title "..." --body "..."
gh issue list

gh api repos/owner/repo/pulls/<number>/comments   # raw API access for anything the CLI doesn't wrap
```

See [GitHub Project Setup](../guides/git/github-project-setup.md) for a fuller `gh`-based repo bootstrap workflow.

## `.gitignore` Quick Reference

```gitignore
node_modules/
.env
*.log
dist/
__pycache__/
```

## Related

- [Git & GitHub Basics](../guides/git/git-github-basics.md)
- [GitHub Project Setup](../guides/git/github-project-setup.md)
- [Idempotency & Race Conditions](../concepts/programming/fundamentals/idempotency-and-race-conditions.md)
