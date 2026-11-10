# Aster public distribution

Free, anonymous device downloads for the Aster firmware and application ecosystem.
Source code remains in `hello-myj/aster-firmware`, `aster-sdk` and `aster-apps`.
This repository contains publishing automation and documentation, not a running backend.

Device source URL:

```text
https://github.com/hello-myj/aster-releases/releases/latest/download/aster-source.json
```

Each immutable release contains the full SD fonts, matching RISC-V/Xtensa Store
packages, the initial TouchTest catalog, icons and independent resource files.
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

The initial channel includes OSPTEK P4/ST7102 (480×480) and lckfb S3 (240×320).
Only explicitly supported hardware appears in each catalog; the device checks the
board, CPU/AOT, ABI, display and capabilities again before installing.

GitHub provides the hosting and TLS. This distribution has no accounts, payment,
activation codes or authorization service. Direct GitHub reachability, download
speed and resumable requests must be validated on the user's network.

## Limits and licensing

One release currently exports at most 1,000 assets, each below 2 GiB. Large game
resource trees may need a future bundled-resource format or separate channels.
This initial channel publishes only system fonts, Store and TouchTest. Font notices
and project licenses remain in their source repositories; retain those licenses
when redistributing downloaded files. GitHub hosting terms also apply.
