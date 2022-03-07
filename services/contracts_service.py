
import json
import traceback
from toolkit import toolkit_

class ContractsService:
    @staticmethod
    def loadAbi(abi):
        return json.load(open("./abis/%s"%(abi)))

    @staticmethod
    def getContractInstance(address, abi_filename):
        return toolkit_.w3.eth.contract(address, abi=ContractsService.loadAbi(abi_filename))
        
    @staticmethod
    def exec_contract(account, nonce, func, gas = None):
        try:
            tx_dict = {'gas': gas} if gas else {}
            tx_dict.update({'from': account.address, 'nonce': nonce})
            transaction = func.buildTransaction(tx_dict)#, 'gasPrice': 2500000})#estimated_gas, #2000000,})
            signed = account.signTransaction(transaction)
            trans_hash = toolkit_.w3.eth.sendRawTransaction(signed.rawTransaction)
            if trans_hash:
                tx_receipt = toolkit_.w3.eth.waitForTransactionReceipt(trans_hash, timeout=60)
        except:
            print("Failed to execute contract.\n")
            traceback.print_exc()
            return None
        print("Transaction succeeded. hash for func %s. %s" % (func, trans_hash.hex()))
        return trans_hash.hex()
