import consts
from web3 import Web3


class Toolkit:
    # self.web3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
    # self.web3.eth.handleRevert = True

    # @staticmethod
    # def loadAbi(abi):
    #     return json.load(open("./abis/%s"%(abi)))

    # @staticmethod
    # def getContractInstance(address, abiFile):
    #     return Toolkit.w3().eth.contract(address, abi=Toolkit.loadAbi(abiFile))
    
    @staticmethod
    def w3():
        # w3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
        # w3.eth.handleRevert = True
        return w3


w3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
w3.eth.handleRevert = True