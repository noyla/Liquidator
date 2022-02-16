import consts
from toolkit import Toolkit
from users.user_data import UserData


class AssetsService:
    def __init__(self):
        self.protocolDataProvider = Toolkit.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        # init tokens

    @staticmethod
    def get_asset(self, asset: str):
        pass

    def get_user_reserve_data(self, asset: str, user: str):
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset, user).call()
        user_data = UserData.from_raw_list(user_data)



