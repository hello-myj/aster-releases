# Aster public distribution

Free, anonymous device downloads for the Aster firmware and application ecosystem.
Source code remains in `hello-myj/aster-firmware`, `aster-sdk` and `aster-apps`.
This repository contains publishing automation and documentation, not a running backend.

Device source URL:

```text
https://aster-releases.obs.cn-south-1.myhuaweicloud.com/aster-source.json
```

The OBS channel is published with this repository's `tools/obs_distribution.py`.
Credentials stay outside repositories. All immutable release files are uploaded
and anonymously read back with SHA256 verification before the root channel entry
is switched. See `docs/obs-distribution.md` for local export/publication.
The GitHub workflow below remains a separate mirror and is not automatically
synchronized to OBS. Its channel is still available at
`https://github.com/hello-myj/aster-releases/releases/latest/download/aster-source.json`.

Each immutable release contains the full SD fonts, matching RISC-V/Xtensa Store
packages, the selected application catalog, icons and independent resource files.
SHA256SUMS lists the assets. The source descriptor pins metadata/downloads to one
release so an update cannot mix pages or switch resource versions mid-install.
Public assets contain no Wi-Fi credentials, personal tokens or device identifiers.

## Publish

Open Actions → **Publish static Aster distribution** → **Run workflow**.
The workflow builds and verifies the RISC-V and Xtensa packages, exports static JSON and
content-addressed payloads, uploads a draft, then publishes it as the latest release.
If building/uploading fails, the prior latest release stays available. A rerun uses
a different tag. Do not overwrite existing assets.

For local export, use `aster-apps/tools/prepare-publication.py`; uploading uses
`aster-sdk/tools/aster.py distribute publish` with an operator `gh` login. Devices
never use the GitHub REST API or embed a token.

[publication.json](publication.json) selects nine APPS projects for OBS. The OBS first-boot profiles currently install Store 0.3.3 separately. The device then sees the newest compatible version for its board, architecture, ABI, capabilities and screen.

- **OSPTEK P4C5**, `osptek-p4-st7102`, 480×480, RISC-V — TouchTest, GoldMiner, OutRun, PixelWheels, PAL, Xiangqi, OpenOMF and OpenTyrian.
- **LCKFB ESP32-S3**, `aster.esp32s3.lckfb`, 240×320, Xtensa — TouchTest, GoldMiner, OutRun, PixelWheels, PAL and Xiangqi.
- **FAKE POD NANO PRO**, `fakepod-s31`, 460×460, RISC-V — TouchTest and Aster Music. The player requires firmware ABI 4.5, the media-player capability and an extended-catalog Store client.

Build the app variants and their resources before exporting the full OBS snapshot. The GitHub mirror workflow selects TouchTest and prepares bootstrap files for all three boards. A source update here and a change to the live OBS channel are separate operations. See [OBS distribution](docs/obs-distribution.md) for the publication procedure and dated snapshots.

## Limits and licensing

A GitHub release currently exports at most 1,000 assets, each below 2 GiB. Large game
resource trees may need a future bundled-resource format or separate channels.
The current channel publishes system fonts, Store and the compatible apps listed above. Font notices
and project licenses remain in their source repositories; retain those licenses
when redistributing downloaded files. GitHub hosting terms also apply.
