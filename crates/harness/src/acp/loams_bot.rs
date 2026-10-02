//! loams: Loams Bot as an ACP agent.
//!
//! The agent itself is `zeron loams bot-acp` (crate `loams-link`): the same
//! binary that is running, so there is nothing to install and the harness
//! cannot drift from the app version. Kept in its own file so the only upstream
//! lines this feature touches in `acp/mod.rs` are `mod loams_bot;` and the
//! match arms the compiler demands elsewhere (see `LOAMS.md`).

use std::path::PathBuf;

use super::{AcpAgentSpec, AcpHarness, default_effort_values, identity_transform};
use zeron_proto::{HarnessId, Model, SteeringMode};

fn loams_bot_spec() -> AcpAgentSpec {
    AcpAgentSpec {
        id: HarnessId::LoamsBot,
        display_name: "Loams Bot",
        // The launch program is always the running executable (see
        // `AcpHarness::loams_bot`); this name only labels error messages.
        executable: "zeron",
        env_override: "LOAMS_BOT_EXECUTABLE",
        args: &["loams", "bot-acp"],
        npm_package: None,
        archive: None,
        extra_paths: current_exe_paths,
        cli_executable: "zeron",
        cli_extra_paths: current_exe_paths,
        install_hint: "Loams Bot ships inside Loams Desktop (`zeron loams bot-acp`); \
             set LOAMS_BOT_EXECUTABLE to point at a different build",
        models: || {
            vec![Model {
                id: "loams-bot".into(),
                label: "Loams Bot".into(),
                description: Some(
                    "One chat that drives the Plane, Zulip, Forgejo, GlitchTip and analytics agents".into(),
                ),
                reasoning_levels: Vec::new(),
                options: Vec::new(),
            }]
        },
        // Prompts are A2A messages: a steer is delivered at the next turn.
        steering_mode: SteeringMode::TurnBoundary,
        reasoning_levels: &[],
        prompt_transform: identity_transform,
        effort_values: default_effort_values,
        ladder_extras: &[],
        prompt_complete_extension: false,
        prompt_stall: None,
        stall_hint: "The Loams agents did not answer; check LOAMS_URL / LOAMS_BOT_URL.",
        effort_in_model_id: false,
        auth_method: None,
        skill_dirs: Vec::new,
        hidden_commands: &[],
        drops_unstarted_cancelled_prompt: false,
    }
}

fn current_exe_paths() -> Vec<PathBuf> {
    std::env::current_exe().into_iter().collect()
}

impl AcpHarness {
    /// Loams Bot (`zeron loams bot-acp`): this binary, speaking ACP on stdio.
    pub fn loams_bot() -> Self {
        let harness = Self::with_spec(loams_bot_spec());
        match std::env::current_exe() {
            Ok(exe) => harness.with_executable(exe),
            Err(_) => harness,
        }
    }
}
