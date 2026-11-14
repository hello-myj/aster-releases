# OBS static distribution

The SDK exports the same board-filtered static protocol to an HTTPS bucket.
GitHub export/publishing remains available. An OBS deployment uses:

- `aster-source.json`: mutable public channel entry.
- `releases/<tag>/`: complete immutable release, including metadata, SHA256SUMS,
  content-addressed fonts/packages/resources, icons and source/license notices.

Use standard storage and public read/private write. Configure credentials only
on the publishing machine (or in CI secrets), never in source or device files.
The device requires no account or storage key.

## Build and export

From the workspace, first build the selected APPS projects using their individual
build tools and resource preparation steps. Then verify/export those packages:

```sh
python aster-apps/tools/prepare-publication.py \
  --tag obs-YYYYMMDD-N --output aster-apps/build/publication/obs-YYYYMMDD-N \
  --catalog aster-releases/publication.json --skip-build \
  --origin https://aster-releases.obs.cn-south-1.myhuaweicloud.com
```

Alternatively, export already staged releases with `aster distribute export`,
passing `--origin` and the usual setup/store data, repository, tag and boards.
Origin must be a plain HTTPS bucket origin, without credentials/query/fragment.

## Publish

From the `aster-releases` checkout, install `pip install -r requirements-obs.txt`.
The SDK is found in the sibling `aster-sdk` checkout by default. Set `ASTER_SDK`
to its checkout path for another layout (for example `build/aster-sdk` in CI).

```sh
python tools/obs_distribution.py --output /path/to/export --tag obs-YYYYMMDD-N \
  --bucket aster-releases --region cn-south-1 \
  --credentials-file /private/path/credentials.csv
```

Or omit `--credentials-file` and set `OBS_ACCESS_KEY_ID` and
`OBS_SECRET_ACCESS_KEY` in the environment. Credential values are never command
arguments or printed. Do not enable SDK debug logging on a credentialed publisher.

The publisher validates every local checksum before network writes, refuses an
already completed release tag, uploads each file and anonymously downloads it
to verify full size and SHA256. Only after all files pass does it PUT the root
`aster-source.json`. Readback itself consumes public download traffic.

If a release fails, use a fresh tag. Failed staging prefixes can be removed by
the operator later; the publisher does not delete existing releases. If the
last PUT succeeds but its verification fails, inspect the channel before retrying.
Rollback consists of republishing a prior verified release's source descriptor
to the root entry, while leaving immutable release files in place.

## Device checks

Use HTTPS with certificate verification. OBS Guangzhou currently chains to
GlobalSign Root CA - R3; firmware includes that public root alongside existing
GitHub roots. Existing devices retain their saved source until explicitly changed;
fresh firmware uses the OBS channel as the first-boot default. Existing local HTTP
resource servers and GitHub channels still work.

Firmware defaults and PEM trust roots are configurable in
`aster-firmware/config/distribution.json`; see that repository's
`docs/distribution-config.md`. Store defaults come from its `app.toml`, not C code.

Validate on both boards: time synchronization, catalog hardware filtering, Range
206/Content-Range, actual payload SHA256, Store install and an AOT app launch.
Passing desktop upload/readback does not establish hardware compatibility.

## Local validation (2026-11-13/14)

Current channel: obs-20261115-xiangqi021, Store 0.3.1. Xiangqi 0.2.1 is included for P4 480×480 and portrait lckfb 240×320 (8 P4 / 6 lckfb catalog entries). All 871 objects passed anonymous full size/SHA256 readback before channel publication; both Xiangqi packages also passed Range 206 validation. Both boards were installed and loaded their OBS catalogs using AOT. The three-size real-WASM UI test covers initial URL prefix visibility, single-step caret movement, long-press acceleration, release/drag-out cancellation, source persistence, size units and download speed. Static download validation and pagination tests also passed. All publication objects passed anonymous full readback before switching the root descriptor.


Published `obs-20261114-apps2` to the Guangzhou bucket with Store 0.2.3. The
catalog is exclusively from `aster-apps`: TouchTest, GoldMiner, OutRun,
PixelWheels, PAL, OpenOMF and OpenTyrian. The last two are P4-only (7 P4 / 5 lckfb
entries). SDK examples and StoreDemo are excluded. All 865 exported objects (about 310 MiB)
passed anonymous full SHA256 readback; Range 206 and returned bytes also matched.
Ten publisher/export tests and the real Store WASM static-flow tests passed,
including old non-NUL-terminated source settings, transient EBUSY/ENOSPC/EAGAIN,
corrupt resources and incompatible hardware rejection. Store request admission
retries transient busy/full conditions for at most 15 seconds.

Both P4 and lckfb were flashed and completed the native resource repair/install
flow (phase 9) over verified OBS HTTPS, using existing SD contents. This was not
an empty-card test: existing fonts were rehashed, not downloaded again. New Store
payloads were actually downloaded: P4 178012 bytes / 1095 ms, lckfb 167952 bytes /
1482 ms (individual transfer measurements, not general throughput guarantees).
Both Store startup tests confirmed the OBS source and loaded catalog/icons.
Manual app installation/launch through the new channel remains a user check.
