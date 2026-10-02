//! Loams identity strings, in one place.
//!
//! The fork keeps zeron's crate, binary and data-directory names so rebasing
//! stays cheap (see `LOAMS.md`). New Loams code takes its names from here, and
//! the few upstream call sites that show a name (window title, app id) read
//! these constants instead of carrying a literal.

/// The product, as shown in window titles and menus.
pub const PRODUCT_NAME: &str = "Loams Desktop";
/// The chat that drives the platform agents (owner ruling, 2026-10-02).
pub const BOT_NAME: &str = "Loams Bot";
/// The loop Loams Bot drives (owner ruling, 2026-10-02).
pub const FACTORY_NAME: &str = "Loams Software Factory";
/// Reverse-DNS application id (Linux app id, macOS bundle id, Windows AUMID).
pub const APP_ID: &str = "dev.loams.desktop";
/// The public OAuth client id registered as an Authentik application
/// (design 37 section 6.5).
pub const OIDC_CLIENT_ID: &str = "loams-desktop";
/// The OS keychain service name for stored credentials.
pub const KEYRING_SERVICE: &str = "dev.loams.desktop";
/// The `loams.dev` custom URL scheme (navigation only, design 37 section 6.7).
pub const URL_SCHEME: &str = "loams";
