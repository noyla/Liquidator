import json
from os import stat

from pkg_resources import safe_extra
import consts
from web3 import Web3

class Toolkit:
    # self.web3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
    # self.web3.eth.handleRevert = True

    @staticmethod
    def loadAbi(abi):
        return json.load(open("./abis/%s"%(abi)))

    @staticmethod
    def getContractInstance(address, abiFile):
        return w3.eth.contract(address, abi=Toolkit.loadAbi(abiFile))
    
    @staticmethod
    def w3():
        return Web3(Web3.HTTPProvider(consts.PROVIDER_URL))

def _init_lending_pool_address_provider():
    lendingPoolAddressProviderRegistry = Toolkit.getContractInstance("0x1E40B561EC587036f9789aF83236f057D1ed2A90", 
                                                                 "LENDING_POOL_PROVIDER_REGISTRY.json")
    lendingPool_providers = lendingPoolAddressProviderRegistry.functions.getAddressesProvidersList().call()
    try:
        lendingpool_provider_address = next(filter(lambda provider: provider != '0x0000000000000000000000000000000000000000',
                                                lendingPool_providers))
    except StopIteration:
        return None
    return Toolkit.getContractInstance(lendingpool_provider_address, "LENDING_POOL_PROVIDER.json") # Kovan

def _init_lending_pool():
    # lendingPoolAddressProvider = Toolkit.getContractInstance("0x88757f2f99175387aB4C6a4b3067c77A695b0349", "LENDING_POOL_PROVIDER.json") # Kovan
    # lendingPool_address = '0x2646FcF7F0AbB1ff279ED9845AdE04019C907EBE'
    lendingPool_address = LendingPoolAddressProvider.functions.getLendingPool().call()
    if not lendingPool_address:
        return None
    return Toolkit.getContractInstance(lendingPool_address, 'LENDING_POOL.json')

def _init_protocol_data_provider():
    PROTOCOL_DATA_PROVIDER = '0x3c73A5E5785cAC854D468F727c606C07488a29D6'
    return Toolkit.getContractInstance(PROTOCOL_DATA_PROVIDER, "PROTOCOL_DATA_PROVIDER.json")

w3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
w3.eth.handleRevert = True
LendingPoolAddressProvider = _init_lending_pool_address_provider()
ProtocolDataProvider = _init_protocol_data_provider()
LendingPool = _init_lending_pool()




    # def get_lending_pool():
        


# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]
