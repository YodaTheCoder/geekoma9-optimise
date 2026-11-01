# Provisioning geekoma9

`uv run harness provision` syncs `harness/remote_scripts/` to `~/agentbench/bin/`, clones the
benchmark mirror (`~/agentbench/bench.git`, over HTTPS) if missing, and runs these checks (all are
run; the exit code is non-zero and names the first failure):

| check | passes when |
|---|---|
| python3 | `python3 --version` >= 3.10 (also needed by the usage proxy) |
| godot | `/srv/agentbench/opt/godot/godot --version` matches `.godot-version` at `base-v1` |
| ollama | `/usr/local/bin/ollama --version` runs |
| deploy-key | `ssh -T git@github-agentbench` says "successfully authenticated" |
| sudo | `sudo -n systemctl --version` works (passwordless sudo; Ollama is never stopped by a check) |
| linger | `loginctl show-user markn -p Linger` is `Linger=yes` |
| model-store | markn can `ls /usr/share/ollama/.ollama/models/manifests` |
| agent-user | `agentrun` exists, `sudo -n -l -U agentrun` shows no sudo rights, markn can `sudo -n -u agentrun`, agentrun can run Godot, `sudo -n -u agentrun test -x /home/markn` fails, and `sudo -n -u agentrun test -r` fails on `~/agentbench/bench.git` and on an earlier attempt's `work/` |

Godot version normalisation: `.godot-version` holds `4.7.2-stable`, `godot --version` prints
`4.7.2.stable.official.<hash>`. The pin has `-` replaced by `.` and is matched as a prefix
(`4.7.2.stable`); the build hash is not pinned.

## System changes made on geekoma9 (owner pre-authorised)

`markn` already has passwordless sudo, so no sudoers rule was added. `run_experiment` stops the
system Ollama with `sudo -n systemctl stop ollama` before the run and starts it again in a `finally`.

1. **Read access to the system Ollama model store** (POSIX ACLs; ownership and modes untouched):
   ```
   sudo setfacl -m u:markn:--x /usr/share/ollama /usr/share/ollama/.ollama
   sudo setfacl -R -m u:markn:rX /usr/share/ollama/.ollama/models
   sudo find /usr/share/ollama/.ollama/models -type d -exec setfacl -d -m u:markn:rX {} +
   ```
   (`acl` was already installed.) Rollback:
   ```
   sudo setfacl -x u:markn /usr/share/ollama /usr/share/ollama/.ollama
   sudo setfacl -R -x u:markn /usr/share/ollama/.ollama/models
   sudo find /usr/share/ollama/.ollama/models -type d -exec setfacl -k {} +
   ```
2. **Linger** so `systemctl --user` works over ssh: `sudo loginctl enable-linger markn`.
   Rollback: `sudo loginctl disable-linger markn`.
3. **Deploy key** `~/.ssh/agentbench_deploy` (ed25519, comment `agentbench@geekoma9`), a
   `Host github-agentbench` block in `~/.ssh/config` (HostName github.com, User git, IdentityFile,
   IdentitiesOnly yes), and github.com's ed25519 host key in `~/.ssh/known_hosts` (fingerprint
   `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`, matching GitHub's published value).
   Rollback: delete the key pair, the config block, and the github.com line in known_hosts.
4. **Mirror and scripts** under `~/agentbench/` (`bench.git`, `bin/`). Rollback: `rm -rf` those.

5. **Godot 4.7.2-stable** (installed in Task 10, unchanged here). Official release
   `https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip`;
   SHA512 `9aa00f7a605200940bce3027a567b782f49bd8e940dd06ae9e987bd65aee1b1467edd56ed84fcdcbdd44354bf613bdbb4e5d2913e925850368e150c59ed54c65`
   verified against the release's `SHA512-SUMS.txt` (`sha512sum -c`: OK). Installed as
   `~/agentbench/opt/godot/Godot_v4.7.2-stable_linux.x86_64` with symlink
   `~/agentbench/opt/godot/godot`; the zip and sums file are kept in `~/agentbench/dl/`.
   Moved to `/srv/agentbench/opt/godot/` with the agent user setup below (the symlink is relative).
   Rollback: `rm -rf /srv/agentbench/opt/godot`.

