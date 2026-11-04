# Setting Up a GitHub Project

## Step 1 — Create the Repository (One Person Only)

1. Go to https://github.com and sign in
2. Click **+** (top right) → **New repository**
3. Fill in:

| Field | Value |
|---|---|
| Repository name | `nextcloud-rag-platform` |
| Visibility | **Private** |
| Initialize with README | Yes |

4. Click **Create repository**

## Step 2 — Add Team Members

1. Repo page → **Settings** → **Collaborators** → **Add people**
2. Search by each member's GitHub username or email
3. Each member accepts the invitation from their email

## Step 3 — Clone the Repository (Every Member)

```bash
git clone https://github.com/<owner-username>/nextcloud-rag-platform.git
cd nextcloud-rag-platform
```

## Step 4 — Configure Git (Once Per Machine)

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Done — the repo is ready and everyone has a local copy to start working.

## Related

- [Git & GitHub Basics](git-github-basics.md)
- [VS Code](../tools/vscode.md)
- [SSH Client Setup](../tools/ssh-client.md)
- [Development Workflow](../tools/development-workflow.md)
- [Local Development Tools](../tools/local-development-tools.md)
- [Git & GitHub Commands](../../commands/git.md)
