# VS Code

## What Is It?

VS Code (Visual Studio Code) is a free, lightweight but powerful code editor by Microsoft. It supports every language used in modern projects — Python, Bash, [Terraform](../../concepts/cloud/iac/terraform.md), [YAML](../../concepts/devops/yaml.md), [JSON](../../concepts/programming/fundamentals/json.md), Markdown — through a rich extension system.

## Install

| OS | Method |
|---|---|
| Windows | Download installer from https://code.visualstudio.com/ |
| Mac | Download `.dmg` from https://code.visualstudio.com/ or `brew install --cask visual-studio-code` |
| Linux / WSL2 | `sudo snap install code --classic` or download `.deb` from the site |

**Verify:**
```bash
code --version
```

## Recommended Extensions

Install from the Extensions panel (`Ctrl+Shift+X`) or from the command line:
```bash
code --install-extension <extension-id>
```

### Universal (install for any project)

| Extension | Publisher | ID | Purpose |
|---|---|---|---|
| GitLens | GitKraken | `eamodio.gitlens` | Git history, blame, and diff inside VS Code |
| Markdown All in One | Yu Zhang | `yzhang.markdown-all-in-one` | Edit and preview `.md` files |
| Draw.io Integration | Henning Dieterichs | `hediet.vscode-drawio` | Edit `.drawio` diagrams inside VS Code |
| EditorConfig | EditorConfig | `editorconfig.editorconfig` | Enforce consistent formatting across editors |
| DotENV | mikestead | `mikestead.dotenv` | Syntax highlighting for `.env` files |

### Python / AI scope

| Extension | Publisher | ID | Purpose |
|---|---|---|---|
| Python | Microsoft | `ms-python.python` | Python syntax, linting, debugging |
| Pylance | Microsoft | `ms-python.vscode-pylance` | IntelliSense and type checking |
| Jupyter | Microsoft | `ms-toolsai.jupyter` | Run notebooks for experiments |
| [REST](../../concepts/backend/api/rest.md) Client | Huachao Mao | `humao.rest-client` | Test [REST](../../concepts/backend/api/rest.md)/[WebDAV](../../concepts/protocols/webdav.md) API calls from `.http` files |

### Deployment / Linux scope

| Extension | Publisher | ID | Purpose |
|---|---|---|---|
| [Docker](../../concepts/containers/docker.md) | Microsoft | `ms-azuretools.vscode-docker` | [Docker Compose](../../concepts/containers/docker-compose.md) syntax, container management |
| [YAML](../../concepts/devops/yaml.md) | Red Hat | `redhat.vscode-yaml` | [YAML](../../concepts/devops/yaml.md) syntax and validation |
| Bash IDE | mads-hartmann | `mads-hartmann.bash-ide-vscode` | Bash script syntax and linting |
| ShellCheck | timonwong | `timonwong.shellcheck` | Bash script error checking |
| Remote - [SSH](../../concepts/protocols/ssh.md) | Microsoft | `ms-vscode-remote.remote-ssh` | Edit files directly on a remote server |

### Infrastructure / Cloud scope

| Extension | Publisher | ID | Purpose |
|---|---|---|---|
| HashiCorp [Terraform](../../concepts/cloud/iac/terraform.md) | HashiCorp | `hashicorp.terraform` | [Terraform](../../concepts/cloud/iac/terraform.md) syntax highlighting and validation |
| [Azure](../../concepts/cloud/azure/azure.md) Tools | Microsoft | `ms-vscode.vscode-node-azure-pack` | [Azure](../../concepts/cloud/azure/azure.md) resource management from VS Code |

### Security scope

| Extension | Publisher | ID | Purpose |
|---|---|---|---|
| [REST](../../concepts/backend/api/rest.md) Client | Huachao Mao | `humao.rest-client` | Test API security — send requests, inspect responses |
| Remote - [SSH](../../concepts/protocols/ssh.md) | Microsoft | `ms-vscode-remote.remote-ssh` | Connect to remote servers for security review |

## Shared Project Settings

Add this to the project repo as `.vscode/settings.json` so all contributors share consistent formatting:

```json
{
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "files.eol": "\n",
  "editor.formatOnSave": true,
  "files.trimTrailingWhitespace": true,
  "editor.rulers": [100],
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

## Tips

- Use `` Ctrl+` `` to open the integrated terminal
- Use `Ctrl+Shift+P` to open the Command Palette — search for any command
- Use `Ctrl+P` to quickly open any file by name
- Split editor with `Ctrl+\` to view two files side by side

## Related

- [SSH Client Setup](ssh-client.md)
- [draw.io](drawio.md)
- [Git & GitHub Basics](../git/git-github-basics.md)
- [Setting Up a GitHub Project](../git/github-project-setup.md)
