from eth_account import Account
import consts
import json
from typing import Tuple
from contracts_service import ContractsService
from models.reserve_configuration_data import ReserveConfigurationData
from pools import LendingPool, PriceOracle
from toolkit import Toolkit
from models.user_data import UserReserveData

class AssetsService:
    def __init__(self):
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self.reserves = self._init_reserves()
        self.reserve_configurations = self._init_reserve_configs(self.reserves)

    def get_asset(self, asset: str):
        asset_address = self.reserves.get(asset, None)
        return ContractsService.getContractInstance(asset_address, f"{asset}.json")

    def get_user_reserve_data(self, asset: str, user: str) -> UserReserveData:
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset, user).call()
        if not user_data:
            return None
        return UserReserveData.from_raw_list(user_data)
    
    def get_reserve_configuraion_data(self, asset: str):
        return self.reserve_configurations.get(asset, None)
    
    def get_allowance(self, asset: str, user: str):
        asset_contract = self.get_asset(asset)
        return asset_contract.functions.allowance(user, LendingPool.address).call()
    
    def get_collaterals_and_debts(self, user: str) -> Tuple[dict, dict]:
        collaterals = []
        debts = []
        for name, address in self.reserves.items():
            user_data = self.get_user_reserve_data(address, user)
            if user_data:
                if user_data.currentATokenBalance != 0 and user_data.usageAsCollateralEnabled:
                    collaterals.append({'userReserveData': user_data, 
                                'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_json())}')
                elif user_data.currentStableDebt or user_data.currentVariableDebt:
                    debts.append({'userReserveData': user_data,
                                'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_json())}')
            
        return collaterals, debts
    
    def get_asset_price(self, asset: str):
        asset_address = self.reserves.get(asset, None)
        return PriceOracle.functions.getAssetPrice(asset_address).call()
    
    def approve(asset_contract: str, amount: int):
        nonce = Toolkit.w3().eth.getTransactionCount(Toolkit.account().address)
        return ContractsService.exec_contract(Toolkit.account(), nonce, 
                        asset_contract.functions.approve(LendingPool.address, amount))
        
    def get_balance(self, asset_contract: str) -> int:
        return asset_contract.functions.balanceOf(Toolkit.account().address).call()

    def _init_reserves(self):
        reserves = self.protocolDataProvider.functions.getAllReservesTokens().call()
        if not reserves:
            return {}
        return dict(reserves)
    
    def _init_reserve_configs(self, reserves):
        reserve_configs = {}
        for name, reserve_address in reserves.items():
            res = self.protocolDataProvider.functions.getReserveConfigurationData(reserve_address).call()
            reserve_configs[name] = ReserveConfigurationData.from_raw_list(res)
        return reserve_configs

if __name__ == '__main__':
    d = AssetsService()
