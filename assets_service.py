import consts
from toolkit import Toolkit
from users.user_data import UserData

class AssetsService:
    def __init__(self):
        self.protocolDataProvider = Toolkit.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self.reserves = self._init_reserves()

    def get_asset(self, asset: str):
        aave_address = self.reserves.get(asset, None)
        aave = Toolkit.getContractInstance(aave_address, f"{asset}.json")
        return aave

    def get_user_reserve_data(self, asset: str, user: str):
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset, user).call()
        user_data = UserData.from_raw_list(user_data)
    
    def _init_reserves(self):
        reserves = self.protocolDataProvider.functions.getAllReservesTokens().call()
        if not reserves:
            return {}
        return dict(reserves)

