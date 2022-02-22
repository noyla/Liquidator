import consts
from contracts_service import ContractsService


def _init_lending_pool_address_provider():
    lendingPoolAddressProviderRegistry = ContractsService.getContractInstance(consts.LENDING_POOL_ADDRESS_PROVIDER_REGISTRY, 
                                                                 "LENDING_POOL_PROVIDER_REGISTRY.json")
    lendingPool_providers = lendingPoolAddressProviderRegistry.functions.getAddressesProvidersList().call()
    try:
        lendingpool_provider_address = next(filter(lambda provider: provider != '0x0000000000000000000000000000000000000000',
                                                lendingPool_providers))
    except StopIteration:
        return None
    return ContractsService.getContractInstance(lendingpool_provider_address, "LENDING_POOL_PROVIDER.json") # Kovan

def _init_lending_pool():
    # lendingPoolAddressProvider = Toolkit.getContractInstance("0x88757f2f99175387aB4C6a4b3067c77A695b0349", "LENDING_POOL_PROVIDER.json") # Kovan
    # lendingPool_address = '0x2646FcF7F0AbB1ff279ED9845AdE04019C907EBE'
    lendingPool_address = LendingPoolAddressProvider.functions.getLendingPool().call()
    if not lendingPool_address:
        return None
    return ContractsService.getContractInstance(lendingPool_address, 'LENDING_POOL.json')

def _init_protocol_data_provider():
    return ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
    "PROTOCOL_DATA_PROVIDER.json")
    
def _init_price_oracle():
    price_oracle = LendingPoolAddressProvider.functions.getPriceOracle().call()
    return ContractsService.getContractInstance(price_oracle, "PRICE_ORACLE.json")

LendingPoolAddressProvider = _init_lending_pool_address_provider()
ProtocolDataProvider = _init_protocol_data_provider()
LendingPool = _init_lending_pool()
PriceOracle = _init_price_oracle()