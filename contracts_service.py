import json

w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
class ContractsService:
    def exec_contract_transaction(self):
        pass

    def loadAbi(abi):
        return json.load(open("./abis/%s"%(abi)))

def getContractInstance(address, abiFile):
    return w3.eth.contract(address, abi=loadAbi(abiFile))