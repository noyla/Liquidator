import json
import consts

from typing import Tuple, Union
from db.engine import session
from models.db.user import User
from models.db.user_reserve_data import UserReserveData
from pools import LendingPool
from services.assets_service import AssetsService
from services.contracts_service import ContractsService
from toolkit import toolkit_


class UsersService:
    def __init__(self) -> None:
        self.protocolDataProvider = ContractsService.getContractInstance(consts.PROTOCOL_DATA_PROVIDER, 
        "PROTOCOL_DATA_PROVIDER.json")
        self._assets_service = None
        pass
    
    @property
    def assets_service(self):
        if not self._assets_service:
            self._assets_service = AssetsService()
        return self._assets_service

    def get_user_data(self, address: str):
        user_data = LendingPool.functions.getUserAccountData(address).call()
        if not user_data:
            return None
        user_data = {'totalCollateralETH': user_data[0], 'totalDebtETH': user_data[1], 'availableBorrowsETH': user_data[2],
                    'currentLiquidationThreshold': user_data[3], 'ltv': user_data[4], 'healthFactor': user_data[5]}
        print(user_data)
        return User.from_dict(user_data)
    
    def get_balance(self, asset_contract: str) -> int:
        return asset_contract.functions.balanceOf(toolkit_.account.address).call()
    
    def get_user_reserve_data(self, asset: str, user: str) -> UserReserveData:
        asset_address = self.assets_service.reserves.get(asset, None)
        user_data = self.protocolDataProvider.functions.getUserReserveData(asset_address, user).call()
        if not user_data:
            return None
        user_data.append(asset)
        user_data.append(user)
        return UserReserveData.from_raw_list(user_data)
    
    def get_collaterals_and_debts(self, user: str) -> Tuple[dict, dict]:
        collaterals = []
        debts = []
        for name, address in self.assets_service.reserves.items():
            user_data = self.get_user_reserve_data(name, user)
            if user_data:
                if user_data.current_aToken_balance != 0 and user_data.usage_as_collateral_enabled:
                    user_data.reserve = name
                    collaterals.append({'userReserveData': user_data})#, 
                                #'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_dict())}')
                elif user_data.current_stable_debt or user_data.current_variable_debt:
                    user_data.reserve = name
                    debts.append({'userReserveData': user_data})#,
                                # 'reserve': name})
                    print(f'User Reserve Data for reserve {name}: {json.dumps(user_data.to_dict())}')
        
        self.save_user_reserve_data([c['userReserveData'] for c in collaterals])
        return collaterals, debts
    
    def save_user_reserve_data(self, user_reserve_data: Union[list, dict]):
        session.add_all(user_reserve_data)
        session.commit()

    def save_user(self, user_data: dict):
        # session.add(user_data)
        session.merge(user_data)
        session.commit()
