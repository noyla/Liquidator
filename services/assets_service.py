import consts
from db.engine import session
from services.contracts_service import ContractsService
from models.db.reserve_configuration_data import Reserve
from pools import LendingPool, PriceOracle
from toolkit import toolkit_


class AssetsService:
    def __init__(self):
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self._reserves = None
        self._reserve_configurations = None

    @property
    def reserves(self):
        if not self._reserves:
            self._reserves = self._init_reserves()
        return self._reserves
    
    @property
    def reserve_configurations(self):
        if not self._reserve_configurations:
            self._reserve_configurations = self._init_reserve_configs(self.reserves)
        return self._reserve_configurations

    def get_asset(self, asset: str):
        asset_address = self.reserves.get(asset, None)
        return ContractsService.getContractInstance(asset_address, f"{asset}.json")
    
    def get_reserve_configuraion_data(self, asset: str):
        return self.reserve_configurations.get(asset, None)
    
    def get_allowance(self, asset: str, user: str):
        asset_contract = self.get_asset(asset)
        return asset_contract.functions.allowance(user, LendingPool.address).call()
    
    def get_asset_price(self, asset: str):
        asset_address = self.reserves.get(asset, None)
        return PriceOracle.functions.getAssetPrice(asset_address).call()
    
    def approve(asset_contract: str, amount: int, gas):
        nonce = toolkit_.w3.eth.getTransactionCount(toolkit_.account.address)
        return ContractsService.exec_contract(toolkit_.account, nonce, 
                asset_contract.functions.approve(LendingPool.address, amount), gas)

    def _init_reserves(self):
        reserves = self.protocolDataProvider.functions.getAllReservesTokens().call()
        if not reserves:
            return {}
        return dict(reserves)
    
    def _init_reserve_configs(self, reserves):
        reserve_configs = {}
        for name, reserve_address in reserves.items():
            res = self.protocolDataProvider.functions.getReserveConfigurationData(reserve_address).call()
            res.append(name)
            res.append(reserve_address)
            reserve_configs[name] = Reserve.from_raw_list(res)
        # session.add_all(list(reserve_configs.values()))
        # session.commit()
        return reserve_configs

if __name__ == '__main__':
    d = AssetsService()
