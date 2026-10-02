# Loams Desktop

Loams Desktop is a fork of [Zeron](https://github.com/zeronsh/zeron) (MIT, Copyright (c) 2026 Wing): a native Rust and GPUI control plane for coding agents, with a small engine per device. Loams adds the server-connected half: sign-in at Authentik, a Connect-RPC client for a local or remote `loams` server, and **Loams Bot**, the one chat that drives the platform agents of the **Loams Software Factory**.

The design is `docs/design/37-desktop-and-mobile-apps.md` section 18 in [`ostrium-labs/loams`](https://github.com/ostrium-labs/loams) (decisions D480 to D499); the plan is `docs/plans/2026-10-02-ap1n-native-desktop-zeron.md`. This file is what a person working in this fork needs.

## Run it

```sh
# Linux (Wayland or X11). Needs the GPUI build libraries and, for the browser tab,
# WebKitGTK 4.1; see docs/reference/linux-browser.md and .github/workflows/loams.yml
cargo run -p zeron                      # the app (debug build; first build is long)

# Windows (PowerShell, MSVC toolchain and the Windows SDK for fxc.exe)
cargo run --release -p zeron

# The Loams commands, with no server, against the in-process mock
LOAMS_MOCK=1 cargo run -p zeron -- loams status
LOAMS_MOCK=1 cargo run -p zeron -- loams bot "file an issue for the checkout 500s"

# Against a real local stack (loams dev ... serves Connect on 127.0.0.1:8080)
LOAMS_URL=http://127.0.0.1:8080 cargo run -p zeron -- loams status
cargo run -p zeron -- loams login       # Authentik, in your browser
```

In the app, **Loams Bot** is one of the agents in the new-session picker. It runs `zeron loams bot-acp` (this same binary) over ACP. With no `LOAMS_BOT_URL` set it answers from the mock agent.

Configuration (all optional): `LOAMS_URL` (also `LOAM_URL`), `LOAMS_MOCK=1`, `LOAMS_BOT_URL` (an A2A JSON-RPC endpoint), `LOAMS_OIDC_ISSUER` (development override), `LOAMS_BOT_EXECUTABLE` (use a different binary for the harness).

## Test it

```sh
cargo test -p loams-brand -p loams-link          # seconds; no GPUI
scripts/loams/smoke.sh target/debug/zeron        # needs a built binary; LOAMS_MOCK is set by the script
scripts/loams/gen-protos.sh                      # regenerate crates/loams-link/src/gen (needs buf and the plugins)
```

`scripts/loams/install-proto-plugins.sh` installs the three pinned protoc plugins into `~/.local/share/loams-tools`.

## What Loams adds

| Path | What |
|---|---|
| `crates/loams-brand` | Identity strings (product, app id, OIDC client id). No dependencies |
| `crates/loams-link` | Connect client and in-process mock, Authentik OIDC sign-in (PKCE, loopback, keychain), the stub A2A client, the ACP agent for Loams Bot, and the `zeron loams` verbs. No GPUI |
| `crates/loams-link/proto`, `buf.gen.yaml`, `src/gen` | Vendored protos (`proto/PIN` records the ref), the buf template, and the committed generated Rust |
| `crates/harness/src/acp/loams_bot.rs` | The `HarnessId::LoamsBot` spec |
| `dist/loams/` | Placeholder icon and the desktop entry |
| `scripts/loams/`, `.github/workflows/loams.yml` | Smoke test, proto scripts, CI |
| `NOTICE` | Attribution |

## The patch ledger (inherited files that Loams changed)

Every change to an inherited file is either a one-line hook marked `// loams:` or a match arm the compiler demanded when `HarnessId` gained `LoamsBot`. Keep this table in step: a change to an inherited file with no row here is a bug. Rebase onto upstream **release tags** (see "Tracking upstream").

| File | Change | Why | Upstreamable |
|---|---|---|---|
| `Cargo.toml` | Two workspace members and two path dependencies | New crates | No |
| `apps/zeron/Cargo.toml` | Depends on `loams-link` | The `loams` subcommand | No |
| `apps/zeron/src/main.rs` | `Loams` subcommand and dispatch; stdout-is-protocol check also covers `loams bot-acp`; **WorkOS client id a non-zeron placeholder; default edge host `edge.loams.invalid`** | Never contact zeron's cloud or install its binaries | Partly (an "unset" default) |
| `crates/update/src/lib.rs` | The two release-page URLs point at this fork | The advisory update strip must not send people to upstream | No |
| `crates/ui/Cargo.toml`, `crates/ui/src/lib.rs` | Depends on `loams-brand`; window title and `app_id` read from it | Branding | No |
| `crates/ui/src/icons.rs`, `crates/ui/assets/icons/loams-mark.svg` | One icon | The Loams Bot picker icon | No |
| `crates/ui/src/pickers.rs`, `settings/accounts.rs`, `settings/harnesses.rs`, `shell/harness_updates.rs` | One match arm each for `LoamsBot` | Exhaustive matches | Disappears if a config-driven custom agent lands upstream |
| `crates/proto/src/agent.rs` | `HarnessId::LoamsBot` | The harness id | Same |
| `crates/harness/src/acp/mod.rs` | `mod loams_bot;` | The spec lives in its own file | Same |
| `crates/harness/src/install.rs`, `skills.rs` | One arm each | Not installable; no skill directories | Same |
| `crates/engine/src/registry.rs` | Registers the harness | Loams Bot in the picker | Same |
| `crates/engine/src/agent_accounts.rs`, `agent_accounts/stores.rs`, `harness_updates.rs` | One arm each | Slug, CLI name, no provider updater | Same |
| `crates/client/src/catalog.rs` | Display name | Picker label | Same |

Changes not made on purpose: the binary, crate, data directory (`~/.zeron`) and `ZERON_*` names stay, so rebases stay cheap (design Q489 and Q490).

## Tracking upstream

```sh
git remote add upstream https://github.com/zeronsh/zeron      # once
git fetch upstream --tags
git rebase <the newest upstream release tag you have tested>   # not upstream/main
```

Upstream ships about two releases a day, so rebase onto a tag at least every two weeks. Resolve conflicts in the ledger's files only; anything else conflicting means a new patch crept in. Send generally useful changes upstream first (a config-driven custom ACP agent, signed update manifests, a persistent browser store, the Windows browser).

## Security notes

- A Loams build **never contacts zeron's backend and never installs zeron's binaries**: the default WorkOS client id is a placeholder (not zeron's tenant) and the default edge host does not resolve. Set `ZERON_EDGE_URL` only to a feed you control and trust. A signed update manifest is plan AP1n Task 9.
- Zeron's workflows that need its secrets or its cloud (`deploy.yml`, `testflight.yml`, `cursor-sdk-update.yml`, `linux-installer.yml` against zeron.sh) are disabled in this repository's Actions settings, not edited, so rebases stay clean.
- Agents run as subprocesses with your rights. Loams tokens are never given to them. See design 37 sections 18.4 and 18.7.

## Licence

Inherited code: MIT (`LICENSE`, Copyright (c) 2026 Wing), unmodified. Code Loams added (the paths in "What Loams adds"): Apache-2.0 (`crates/loams-link/LICENSE`). See `NOTICE`.
