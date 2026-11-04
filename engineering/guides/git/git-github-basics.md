# Git & GitHub Basics

## What Is It?

Git is the industry-standard version control system. It tracks every change to every file, allows multiple people to work in parallel without overwriting each other, and maintains a full history of the project. GitHub is the cloud platform that hosts Git repositories and adds collaboration features — pull requests, code review, issues, and access control.

## Install Git

| OS | Method |
|---|---|
| Windows | Download from https://git-scm.com/download/win — use all defaults during install |
| Mac | `brew install git` or install Xcode Command Line Tools: `xcode-select --install` |
| Linux / WSL2 | `sudo apt install git` |

**Verify:**
```bash
git --version
```

## Install GitHub Desktop (Optional — GUI for Git)

Recommended for anyone less comfortable with command-line Git.

**Download:** https://desktop.github.com/

## Install GitHub CLI (Optional — Recommended)

Manage GitHub from the terminal — create pull requests, check status, open issues.

| OS | Method |
|---|---|
| Windows | `winget install GitHub.cli` |
| Mac | `brew install gh` |
| Linux / WSL2 | `sudo apt install gh` or see https://cli.github.com/ |

**Login:**
```bash
gh auth login
```

**Verify:**
```bash
gh --version
```

## First-Time Setup

Run these once after installing Git:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global core.autocrlf input   # Linux/Mac/WSL2
git config --global core.autocrlf true    # Windows only
git config --global init.defaultBranch main
```

## Clone a Repository

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

## Branching Convention

```
main                        ← stable code only — never push directly
├── feature/your-feature    ← one branch per task or feature
├── fix/bug-description     ← bug fix branches
└── docs/update-readme      ← documentation-only changes
```

## Daily Workflow

```bash
# 1. Always start by syncing with main
git pull origin main

# 2. Create a branch for your task
git checkout -b feature/your-task-name

# 3. Do your work, then stage changes
git add .                        # stage all changes
git add path/to/specific/file    # or stage specific files

# 4. Commit with a clear message
git commit -m "feat: add document chunking pipeline"

# 5. Push your branch
git push origin feature/your-task-name

# 6. Open a Pull Request on GitHub (or via CLI)
gh pr create --title "feat: add chunking pipeline" --body "Implements text chunking"
```

## Commit Message Convention

Use the format: `type: short description`

| Type | When to use |
|---|---|
| `feat:` | A new feature or capability |
| `fix:` | A bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code restructure without behavior change |
| `test:` | Adding or updating tests |
| `chore:` | Config, dependencies, tooling |

Examples:
```
feat: add permission-aware retrieval filter
fix: correct volume mount path in docker-compose
docs: update deployment guide with Terraform steps
chore: add .gitignore entries for terraform state
```

## What Must Never Be Committed

Always add a `.gitignore` to the repo root. At minimum include:

```gitignore
# Secrets
.env
*.env

# Terraform state
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS files
.DS_Store
Thumbs.db

# SSH private keys
*.pem
id_rsa
id_ed25519
```

## Useful Commands

```bash
git status                        # show changed files
git log --oneline --graph         # visual commit history
git diff                          # show unstaged changes
git stash                         # temporarily shelve changes
git stash pop                     # restore stashed changes
git checkout main                 # switch to main branch
git branch -d feature/old-branch  # delete a merged branch
git fetch origin                  # download remote changes without merging
```

## Related

- [Setting Up a GitHub Project](github-project-setup.md)
- [VS Code](../tools/vscode.md)
- [SSH Client Setup](../tools/ssh-client.md)
- [Development Workflow](../tools/development-workflow.md)
- [Local Development Tools](../tools/local-development-tools.md)
- [Git & GitHub Commands](../../commands/git.md)
