import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import obs_distribution as obs


class OBSPublication(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.origin = 'https://bucket.obs.cn-south-1.myhuaweicloud.com'
        (self.root/'aster-source.json').write_text(json.dumps({
            'schema':1, 'kind':'aster-static-source', 'base_url':self.origin+'/releases/test-1'}))
        (self.root/'blob-test').write_bytes(b'public fixture')
        (self.root/'SHA256SUMS').write_text(''.join(
            hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
            for p in sorted(self.root.iterdir())))
        self.calls = []
        self.client = SimpleNamespace(getObjectMetadata=lambda *args:SimpleNamespace(status=404),
            putFile=lambda bucket,key,path:(self.calls.append(key) or SimpleNamespace(status=200)))
    def tearDown(self):
        self.temp.cleanup()
    def publish(self, verifier=lambda *args:None):
        with patch('builtins.print'):
            obs.publish(self.client,'bucket',self.root,'owner/repo','test-1',self.origin,verifier)
    def test_switches_channel_only_after_immutable_release(self):
        self.publish()
        self.assertEqual(self.calls[-2:],['releases/test-1/aster-source.json','aster-source.json'])
    def test_public_read_failure_keeps_channel_untouched(self):
        def fail(*args):raise RuntimeError('read failed')
        with self.assertRaises(RuntimeError):self.publish(fail)
        self.assertNotIn('aster-source.json',self.calls)
    def test_existing_tag_is_not_overwritten(self):
        self.client.getObjectMetadata=lambda *args:SimpleNamespace(status=200)
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(self.calls,[])
    def test_modified_local_export_never_uploads(self):
        (self.root/'blob-test').write_bytes(b'changed')
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(self.calls,[])
    def test_credential_parser_and_error_redaction(self):
        credential=self.root/'credentials.csv'
        credential.write_text('Access Key Id,Secret Access Key\nfixture-ak,fixture-sk\n')
        self.assertEqual(obs.credentials(credential),('fixture-ak','fixture-sk'))
        with patch.object(obs,'_main',side_effect=RuntimeError('private detail')),patch('builtins.print') as output:
            self.assertEqual(obs.main([]),1)
        self.assertNotIn('private detail',str(output.call_args_list))