### Pre/post state of the ACL targets

Before the change there were no ACL entries (plain modes only; `/usr/share/ollama` is
`drwxr-x--- ollama ollama`). The ACLs that exist now (`sudo getfacl -p`, read-only):

```
# /usr/share/ollama           user::rwx user:markn:--x group::r-x mask::r-x other::---
# /usr/share/ollama/.ollama   user::rwx user:markn:--x group::r-x mask::r-x other::r-x
# .../.ollama/models          user::rwx user:markn:r-x group::r-x mask::r-x other::r-x
#                             default:user::rwx default:user:markn:r-x default:group::r-x
#                             default:mask::r-x default:other::r-x
```

The rollback (`setfacl -x`, `setfacl -k`) assumes no other default ACLs were present, which held
before this change.

## Agent user `agentrun` (one-time setup, not yet done)

Command agents (OpenCode, Claude Code, ...) run as the unprivileged user `agentrun`, so they cannot
read or change the hidden tests, the reference solutions, the scorer or earlier attempts. The harness
does the per-attempt part itself:

- `CommandAgent` runs the agent as `sudo -n -u agentrun -H bash -c <command>` inside the usual
  `setsid`/`timeout` wrapper. Before the run it gives the workdir and issue file to the agent
  (`sudo -n chown -R agentrun: <workdir> <issue>`), and takes them back afterwards
  (`sudo -n chown -R markn: ...`) before the commit. `agent.log` is opened by the wrapper and stays
  markn's. After the run it kills the wrapper's session and every `agentrun` process
  (`sudo -n pkill -KILL -s <sid>`, `sudo -n pkill -KILL -u agentrun`).
- Each attempt root is created `0711` (its run folder too): the agent reaches its workdir and issue by
  path but can list nothing. The task files (hidden tests, `solution.patch`, `score_extra.sh`, ...)
  are exported only after the agent has exited and no `agentrun` process is left, into
  `<attempt>/score/task` inside the `0700` folder `score/`. After scoring, `score/task` and
  `score/project` are deleted (logs, XML and `score.json` are kept) and the attempt root becomes `0700`.
  At run start every older attempt root is made `0700` and every run folder `0711`.
