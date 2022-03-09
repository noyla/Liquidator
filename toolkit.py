import os, psutil
import redis
import consts

from dotenv import load_dotenv
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
        self.redis = redis.Redis(charset="utf-8", decode_responses=True)
    
    def is_connected(self):
        is_connected = toolkit_.w3.isConnected()
        return is_connected
    
    def trace_resoucrce_usage(self):
        process = psutil.Process(os.getpid())
        mem_usage_mb = process.memory_info().rss / 1024 ** 2
        self.redis.set('MEMORY_USAGE', mem_usage_mb)  # in MB 
        print(f'Memory usage: {mem_usage_mb}')

toolkit_ = Toolkit()

load_dotenv()  # take environment variables from .env.