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
The workflow compiles and verifies both hardware builds, exports static JSON and
content-addressed payloads, uploads a draft, then publishes it as the latest release.
If building/uploading fails, the prior latest release stays available. A rerun uses
a different tag. Do not overwrite existing assets.

For local export, use `aster-apps/tools/prepare-publication.py`; uploading uses
`aster-sdk/tools/aster.py distribute publish` with an operator `gh` login. Devices
never use the GitHub REST API or embed a token.

`publication.json` defines the complete OBS catalog, exclusively from `aster-apps`:
TouchTest, GoldMiner, OutRun, PixelWheels, PAL, OpenOMF and OpenTyrian.
OpenOMF/OpenTyrian are P4-only; lckfb receives the other five projects. SDK samples
are not part of this catalog. Locally, build each game with its own project tools,
then use `prepare-publication.py --catalog publication.json --skip-build` to verify
and export the existing packages/resources. The GitHub workflow currently builds
only TouchTest; full game build preparation is not automated in CI.

The channel includes OSPTEK P4/ST7102 (480×480) and lckfb S3 (240×320).
Only explicitly supported hardware appears in each catalog; the device checks the
board, CPU/AOT, ABI, display and capabilities again before installing.

GitHub provides the hosting and TLS. This distribution has no accounts, payment,
activation codes or authorization service. Direct GitHub reachability, download
speed and resumable requests must be validated on the user's network.

## Limits and licensing

One release currently exports at most 1,000 assets, each below 2 GiB. Large game
resource trees may need a future bundled-resource format or separate channels.
The current channel publishes system fonts, Store and the compatible apps listed above. Font notices
and project licenses remain in their source repositories; retain those licenses
when redistributing downloaded files. GitHub hosting terms also apply.
