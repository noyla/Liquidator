import os
import consts
from web3 import Web3

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Toolkit(metaclass=Singleton):
    def __init__(self) -> None:
        self.w3 = Web3(Web3.HTTPProvider(consts.PROVIDER_URL))
        self.w3.eth.handleRevert = True
        self.account = self.w3.eth.account.privateKeyToAccount(
            os.environ.get("ACCOUNT1_PRIVATE_KEY"))
    
    def is_connected(self):
        is_connected = toolkit_.w3.isConnected()
        print(is_connected)
        return is_connected

toolkit_ = Toolkit()