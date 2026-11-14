#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Publish a verified export to OBS, switching the public channel last.

Install optional dependency esdk-obs-python. Credentials are read only from a
local Huawei credentials.csv or OBS_ACCESS_KEY_ID/OBS_SECRET_ACCESS_KEY.
No SDK debug logging is enabled. Never pass credentials on the command line.
"""
import argparse
import csv
import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

def sdk_tools():
    sdk = Path(os.environ.get('ASTER_SDK', Path(__file__).resolve().parents[2] / 'aster-sdk'))
    if not (sdk / 'tools/static_distribution.py').is_file():
        raise RuntimeError('Set ASTER_SDK to the SDK checkout directory')
    sys.path.insert(0, str(sdk / 'tools'))
    import static_distribution
    return static_distribution


def credentials(path=None):
    if path:
        with path.open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != 1:
            raise ValueError('Expected one credential record')
        record = {k.strip().lower().replace(' ', ''): v.strip() for k, v in rows[0].items()}
        ak, sk = record.get('accesskeyid'), record.get('secretaccesskey')
    else:
        ak, sk = os.environ.get('OBS_ACCESS_KEY_ID'), os.environ.get('OBS_SECRET_ACCESS_KEY')
    if not ak or not sk:
        raise ValueError('Missing OBS credentials')
    return ak, sk


def check(response):
    if not 200 <= response.status < 300:
        # SDK response messages may contain signed request details; do not log them.
        raise RuntimeError(f'OBS request failed: HTTP {response.status}')


def verify_public(url, path):
    expected = hashlib.sha256(path.read_bytes()).digest()
    digest = hashlib.sha256()
    size = 0
    with urlopen(Request(url, headers={'Cache-Control': 'no-cache'}), timeout=120) as response:
        if response.status != 200:
            raise RuntimeError('Public object GET failed')
        while data := response.read(256 * 1024):
            digest.update(data)
            size += len(data)
    if size != path.stat().st_size or digest.digest() != expected:
        raise RuntimeError('Public object size/SHA256 mismatch')


def publish(client, bucket, output, repository, tag, origin, verifier=verify_public):
    distribution = sdk_tools()
    distribution.validate_export(output, repository, tag, origin)
    base, channel = distribution.source_urls(repository, tag, origin)
    prefix = 'releases/' + tag + '/'
    state = client.getObjectMetadata(bucket, prefix + 'aster-source.json')
    if state.status != 404:
        if 200 <= state.status < 300:
            raise ValueError('Release already exists; choose a new tag')
        check(state)
    # Keep the root channel untouched if any upload or public readback fails.
    # Include an immutable source descriptor last, as the release completion marker.
    def upload(path):
        check(client.putFile(bucket, prefix + path.name, str(path)))
        verifier(base + '/' + path.name, path)
        print('Verified:', path.name, flush=True)
    paths = sorted(p for p in output.iterdir() if p.name != 'aster-source.json')
    with ThreadPoolExecutor(max_workers=4) as pool:
        # Each immutable file is independent; publication waits for every result.
        for _ in pool.map(upload, paths):
            pass
    upload(output / 'aster-source.json')
    check(client.putFile(bucket, 'aster-source.json', str(output / 'aster-source.json')))
    verifier(channel, output / 'aster-source.json')
    print('Published:', channel)


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repository', default='hello-myj/aster-releases')
    parser.add_argument('--tag', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--credentials-file', type=Path)
    args = parser.parse_args(argv)
    distribution = sdk_tools()
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]', args.bucket):
        parser.error('Invalid OBS bucket')
    if not re.fullmatch(r'[a-z]{2}-[a-z]+-\d+', args.region):
        parser.error('Invalid OBS region')
    origin = f'https://{args.bucket}.obs.{args.region}.myhuaweicloud.com'
    distribution.validate_export(args.output, args.repository, args.tag, origin)
    from obs import ObsClient
    import certifi
    ak, sk = credentials(args.credentials_file)
    client = ObsClient(access_key_id=ak, secret_access_key=sk, ssl_verify=certifi.where(),
                       server=f'https://obs.{args.region}.myhuaweicloud.com')
    try:
        publish(client, args.bucket, args.output, args.repository, args.tag, origin)
    finally:
        client.close()
    return 0


def main(argv=None):
    # Suppress third-party errors that could contain signed request details.
    try:
        return _main(argv)
    except Exception as error:
        print('Publication failed (' + type(error).__name__ + '). Channel may still point to the prior release.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
