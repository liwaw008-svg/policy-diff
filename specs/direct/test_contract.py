from conftest import CONTRACT
OLD='https://regulator.example/policy/v1';NEW='https://regulator.example/policy/v2'
def mocks(vm):
 vm.strict_mocks=True;vm.check_pickling=True
 vm.mock_web(r'/v1',{'status':200,'body':'Clause 4: report annually.'});vm.mock_web(r'/v2',{'status':200,'body':'Clause 4: report quarterly from 2027. Clause 8: retain records 5 years.'})
 vm.mock_llm(r'.*Regulatory obligation change extraction.*','{"added":["retain records 5 years"],"removed":[],"modified":["annual reporting -> quarterly"],"effective_date":"2027-01-01","ambiguities":[]}')
def test_version_chain_and_digest_lineage(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.propose_version(' pol-a ',1,OLD,NEW,'');c.finalize('POL-A',1);v=c.get_version(' pol-a ',1)
 assert v['state']=='FINAL' and len(v['changes']['newDigest'])==64
 c.propose_version('POL-A',2,NEW,'https://regulator.example/policy/v3',v['changes']['newDigest'])
def test_duplicate_and_bad_predecessor_rejected(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);c.propose_version('P',1,OLD,NEW,'')
 with direct_vm.expect_revert('duplicate policy version'):c.propose_version(' p ',1,OLD,NEW,'')
 with direct_vm.expect_revert('finalized predecessor'):c.propose_version('P',2,NEW,'https://regulator.example/policy/v3','abc')
 with direct_vm.expect_revert('first version has no predecessor'):c.propose_version('Q',1,OLD,NEW,'abc')
def test_validator_rejects_forged_change(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.propose_version('R',1,OLD,NEW,'');result=c._diff(c.versions['R#1']);direct_vm.mock_llm(r'.*Independently verify.*','{"valid":true}');assert direct_vm.run_validator(leader_result=result) is True;forged=dict(result);forged['newDigest']='0'*64
 assert direct_vm.run_validator(leader_result=forged) is False
