import consts
from web3 import Web3

class Toolkit:
    web3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
    web3.eth.handleRevert = True