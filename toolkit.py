import json
from os import stat

from pkg_resources import safe_extra
import consts
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
w3.eth.handleRevert = True

class Toolkit:
    # self.web3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
    # self.web3.eth.handleRevert = True

    @staticmethod
    def loadAbi(abi):
        return json.load(open("./abis/%s"%(abi)))

    @staticmethod
    def getContractInstance(self, address, abiFile):
        return w3.eth.contract(address, abi=Toolkit.loadAbi(abiFile))
    
    def w3():
        pass


# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]
