import json,re,time
from pathlib import Path
from genlayer_py import create_client,create_account
from genlayer_py.chains import studionet
ROOT=Path(__file__).parents[1];ENV=(ROOT.parents[3]/'accounts.env').read_text()
def secret(n):return re.search(rf'^ACCOUNT_{n}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)',ENV,re.M).group(1).strip()
deploy=json.loads((ROOT/"deployments/studio.json").read_text());contract=deploy['contract']
account=create_account(account_private_key=secret(4));client=create_client(chain=studionet,account=account)
def send(c,fn,args):
 tx=c.write_contract(address=contract,function_name=fn,args=args);print(fn,tx,flush=True)
 c.wait_for_transaction_receipt(transaction_hash=tx,status='ACCEPTED',retries=120,interval=10000);info=c.get_transaction(transaction_hash=tx)
 if info.get('status_name')!='ACCEPTED' or not any(r.get('execution_result')=='SUCCESS' for r in info.get('consensus_data',{}).get('leader_receipt',[])):raise RuntimeError({'function':fn,'tx':tx,'status':info.get('status_name'),'execution':info.get('tx_execution_result_name')})
 return tx
def negative(c,fn,args,label):
 try:c.simulate_write_contract(address=contract,function_name=fn,args=args);raise RuntimeError(label+' unexpectedly passed')
 except RuntimeError:raise
 except Exception:print('negative',label,'rejected',flush=True)
policy='PD-'+str(int(time.time()))
base=f'https://raw.githubusercontent.com/liwaw008-svg/policy-diff/{deploy["evidenceCommit"]}/examples/versions/'
args=[policy,1,base+'policy-v1.txt',base+'policy-v2.txt','']
proposed=send(client,'propose_version',args)
negative(client,'propose_version',args,'duplicate version')
finalized=send(client,'finalize',[policy,1])
state=client.read_contract(address=contract,function_name='get_version',args=[policy,1])
assert state['state']=='FINAL' and len(state['changes']['oldDigest'])==64 and len(state['changes']['newDigest'])==64 and (state['changes']['added'] or state['changes']['modified'] or state['changes']['removed'])
proof={'policyId':policy,'transactions':{'propose':proposed,'finalize':finalized},'state':state}
(ROOT/"examples/change-trace.json").parent.mkdir(parents=True,exist_ok=True)
(ROOT/"examples/change-trace.json").write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
