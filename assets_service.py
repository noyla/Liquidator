import consts
from contracts_service import ContractsService
from toolkit import Toolkit
from models.user_data import UserData

class AssetsService:
    def __init__(self):
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self.reserves = self._init_reserves()
        self.reserve_configurations = self._init_reserve_configs(self.reserves)

    def get_asset(self, asset: str):
        asset_address = self.reserves.get(asset, None)
        asset_contract = ContractsService.getContractInstance(asset_address, f"{asset}.json")
        return asset_contract

    def get_user_reserve_data(self, asset: str, user: str) -> UserData:
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset, user).call()
        if not user_data:
            return None
        # user_data = {'currentATokenBalance': user_data[0], 'currentStableDebt': user_data[1],
        #              'currentVariableDebt': user_data[2], 'principalStableDebt': user_data[3],
        #              'scaledVariableDebt': user_data[3], 'stableBorrowRate': user_data[4],
        #              'liquidityRate': user_data[5], 'stableRateLastUpdated': user_data[6],
        #              'usageAsCollateralEnabled': user_data[7]}
        # return user_data
        return UserData.from_raw_list(user_data)
    
    def get_reserve_configuraion_data(self, asset: str):
        return self.reserve_configurations.get(asset)
    
    def get_user_collateral_assets(self, user: str) -> dict:
        collaterals = []
        for name, address in self.reserves.items():
            user_data = self.get_user_reserve_data(address, user)
            if not user_data or user_data.currentATokenBalance == 0:
                continue
            print(f'User Reserve Data for reserve {name}: {user_data}')
            collaterals.append({'userReserveData': user_data, 
                                'reserve': name})
        return collaterals
    
    def _init_reserves(self):
        reserves = self.protocolDataProvider.functions.getAllReservesTokens().call()
        if not reserves:
            return {}
        return dict(reserves)
    
    def _init_reserve_configs(self, reserves):
        for name, reserve_address in reserves.items():
            reserve_configs = self.protocolDataProvider.functions.getReserveConfigurationData(reserve_address).call()

