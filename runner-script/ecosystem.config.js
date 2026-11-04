// PM2 config for git_sync.py -- the host-native companion to the Dockerized
// link-sweep-watcher. Deliberately NOT run in Docker: it holds live GitHub
// push access via this machine's own SSH agent / osxkeychain credential
// helper, and an unattended container with that access is a worse trust
// boundary than a script running as you, on your own Mac (see git_sync.py's
// own docstring). Runs in its own .venv (just the `watchdog` package) rather
// than system Python.
//
// Usage (from this directory):
//   pm2 start ecosystem.config.js
//   pm2 stop git-sync
//   pm2 restart git-sync
//   pm2 logs git-sync
//   pm2 save               // persist across reboots (with pm2 startup)
module.exports = {
  apps: [
    {
      name: "git-sync",
      script: ".venv/bin/python3",
      args: "git_sync.py",
      cwd: __dirname,
      autorestart: true,
      watch: false, // git_sync.py does its own file-watching internally
      max_restarts: 10,
      restart_delay: 5000,
      out_file: "./.pm2-git-sync.out.log",
      error_file: "./.pm2-git-sync.err.log",
    },
  ],
};
