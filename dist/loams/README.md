# Loams packaging overlay

Assets for the Loams build, kept apart from upstream's `dist/` so rebases never
conflict. The packaging scripts (`scripts/package-*.sh`, `package-windows.ps1`)
are still upstream's and still produce `zeron-<version>-…` artifacts; the
overlay that renames them and swaps these assets in is plan AP1n Task 9.

| File | Use |
|---|---|
| `dev.loams.desktop.svg` | Placeholder mark (replace with the brand artwork; Q-brand) |
| `loams-desktop.desktop` | XDG entry with `StartupWMClass=dev.loams.desktop`, matching the window `app_id` set from `loams-brand` |

Identity strings live in `crates/loams-brand`, not in a config file, so a
rename is one reviewed change.
