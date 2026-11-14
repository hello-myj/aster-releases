"""Upload immutable build artifacts; does not change the device Store channel."""
import argparse,hashlib,json
from pathlib import Path
from obs_distribution import credentials,check,verify_public
def main():
    parser=argparse.ArgumentParser();parser.add_argument('files',nargs='+',type=Path);parser.add_argument('--credentials-file',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    from obs import ObsClient
    import certifi
    ak,sk=credentials(args.credentials_file);client=ObsClient(access_key_id=ak,secret_access_key=sk,ssl_verify=certifi.where(),server='https://obs.cn-south-1.myhuaweicloud.com');records=[]
    try:
        for file in args.files:
            sha=hashlib.sha256(file.read_bytes()).hexdigest();key='artifacts/'+sha+'/'+file.name;url='https://aster-releases.obs.cn-south-1.myhuaweicloud.com/'+key
            metadata=client.getObjectMetadata('aster-releases',key)
            if metadata.status==404:check(client.putFile('aster-releases',key,str(file)))
            else:check(metadata)
            verify_public(url,file);records.append({'file':file.name,'bytes':file.stat().st_size,'sha256':sha,'url':url});print('Verified:',file.name,flush=True)
    finally:client.close()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':
    try:main()
    except Exception as error:raise SystemExit('Artifact publication failed ('+type(error).__name__+')')
