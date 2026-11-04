# npm & pnpm Commands

The Node.js package manager commands used daily. `npm` ships with Node itself; `pnpm` is a faster, disk-efficient alternative (a single content-addressable store shared across projects, instead of a full `node_modules` copy per project) commonly used for monorepos. The commands below are shown side by side since they're nearly 1:1.

## Installing Dependencies

| Task | npm | pnpm |
|---|---|---|
| Install everything from `package.json` | `npm install` | `pnpm install` |
| Add a dependency | `npm install express` | `pnpm add express` |
| Add a dev dependency | `npm install -D typescript` | `pnpm add -D typescript` |
| Add a global tool | `npm install -g nodemon` | `pnpm add -g nodemon` |
| Remove a dependency | `npm uninstall express` | `pnpm remove express` |
| Install exact versions from the lockfile (CI) | `npm ci` | `pnpm install --frozen-lockfile` |

`npm ci`/`--frozen-lockfile` are what CI pipelines should use, not `install` — they fail loudly if the lockfile is out of sync with `package.json`, instead of silently updating it.

## Running Scripts

```bash
npm run dev              # pnpm run dev  (or just: pnpm dev)
npm run build
npm test                 # npm/pnpm both support this shorthand for the "test" script
npm run <script> -- --flag   # pass extra flags through to the underlying script
```

## Inspecting Dependencies

```bash
npm list                 # pnpm list — installed dependency tree
npm outdated             # pnpm outdated — which deps have newer versions available
npm audit                # pnpm audit — check for known vulnerabilities in dependencies
```

## pnpm Workspaces (Monorepos)

```bash
pnpm install                              # installs for every package in the workspace at once
pnpm --filter <package-name> add express  # add a dependency to one specific workspace package
pnpm --filter <package-name> run build    # run a script in one specific workspace package
pnpm -r run build                         # run a script in every workspace package
```

A `pnpm-workspace.yaml` at the repo root declares which directories are workspace packages — this is the pattern behind a monorepo layout like `apps/*` + `packages/*` sharing one lockfile and one `node_modules`.

## `package.json` Version Ranges

| Prefix | Meaning |
|---|---|
| `^1.2.3` | Accept `1.x.x` — any minor/patch update, no major |
| `~1.2.3` | Accept `1.2.x` — patch updates only |
| `1.2.3` | Exact version only |
| `*` or no prefix | Any version — almost never what you actually want |

## Common Questions

**Why would a project use pnpm over plain npm?**
> Mainly disk space and install speed at scale — pnpm keeps one global content-addressable store and hard-links/symlinks packages into each project's `node_modules`, instead of duplicating every package's files per project. This matters most in monorepos with many packages sharing overlapping dependencies, or CI environments doing repeated installs.

## Related

- [NestJS Overview](../concepts/backend/nestjs/nestjs-overview.md)
- [Next.js Overview](../concepts/frontend/nextjs-overview.md)
- [uv (Python)](../concepts/programming/python/uv.md) — the equivalent fast-installer idea in the Python ecosystem
