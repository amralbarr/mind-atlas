# Bash & Shell Commands

Everyday shell commands and the handful of Bash scripting patterns that come up constantly when writing automation scripts (deploy scripts, backup scripts, CI steps).

## File & Directory Navigation

```bash
pwd                                        # current directory
ls -la                                     # list all files, including hidden, with details
cd -                                       # jump back to the previous directory
find . -name "*.log"                       # find files by name pattern
find . -type f -mtime -1                   # files modified in the last day
```

## Text Search & Processing

```bash
grep -rn "pattern" .                       # recursive search, show line numbers
grep -v "pattern" file                     # invert match — lines NOT matching
grep -l "pattern" *.md                     # just filenames that match, not the matching lines

cat file | head -n 20                      # first 20 lines
cat file | tail -n 20                      # last 20 lines
tail -f app.log                            # follow a growing log file live

sed 's/old/new/g' file                     # replace text (stream editor)
awk '{print $1}' file                      # extract a column of whitespace-separated text
cut -d',' -f2 file                         # extract field 2, splitting on a delimiter (comma here)

sort file | uniq -c | sort -rn             # count occurrences, most frequent first
wc -l file                                 # count lines
```

## Permissions & Ownership

```bash
chmod +x script.sh                         # make a file executable
chmod 644 file                             # rw-r--r--
chown user:group file                      # change ownership
```

## Processes

```bash
ps aux | grep node                         # find a running process
kill <pid>                                 # ask a process to stop (SIGTERM)
kill -9 <pid>                              # force-kill (SIGKILL) — last resort
lsof -i :3000                              # what process is using port 3000
htop                                       # interactive process/resource viewer
```

This exact check — confirming something is actually bound to the port before suspecting anything downstream — is the first move when a Cloudflare Tunnel [ingress](../concepts/distributed-systems/kubernetes/ingress.md) rule "exists but doesn't work"; see [Cloudflare Tunnel § Debugging](cloudflare-tunnel.md#debugging-ingress-rule-exists-but-it-doesnt-work).

## Environment Variables

```bash
export API_KEY="value"                     # set for this shell session and its children
echo $API_KEY
unset API_KEY
env                                        # list all environment variables
source .env                                # load variables from a file into the current shell
```

### Extracting One Value From a `.env` File Without Sourcing It

Sourcing the whole file (`source .env`) pulls every variable into the current shell — sometimes you just want one value, e.g. to inline into a curl call in a script:

```bash
TOKEN=$(grep NODE_AGENT_SHARED_TOKEN .env | cut -d= -f2)

curl -H "Authorization: Bearer $TOKEN" https://gpu-node-01.internal:9100/health
```

`grep KEY .env` finds the line (`NODE_AGENT_SHARED_TOKEN=abc123`); `cut -d= -f2` splits it on `=` and keeps everything after the first split; `$(...)` (command substitution) captures that output into a variable. This is fragile the moment the value itself contains an `=` or is wrapped in quotes in the file — for anything beyond a quick script, prefer a real `.env` parser (e.g. `dotenv` in Node, `python-dotenv` in Python) or `export $(grep -v '^#' .env | xargs)` to load the whole file safely at once.

## Bash Scripting Essentials

```bash
#!/bin/bash
set -e          # exit immediately if any command fails
set -u          # error on undefined variables instead of silently treating them as empty
set -o pipefail # a pipeline fails if ANY command in it fails, not just the last one
```

`set -euo pipefail` at the top of nearly every real deploy/backup script is what turns "a mid-script command silently failed and the rest kept running anyway" into "the script stops immediately and reports the actual failure."

```bash
# Variables and conditionals
NAME="world"
if [ "$NAME" == "world" ]; then
  echo "Hello, $NAME"
fi

# Command substitution
DATE=$(date +%Y%m%d_%H%M%S)

# Loops
for f in *.txt; do
  echo "$f"
done

# Functions
backup() {
  local dir="$1"
  tar czf "backup_$(date +%s).tar.gz" "$dir"
}
backup /opt/data

# Argument handling
echo "Script name: $0"
echo "First arg: $1"
echo "All args: $@"
echo "Arg count: $#"
```

## Redirection & Piping

```bash
command > file          # overwrite file with stdout
command >> file         # append stdout to file
command 2> errors.log   # redirect stderr only
command > out.log 2>&1  # redirect both stdout and stderr to the same file
command1 | command2     # pipe command1's stdout into command2's stdin
```

## Common Questions

**Why does a script that works when run manually sometimes fail when run from cron or CI?**
> Cron and CI often run with a much smaller `PATH` and no interactive shell profile (`.bashrc`/`.zshrc`) loaded — a command or environment variable that resolves fine in an interactive terminal can be missing entirely in that stripped-down environment. Use absolute paths and explicitly `source` any needed environment file inside the script itself, rather than relying on shell startup files.

## Related

- [Ansible](../concepts/cloud/iac/ansible.md)
- [Idempotency & Race Conditions](../concepts/programming/fundamentals/idempotency-and-race-conditions.md)
- [Docker Commands](docker.md)
