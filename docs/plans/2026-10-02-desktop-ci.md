# Desktop CI follow-up (#305 in ostrium-labs/loams)

Status: Implemented; local validation and CI review in progress.

## Global constraints

Keep production shell startup and all existing test assertions. Isolate only
child shells created by the delayed-startup test. No dependency changes.
Serialize Cargo commands with the shared lock and build only zeron-engine.
Native macOS behavior must be verified on CI, not inferred from Linux.

## Task 0: Reconciliation

The dev branch already has the CI runner changes from desktop#4. Its global
zsh setup mutates the runner home, and a temporary DEBUG probe remains.
Dev run 37037266833 passed core-tests and macos-frame-recovery. The native
frame step compiled for 4m28s, then executed in about 50ms; the complete
macOS job took 39m39s. There is no demonstrated native-test hang in this run.
The custom main-thread native test must retain that harness.

## Tasks

- [x] Make the existing long-command test assert global rc isolation in zsh;
  demonstrate its failure before the fix.
- [x] Give child shells a temporary ZDOTDIR containing no_global_rcs and an
  empty .zshrc; remove the runner-home workaround and DEBUG probe.
- [x] Add failing-then-passing watchdog tests for success, nonzero exit, and
  a planted hang retaining diagnostics.
- [x] Compile the native regression separately; enforce a 60-second test
  deadline, capture a macOS process sample on timeout, and upload diagnostics.
- [ ] Obtain green CI/DCO and CodeRabbit review, merge to dev, and close #305.

## Rulings made during execution

| # | Ruling | Reason |
|---|---|---|
| 1 | ZDOTDIR is passed as a child environment override; do not change HOME or production terminal defaults. | Prevents global compinit prompts and zsh's new-user wizard without changing the user's shell configuration. |
| 2 | Bound test execution separately from compilation, retain the 45-minute job limit. | The observed 4m28s compilation is not a 50ms test hang. A stalled test now fails after 60s with diagnostics; #305 tracks any future sampled hang. |

## Evidence

The zsh assertion failed before isolation (10-second command deadline).
Both initial-command tests passed afterward in 0.80s. Watchdog regressions
pass and the planted hang returns 124 with preserved output. Native dev CI:
https://github.com/ostrium-labs/loams-desktop/actions/runs/37037266833.

The stable toolchain on this machine is Rust 1.97. Local workspace fmt
reports pre-existing changes in 21 untouched files; only the modified
terminal source was formatted. Strict clippy stops on 20 pre-existing
zeron-harness errors (including collapsible_if in skills.rs). These were
not weakened or swept into this CI task; full core-tests remains a CI gate.