- Preflight fails if any `agentrun` process exists; the stray kill also kills them.
- Before each agent run, agentrun's home is reset as that user: everything goes except
  `~/.claude/.credentials.json`, `~/.claude.json`, `~/.local/bin/claude` and `~/.local/share/claude`
  (Claude Code's install and login), then the template `/srv/agentbench/agent-home/` is copied in, and
  agentrun's entries in `/tmp`, `/var/tmp` and `/dev/shm` are deleted. So no attempt, not even a
  repeat of the same task, sees an earlier one's OpenCode sessions, Claude Code transcripts, caches or
  scratch files, and every attempt starts with the same warm tool caches.
- The run-start sweep that closes old attempt roots runs again before every attempt.
- The oracle applies `solution.patch` straight from the mirror; null and oracle run as markn.

Attempts live in `/srv/agentbench/runs/` and the Godot that agents run in `/srv/agentbench/opt/`, both
outside `/home/markn`, which stays `0750` so agentrun cannot enter it. A traversable home would expose
every world-readable path in it, including `~/.claude/projects` (Claude Code transcripts, among them the
calibration run's solutions), `~/src` and `~/_dev`. The mirror, scripts, run lock and the attempts from
before the move stay in `~/agentbench`.

One-time setup on geekoma9 (run as markn, who has passwordless sudo):

```
sudo useradd --create-home --shell /bin/bash --user-group agentrun   # no sudo group, no password
sudo install -d -o markn -g markn -m 711 /srv/agentbench /srv/agentbench/runs
sudo install -d -o markn -g markn -m 755 /srv/agentbench/opt
mv ~/agentbench/opt/godot /srv/agentbench/opt/ && rmdir ~/agentbench/opt
ln -sfn Godot_v4.7.2-stable_linux.x86_64 /srv/agentbench/opt/godot/godot
chmod -R u=rwX,go=rX /srv/agentbench/opt                               # agents run Godot themselves
chmod 750 /home/markn && chmod 700 ~/agentbench/bench.git
sudo install -d -o agentrun -g agentrun -m 700 /home/agentrun/.config/agentbench
sudo install -o agentrun -g agentrun -m 600 /home/markn/.config/agentbench/opencode.json \
    /home/agentrun/.config/agentbench/opencode.json
echo agentrun | sudo tee -a /etc/cron.deny /etc/at.deny             # no jobs that outlive the attempt
```

Home template (with no harness run in progress: the harness kills every agentrun process). Warm
OpenCode once as agentrun so it installs its plugin packages (`~/.config/opencode/node_modules`) and
fetches its model list (`~/.cache/opencode/models.json`); the run itself may fail, the endpoint is
unused. Then keep only config and caches (not `~/.local/share/opencode`, its session store):

```
sudo -u agentrun -H bash -c 'd=$(mktemp -d) && git -C "$d" init -q && cd "$d" &&
  OPENCODE_CONFIG=$HOME/.config/agentbench/opencode.json BENCH_ENDPOINT=http://127.0.0.1:1 \
  timeout 300 opencode run --auto --format json --dir "$d" -m bench/qwen3-coder:30b hi < /dev/null'
sudo install -d -o markn -g markn -m 755 /srv/agentbench/agent-home
sudo cp -r /home/agentrun/.config /home/agentrun/.cache /srv/agentbench/agent-home/
sudo chown -R markn: /srv/agentbench/agent-home && chmod -R u=rwX,go=rX /srv/agentbench/agent-home
```

Rebuild it the same way after changing `opencode.json` or upgrading OpenCode.

Then `uv run harness provision` must show `OK   agent-user`. Things to confirm on the live host:
`sudo -n -l -U agentrun` prints "is not allowed to run sudo"; `sudo -n -u agentrun -H opencode --version`
works (OpenCode is in `/usr/local/bin`, on sudo's `secure_path`); geekoma9's sudoers sets `use_pty`,
which is why the harness kills by user and not only by session. Before the change `/home/markn` was 750
and `~/agentbench/bench.git` 775; `/srv` held nothing.

Rollback (copy anything in `/srv/agentbench/runs` worth keeping first; the harness also needs this
change reverted, `git revert` of the commit that moved the paths to `/srv`):

```
sudo pkill -KILL -u agentrun; sudo userdel -r agentrun
sudo sed -i '/^agentrun$/d' /etc/cron.deny /etc/at.deny
mkdir -p ~/agentbench/opt && mv /srv/agentbench/opt/godot ~/agentbench/opt/
sudo rm -rf /srv/agentbench
chmod 775 ~/agentbench/bench.git
```

Frontier calibration: a calibration run (`experiments/calibration-frontier`) now runs Claude Code as
`agentrun`, which cannot reach `/home/markn/.local/bin/claude`. Install Claude Code for agentrun
(`sudo -u agentrun -H bash -c 'curl -fsSL https://claude.ai/install.sh | bash'`), log in as that user
(`ssh -t markn@geekoma9.local sudo -u agentrun -H /home/agentrun/.local/bin/claude`, then `/login`;
credentials live in `/home/agentrun/.claude`), and change the path in the config to
`/home/agentrun/.local/bin/claude`.

## Recovery if the orchestrator is hard-killed

The harness stops the owner's Ollama for a run and restores it in a `finally`. If the orchestrator
is killed (SIGKILL, power loss) mid-run, restore it by hand: `sudo systemctl start ollama`
(only if it was running before; the harness itself restarts it only when `systemctl is-active ollama`
said `active` at run start). SIGTERM and SIGHUP (closing the tmux pane) do run the cleanup.

A run holds `flock -n ~/agentbench/run.lock` on geekoma9 through a detached helper
(`flock ... sleep infinity`) for its whole length, so a second `harness run` fails at once. After a
hard kill that helper is left holding the lock: `pkill -f 'agentbench/run.lock'` releases it.
Every run also syncs `harness/remote_scripts/` to `~/agentbench/bin/` at start, so records always
name (in `versions.remote_scripts`) the scripts that scored them.
If the automatic restore fails after 3 tries the harness prints
`system Ollama NOT restarted ... run: sudo systemctl start ollama` to stderr.

## Owner action still required

Add the public key `~/.ssh/agentbench_deploy.pub` as a **deploy key with write access** on
`YodaTheCoder/godot-agent-bench` (Settings > Deploy keys). Until then the `deploy-key` check fails
and attempt branches cannot be pushed. The check proves authentication only: tick **Allow write
access** when adding the key, or pushes will fail even though the check passes.

## Claude Code (frontier calibration only)

Installed 2026-10-31 with Anthropic's native installer (`curl -fsSL https://claude.ai/install.sh`,
inspected before running, `stable` channel): Claude Code 2.1.309 at `~/.local/bin/claude`, data in
`~/.claude`. `~/.local/bin` is not on the non-interactive PATH, so configs use the absolute path.
The owner logs in interactively (`ssh -t markn@geekoma9.local ~/.local/bin/claude`, then `/login`).
Used only by `experiments/calibration-frontier`. Rollback: `rm -rf ~/.local/bin/claude
~/.local/share/claude ~/.claude`.

## Mac side: ssh over IPv4

`geekoma9.local` resolves to an IPv6 link-local address first, and geekoma9's UFW drops IPv6
port 22, so each connection stalled 10 s before falling back to IPv4 (enough to hit the harness's
15 s ssh timeouts). The Mac's `~/.ssh/config` now has `Host geekoma9.local` / `AddressFamily inet`.
Rollback: remove that block (backup at `~/.ssh/config.bak-20261031`).

## Orchestrator: newbuntu.local

Long runs are orchestrated from `newbuntu.local` (Ubuntu 24.04, wired, always on) inside `tmux`,
so no laptop has to stay connected. Changes made there on 2026-10-31: geekoma9's host keys copied
into `~/.ssh/known_hosts` from the Mac's (already trusted) copy; `Host geekoma9.local` /
`AddressFamily inet` in `~/.ssh/config` (backup `~/.ssh/config.bak-20261031`); `tmux` via apt;
`uv` 0.13.6 via Astral's installer into `~/.local/bin`; this repo copied to `~/geekoma9-optimise`.
The owner adds newbuntu's `~/.ssh/id_rsa.pub` to geekoma9's `~/.ssh/authorized_keys`.
Rollback: remove the known_hosts lines, the ssh config block and that authorized_keys line;
`sudo apt remove tmux`; `rm ~/.local/bin/uv ~/.local/bin/uvx`; `rm -rf ~/geekoma9-optimise`.

## E1 memory settings

BIOS UMA frame-buffer size: as found 24 GiB (Linux sees 7.4 GiB). E1 settings: 24 GiB (uma24),
16 GiB (uma16), the BIOS minimum (umamin). The owner makes BIOS changes at the machine.

BIOS path: (recorded when the owner makes the first change)

### umamin_gtt24 only: kernel TTM limits

Applies only to the umamin_gtt24 setting, and only after owner confirmation. Adds
`ttm.pages_limit=6291456 ttm.page_pool_size=6291456` (24 GiB = 24 × 262144 pages) to the kernel
command line:

1. Back up the grub config:
   ```
   sudo cp /etc/default/grub /etc/default/grub.bak-e1
   ```
2. Append the two parameters to `GRUB_CMDLINE_LINUX_DEFAULT` in `/etc/default/grub`.
3. Regenerate the grub config and reboot:
   ```
   sudo update-grub
   sudo reboot
   ```

Rollback: `sudo cp /etc/default/grub.bak-e1 /etc/default/grub && sudo update-grub`, reboot; BIOS UMA
back to 24 GiB.

### Verify after any change

```
cat /sys/class/drm/card0/device/mem_info_vram_total /sys/class/drm/card0/device/mem_info_gtt_total /sys/module/ttm/parameters/pages_limit
grep -E 'MemTotal|SwapTotal' /proc/meminfo
```

The harness also checks these against each config's `host:` section (±0.25 GiB) and refuses to run
on a mismatch.
