# Provisioning geekoma9

`uv run harness provision` syncs `harness/remote_scripts/` to `~/agentbench/bin/`, clones the
benchmark mirror (`~/agentbench/bench.git`, over HTTPS) if missing, and runs these checks (all are
run; the exit code is non-zero and names the first failure):

| check | passes when |
|---|---|
| python3 | `python3 --version` >= 3.10 (also needed by the usage proxy) |
| godot | `~/agentbench/opt/godot/godot --version` matches `.godot-version` at `base-v1` |
| ollama | `/usr/local/bin/ollama --version` runs |
| deploy-key | `ssh -T git@github-agentbench` says "successfully authenticated" |
| sudo | `sudo -n systemctl --version` works (passwordless sudo; Ollama is never stopped by a check) |
| linger | `loginctl show-user markn -p Linger` is `Linger=yes` |
| model-store | markn can `ls /usr/share/ollama/.ollama/models/manifests` |

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

## Owner action still required

Add the public key `~/.ssh/agentbench_deploy.pub` as a **deploy key with write access** on
`YodaTheCoder/godot-agent-bench` (Settings > Deploy keys). Until then the `deploy-key` check fails
and attempt branches cannot be pushed.
